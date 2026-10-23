"""Evaluation runner comparing pipeline outputs against ground truth cases."""

from __future__ import annotations

import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

from core.extractor import extract_form
from core.safety import check_danger
from core.verifier import verify_form


def _get_audio_file(case_id: str) -> tuple[str | None, str | None]:
    """Find audio file matching eval/audio/<case_id>.* and return (path, mime)."""
    matches = glob.glob(os.path.join("eval", "audio", f"{case_id}.*"))
    if not matches:
        return None, None
    path = matches[0]
    p_lower = path.lower()
    if ".wav" in p_lower:
        mime = "audio/wav"
    elif ".mp3" in p_lower:
        mime = "audio/mp3"
    elif ".ogg" in p_lower:
        mime = "audio/ogg"
    else:
        mime = "audio/mp4"
    return path, mime


def _contains(needle: str, haystack: str) -> bool:
    return needle.strip().lower() in haystack.strip().lower()


def _check_field(exp, act) -> bool:
    if exp is None:
        return True
    if isinstance(exp, list):
        if not exp:
            return not act
        act_str = " ".join(act).lower() if isinstance(act, list) else str(act or "").lower()
        return all(_contains(x, act_str) for x in exp)
    return _contains(str(exp), str(act or ""))


def run_evaluation() -> dict:
    cases_file = os.path.join("eval", "cases.json")
    with open(cases_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    tot_exp, cor_exp, hall_cnt = 0, 0, 0
    d_true, d_flagged, false_alarms = 0, 0, 0
    results, cases_table = [], []

    print(f"{'Case ID':<22} | {'Status':<8} | {'Risk':<7} | {'Diff / Notes'}", flush=True)
    print("-" * 75, flush=True)

    for c in cases:
        cid, exp = c["id"], c["expected"]
        audio_path, mime = _get_audio_file(cid)

        if not audio_path:
            print(f"{cid:<22} | {'MISSING':<8} | {'-':<7} | Audio file not found", flush=True)
            cases_table.append({"Case ID": cid, "Status": "MISSING", "Risk": "-", "Notes": "Audio file not found"})
            results.append({"id": cid, "status": "MISSING", "expected": exp, "actual": None, "diff": "Audio missing"})
            continue

        with open(audio_path, "rb") as f:
            data = f.read()

        try:
            form = extract_form(data, mime)
            form = verify_form(form, check_llm=False)
            safety = check_danger(form)
        except Exception as e:
            print(f"{cid:<22} | {'ERROR':<8} | {'-':<7} | {e}", flush=True)
            cases_table.append({"Case ID": cid, "Status": "ERROR", "Risk": "-", "Notes": str(e)})
            continue

        act_map = {
            "name": form.name.value, "age": form.age.value, "village": form.village.value,
            "symptoms": [s.value for s in form.symptoms if s.value], "duration": form.duration.value,
            "temperature": form.temperature.value, "medicines": [m.value for m in form.medicines_taken if m.value],
            "pregnant": form.pregnant.value,
        }

        diffs = []
        for k in ["name", "age", "village", "symptoms", "duration", "medicines", "pregnant"]:
            if exp.get(k) is not None:
                tot_exp += 1
                if _check_field(exp[k], act_map.get(k)):
                    cor_exp += 1
                else:
                    diffs.append(f"{k}: exp {exp[k]}, got {act_map.get(k)}")

        for ns in exp.get("not_said", []):
            val = act_map.get(ns)
            if val is not None and val != "" and val != []:
                hall_cnt += 1
                diffs.append(f"hallucinated {ns}={val}")

        if exp.get("danger") is True:
            d_true += 1
            if safety.risk in ("medium", "high"):
                d_flagged += 1
            else:
                diffs.append("missed expected danger")
        elif exp.get("danger") is False:
            if safety.risk == "high":
                false_alarms += 1
                diffs.append("false alarm: risk is high")

        status = "FAIL" if diffs else "PASS"
        notes = "; ".join(diffs) if diffs else "All matched"
        print(f"{cid:<22} | {status:<8} | {safety.risk:<7} | {notes}", flush=True)
        cases_table.append({"Case ID": cid, "Status": status, "Risk": safety.risk, "Notes": notes})
        results.append({"id": cid, "status": status, "expected": exp, "actual": act_map, "risk": safety.risk, "diff": notes})

    field_acc = round(cor_exp / tot_exp, 3) if tot_exp > 0 else 0.0
    danger_rec = round(d_flagged / d_true, 3) if d_true > 0 else 0.0
    metrics = {
        "field_accuracy": field_acc, "hallucination_count": hall_cnt,
        "danger_recall": danger_rec, "false_alarms": false_alarms,
    }

    print("-" * 75, flush=True)
    print(f"Field Accuracy:      {field_acc:.1%} ({cor_exp}/{tot_exp})", flush=True)
    print(f"Hallucination Count: {hall_cnt}", flush=True)
    print(f"Danger Recall:       {danger_rec:.1%} ({d_flagged}/{d_true})", flush=True)
    print(f"False Alarms:        {false_alarms}", flush=True)

    out_data = {"metrics": metrics, "cases": results, "cases_table": cases_table}
    res_path = os.path.join("eval", "results.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved results to {res_path}", flush=True)
    return out_data


if __name__ == "__main__":
    run_evaluation()

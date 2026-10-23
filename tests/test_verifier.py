"""Tests for deterministic evidence verification in PatientForm."""

from core.schema import Item, PatientForm
from core.verifier import verify_form


def _make_test_form(
    transcript: str,
    name_val: str = "Sunita",
    name_ev: str = "मेरा नाम सुनीता है",
    pregnant_val: str | None = None,
    pregnant_ev: str | None = None,
    symptoms: list[tuple[str, str]] | None = None,
) -> PatientForm:
    """Build a hand-made PatientForm for testing."""
    empty_item = Item(value=None, evidence=None, confidence="low")
    sym_items = [
        Item(value=val, evidence=ev, confidence="high")
        for val, ev in (symptoms or [])
    ]
    return PatientForm(
        transcript=transcript,
        name=Item(value=name_val, evidence=name_ev, confidence="high"),
        age=empty_item,
        gender=empty_item,
        village=empty_item,
        symptoms=sym_items,
        duration=empty_item,
        temperature=empty_item,
        medicines_taken=[],
        pregnant=Item(value=pregnant_val, evidence=pregnant_ev, confidence="high") if pregnant_val else empty_item,
        pregnancy_details=empty_item,
        danger_signs_llm=[],
        missing_info=[],
        follow_up_questions_hi=[],
        summary_hi="Test summary",
    )


def test_unsupported_evidence_removed():
    """Unsupported field is removed: value set to None, confidence 'low', added to missing_info."""
    form = _make_test_form(
        transcript="नमस्ते, मेरा नाम सुनीता है। मुझे सिरदर्द है।",
        pregnant_val="yes",
        pregnant_ev="she is eight months pregnant",
    )
    verified = verify_form(form, check_llm=False)
    assert verified.pregnant.value is None
    assert verified.pregnant.confidence == "low"
    assert "pregnant" in verified.missing_info


def test_supported_evidence_kept():
    """Supported field with matching evidence in transcript is kept intact."""
    form = _make_test_form(
        transcript="नमस्ते, मेरा नाम सुनीता है।",
        name_val="Sunita",
        name_ev="मेरा नाम सुनीता है",
    )
    verified = verify_form(form, check_llm=False)
    assert verified.name.value == "Sunita"
    assert verified.name.confidence == "high"
    assert "name" not in verified.missing_info


def test_fuzzy_evidence_match():
    """Evidence matching transcript with minor punctuation or spacing differences is preserved."""
    form = _make_test_form(
        transcript="जी, मेरा नाम   सुनीता   है!",
        name_val="Sunita",
        name_ev="मेरा नाम सुनीता है",
    )
    verified = verify_form(form, check_llm=False)
    assert verified.name.value == "Sunita"


def test_unsupported_symptom_removed():
    """Symptom whose evidence does not appear in transcript is removed."""
    form = _make_test_form(
        transcript="मुझे केवल सिरदर्द है",
        symptoms=[
            ("headache", "सिरदर्द"),
            ("vomiting", "बहुत उल्टी हो रही है"),
        ],
    )
    verified = verify_form(form, check_llm=False)
    assert verified.symptoms[0].value == "headache"
    assert verified.symptoms[1].value is None
    assert verified.symptoms[1].confidence == "low"

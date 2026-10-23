"""Tests for rule-based clinical danger signs evaluation."""

from core.safety import check_danger
from core.schema import Item, PatientForm


def _make_form(
    transcript: str = "",
    age: str = "25",
    pregnant: str | None = None,
    symptoms: list[str] | None = None,
    duration: str | None = None,
) -> PatientForm:
    """Helper to build a valid PatientForm by hand for testing."""
    sym_items = [
        Item(value=s, evidence=s, confidence="high")
        for s in (symptoms or [])
    ]
    empty_item = Item(value=None, evidence=None, confidence="low")

    return PatientForm(
        transcript=transcript,
        name=Item(value="Patient", evidence="Patient", confidence="high"),
        age=Item(value=age, evidence=age, confidence="high"),
        gender=Item(value="female", evidence="female", confidence="high"),
        village=empty_item,
        symptoms=sym_items,
        duration=Item(value=duration, evidence=duration, confidence="high") if duration else empty_item,
        temperature=empty_item,
        medicines_taken=[],
        pregnant=Item(value=pregnant, evidence=pregnant, confidence="high") if pregnant else empty_item,
        pregnancy_details=empty_item,
        danger_signs_llm=[],
        missing_info=[],
        follow_up_questions_hi=[],
        summary_hi="Test summary",
    )


def test_r1_pregnant_danger():
    """R1: Pregnant patient with severe headache or swelling -> HIGH risk."""
    form = _make_form(
        transcript="मुझे बहुत तेज सिरदर्द हो रहा है",
        pregnant="yes",
        symptoms=["severe headache"],
    )
    result = check_danger(form)
    assert result.risk == "high"
    assert any(f.rule_id == "R1" for f in result.flags)
    assert "doctor" in result.flags[0].reason_en.lower()


def test_r2_child_under_5_danger():
    """R2: Child under 5 years with fast breathing or vomiting -> HIGH risk."""
    form = _make_form(
        transcript="बच्चे को तेज़ सांस आ रही है और उल्टी हो रही है",
        age="3",
        symptoms=["fast breathing", "repeated vomiting"],
    )
    result = check_danger(form)
    assert result.risk == "high"
    assert any(f.rule_id == "R2" for f in result.flags)


def test_r3_emergency_anyone():
    """R3: Anyone with unconsciousness, fits or severe chest pain -> HIGH risk."""
    form = _make_form(
        transcript="मरीज अचानक बेहोश हो गया और सीने में दर्द है",
        age="45",
        symptoms=["chest pain", "unconscious"],
    )
    result = check_danger(form)
    assert result.risk == "high"
    assert any(f.rule_id == "R3" for f in result.flags)


def test_r4_fever_3_days():
    """R4: Fever for 3 or more days without emergency signs -> MEDIUM risk."""
    form = _make_form(
        transcript="मुझे 4 दिन से बुखार आ रहा है",
        age="28",
        symptoms=["fever"],
        duration="4 days",
    )
    result = check_danger(form)
    assert result.risk == "medium"
    assert any(f.rule_id == "R4" for f in result.flags)


def test_no_danger():
    """Normal mild case -> LOW risk and no danger flags."""
    form = _make_form(
        transcript="कल से हल्की सर्दी और जुकाम है",
        age="25",
        symptoms=["mild cold"],
        duration="1 day",
    )
    result = check_danger(form)
    assert result.risk == "low"
    assert len(result.flags) == 0

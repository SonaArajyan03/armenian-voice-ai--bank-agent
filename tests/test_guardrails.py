from bank_support.guardrails import detect_scope


def test_detects_credit_scope_in_armenian() -> None:
    result = detect_scope("Մելլաթ բանկի հիփոթեքային վարկերի մասին տեղեկություն տուր")
    assert result.in_scope is True
    assert result.topic == "credits"
    assert "mellat bank" in result.banks


def test_rejects_card_question() -> None:
    result = detect_scope("What are the card maintenance fees at ACBA?")
    assert result.in_scope is False

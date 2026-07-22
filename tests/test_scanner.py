from scanner import scan_for_risks


def test_scan_for_risks_green_for_plain_sample_text():
    result = scan_for_risks("This is a generic brainstorming note about lunch.")

    assert result["risk_score"] == "Green"
    assert result["findings"] == []


def test_scan_for_risks_red_for_pii():
    result = scan_for_risks("Contact Jane at jane@example.com before the review.")

    assert result["risk_score"] == "Red"
    assert result["possible_pii"] is True
    assert "Email address" in result["findings"]
    assert "jane@example.com" not in result["redacted_text"]
    assert "[EMAIL_REDACTED]" in result["redacted_text"]


def test_scan_for_risks_yellow_for_govcon_procurement_terms():
    result = scan_for_risks("The COR needs the updated spend plan for the PWS.")

    assert result["risk_score"] == "Yellow"
    assert result["possible_government_data"] is True
    assert result["possible_financial_data"] is True


def test_scan_for_risks_returns_redaction_preview_summary():
    result = scan_for_risks(
        "Call 555-123-4567 about CUI and contract ABCD-1234-XYZ."
    )

    assert result["redaction_count"] == 4
    assert "[PHONE_REDACTED]" in result["redacted_text"]
    assert "[CUI_TERM_REDACTED]" in result["redacted_text"]
    assert "[GOV_TERM_REDACTED]" in result["redacted_text"]
    assert "[DOCUMENT_ID_REDACTED]" in result["redacted_text"]
    assert result["redactions"] == [
        {
            "label": "Phone number",
            "placeholder": "[PHONE_REDACTED]",
            "count": 1,
        },
        {
            "label": "Possible contract or document identifier",
            "placeholder": "[DOCUMENT_ID_REDACTED]",
            "count": 1,
        },
        {
            "label": "Possible CUI / FOUO indicator",
            "placeholder": "[CUI_TERM_REDACTED]",
            "count": 1,
        },
        {
            "label": "Possible government-related data",
            "placeholder": "[GOV_TERM_REDACTED]",
            "count": 1,
        },
    ]

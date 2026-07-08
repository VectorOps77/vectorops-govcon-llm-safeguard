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


def test_scan_for_risks_yellow_for_govcon_procurement_terms():
    result = scan_for_risks("The COR needs the updated spend plan for the PWS.")

    assert result["risk_score"] == "Yellow"
    assert result["possible_government_data"] is True
    assert result["possible_financial_data"] is True

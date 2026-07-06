import re


def scan_for_risks(text: str) -> dict:
    """
    Scan text for possible GovCon, PII, CUI, financial, and procurement risk indicators.
    This is a rule-based scanner. It does not guarantee classification.
    """

    findings = {
        "possible_pii": False,
        "possible_contract_number": False,
        "possible_government_data": False,
        "possible_cui": False,
        "possible_financial_data": False,
        "risk_score": "Green",
        "findings": [],
    }

    pii_patterns = {
        "Email address": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "Phone number": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "SSN-like pattern": r"\b\d{3}-\d{2}-\d{4}\b",
    }

    gov_keywords = [
        "DoD",
        "DHS",
        "Navy",
        "Army",
        "Air Force",
        "Marine Corps",
        "contract",
        "task order",
        "COR",
        "COTR",
        "government",
        "federal",
        "deliverable",
        "SOW",
        "PWS",
    ]

    cui_keywords = [
        "CUI",
        "FOUO",
        "controlled unclassified information",
        "export controlled",
        "ITAR",
        "EAR",
        "sensitive but unclassified",
    ]

    financial_keywords = [
        "funding",
        "budget",
        "invoice",
        "CLIN",
        "SLIN",
        "cost",
        "obligation",
        "burn rate",
        "spend plan",
        "procurement",
        "acquisition",
    ]

    for label, pattern in pii_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            findings["possible_pii"] = True
            findings["findings"].append(label)

    if re.search(r"\b[A-Z0-9]{4,}[-][A-Z0-9-]{4,}\b", text, re.IGNORECASE):
        findings["possible_contract_number"] = True
        findings["findings"].append("Possible contract or document identifier")

    if any(keyword.lower() in text.lower() for keyword in gov_keywords):
        findings["possible_government_data"] = True
        findings["findings"].append("Possible government-related data")

    if any(keyword.lower() in text.lower() for keyword in cui_keywords):
        findings["possible_cui"] = True
        findings["findings"].append("Possible CUI / FOUO indicator")

    if any(keyword.lower() in text.lower() for keyword in financial_keywords):
        findings["possible_financial_data"] = True
        findings["findings"].append("Possible financial or procurement data")

    if findings["possible_cui"] or findings["possible_pii"]:
        findings["risk_score"] = "Red"
    elif (
        findings["possible_government_data"]
        or findings["possible_financial_data"]
        or findings["possible_contract_number"]
    ):
        findings["risk_score"] = "Yellow"
    else:
        findings["risk_score"] = "Green"

    return findings
import re


PII_PATTERNS = {
    "Email address": {
        "pattern": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "placeholder": "[EMAIL_REDACTED]",
    },
    "Phone number": {
        "pattern": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "placeholder": "[PHONE_REDACTED]",
    },
    "SSN-like pattern": {
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "placeholder": "[SSN_REDACTED]",
    },
}

CONTRACT_IDENTIFIER_PATTERN = r"\b[A-Z0-9]{4,}[-][A-Z0-9-]{4,}\b"

GOV_KEYWORDS = [
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

CUI_KEYWORDS = [
    "CUI",
    "FOUO",
    "controlled unclassified information",
    "export controlled",
    "ITAR",
    "EAR",
    "sensitive but unclassified",
]

FINANCIAL_KEYWORDS = [
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


def _replace_pattern(text: str, pattern: str, placeholder: str) -> tuple[str, int]:
    return re.subn(pattern, placeholder, text, flags=re.IGNORECASE)


def _replace_keywords(
    text: str, keywords: list[str], placeholder: str
) -> tuple[str, int]:
    updated_text = text
    total_count = 0

    for keyword in sorted(keywords, key=len, reverse=True):
        pattern = rf"(?<![A-Za-z0-9]){re.escape(keyword)}(?![A-Za-z0-9])"
        updated_text, count = _replace_pattern(updated_text, pattern, placeholder)
        total_count += count

    return updated_text, total_count


def redact_sensitive_text(text: str) -> dict:
    """Return a redacted preview without exposing matched sensitive values."""
    redacted_text = text
    redactions = []

    for label, config in PII_PATTERNS.items():
        redacted_text, count = _replace_pattern(
            redacted_text, config["pattern"], config["placeholder"]
        )
        if count:
            redactions.append(
                {
                    "label": label,
                    "placeholder": config["placeholder"],
                    "count": count,
                }
            )

    redacted_text, contract_count = _replace_pattern(
        redacted_text, CONTRACT_IDENTIFIER_PATTERN, "[DOCUMENT_ID_REDACTED]"
    )
    if contract_count:
        redactions.append(
            {
                "label": "Possible contract or document identifier",
                "placeholder": "[DOCUMENT_ID_REDACTED]",
                "count": contract_count,
            }
        )

    keyword_groups = [
        ("Possible CUI / FOUO indicator", CUI_KEYWORDS, "[CUI_TERM_REDACTED]"),
        ("Possible government-related data", GOV_KEYWORDS, "[GOV_TERM_REDACTED]"),
        (
            "Possible financial or procurement data",
            FINANCIAL_KEYWORDS,
            "[PROCUREMENT_TERM_REDACTED]",
        ),
    ]

    for label, keywords, placeholder in keyword_groups:
        redacted_text, count = _replace_keywords(redacted_text, keywords, placeholder)
        if count:
            redactions.append(
                {
                    "label": label,
                    "placeholder": placeholder,
                    "count": count,
                }
            )

    return {
        "redacted_text": redacted_text,
        "redactions": redactions,
        "redaction_count": sum(redaction["count"] for redaction in redactions),
    }


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
        "redacted_text": text,
        "redactions": [],
        "redaction_count": 0,
    }

    for label, config in PII_PATTERNS.items():
        if re.search(config["pattern"], text, re.IGNORECASE):
            findings["possible_pii"] = True
            findings["findings"].append(label)

    if re.search(CONTRACT_IDENTIFIER_PATTERN, text, re.IGNORECASE):
        findings["possible_contract_number"] = True
        findings["findings"].append("Possible contract or document identifier")

    if any(keyword.lower() in text.lower() for keyword in GOV_KEYWORDS):
        findings["possible_government_data"] = True
        findings["findings"].append("Possible government-related data")

    if any(keyword.lower() in text.lower() for keyword in CUI_KEYWORDS):
        findings["possible_cui"] = True
        findings["findings"].append("Possible CUI / FOUO indicator")

    if any(keyword.lower() in text.lower() for keyword in FINANCIAL_KEYWORDS):
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

    findings.update(redact_sensitive_text(text))

    return findings

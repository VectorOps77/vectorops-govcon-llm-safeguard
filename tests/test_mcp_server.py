from mcp_server import SERVER_NAME, scan_govcon_prompt


def test_scan_govcon_prompt_returns_structured_results():
    result = scan_govcon_prompt(
        "Draft Navy task order update for contract ABCD-1234-XYZ."
    )

    assert result["risk_score"] == "Yellow"
    assert result["possible_government_data"] is True
    assert result["possible_contract_number"] is True
    assert "Possible government-related data" in result["findings"]


def test_server_name_identifies_vectorops_safeguard():
    assert SERVER_NAME == "VectorOps GovCon LLM Safeguard Checker"

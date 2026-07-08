from scanner import scan_for_risks

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    FastMCP = None


SERVER_NAME = "VectorOps GovCon LLM Safeguard Checker"


def scan_govcon_prompt(prompt: str) -> dict:
    """Return GovCon prompt risk results for MCP-compatible AI tools."""
    return scan_for_risks(prompt)


def create_mcp_server():
    if FastMCP is None:
        raise RuntimeError(
            "The MCP SDK is not installed. Run `pip install -r requirements.txt` first."
        )

    server = FastMCP(SERVER_NAME)
    server.tool()(scan_govcon_prompt)
    return server


mcp = create_mcp_server() if FastMCP is not None else None


if __name__ == "__main__":
    if mcp is None:
        raise SystemExit(
            "The MCP SDK is not installed. Run `pip install -r requirements.txt` first."
        )

    mcp.run(transport="stdio")

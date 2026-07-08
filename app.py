import streamlit as st
from scanner import scan_for_risks

st.set_page_config(
    page_title="VectorOps GovCon LLM Safeguard",
    page_icon="🛡️",
)

st.title("🛡️ VectorOps GovCon LLM Data Safeguard Checker")

st.write(
    "Scan text before submitting it to an AI model. "
    "This tool checks for possible PII, CUI, government, contract, financial, "
    "and procurement-sensitive indicators."
)

st.info(
    "Use fake/sample data only. Do not paste real government, client, classified, "
    "CUI, proprietary, or personal information."
)

user_prompt = st.text_area(
    "Paste text to scan",
    height=220,
    placeholder="Example: John Doe, john.doe@example.com, Navy task order update...",
)

if st.button("Run Safeguard Check"):
    if not user_prompt.strip():
        st.warning("Paste some text first.")
    else:
        results = scan_for_risks(user_prompt)

        st.subheader("Risk Score")

        if results["risk_score"] == "Green":
            st.success("🟢 Green — No obvious sensitive indicators detected.")
        elif results["risk_score"] == "Yellow":
            st.warning("🟡 Yellow — Review recommended before using with an AI model.")
        else:
            st.error("🔴 Red — Do not submit without security/data owner review.")

        st.subheader("Scanner Findings")

        if results["findings"]:
            for finding in results["findings"]:
                st.write(f"- {finding}")
        else:
            st.write("- No obvious risk indicators found.")

        st.subheader("Governance Questions")

        st.write("**What data goes into the model?**")
        st.write("The pasted text would be the data submitted for AI processing.")

        st.write("**Is it government data?**")
        if results["possible_government_data"]:
            st.write("Possibly yes. Government-related terms were detected.")
        else:
            st.write("No obvious government indicators were detected.")

        st.write("**Is it logged?**")
        st.write(
            "This local app does not intentionally log prompt content, but future versions "
            "should clearly define audit logging, storage, and retention rules."
        )

        st.write("**Is it used for training?**")
        st.write(
            "A local LLM through Ollama does not train itself from prompts by default. "
            "However, users should still verify app storage, telemetry, and model settings."
        )

        st.write("**Who approves outputs?**")
        if results["risk_score"] == "Red":
            st.write("Security, data owner, PM, and contract leadership should review.")
        elif results["risk_score"] == "Yellow":
            st.write("PM, data owner, COR/COTR, or contract lead review is recommended.")
        else:
            st.write("Standard project team review may be sufficient.")

        st.subheader("Recommendation")

        if results["risk_score"] == "Green":
            st.success("Safe for low-risk testing with sample data.")
        elif results["risk_score"] == "Yellow":
            st.warning("Needs review before use with an AI model.")
        else:
            st.error("Do not submit without approval.")

import html

import streamlit as st

from scanner import scan_for_risks


st.set_page_config(
    page_title="VectorOps GovCon LLM Safeguard",
    page_icon="⚓",
    layout="wide",
)


COLORS = {
    "Green": {
        "label": "Green",
        "tone": "#13795b",
        "surface": "#e8f6ef",
        "border": "#9fd8bf",
        "message": "No obvious sensitive indicators detected.",
        "recommendation": "Safe for low-risk testing with sample data.",
    },
    "Yellow": {
        "label": "Yellow",
        "tone": "#9a6700",
        "surface": "#fff4d6",
        "border": "#e9c46a",
        "message": "Review recommended before using with an AI model.",
        "recommendation": "Needs review before use with an AI model.",
    },
    "Red": {
        "label": "Red",
        "tone": "#b42318",
        "surface": "#fde7e9",
        "border": "#f1aeb5",
        "message": "Do not submit without security or data owner review.",
        "recommendation": "Do not submit without approval.",
    },
}

SAMPLE_PROMPTS = {
    "Green sample": "This is a generic brainstorming note about team meeting topics.",
    "Yellow sample": "The COR needs the updated spend plan for the Navy PWS.",
    "Red sample": "Contact Jane at jane@example.com about this CUI task order.",
}


def load_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --navy: #071d3a;
                --navy-2: #0c356a;
                --blue: #1b5f97;
                --gold: #c5a253;
                --gold-2: #f2d488;
                --ink: #102033;
                --muted: #5f6f83;
                --line: #d7dee8;
                --paper: #f7f9fc;
                --white: #ffffff;
                --teal: #1f7a8c;
            }

            .stApp {
                background:
                    linear-gradient(180deg, rgba(7, 29, 58, 0.06), rgba(247, 249, 252, 0) 280px),
                    var(--paper);
                color: var(--ink);
            }

            .block-container {
                max-width: 1180px;
                padding-top: 1.25rem;
                padding-bottom: 3rem;
            }

            header[data-testid="stHeader"] {
                background: var(--paper);
                color: var(--navy);
            }

            [data-testid="stToolbar"],
            [data-testid="stToolbar"] * {
                color: var(--navy);
            }

            [data-testid="stSidebar"] {
                background: #081f3f;
                border-right: 1px solid rgba(197, 162, 83, 0.45);
            }

            [data-testid="stSidebar"] * {
                color: #edf4ff;
            }

            [data-testid="stSidebar"] div.stButton > button {
                width: 100%;
                border: 1px solid rgba(242, 212, 136, 0.45);
                background: rgba(255, 255, 255, 0.08);
                color: #ffffff;
            }

            .hero {
                border: 1px solid rgba(197, 162, 83, 0.75);
                background:
                    radial-gradient(circle at 85% 15%, rgba(242, 212, 136, 0.23), transparent 28%),
                    linear-gradient(135deg, #061a33 0%, #0c356a 62%, #123f68 100%);
                border-radius: 8px;
                color: white;
                margin-bottom: 1rem;
                overflow: hidden;
                position: relative;
            }

            .hero-inner {
                align-items: center;
                display: grid;
                gap: 1.5rem;
                grid-template-columns: minmax(0, 1fr) 190px;
                padding: 1.5rem 1.6rem;
            }

            .eyebrow {
                color: var(--gold-2);
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0.08em;
                margin-bottom: 0.35rem;
                text-transform: uppercase;
            }

            .hero h1 {
                color: #ffffff;
                font-size: clamp(2rem, 3.8vw, 3.2rem);
                line-height: 1.02;
                margin: 0 0 0.75rem;
                letter-spacing: 0;
            }

            .hero p {
                color: #dfeaf7;
                font-size: 1.02rem;
                line-height: 1.55;
                margin: 0;
                max-width: 770px;
            }

            .hero-mark {
                align-items: center;
                display: flex;
                justify-content: center;
            }

            .panel {
                background: var(--white);
                border: 1px solid var(--line);
                border-radius: 8px;
                box-shadow: 0 16px 45px rgba(7, 29, 58, 0.08);
                padding: 1rem;
            }

            .panel h2,
            .panel h3 {
                color: var(--navy);
                letter-spacing: 0;
                margin-top: 0;
            }

            .scanner-title {
                background: linear-gradient(135deg, var(--navy), var(--navy-2));
                border: 1px solid rgba(197, 162, 83, 0.5);
                border-radius: 8px;
                color: #ffffff;
                font-size: 1.35rem;
                font-weight: 800;
                margin: 0 0 1rem;
                padding: 0.8rem 1rem;
            }

            .notice {
                align-items: flex-start;
                background: #eef5fb;
                border-left: 5px solid var(--gold);
                border-radius: 8px;
                color: var(--ink);
                display: flex;
                gap: 0.75rem;
                margin: 0.75rem 0 1rem;
                padding: 0.85rem 1rem;
            }

            .notice strong {
                color: var(--navy);
            }

            .stTextArea textarea {
                border: 1px solid #aebbd0;
                border-radius: 8px;
                background: #071d3a;
                caret-color: var(--gold-2);
                color: #ffffff !important;
                font-size: 1rem;
            }

            .stTextArea textarea:focus {
                background: #071d3a;
                border-color: var(--gold);
                color: #ffffff !important;
                box-shadow: 0 0 0 1px rgba(197, 162, 83, 0.45);
            }

            .stTextArea textarea::placeholder {
                color: #c8d6e8;
                opacity: 1;
            }

            div.stButton > button:first-child {
                background: linear-gradient(135deg, var(--gold), #e4c46e);
                border: 1px solid #a8883e;
                border-radius: 6px;
                color: #071d3a;
                font-weight: 800;
                min-height: 2.85rem;
            }

            div.stButton > button:first-child:hover {
                border-color: #80651f;
                color: #071d3a;
            }

            .risk-card {
                border-radius: 8px;
                border: 1px solid;
                padding: 1rem;
            }

            .risk-label {
                font-size: 0.78rem;
                font-weight: 800;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }

            .risk-score {
                font-size: 2.3rem;
                font-weight: 900;
                line-height: 1;
                margin: 0.35rem 0;
            }

            .finding-grid {
                display: grid;
                gap: 0.7rem;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                margin-top: 0.75rem;
            }

            .finding {
                background: #f8fafc;
                border: 1px solid var(--line);
                border-radius: 8px;
                padding: 0.75rem;
            }

            .finding-on {
                border-color: rgba(197, 162, 83, 0.8);
                box-shadow: inset 4px 0 0 var(--gold);
            }

            .finding-title {
                color: var(--navy);
                font-weight: 800;
                margin-bottom: 0.2rem;
            }

            .finding-body {
                color: var(--muted);
                font-size: 0.9rem;
                line-height: 1.35;
            }

            .redaction-preview {
                background: #071d3a;
                border: 1px solid rgba(197, 162, 83, 0.65);
                border-radius: 8px;
                box-shadow: 0 12px 30px rgba(7, 29, 58, 0.12);
                color: #ffffff;
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                line-height: 1.5;
                margin: 0.6rem 0 1rem;
                overflow-x: auto;
                padding: 1rem;
                white-space: pre-wrap;
            }

            .redaction-summary {
                color: var(--muted);
                margin: 0.35rem 0 0.8rem;
            }

            .question {
                border-top: 1px solid var(--line);
                padding: 0.8rem 0;
            }

            .question:first-child {
                border-top: 0;
                padding-top: 0;
            }

            .question strong {
                color: var(--navy);
                display: block;
                margin-bottom: 0.15rem;
            }

            .question span {
                color: var(--muted);
                line-height: 1.45;
            }

            @media (max-width: 760px) {
                .hero-inner {
                    grid-template-columns: 1fr;
                }

                .hero-mark {
                    justify-content: flex-start;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero">
            <div class="hero-inner">
                <div>
                    <div class="eyebrow">AI Governance Safeguard</div>
                    <h1>VectorOps GovCon LLM Safeguard Checker</h1>
                    <p>
                        Scan prompt text before it reaches an AI model. The checker flags
                        possible PII, CUI, contract, financial, procurement, and government
                        indicators, then gives a clear governance recommendation.
                    </p>
                </div>
                <div class="hero-mark" aria-hidden="true">
                    <svg width="168" height="168" viewBox="0 0 168 168" role="img">
                        <defs>
                            <linearGradient id="shieldFill" x1="0" x2="1">
                                <stop offset="0%" stop-color="#f2d488"/>
                                <stop offset="100%" stop-color="#c5a253"/>
                            </linearGradient>
                        </defs>
                        <circle cx="84" cy="84" r="76" fill="none" stroke="#f2d488" stroke-width="3"/>
                        <circle cx="84" cy="84" r="57" fill="rgba(255,255,255,0.08)" stroke="#dfeaf7" stroke-width="2"/>
                        <path d="M84 34l38 14v30c0 31-16 49-38 58-22-9-38-27-38-58V48l38-14z"
                              fill="url(#shieldFill)" stroke="#fff3c2" stroke-width="2"/>
                        <path d="M84 49v72" stroke="#071d3a" stroke-width="6" stroke-linecap="round"/>
                        <path d="M57 76h54" stroke="#071d3a" stroke-width="6" stroke-linecap="round"/>
                        <path d="M67 98c8 8 26 8 34 0" fill="none" stroke="#071d3a" stroke-width="6" stroke-linecap="round"/>
                        <circle cx="84" cy="76" r="10" fill="#071d3a"/>
                        <path d="M84 14v16M84 138v16M14 84h16M138 84h16" stroke="#f2d488" stroke-width="4" stroke-linecap="round"/>
                    </svg>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def set_sample_prompt(prompt: str) -> None:
    st.session_state["prompt_text"] = prompt


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### VectorOps")
        st.caption("GovCon LLM Safeguard")
        st.divider()
        st.markdown("**Sample prompts**")
        for label, prompt in SAMPLE_PROMPTS.items():
            st.button(label, on_click=set_sample_prompt, args=(prompt,))
        st.divider()
        st.markdown("**Risk model**")
        st.markdown(
            """
            Green: low-risk sample text

            Yellow: government, contract, financial, or procurement indicators

            Red: PII, CUI, FOUO, or highly sensitive indicators
            """
        )


def render_risk_card(results: dict) -> None:
    risk = results["risk_score"]
    style = COLORS[risk]
    st.markdown(
        f"""
        <div class="risk-card" style="background:{style["surface"]}; border-color:{style["border"]};">
            <div class="risk-label" style="color:{style["tone"]};">Risk Score</div>
            <div class="risk-score" style="color:{style["tone"]};">{style["label"]}</div>
            <div style="color:#102033; font-weight:700;">{style["message"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_findings(results: dict) -> None:
    finding_cards = [
        (
            "PII",
            results["possible_pii"],
            "Email, phone, SSN-like, or personal identifiers.",
        ),
        (
            "Gov Data",
            results["possible_government_data"],
            "Agency, program, COR/COTR, SOW, PWS, or federal terms.",
        ),
        (
            "CUI / FOUO",
            results["possible_cui"],
            "Controlled or restricted data handling indicators.",
        ),
        (
            "Contract ID",
            results["possible_contract_number"],
            "Possible contract, task order, or document identifier.",
        ),
        (
            "Financial",
            results["possible_financial_data"],
            "Funding, CLIN, invoice, budget, or procurement terms.",
        ),
    ]

    cards = []
    for title, detected, body in finding_cards:
        card_class = "finding finding-on" if detected else "finding"
        state = "Detected" if detected else "Clear"
        cards.append(
            f'<div class="{card_class}">'
            f'<div class="finding-title">{html.escape(title)}: {state}</div>'
            f'<div class="finding-body">{html.escape(body)}</div>'
            "</div>"
        )

    st.markdown(
        f'<div class="finding-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )

    if results["findings"]:
        st.markdown("**Scanner findings**")
        for finding in results["findings"]:
            st.write(f"- {finding}")
    else:
        st.write("No obvious risk indicators found.")


def render_redaction_preview(results: dict) -> None:
    redaction_count = results["redaction_count"]

    st.markdown("## Redaction Preview")
    if redaction_count == 0:
        st.info("No redactions were needed for this prompt.")
        return

    st.markdown(
        f'<div class="redaction-summary">{redaction_count} potential sensitive indicator(s) masked. Review the preview before sharing prompt text with an AI model.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="redaction-preview">{html.escape(results["redacted_text"])}</div>',
        unsafe_allow_html=True,
    )

    for redaction in results["redactions"]:
        st.write(
            f'- {redaction["label"]}: {redaction["count"]} replaced with `{redaction["placeholder"]}`'
        )


def get_approval_guidance(results: dict) -> str:
    if results["risk_score"] == "Red":
        return "Security, data owner, PM, and contract leadership should review."
    if results["risk_score"] == "Yellow":
        return "PM, data owner, COR/COTR, or contract lead review is recommended."
    return "Standard project team review may be sufficient."


def render_governance(results: dict) -> None:
    gov_data = (
        "Possibly yes. Government-related terms were detected."
        if results["possible_government_data"]
        else "No obvious government indicators were detected."
    )
    recommendation = COLORS[results["risk_score"]]["recommendation"]
    approval = get_approval_guidance(results)

    st.markdown(
        f"""
        <div class="question">
            <strong>What data goes into the model?</strong>
            <span>The pasted text would be the data submitted for AI processing.</span>
        </div>
        <div class="question">
            <strong>Is it government data?</strong>
            <span>{gov_data}</span>
        </div>
        <div class="question">
            <strong>Is it logged?</strong>
            <span>This local app does not intentionally log prompt content. Future versions should define audit logging, storage, and retention rules.</span>
        </div>
        <div class="question">
            <strong>Is it used for training?</strong>
            <span>A local LLM through Ollama does not train itself from prompts by default. Users should still verify app storage, telemetry, and model settings.</span>
        </div>
        <div class="question">
            <strong>Who approves outputs?</strong>
            <span>{approval}</span>
        </div>
        <div class="question">
            <strong>Recommendation</strong>
            <span>{recommendation}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


load_styles()
render_sidebar()
render_hero()

if "prompt_text" not in st.session_state:
    st.session_state["prompt_text"] = ""

st.markdown(
    """
    <div class="notice">
        <div style="font-size:1.35rem; line-height:1;">⚠</div>
        <div>
            <strong>Use fake or sample data only.</strong><br>
            Do not paste real government, client, classified, CUI, proprietary,
            or personal information.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

input_col, result_col = st.columns([1.12, 0.88], gap="large")

with input_col:
    st.markdown('<div class="scanner-title">Prompt Scanner</div>', unsafe_allow_html=True)
    user_prompt = st.text_area(
        "Paste text to scan",
        height=250,
        key="prompt_text",
        placeholder="Example: Navy task order update for contract ABCD-1234-XYZ...",
    )
    scan_clicked = st.button("Run Safeguard Check", use_container_width=True)

with result_col:
    st.subheader("Readiness Signals")
    st.write("The scanner checks for GovCon-sensitive terms and routes the prompt to a Green, Yellow, or Red recommendation.")
    st.markdown(
        """
        <div class="finding-grid">
            <div class="finding"><div class="finding-title">Local First</div><div class="finding-body">Prompt text is scanned in this app session.</div></div>
            <div class="finding"><div class="finding-title">MCP Ready</div><div class="finding-body">The same logic is available to compatible AI tools.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if scan_clicked:
    if not user_prompt.strip():
        st.warning("Paste some text first.")
    else:
        results = scan_for_risks(user_prompt)

        st.markdown("## Safeguard Result")
        score_col, findings_col = st.columns([0.72, 1.28], gap="large")
        with score_col:
            render_risk_card(results)
        with findings_col:
            render_findings(results)

        render_redaction_preview(results)

        st.markdown("## Governance Guidance")
        render_governance(results)

import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder

API_BASE_URL = "http://localhost:8000/api"


def api_call(method, endpoint, **kwargs):
    """Centralized API caller with error handling."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        kwargs.setdefault("timeout", 30)
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the API server. Make sure it's running on localhost:8000.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out. The server may be busy.")
        return None
    except requests.exceptions.HTTPError as e:
        detail = str(e)
        try:
            detail = e.response.json().get("detail", detail)
        except Exception:
            pass
        st.error(f"API error: {detail}")
        return None


def transcribe_audio(audio_bytes: bytes) -> str | None:
    """Send audio bytes to the backend STT endpoint and return the transcribed text."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/speech_to_text",
            files={"file": ("recording.wav", audio_bytes, "audio/wav")},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("text", "").strip() or None
    except Exception as e:
        st.error(f"Speech-to-text failed: {e}")
        return None


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "case_id": None,
        "case_active": False,
        "messages": [],
        "evaluation": None,
        "disease_revealed": None,
        "voice_text": None,
        "last_audio_id": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def inject_css():
    """Inject custom medical-themed CSS."""
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1565C0;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: #1565C0;
        margin: 0;
    }
    .main-header p {
        color: #555;
        margin: 0.25rem 0 0 0;
    }
    .score-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border-left: 4px solid #1565C0;
    }
    .score-card h3 {
        margin: 0 0 0.3rem 0;
        font-size: 0.85rem;
        color: #555;
    }
    .score-card .score-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .score-good { color: #2E7D32; }
    .score-mid { color: #F57F17; }
    .score-low { color: #C62828; }
    .disease-reveal {
        background: linear-gradient(135deg, #1565C0, #00897B);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    .sidebar-status {
        background: #f0f4f8;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
    }
    .voice-hint {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
        border-radius: 8px;
        font-size: 0.85rem;
        color: #555;
        margin-bottom: 0.5rem;
    }
    .transcribing-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1rem;
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        border-radius: 4px;
        font-size: 0.9rem;
        animation: pulse 1.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    </style>
    """, unsafe_allow_html=True)


def score_color_class(score, max_val=10):
    """Return CSS class based on score value."""
    ratio = score / max_val
    if ratio >= 0.7:
        return "score-good"
    elif ratio >= 0.4:
        return "score-mid"
    return "score-low"


def render_sidebar():
    """Render the sidebar with controls."""
    with st.sidebar:
        st.markdown("## Medical AI Consultation")
        st.caption("Practice your diagnostic skills with an AI patient")
        st.divider()

        # Start new case
        if st.button("Start New Case", use_container_width=True, type="primary"):
            data = api_call("POST", "/start_case")
            if data:
                st.session_state.case_id = data["case_id"]
                st.session_state.case_active = True
                st.session_state.messages = [
                    {"role": "patient", "content": data["initial_message"]}
                ]
                st.session_state.evaluation = None
                st.session_state.disease_revealed = None
                st.session_state.voice_text = None
                st.session_state.last_audio_id = None
                st.rerun()

        # Case status
        if st.session_state.case_id:
            doctor_msgs = [m for m in st.session_state.messages if m["role"] == "doctor"]
            status = "Active" if st.session_state.case_active else "Evaluated"
            st.markdown(f"""
            <div class="sidebar-status">
                <b>Status:</b> {status}<br>
                <b>Messages:</b> {len(st.session_state.messages)}<br>
                <b>Your questions:</b> {len(doctor_msgs)}
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # Evaluate button
            can_evaluate = st.session_state.case_active and len(doctor_msgs) >= 1
            if st.button(
                "Evaluate My Performance",
                use_container_width=True,
                disabled=not can_evaluate,
                type="secondary",
            ):
                with st.spinner("Evaluating your consultation..."):
                    data = api_call("POST", "/evaluate", json={"case_id": st.session_state.case_id}, timeout=60)
                if data:
                    st.session_state.evaluation = data["evaluation"]
                    st.session_state.disease_revealed = data["disease_revealed"]
                    st.session_state.case_active = False
                    st.rerun()

            if not can_evaluate and st.session_state.case_active:
                st.caption("Ask at least one question before evaluating.")
        else:
            st.info("Click **Start New Case** to begin.")


def _send_doctor_message(prompt: str):
    """Send a doctor message and get the patient's response."""
    with st.chat_message("user", avatar= None):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "doctor", "content": prompt})

    with st.chat_message("assistant", avatar= None):
        with st.spinner("Patient is responding..."):
            data = api_call("POST", "/doctor_input", json={
                "case_id": st.session_state.case_id,
                "doctor_text": prompt,
            })
        if data:
            st.markdown(data["patient_response"])
            st.session_state.messages.append({
                "role": "patient",
                "content": data["patient_response"],
            })
        else:
            st.warning("Failed to get a response. Try again.")


def render_chat_tab():
    """Render the consultation chat tab."""
    if not st.session_state.case_id:
        st.markdown("""
        <div class="main-header">
            <h1>Welcome, Doctor</h1>
            <p>Start a new case from the sidebar to begin your consultation.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### How it works
        1. Click **Start New Case** in the sidebar
        2. A simulated patient with a hidden condition will greet you
        3. Ask diagnostic questions to identify the condition
        4. When ready, click **Evaluate My Performance** for your score
        """)
        return

    # Render messages
    for msg in st.session_state.messages:
        if msg["role"] == "doctor":
            with st.chat_message("user", avatar=None):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar=None):
                st.markdown(msg["content"])

    # Voice + Chat input
    if st.session_state.case_active:
        # ── Voice input: real-time mic capture ───────────────────────────
        col_hint, col_mic = st.columns([5, 1])
        with col_hint:
            st.markdown(
                '<div class="voice-hint">'
                "<b>Voice Input</b> — Click the mic icon to speak your question. "
                "</div>",
                unsafe_allow_html=True,
            )
        with col_mic:
            audio_bytes = audio_recorder(
                text="",
                recording_color="#e74c3c",
                neutral_color="#1565C0",
                icon_size="2x",
                pause_threshold=2.0,   # auto-stop after 2s of silence
                sample_rate=41_000,
            )

        # Process captured audio automatically
        if audio_bytes:
            # Deduplicate: only process new audio (avoid re-processing on rerun)
            audio_id = hash(audio_bytes)
            if audio_id != st.session_state.last_audio_id:
                st.session_state.last_audio_id = audio_id

                st.markdown(
                    '<div class="transcribing-status">'
                    "🔄 Transcribing your speech…"
                    "</div>",
                    unsafe_allow_html=True,
                )
                transcription = transcribe_audio(audio_bytes)

                if transcription:
                    st.session_state.voice_text = transcription
                    st.rerun()
                else:
                    st.warning("Could not transcribe audio. Please try again or type your question below.")

        # If a voice transcription is ready, send it as a doctor message
        if st.session_state.voice_text:
            prompt = st.session_state.voice_text
            st.session_state.voice_text = None
            _send_doctor_message(prompt)

        # ── Regular text chat input ──────────────────────────────────────
        if prompt := st.chat_input("Ask the patient a question..."):
            _send_doctor_message(prompt)
    else:
        st.info("This case has been evaluated. Start a new case from the sidebar.")


def render_evaluation_tab():
    """Render the evaluation results tab."""
    ev = st.session_state.evaluation
    if not ev:
        st.info("No evaluation yet. Complete a consultation and click **Evaluate My Performance**.")
        return

    # Disease reveal
    st.markdown(f"""
    <div class="disease-reveal">
        The patient's condition was: <b>{st.session_state.disease_revealed}</b>
    </div>
    """, unsafe_allow_html=True)

    # Overall score
    overall = ev.get("overall_score", 0)
    overall_color = score_color_class(overall, 100)
    st.markdown(f"""
    <div class="score-card" style="border-left-width: 6px; margin-bottom: 1.5rem;">
        <h3>OVERALL SCORE</h3>
        <div class="score-value {overall_color}">{overall:.0f} / 100</div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(min(overall / 100, 1.0))

    st.markdown("---")

    # Category scores in 4 columns
    scores = [
        ("Diagnostic Quality", "diagnostic_score", "🔍"),
        ("Symptom Understanding", "symptom_understanding_score", "🧠"),
        ("Treatment Accuracy", "treatment_score", "💊"),
        ("Communication", "communication_score", "💬"),
    ]
    cols = st.columns(4)
    for col, (label, key, icon) in zip(cols, scores):
        val = ev.get(key, 0)
        color_cls = score_color_class(val)
        with col:
            st.markdown(f"""
            <div class="score-card">
                <h3>{icon} {label}</h3>
                <div class="score-value {color_cls}">{val:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(min(val / 10, 1.0))

    st.markdown("---")

    # Feedback
    st.subheader("Feedback")
    st.info(ev.get("feedback", "No feedback available."))

    # Question analysis
    asked = ev.get("asked_questions", [])
    correct = ev.get("correct_questions", [])
    missing = ev.get("missing_questions", [])

    col_left, col_right = st.columns(2)

    with col_left:
        with st.expander(f"Questions You Asked ({len(asked)})", expanded=False):
            if asked:
                for q in asked:
                    st.markdown(f"- {q}")
            else:
                st.caption("No questions recorded.")

        with st.expander(f"Correct Diagnostic Questions ({len(correct)})", expanded=True):
            if correct:
                for q in correct:
                    st.markdown(f"- :green[{q}]")
            else:
                st.caption("None of the questions matched recommended diagnostic areas.")

    with col_right:
        with st.expander(f"Critical Areas Missed ({len(missing)})", expanded=True):
            if missing:
                for q in missing:
                    st.markdown(f"- :red[{q}]")
            else:
                st.markdown(":green[Great job! You covered all the critical diagnostic areas.]")


def main():
    st.set_page_config(
        page_title="Medical AI Consultation",
        page_icon="🩺",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()
    init_session_state()
    render_sidebar()

    tab_chat, tab_eval = st.tabs(["Consultation", "Evaluation Results"])

    with tab_chat:
        render_chat_tab()

    with tab_eval:
        render_evaluation_tab()


if __name__ == "__main__":
    main()

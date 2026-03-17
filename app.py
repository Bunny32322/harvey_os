"""
HARVEY OS – Hybrid Strategic AI Command Center
Streamlit dashboard with 10 tabs for strategic analysis, habit tracking,
profile management, daily reflections, decision tracking, scenario
simulation, board-of-directors mode, trajectory forecasting,
weekly reports, and conversation training.
"""

import sys
from pathlib import Path

import streamlit as st

# ── Ensure project root is on sys.path ──────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_system_prompt, ASSETS_DIR
from core.brain import Brain
from core.memory import UserProfile
from core.leverage import LeverageScorer
from core.psychology import PatternAnalyzer
from core.scoring import DecisionTracker
from core.engine import StrategicEngine
from core.simulation import ScenarioSimulator
from core.board import BoardOfDirectors
from core.trajectory import TrajectoryPredictor
from core.personality import get_personality_prompt, list_modes, get_mode_info, MODES
from core.learning import DecisionLearner
from core.reporting import ReportEngine
from core.conversation_training import ConversationTrainer
from core import vector_store

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HARVEY OS",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load External CSS ──────────────────────────────────────────────────────
css_path = ASSETS_DIR / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

def render_sidebar() -> tuple:
    """Render sidebar controls and return (Brain, personality_mode)."""
    with st.sidebar:
        st.markdown("# ⚖️ HARVEY OS")
        st.caption("Hybrid Strategic AI Command Center")
        st.divider()

        # AI mode
        mode = st.radio(
            "🧠 AI Mode",
            ["offline", "online"],
            index=0,
            help="**Offline** → LM Studio local LLM  \n**Online** → OpenAI API",
        )
        brain = Brain(mode=mode)

        st.divider()

        # Personality mode
        personality = st.selectbox(
            "🎭 Personality",
            list_modes(),
            index=0,
            help="Adjusts the strategic analysis style.",
        )
        info = get_mode_info(personality)
        st.caption(info["description"])

        st.divider()

        # Status indicators
        mem_count = vector_store.memory_count()
        st.metric("Vector Memories", mem_count)

        profile = UserProfile()
        patterns = profile.get("patterns", [])
        st.metric("Detected Patterns", len(patterns))

        scorer = LeverageScorer()
        financial = st.slider("💰 Financial Stability", 0, 10, 5, key="fin_sidebar")
        lev = scorer.score(financial)
        st.metric("Leverage Score", f"{lev}/10")

        st.divider()

        # Voice toggle
        voice_enabled = st.checkbox("🎙️ Voice Interface", value=False,
                                    help="Enable spoken input/output (requires mic)")

        st.divider()
        st.caption("Built with 🏛 by Harvey OS")

    return brain, personality, voice_enabled


# ═══════════════════════════════════════════════════════════════════════════
# VOICE HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def voice_input() -> str:
    """Capture voice input using SpeechRecognition. Returns text or ''."""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎙️ Listening… speak now.")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=30)
        text = recognizer.recognize_google(audio)
        return text
    except Exception as exc:
        st.warning(f"Voice input failed: {exc}")
        return ""


def voice_output(text: str) -> None:
    """Speak text aloud using pyttsx3."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        engine.say(text[:1000])  # Limit spoken length
        engine.runAndWait()
    except Exception as exc:
        st.warning(f"Voice output failed: {exc}")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 – Strategic Engine
# ═══════════════════════════════════════════════════════════════════════════

def tab_strategic_engine(brain: Brain, personality: str, voice: bool):
    st.header("🎯 Strategic Engine")
    st.markdown("Enter a situation and receive a full strategic analysis powered by your AI brain, vector memory, and leverage score.")

    # Voice input option
    situation = ""
    if voice:
        col_v, col_t = st.columns([1, 4])
        with col_v:
            if st.button("🎙️ Speak", key="voice_engine"):
                situation = voice_input()
        with col_t:
            situation = st.text_area(
                "Describe your situation", height=150, value=situation,
                placeholder="e.g. My boss offered me a lateral move…",
                key="engine_situation",
            )
    else:
        situation = st.text_area(
            "Describe your situation", height=150,
            placeholder="e.g. My boss offered me a lateral move to a new department…",
            key="engine_situation",
        )

    fin = st.slider("Financial Stability (0–10)", 0, 10, 5, key="engine_fin")

    if st.button("⚡ Analyze", key="engine_go", use_container_width=True):
        if not situation.strip():
            st.warning("Please describe a situation first.")
            return
        with st.spinner("Harvey is thinking…"):
            profile = UserProfile()
            scorer = LeverageScorer()
            engine = StrategicEngine(brain, profile, scorer)

            # Inject personality modifier into system prompt
            pers_prompt = get_personality_prompt(personality)
            original_prompt = brain._system_prompt
            brain._system_prompt = f"{original_prompt}\n\n{pers_prompt}"

            result = engine.analyze(situation, financial_stability=fin)

            # Restore original
            brain._system_prompt = original_prompt

            # Log conversation
            trainer = ConversationTrainer()
            trainer.add_conversation(situation, result, tag="strategic_engine")

        st.markdown("---")
        st.markdown(result)

        if voice:
            voice_output(result)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 – Habits Tracker
# ═══════════════════════════════════════════════════════════════════════════

def tab_habits_tracker():
    st.header("📊 Habits Tracker")
    scorer = LeverageScorer()

    col1, col2 = st.columns(2)
    with col1:
        dw = st.number_input("Deep Work Hours", min_value=0.0, max_value=16.0,
                             value=float(scorer.habits.get("deep_work_hours", 0)),
                             step=0.5, key="habit_dw")
        lh = st.number_input("Learning Hours", min_value=0.0, max_value=16.0,
                             value=float(scorer.habits.get("learning_hours", 0)),
                             step=0.5, key="habit_lh")
    with col2:
        wo = st.number_input("Workout (hours)", min_value=0.0, max_value=5.0,
                             value=float(scorer.habits.get("workout", 0)),
                             step=0.5, key="habit_wo")
        na = st.number_input("Networking Actions", min_value=0, max_value=20,
                             value=int(scorer.habits.get("networking_actions", 0)),
                             step=1, key="habit_na")

    if st.button("💾 Save Habits", key="save_habits", use_container_width=True):
        new_habits = {
            "deep_work_hours": dw,
            "learning_hours": lh,
            "workout": wo,
            "networking_actions": na,
        }
        scorer.save(new_habits)
        st.success("Habits saved!")

    # Breakdown
    st.markdown("### Leverage Breakdown")
    fin = st.slider("Financial Stability", 0, 10, 5, key="habit_fin")
    bd = scorer.breakdown(fin)
    cols = st.columns(len(bd))
    for col, (k, v) in zip(cols, bd.items()):
        col.metric(k.replace("_", " ").title(), f"{v}/10")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 – Profile Setup
# ═══════════════════════════════════════════════════════════════════════════

def tab_profile_setup():
    st.header("👤 Profile Setup")
    profile = UserProfile()

    career = st.text_input("Career Position",
                           value=profile.get("career_position", ""),
                           key="prof_career")
    finance = st.text_input("Financial Status",
                            value=profile.get("financial_status", ""),
                            key="prof_finance")
    rel = st.text_input("Relationship Status",
                        value=profile.get("relationship_status", ""),
                        key="prof_rel")

    if st.button("💾 Save Profile", key="save_profile", use_container_width=True):
        profile.set("career_position", career)
        profile.set("financial_status", finance)
        profile.set("relationship_status", rel)
        profile.save()
        st.success("Profile saved!")

    patterns = profile.get("patterns", [])
    if patterns:
        st.markdown("### Detected Patterns")
        for p in patterns:
            st.markdown(f"• {p.replace('_', ' ').title()}")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 – Daily Reflection
# ═══════════════════════════════════════════════════════════════════════════

def tab_daily_reflection():
    st.header("📝 Daily Reflection")
    st.markdown("Log your thoughts. Harvey OS will analyze them for psychological patterns.")

    reflection = st.text_area(
        "What's on your mind today?", height=150,
        placeholder="e.g. I noticed I kept avoiding the difficult conversation…",
        key="reflection_text",
    )

    if st.button("🔍 Analyze & Save", key="save_reflection", use_container_width=True):
        if not reflection.strip():
            st.warning("Write something first.")
            return

        profile = UserProfile()
        analyzer = PatternAnalyzer()
        detected = analyzer.analyze(reflection)
        for p in detected:
            profile.add_pattern(p)

        profile.add_reflection(reflection)
        vector_store.add_memory(reflection)

        if detected:
            st.warning(f"Patterns detected: {', '.join(p.replace('_', ' ').title() for p in detected)}")
        else:
            st.success("Reflection saved. No dominant patterns detected.")

    # History
    profile = UserProfile()
    reflections = profile.get("reflections", [])
    if reflections:
        st.markdown("### Reflection History")
        for i, r in enumerate(reversed(reflections[-10:]), 1):
            with st.expander(f"Reflection #{len(reflections) - i + 1}"):
                st.write(r)

        st.markdown("### Pattern Summary")
        analyzer = PatternAnalyzer()
        st.markdown(analyzer.summary(reflections))


# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 – Decision Tracker
# ═══════════════════════════════════════════════════════════════════════════

def tab_decision_tracker():
    st.header("📋 Decision Tracker")
    tracker = DecisionTracker()

    with st.expander("➕ Log New Decision", expanded=True):
        dec = st.text_input("Decision", key="dt_dec")
        strat = st.text_input("Strategy Used", key="dt_strat")
        conf = st.slider("Confidence Level", 1, 10, 5, key="dt_conf")
        outcome = st.text_input("Outcome (optional)", key="dt_outcome")
        score = st.slider("Score (0-10)", 0, 10, 0, key="dt_score")

        if st.button("💾 Save Decision", key="save_dec", use_container_width=True):
            if dec.strip():
                tracker.add(dec, strat, conf, outcome, score)
                st.success("Decision logged!")
                st.rerun()
            else:
                st.warning("Enter a decision first.")

    # Learning insights
    decisions = tracker.list_all()
    if decisions:
        st.markdown("### Decision Learning Insights")
        learner = DecisionLearner()
        st.markdown(learner.summary(decisions))

        st.markdown("### Decision History")
        for d in reversed(decisions):
            with st.expander(f"#{d['id']} – {d['decision'][:60]}"):
                st.markdown(f"**Strategy:** {d['strategy_used']}")
                st.markdown(f"**Confidence:** {d['confidence_level']}/10")
                st.markdown(f"**Outcome:** {d.get('outcome', '—')}")
                st.markdown(f"**Score:** {d.get('score', 0)}/10")
                st.caption(d.get("timestamp", ""))


# ═══════════════════════════════════════════════════════════════════════════
# TAB 6 – Scenario Simulator
# ═══════════════════════════════════════════════════════════════════════════

def tab_scenario_simulator(brain: Brain, personality: str):
    st.header("🎲 Scenario Simulator")
    st.markdown("Describe a decision you're facing. Harvey OS will generate **three strategies** with predicted outcomes.")

    situation = st.text_area(
        "Describe the decision", height=150,
        placeholder="e.g. I received two job offers…",
        key="sim_situation",
    )

    profile = UserProfile()
    context = profile.summary()

    if st.button("🚀 Simulate", key="sim_go", use_container_width=True):
        if not situation.strip():
            st.warning("Describe a scenario first.")
            return
        with st.spinner("Simulating three strategies…"):
            pers_prompt = get_personality_prompt(personality)
            original = brain._system_prompt
            brain._system_prompt = f"{original}\n\n{pers_prompt}"

            sim = ScenarioSimulator(brain)
            result = sim.simulate(situation, context)

            brain._system_prompt = original

            trainer = ConversationTrainer()
            trainer.add_conversation(situation, result, tag="scenario_simulator")

        st.markdown("---")
        st.markdown(result)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 7 – Board Mode
# ═══════════════════════════════════════════════════════════════════════════

def tab_board_mode(brain: Brain):
    st.header("🏛 Board of Directors Mode")
    st.markdown("Five AI personas analyze your situation independently, then Harvey OS produces a final synthesis.")

    situation = st.text_area(
        "Describe the situation for the board", height=150,
        placeholder="e.g. Our company is considering a pivot…",
        key="board_situation",
    )

    if st.button("🧠 Convene the Board", key="board_go", use_container_width=True):
        if not situation.strip():
            st.warning("Describe a situation first.")
            return

        board = BoardOfDirectors(brain)
        with st.spinner("The board is deliberating…"):
            results = board.convene(situation)

        for name, analysis in results.items():
            if name == "Synthesis":
                continue
            with st.expander(f"💼 {name}"):
                st.markdown(analysis)

        st.markdown("---")
        st.markdown("### ⚖️ Final Synthesis")
        st.markdown(results.get("Synthesis", ""))


# ═══════════════════════════════════════════════════════════════════════════
# TAB 8 – Trajectory Forecast
# ═══════════════════════════════════════════════════════════════════════════

def tab_trajectory(brain: Brain):
    st.header("📈 Trajectory Forecast")
    st.markdown("Predict your 1-year, 3-year, and 5-year outcomes based on current data.")

    fin = st.slider("Financial Stability (0–10)", 0, 10, 5, key="traj_fin")

    if st.button("🔮 Predict Trajectory", key="traj_go", use_container_width=True):
        with st.spinner("Forecasting your trajectory…"):
            profile = UserProfile()
            scorer = LeverageScorer()
            predictor = TrajectoryPredictor(brain)
            result = predictor.predict(profile, scorer, financial_stability=fin)
        st.markdown("---")
        st.markdown(result)


# ═══════════════════════════════════════════════════════════════════════════
# TAB 9 – Weekly Reports
# ═══════════════════════════════════════════════════════════════════════════

def tab_weekly_reports():
    st.header("📊 Weekly Reports")
    st.markdown("Generate a performance report covering leverage, habits, decisions, and patterns.")

    fin = st.slider("Financial Stability (0–10)", 0, 10, 5, key="report_fin")

    col1, col2 = st.columns(2)
    with col1:
        gen_md = st.button("📝 Generate Report", key="gen_report", use_container_width=True)
    with col2:
        gen_pdf = st.button("📄 Export PDF", key="gen_pdf", use_container_width=True)

    engine = ReportEngine()

    if gen_md:
        with st.spinner("Building report…"):
            md = engine.generate_markdown(fin)
        st.markdown(md)

    if gen_pdf:
        with st.spinner("Generating PDF…"):
            pdf_bytes = engine.generate_pdf(fin)
        st.download_button(
            label="⬇️ Download PDF",
            data=pdf_bytes,
            file_name="harvey_os_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.success("PDF ready for download!")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 10 – Conversation Training
# ═══════════════════════════════════════════════════════════════════════════

def tab_conversation_training():
    st.header("🧬 Conversation Training")
    st.markdown("Analyze past conversations to extract strategic insights and feed them into vector memory.")

    trainer = ConversationTrainer()

    st.metric("Stored Conversations", len(trainer.conversations))

    if st.button("🔬 Run Training Analysis", key="train_go", use_container_width=True):
        with st.spinner("Mining conversations for patterns…"):
            summary = trainer.summary()
        st.markdown("---")
        st.markdown(summary)

    # Show recent conversations
    if trainer.conversations:
        st.markdown("### Recent Conversations")
        for c in reversed(trainer.conversations[-10:]):
            with st.expander(f"🗣 {c.get('tag', 'chat')} – {c['timestamp'][:16]}"):
                st.markdown(f"**You:** {c['user'][:200]}…" if len(c['user']) > 200 else f"**You:** {c['user']}")
                st.markdown(f"**Harvey OS:** {c['ai'][:300]}…" if len(c['ai']) > 300 else f"**Harvey OS:** {c['ai']}")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    brain, personality, voice = render_sidebar()

    tabs = st.tabs([
        "🎯 Strategic Engine",
        "📊 Habits Tracker",
        "👤 Profile Setup",
        "📝 Daily Reflection",
        "📋 Decision Tracker",
        "🎲 Scenario Simulator",
        "🏛 Board Mode",
        "📈 Trajectory Forecast",
        "📊 Weekly Reports",
        "🧬 Conversation Training",
    ])

    with tabs[0]:
        tab_strategic_engine(brain, personality, voice)
    with tabs[1]:
        tab_habits_tracker()
    with tabs[2]:
        tab_profile_setup()
    with tabs[3]:
        tab_daily_reflection()
    with tabs[4]:
        tab_decision_tracker()
    with tabs[5]:
        tab_scenario_simulator(brain, personality)
    with tabs[6]:
        tab_board_mode(brain)
    with tabs[7]:
        tab_trajectory(brain)
    with tabs[8]:
        tab_weekly_reports()
    with tabs[9]:
        tab_conversation_training()


if __name__ == "__main__":
    main()

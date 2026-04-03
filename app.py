"""
HARVEY OS – Hybrid Strategic AI Command Center (v2)
Streamlit dashboard with 12 tabs: strategic analysis, habits, profile,
reflections, decisions, scenarios, board mode, trajectory, reports,
conversation training, conversation threads, and episodic memory.
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
from core.conversation_memory import ConversationMemory
from core.episodic_memory import EpisodicMemory, EMOTIONS, CATEGORIES
from core import vector_store

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HARVEY OS v2",
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
        st.markdown("# ⚖️ HARVEY OS v2")
        st.caption("Beyond Jarvis – Strategic AI Command Center")
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

        # Memory stats
        conv_memory = ConversationMemory()
        conv_stats = conv_memory.stats()
        st.metric("Conversation Threads", conv_stats["total_threads"])
        st.metric("Total Messages", conv_stats["total_messages"])

        episodes = EpisodicMemory()
        ep_stats = episodes.stats()
        st.metric("Life Episodes", ep_stats["total_episodes"])

        st.divider()

        # Voice toggle
        voice_enabled = st.checkbox("🎙️ Voice Interface", value=False,
                                    help="Enable spoken input/output (requires mic)")

        st.divider()
        st.caption("Built with 🏛 by Harvey OS v2")

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
    st.markdown("Enter a situation and receive a full strategic analysis powered by your AI brain, vector memory, episodic memory, and leverage score.")

    # Thread selection
    conv_memory = ConversationMemory()
    threads = conv_memory.list_threads(limit=20)
    thread_options = ["🆕 New Thread"] + [
        f"{t['title'][:50]} ({t['id'][:8]}…)" for t in threads
    ]
    selected = st.selectbox("💬 Conversation Thread", thread_options, key="engine_thread")

    thread_id = None
    if selected != "🆕 New Thread":
        idx = thread_options.index(selected) - 1
        thread_id = threads[idx]["id"]

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

            # Create thread if new
            if not thread_id:
                thread_id = brain.start_thread(
                    title=situation[:80], tag="strategic_engine"
                )

            result = engine.analyze(
                situation,
                financial_stability=fin,
                thread_id=thread_id,
            )

            # Restore original
            brain._system_prompt = original_prompt

            # Log conversation
            trainer = ConversationTrainer()
            trainer.add_conversation(situation, result, tag="strategic_engine")

        st.markdown("---")
        st.markdown(result)
        st.caption(f"🧵 Thread: {thread_id[:8]}…")

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

    patterns = profile.get_pattern_counts()
    if patterns:
        st.markdown("### Detected Patterns")
        for p, count in patterns.items():
            st.markdown(f"• {p.replace('_', ' ').title()} (detected {count}x)")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 – Daily Reflection
# ═══════════════════════════════════════════════════════════════════════════

def tab_daily_reflection():
    st.header("📝 Daily Reflection")
    st.markdown("Log your thoughts. Harvey OS will analyze them for psychological patterns and store them as episodic memories.")

    reflection = st.text_area(
        "What's on your mind today?", height=150,
        placeholder="e.g. I noticed I kept avoiding the difficult conversation…",
        key="reflection_text",
    )

    # Emotional tagging
    col1, col2 = st.columns(2)
    with col1:
        emotion = st.selectbox("How are you feeling?", EMOTIONS, key="reflection_emotion")
    with col2:
        importance = st.slider("How significant is this?", 1, 10, 5, key="reflection_importance")

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

        # Store in vector memory with metadata
        vector_store.add_memory(
            reflection,
            source="reflection",
            importance=float(importance),
            tags=detected,
        )

        # Store as episodic memory
        episodes = EpisodicMemory()
        episodes.record(
            content=reflection,
            category="general",
            importance=float(importance),
            emotion=emotion,
            tags=detected,
        )

        if detected:
            st.warning(f"Patterns detected: {', '.join(p.replace('_', ' ').title() for p in detected)}")
        else:
            st.success("Reflection saved. No dominant patterns detected.")

    # History
    profile = UserProfile()
    reflections = profile.get_reflections(limit=10)
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
# TAB 11 – Conversation Threads (NEW)
# ═══════════════════════════════════════════════════════════════════════════

def tab_conversation_threads(brain: Brain, personality: str, voice: bool):
    st.header("💬 Conversation Threads")
    st.markdown("Have a continuous, threaded conversation with Harvey OS. He remembers everything in this thread.")

    conv_memory = ConversationMemory()

    # Thread management
    col_new, col_list = st.columns([1, 3])
    with col_new:
        if st.button("🆕 New Thread", key="new_thread", use_container_width=True):
            new_id = conv_memory.start_thread(title="New Conversation")
            st.session_state["active_thread"] = new_id
            st.rerun()

    # Thread selector
    threads = conv_memory.list_threads(limit=30)
    if threads:
        thread_names = [f"{t['title'][:40]} ({t['msg_count']} msgs)" for t in threads]
        with col_list:
            selected_idx = st.selectbox(
                "Select thread", range(len(thread_names)),
                format_func=lambda i: thread_names[i],
                key="thread_selector",
            )
        active_thread_id = threads[selected_idx]["id"]
        st.session_state["active_thread"] = active_thread_id

        # Show thread messages
        messages = conv_memory.get_messages(active_thread_id)
        if messages:
            st.markdown("---")
            for msg in messages:
                if msg["role"] == "user":
                    st.markdown(f"**🗣️ You:** {msg['content']}")
                elif msg["role"] == "assistant":
                    st.markdown(f"**🤖 Harvey:** {msg['content']}")
                elif msg["role"] == "system":
                    st.caption(f"📋 {msg['content'][:100]}…")
            st.markdown("---")

        # Chat input
        user_msg = ""
        if voice:
            col_v, col_t = st.columns([1, 4])
            with col_v:
                if st.button("🎙️ Speak", key="voice_thread"):
                    user_msg = voice_input()
            with col_t:
                user_msg = st.text_area(
                    "Your message", height=100, value=user_msg,
                    placeholder="Type your message to Harvey...",
                    key="thread_input",
                )
        else:
            user_msg = st.text_area(
                "Your message", height=100,
                placeholder="Type your message to Harvey...",
                key="thread_input",
            )

        if st.button("📤 Send", key="send_msg", use_container_width=True):
            if user_msg.strip():
                with st.spinner("Harvey is thinking…"):
                    # Inject personality
                    pers_prompt = get_personality_prompt(personality)
                    original = brain._system_prompt
                    brain._system_prompt = f"{original}\n\n{pers_prompt}"

                    response = brain.think(
                        user_msg,
                        thread_id=active_thread_id,
                    )

                    brain._system_prompt = original

                    # Also log to conversation training
                    trainer = ConversationTrainer()
                    trainer.add_conversation(user_msg, response, tag="thread_chat")

                st.rerun()
            else:
                st.warning("Type a message first.")

        # Thread stats
        with st.expander("📊 Thread Stats"):
            thread_info = conv_memory.get_thread(active_thread_id)
            if thread_info:
                st.markdown(f"**Thread ID:** `{active_thread_id}`")
                st.markdown(f"**Created:** {thread_info['created_at']}")
                st.markdown(f"**Messages:** {conv_memory.message_count(active_thread_id)}")
                if thread_info.get("summary"):
                    st.markdown(f"**Summary:** {thread_info['summary']}")
    else:
        st.info("No threads yet. Click '🆕 New Thread' to start a conversation.")


# ═══════════════════════════════════════════════════════════════════════════
# TAB 12 – Episodic Memory (NEW)
# ═══════════════════════════════════════════════════════════════════════════

def tab_episodic_memory():
    st.header("🧠 Episodic Memory")
    st.markdown("Your life event timeline. Record significant events, and Harvey will use them for context in all future analyses.")

    episodes_mgr = EpisodicMemory()

    # Record new episode
    with st.expander("➕ Record New Life Event", expanded=True):
        content = st.text_area(
            "What happened?", height=100,
            placeholder="e.g. Got promoted to Senior Engineer at Acme Corp…",
            key="ep_content",
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            category = st.selectbox("Category", CATEGORIES, key="ep_category")
        with col2:
            emotion = st.selectbox("Emotion", EMOTIONS, key="ep_emotion")
        with col3:
            importance = st.slider("Importance (1-10)", 1, 10, 5, key="ep_importance")

        tags_input = st.text_input(
            "Tags (comma-separated)", key="ep_tags",
            placeholder="e.g. career, milestone, promotion",
        )

        if st.button("💾 Record Episode", key="save_ep", use_container_width=True):
            if content.strip():
                tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
                ep_id = episodes_mgr.record(
                    content=content,
                    category=category,
                    importance=float(importance),
                    emotion=emotion,
                    tags=tags,
                )
                # Also add to vector memory
                vector_store.add_memory(
                    content,
                    source="episode",
                    importance=float(importance),
                    tags=tags,
                )
                st.success(f"Episode #{ep_id} recorded!")
                st.rerun()
            else:
                st.warning("Describe the event first.")

    # Memory stats
    stats = episodes_mgr.stats()
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Episodes", stats["total_episodes"])
    with col_b:
        st.metric("Avg Importance", f"{stats['average_importance']}/10")
    with col_c:
        if st.button("🗑️ Prune Old Memories", key="prune_ep"):
            pruned = episodes_mgr.prune()
            st.info(f"Pruned {pruned} decayed memories.")

    # Filters
    st.markdown("### 📅 Episode Timeline")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_cat = st.selectbox("Filter Category", ["All"] + CATEGORIES, key="ep_filter_cat")
    with col_f2:
        filter_emotion = st.selectbox("Filter Emotion", ["All"] + EMOTIONS, key="ep_filter_emo")
    with col_f3:
        filter_importance = st.slider("Min Importance", 0, 10, 0, key="ep_filter_imp")

    results = episodes_mgr.recall(
        category=filter_cat if filter_cat != "All" else None,
        emotion=filter_emotion if filter_emotion != "All" else None,
        min_importance=float(filter_importance),
        limit=30,
    )

    if results:
        for ep in results:
            imp_stars = "⭐" * int(ep["importance"] // 2)
            with st.expander(f"{ep['created_at'][:10]} | {ep['category'].title()} | {imp_stars} {ep['content'][:60]}…"):
                st.markdown(f"**Event:** {ep['content']}")
                st.markdown(f"**Category:** {ep['category'].title()}")
                st.markdown(f"**Emotion:** {ep['emotion'].title()}")
                st.markdown(f"**Importance:** {ep['importance']}/10")
                if ep.get("tags"):
                    st.markdown(f"**Tags:** {', '.join(ep['tags'])}")
                st.caption(f"Recorded: {ep['created_at']}")
                if ep.get("decay_at"):
                    st.caption(f"⏳ Will decay: {ep['decay_at'][:10]}")
    else:
        st.info("No episodes match your filters.")


# ═══════════════════════════════════════════════════════════════════════════
# DATA MIGRATION TAB
# ═══════════════════════════════════════════════════════════════════════════

def tab_data_migration():
    st.header("🔄 Data Migration")
    st.markdown("One-time migration of legacy JSON data into the new SQLite + ChromaDB database.")

    st.warning("⚠️ Only run this once. It will import your existing JSON data into the new database.")

    if st.button("🚀 Run Migration", key="run_migration", use_container_width=True):
        with st.spinner("Migrating data…"):
            from core.database import migrate_json_to_sqlite
            counts = migrate_json_to_sqlite()

            # Migrate FAISS to ChromaDB
            faiss_count = vector_store.migrate_from_faiss()
            counts["vector_memories"] = faiss_count

        st.success("Migration complete!")
        for table, count in counts.items():
            st.markdown(f"• **{table}:** {count} records migrated")


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
        "💬 Threads",
        "🧠 Episodic Memory",
        "🔄 Migration",
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
    with tabs[10]:
        tab_conversation_threads(brain, personality, voice)
    with tabs[11]:
        tab_episodic_memory()
    with tabs[12]:
        tab_data_migration()


if __name__ == "__main__":
    main()

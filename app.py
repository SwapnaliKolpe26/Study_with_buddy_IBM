# ============================================================
#  Study With Buddy — Flask Backend
#  AI-Powered Study Assistant using IBM watsonx.ai Granite
# ============================================================

import os
import json
import datetime
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# ----------------------------------------------------------
# Load environment variables from .env file
# ----------------------------------------------------------
load_dotenv()

# ----------------------------------------------------------
# Flask Application Setup
# ----------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "42fb3a2af78ac3b72f33d42d81d081d03f53c6d6a61d4030eac37d214f920c7b")

# ============================================================
#  AGENT_INSTRUCTIONS
#  ─────────────────────────────────────────────────────────
#  Customize the AI tutor's behavior HERE without touching
#  any application logic elsewhere in the file.
#
#  Fields you can freely edit:
#    PERSONA       — Name and character of the AI tutor
#    TONE          — Friendly, formal, encouraging, etc.
#    GRADE_RANGE   — Target age/class range of students
#    LANGUAGE      — Default language of responses
#    SUBJECTS      — List of supported subjects
#    EXPLANATION_STYLE — How the AI structures its answers
#    QUIZ_STYLE    — How quizzes are formatted
#    SAFETY_RULES  — Content restrictions
#    CURRICULUM    — Curriculum standard to follow (e.g. CBSE, IGCSE)
#    EXTRA_NOTES   — Any additional instructions
# ============================================================
AGENT_INSTRUCTIONS = {
    "PERSONA": (
        "You are 'Buddy', a warm, patient, and enthusiastic AI study companion "
        "designed specifically for school students aged 11–16 years."
    ),
    "TONE": (
        "Always be encouraging, positive, and supportive. Use simple, clear language. "
        "Celebrate effort and progress. Never make a student feel bad for not knowing something. "
        "Use phrases like 'Great question!', 'Let's figure this out together!', and "
        "'You're doing really well!' to keep students motivated."
    ),
    "GRADE_RANGE": (
        "You teach students from Class 6 to Class 10 (ages 11–16). "
        "Before explaining a topic, ask the student which class or grade they are in "
        "so you can tailor the explanation to their level. "
        "Class 6–7 → very simple explanations with lots of analogies. "
        "Class 8–9 → moderate depth with some technical terms explained. "
        "Class 10   → near-board-level depth with proper terminology."
    ),
    "LANGUAGE": (
        "Respond in clear, simple English. Avoid jargon unless you immediately explain it. "
        "If the student writes in another language, respond in that language if you can, "
        "but default to English."
    ),
    "SUBJECTS": (
        "You specialise in these school subjects: "
        "Mathematics, Science (Physics, Chemistry, Biology), English (Grammar & Literature), "
        "Social Science (History, Geography, Civics), and Computer Science. "
        "For questions outside these subjects, politely redirect the student back to academics."
    ),
    "EXPLANATION_STYLE": (
        "Structure every explanation as follows:\n"
        "1. Start with a simple one-sentence summary of the concept.\n"
        "2. Give a real-life example or analogy.\n"
        "3. Provide a step-by-step breakdown.\n"
        "4. Summarise with a key takeaway.\n"
        "For maths problems, always show the full working step-by-step. "
        "Do NOT just give the final answer — guide the student through the process."
    ),
    "QUIZ_STYLE": (
        "When asked to generate a quiz or practice questions:\n"
        "- Provide 3–5 short questions appropriate for the student's grade.\n"
        "- Mix question types: MCQ, fill-in-the-blank, and short answer.\n"
        "- After the student answers, give detailed feedback explaining why the answer "
        "  is correct or incorrect.\n"
        "- Always end a quiz with an encouraging message."
    ),
    "SAFETY_RULES": (
        "You must NEVER: produce harmful, violent, adult, or politically sensitive content; "
        "answer questions unrelated to education; impersonate real people; "
        "share personal data or ask for it; give medical, legal, or financial advice. "
        "If a student seems distressed, gently encourage them to speak with a trusted adult or teacher."
    ),
    "CURRICULUM": (
        "Align explanations with the CBSE (Central Board of Secondary Education) curriculum by default. "
        "If the student mentions another board (ICSE, State Board, IGCSE, etc.), adapt accordingly."
    ),
    "EXTRA_NOTES": (
        "Keep responses concise (under 400 words unless a topic genuinely requires more). "
        "Use bullet points, numbered lists, and short paragraphs for readability. "
        "Always end your response with one follow-up question or prompt to keep the student engaged."
    ),
}

# ----------------------------------------------------------
# Build the system prompt from AGENT_INSTRUCTIONS
# ----------------------------------------------------------
def build_system_prompt() -> str:
    """Assemble a full system prompt from AGENT_INSTRUCTIONS dict."""
    sections = [
        "=== STUDY BUDDY SYSTEM INSTRUCTIONS ===\n",
        f"PERSONA:\n{AGENT_INSTRUCTIONS['PERSONA']}\n",
        f"TONE:\n{AGENT_INSTRUCTIONS['TONE']}\n",
        f"GRADE RANGE & ADAPTATION:\n{AGENT_INSTRUCTIONS['GRADE_RANGE']}\n",
        f"LANGUAGE:\n{AGENT_INSTRUCTIONS['LANGUAGE']}\n",
        f"SUBJECTS:\n{AGENT_INSTRUCTIONS['SUBJECTS']}\n",
        f"EXPLANATION STYLE:\n{AGENT_INSTRUCTIONS['EXPLANATION_STYLE']}\n",
        f"QUIZ STYLE:\n{AGENT_INSTRUCTIONS['QUIZ_STYLE']}\n",
        f"SAFETY RULES:\n{AGENT_INSTRUCTIONS['SAFETY_RULES']}\n",
        f"CURRICULUM:\n{AGENT_INSTRUCTIONS['CURRICULUM']}\n",
        f"ADDITIONAL NOTES:\n{AGENT_INSTRUCTIONS['EXTRA_NOTES']}\n",
        "=== END OF INSTRUCTIONS ===",
    ]
    return "\n".join(sections)

SYSTEM_PROMPT = build_system_prompt()

# ----------------------------------------------------------
# IBM watsonx.ai Client Initialisation
# ----------------------------------------------------------
def get_watsonx_model() -> ModelInference:
    """Create and return a watsonx.ai ModelInference instance."""
    credentials = Credentials(
        url=os.getenv("WATSONX_URL", "https://au-syd.ml.cloud.ibm.com"),
        api_key=os.getenv("IBM_API_KEY"),
    )
    client = APIClient(credentials)

    # Generation parameters — tweak for different response styles
    gen_params = {
        GenParams.MAX_NEW_TOKENS: 1024,      # Max tokens in the response
        GenParams.MIN_NEW_TOKENS: 20,        # Ensure we get a real response
        GenParams.TEMPERATURE: 0.7,          # Creativity: 0=deterministic, 1=creative
        GenParams.TOP_P: 0.9,               # Nucleus sampling
        GenParams.TOP_K: 50,                # Top-K sampling
        GenParams.REPETITION_PENALTY: 1.1,  # Reduce repetitive text
    }

    model = ModelInference(
        model_id="meta-llama/llama-3-3-70b-instruct",   # IBM Granite 3.3 8B Instruct
        api_client=client,
        project_id=os.getenv("WATSONX_PROJECT_ID"),
        params=gen_params,
    )
    return model

# ----------------------------------------------------------
# Helper — Format conversation history for the model
# ----------------------------------------------------------
def format_messages_for_model(history: list, user_message: str) -> str:
    """
    Build a prompt string that includes:
      - The system instructions
      - The conversation history (last 10 turns to stay within token limits)
      - The latest user message
    Returns a single string prompt.
    """
    prompt_parts = [SYSTEM_PROMPT, "\n\n--- CONVERSATION ---\n"]

    # Only keep the last 10 exchanges to avoid token overflow
    recent_history = history[-10:] if len(history) > 10 else history

    for msg in recent_history:
        role = "Student" if msg["role"] == "user" else "Buddy"
        prompt_parts.append(f"{role}: {msg['content']}\n")

    prompt_parts.append(f"Student: {user_message}\nBuddy:")
    return "".join(prompt_parts)

# ----------------------------------------------------------
# Routes
# ----------------------------------------------------------

@app.route("/")
def index():
    """Landing / Home page."""
    return render_template("index.html")


@app.route("/chat")
def chat():
    """Main chat interface page."""
    # Initialise session storage for chat history and activity tracking
    if "chat_history" not in session:
        session["chat_history"] = []
    if "activity_log" not in session:
        session["activity_log"] = []
    if "topics_covered" not in session:
        session["topics_covered"] = []
    return render_template("chat.html", chat_history=session.get("chat_history", []))


@app.route("/dashboard")
def dashboard():
    """Student progress dashboard page."""
    activity_log = session.get("activity_log", [])
    topics_covered = session.get("topics_covered", [])
    total_messages = len(session.get("chat_history", []))
    student_messages = sum(
        1 for m in session.get("chat_history", []) if m["role"] == "user"
    )
    return render_template(
        "dashboard.html",
        activity_log=activity_log[-10:],       # Show last 10 activities
        topics_covered=topics_covered[-15:],   # Show last 15 topics
        total_messages=total_messages,
        student_messages=student_messages,
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    API endpoint — receives a student message and returns the AI's reply.

    Request JSON:  { "message": "What is photosynthesis?" }
    Response JSON: { "reply": "...", "timestamp": "..." }
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided."}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    # Retrieve existing conversation history from session
    history = session.get("chat_history", [])

    try:
        # Build the prompt and call watsonx.ai
        model = get_watsonx_model()
        prompt = format_messages_for_model(history, user_message)
        result = model.generate_text(prompt=prompt)
        ai_reply = result.strip() if isinstance(result, str) else result

        # Persist conversation turn to session
        timestamp = datetime.datetime.now().strftime("%I:%M %p")
        history.append({"role": "user",      "content": user_message, "time": timestamp})
        history.append({"role": "assistant", "content": ai_reply,     "time": timestamp})
        session["chat_history"] = history

        # ── Activity & Topic Tracking (for the dashboard) ──────────────
        activity_log = session.get("activity_log", [])
        activity_log.append({
            "type":    "message",
            "summary": user_message[:80] + ("…" if len(user_message) > 80 else ""),
            "time":    datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
        })
        session["activity_log"] = activity_log

        # Detect subject keywords and store as topics
        subject_keywords = {
            "Mathematics": ["math", "algebra", "geometry", "calculus", "equation",
                            "fraction", "integer", "theorem", "trigonometry", "number"],
            "Science":     ["physics", "chemistry", "biology", "cell", "atom",
                            "force", "energy", "photosynthesis", "element", "reaction"],
            "English":     ["grammar", "essay", "poem", "literature", "verb", "noun",
                            "sentence", "paragraph", "story", "comprehension"],
            "Social Science": ["history", "geography", "civics", "map", "constitution",
                               "empire", "climate", "democracy", "culture", "resources"],
            "Computer Science": ["programming", "algorithm", "python", "loop", "variable",
                                 "function", "database", "network", "binary", "code"],
        }
        msg_lower = user_message.lower()
        topics_covered = session.get("topics_covered", [])
        for subject, keywords in subject_keywords.items():
            if any(kw in msg_lower for kw in keywords):
                entry = {
                    "subject": subject,
                    "query":   user_message[:60] + ("…" if len(user_message) > 60 else ""),
                    "time":    datetime.datetime.now().strftime("%d %b, %I:%M %p"),
                }
                topics_covered.append(entry)
                break
        session["topics_covered"] = topics_covered
        session.modified = True

        return jsonify({"reply": ai_reply, "timestamp": timestamp})

    except Exception as exc:   # noqa: BLE001
        app.logger.error("watsonx.ai error: %s", exc)
        return jsonify({
            "error": (
                "Oops! Buddy is having a little trouble right now. "
                "Please check your IBM API credentials in the .env file and try again. "
                f"Details: {str(exc)}"
            )
        }), 500


@app.route("/api/clear-chat", methods=["POST"])
def clear_chat():
    """Clear the current conversation history from the session."""
    session["chat_history"] = []
    session.modified = True
    return jsonify({"status": "ok", "message": "Chat cleared successfully."})


@app.route("/api/history", methods=["GET"])
def get_history():
    """Return the full chat history as JSON (used by the frontend on page load)."""
    return jsonify({"history": session.get("chat_history", [])})


# ----------------------------------------------------------
# App Entry Point
# ----------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    print(f"\n{'='*55}")
    print(f"  📚  Study With Buddy is running!")
    print(f"  🌐  Open http://localhost:{port} in your browser")
    print(f"{'='*55}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)

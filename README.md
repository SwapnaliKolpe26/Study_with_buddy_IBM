# Study With Buddy 📚🤖

> An AI-powered Study Assistant web application for students aged **11–16 years**.  
> Built with **Python Flask** + **IBM watsonx.ai Granite 3.3 8B Instruct** + **Bootstrap 5**.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🧠 **AI Tutor** | IBM Granite model explains topics, solves problems, and answers questions |
| 🎓 **Grade-Adaptive** | Buddy asks your class (6–10) and tailors depth accordingly |
| 📝 **Practice Quizzes** | Auto-generated MCQs, fill-in-the-blank, short-answer questions |
| 💬 **Chat Interface** | Markdown-rendered chat bubbles, typing animation, history, clear option |
| 🌙 **Dark Mode** | One-click toggle, preference saved in `localStorage` |
| 📊 **Student Dashboard** | Tracks activity, topics explored, subject coverage, and study tips |
| 🔒 **Safe & Focused** | Content rules restrict Buddy to education-only responses |
| 📱 **Mobile-Friendly** | Fully responsive Bootstrap 5 layout |
| ⚙️ **AGENT_INSTRUCTIONS** | Easy customization block — change tone, grade, curriculum with zero app logic changes |

---

## 📁 Project Structure

```
study-with-buddy/
│
├── app.py                    ← Flask backend + AGENT_INSTRUCTIONS
├── requirements.txt          ← Python dependencies
├── .env.example              ← Environment variable template
├── .gitignore
│
├── templates/
│   ├── base.html             ← Shared layout (navbar, footer, theme toggle)
│   ├── index.html            ← Landing / home page
│   ├── chat.html             ← Main chat interface
│   └── dashboard.html        ← Student progress dashboard
│
└── static/
    ├── css/
    │   └── style.css         ← All custom styles (light + dark mode)
    └── js/
        └── main.js           ← Theme, chat send/receive, markdown render
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites

- Python 3.9 or higher
- An **IBM Cloud account** — [sign up free](https://cloud.ibm.com/registration)
- An **IBM watsonx.ai** project

### Step 1 — Clone / Download

```bash
# If cloned from git:
cd study-with-buddy

# Or just navigate into the project folder you created
```

### Step 2 — Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set Up Environment Variables

```bash
# Copy the example file
copy .env.example .env          # Windows
cp .env.example .env            # macOS/Linux
```

Open `.env` in any text editor and fill in your values:

```env
IBM_API_KEY=your_actual_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_actual_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=a_long_random_string_here
FLASK_ENV=development
FLASK_PORT=5000
```

#### How to get your IBM credentials:

1. **IBM Cloud API Key**
   - Go to [https://cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)
   - Click **Create an IBM Cloud API key**
   - Copy and save it — you won't see it again

2. **watsonx.ai Project ID**
   - Go to [https://dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
   - Create or open a project
   - Go to **Manage → General** tab
   - Copy the **Project ID**

3. **watsonx.ai URL** (region-specific)
   | Region | URL |
   |---|---|
   | Dallas (us-south) | `https://us-south.ml.cloud.ibm.com` |
   | Frankfurt (eu-de) | `https://eu-de.ml.cloud.ibm.com` |
   | London (eu-gb) | `https://eu-gb.ml.cloud.ibm.com` |
   | Tokyo (jp-tok) | `https://jp-tok.ml.cloud.ibm.com` |

### Step 5 — Run the Application

```bash
python app.py
```

Open your browser at **http://localhost:5000** 🎉

---

## ⚙️ Customizing the AI (AGENT_INSTRUCTIONS)

All AI behavior is controlled by the `AGENT_INSTRUCTIONS` dictionary at the **top of `app.py`** (lines ~43–100). You do not need to touch any other part of the code.

```python
AGENT_INSTRUCTIONS = {
    "PERSONA":            "Change Buddy's name or character here",
    "TONE":               "Adjust formality, encouragement style",
    "GRADE_RANGE":        "Change age/class targeting (e.g., K-12, college)",
    "LANGUAGE":           "Set default response language",
    "SUBJECTS":           "Add or remove supported subjects",
    "EXPLANATION_STYLE":  "Control how answers are structured",
    "QUIZ_STYLE":         "Customize quiz format and feedback style",
    "SAFETY_RULES":       "Tighten or adjust content restrictions",
    "CURRICULUM":         "Switch from CBSE to IGCSE, Common Core, etc.",
    "EXTRA_NOTES":        "Add any other behavior instructions",
}
```

**Examples of easy customizations:**

- Change curriculum: `"CURRICULUM": "Align with IGCSE Cambridge curriculum."`
- Change language: `"LANGUAGE": "Respond in Hindi by default."`
- Change grade: `"GRADE_RANGE": "You teach students from Class 1 to Class 5 (ages 6–11)."`
- Change tone: `"TONE": "Be formal, precise, and concise."`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Home / landing page |
| `GET` | `/chat` | Chat interface page |
| `GET` | `/dashboard` | Student dashboard |
| `POST` | `/api/chat` | Send a message, get AI reply |
| `POST` | `/api/clear-chat` | Clear session chat history |
| `GET` | `/api/history` | Get full chat history as JSON |

### `/api/chat` — Request / Response

**Request:**
```json
{ "message": "What is photosynthesis?" }
```

**Response:**
```json
{
  "reply": "Great question! Photosynthesis is...",
  "timestamp": "10:32 AM"
}
```

---

## 🌐 Deployment (Production)

### Option A — Gunicorn (Linux/macOS)

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### Option B — Waitress (Windows)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

### Option C — IBM Code Engine / Cloud Foundry

1. Set all environment variables in the platform's config panel (never commit `.env`)
2. Use `gunicorn app:app` as the start command
3. Set `FLASK_ENV=production`

---

## 🛡️ Security Notes

- **Never commit your `.env` file** — it's in `.gitignore`
- The `FLASK_SECRET_KEY` must be a long, random string in production
- Session data is stored server-side in Flask sessions (cookie-signed)
- The AI has built-in safety rules to restrict non-educational content

---

## 🧩 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+, Flask 3.0 |
| AI Model | IBM watsonx.ai — `ibm/granite-3-3-8b-instruct` |
| IBM SDK | `ibm-watsonx-ai` 1.1.x |
| Frontend | Bootstrap 5.3, Bootstrap Icons |
| Markdown | Marked.js (CDN) |
| Fonts | Inter, JetBrains Mono (Google Fonts) |
| Env Mgmt | python-dotenv |

---

## 📄 License

MIT — free to use, modify, and distribute with attribution.

---

*Made with ♥ using IBM watsonx.ai Granite & Flask*

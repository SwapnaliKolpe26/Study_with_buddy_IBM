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

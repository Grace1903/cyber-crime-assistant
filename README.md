# 🛡️ Cyber Crime Intelligence Assistant

An AI-powered web application that helps victims of cyber crime in India understand their situation, take immediate action, and navigate the reporting process — built with Flask and Groq AI.

🔗 **Live Demo:** [cyber-crime-assistant.onrender.com](https://cyber-crime-assistant.onrender.com)

---

## 🎯 Problem Statement

Cyber crime victims in India often don't know:
- What type of crime they've experienced
- What to do immediately after an incident
- Which laws apply to their case
- How and where to file a complaint

This assistant uses Generative AI to analyze free-text complaints and provide instant, actionable guidance.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🔍 **Crime Classification** | AI identifies the exact type of cyber crime |
| ⚠️ **Risk Scoring** | Scores severity from 1–100 with visual indicator |
| ⚡ **Immediate Actions** | Tells victims exactly what to do right now |
| 📷 **Evidence Guide** | What screenshots/documents to collect |
| ⚖️ **Legal Sections** | Applicable IT Act and IPC sections |
| 🔎 **Similar Case Finder** | Matches complaint against known fraud patterns |
| 🛡️ **Prevention Coach** | How to avoid this crime in future |
| 📄 **Investigation Report** | One-click AI-generated report with copy option |
| 🚨 **Smart CTA** | Filing recommendation based on risk level |
| 📞 **Emergency Helplines** | 1930, 181, 1098 always visible |

---

## 🏷️ Crime Categories Covered

- 💰 Financial Fraud (OTP Scam, UPI Fraud, Phishing, KYC Scam)
- 😡 Online Harassment & Cyberbullying
- 🚨 Women Safety (Sextortion, Obscene Messages, Blackmail)
- 📱 Social Media Crime (Fake Profiles, Account Hacking)
- 🪪 Identity Theft & Document Misuse
- 👶 Child Safety

---

## 🧠 How It Works

```
User Complaint + Category
        ↓
Flask Backend
        ↓
Groq AI (llama-3.3-70b-versatile)
        ↓
JSON Analysis (crime type, risk score, legal sections, actions)
        ↓
Similar Case Matching (SQLite)
        ↓
Frontend Dashboard
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, Bootstrap 5, JavaScript |
| Backend | Python, Flask |
| AI | Groq API (llama-3.3-70b-versatile) |
| Database | SQLite |
| Deployment | Render |

---

## 🚀 Setup & Run Locally

```bash
# Clone the repo
git clone https://github.com/Grace1903/cyber-crime-assistant.git
cd cyber-crime-assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

Run the app:
```bash
python app.py
```

Open `http://localhost:5000`

---

## 🔐 Security

- API keys stored in environment variables, never in code
- Input validation on all endpoints
- Exception handling with safe error responses
- HTTPS enforced via Render deployment
- No sensitive user data stored permanently

---

## 📞 Indian Cyber Crime Resources

| Helpline | Purpose |
|---------|---------|
| **1930** | National Cyber Crime Helpline |
| **181** | Women Helpline |
| **1098** | Child Helpline |
| **cybercrime.gov.in** | File Official Complaint Online |

---

## 🔮 Future Enhancements

- RAG with RBI guidelines and cybercrime portal FAQs
- Multilingual support (Hindi, Malayalam, Tamil)
- Fraud trend dashboard with analytics
- AI chatbot for follow-up questions
- PDF report download

---

## 👩‍💻 Author

**Grace Elizabeth Jose**
[GitHub](https://github.com/Grace1903)

---

> Built to make cyber crime reporting accessible to every Indian citizen.

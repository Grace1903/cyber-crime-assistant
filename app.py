from flask import Flask, request, jsonify, render_template
from groq import Groq
import sqlite3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def init_db():
    conn = sqlite3.connect("/tmp/fraud.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cyber_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crime_category TEXT,
            crime_type TEXT,
            description TEXT,
            risk_level TEXT,
            keywords TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_complaint TEXT,
            crime_category TEXT,
            crime_type TEXT,
            risk_score INTEGER,
            summary TEXT,
            actions TEXT,
            prevention_tips TEXT,
            legal_sections TEXT,
            created_at TEXT
        )
    """)
    c.execute("SELECT COUNT(*) FROM cyber_cases")
    if c.fetchone()[0] == 0:
        dummy_cases = [
            ("Financial Fraud", "OTP Scam", "Caller pretended to be from SBI and asked for OTP. Victim shared it and money was deducted.", "High", "otp bank call sbi share"),
            ("Financial Fraud", "UPI Fraud", "Received a UPI collect request from unknown number saying it was for prize money.", "High", "upi collect request prize money"),
            ("Financial Fraud", "Phishing", "Received email from fake Amazon saying account was suspended, clicked link and entered credentials.", "Medium", "email link click amazon credentials password"),
            ("Financial Fraud", "KYC Scam", "Received WhatsApp message saying KYC update needed or account will be blocked. Shared Aadhaar.", "High", "kyc whatsapp aadhaar block update"),
            ("Financial Fraud", "Identity Theft", "Someone used my PAN and Aadhaar to open a loan account without my knowledge.", "Critical", "pan aadhaar loan identity documents"),
            ("Online Harassment", "Cyberstalking", "Someone keeps sending threatening messages and tracking my location through social media.", "High", "threatening messages stalking track location follow"),
            ("Online Harassment", "Cyberbullying", "Classmates created a group and are continuously sending abusive messages and spreading rumours.", "Medium", "bully abusive rumour group messages classmate"),
            ("Women Safety", "Sextortion", "Someone got my private photos and is threatening to share them unless I send money.", "Critical", "private photos threatening share money blackmail"),
            ("Women Safety", "Online Harassment", "Man keeps sending obscene messages and unsolicited photos despite being blocked multiple times.", "High", "obscene messages photos blocked unwanted"),
            ("Social Media Crime", "Fake Profile", "Someone created a fake Facebook profile using my photos and is messaging my contacts.", "High", "fake profile facebook photos contacts impersonate"),
        ]
        c.executemany(
            "INSERT INTO cyber_cases (crime_category, crime_type, description, risk_level, keywords) VALUES (?,?,?,?,?)",
            dummy_cases
        )
    conn.commit()
    conn.close()

def analyze_with_groq(complaint, category):
    prompt = f"""You are an Indian Cyber Crime Legal Assistant. Analyze the complaint and return ONLY valid JSON, no markdown, no explanation.

Crime Category selected by user: {category}

Return this exact JSON format:
{{
  "crime_category": "Financial Fraud / Online Harassment / Women Safety / Social Media Crime / Identity Theft / Other",
  "crime_type": "Specific type like OTP Scam / Cyberstalking / Sextortion etc",
  "risk_score": 85,
  "summary": "2-3 sentence summary of what happened and why it is a crime",
  "immediate_actions": [
    "Action 1",
    "Action 2",
    "Action 3"
  ],
  "next_steps": [
    "Step 1",
    "Step 2"
  ],
  "evidence_to_collect": [
    "Evidence 1",
    "Evidence 2"
  ],
  "legal_sections": [
    "IT Act Section X - description",
    "IPC Section Y - description"
  ],
  "helpline_numbers": [
    "1930 - National Cyber Crime Helpline",
    "Any other relevant helpline"
  ],
  "prevention_tips": [
    "Tip 1",
    "Tip 2",
    "Tip 3"
  ]
}}

Complaint:
{complaint}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

def find_similar_cases(complaint, crime_type):
    conn = sqlite3.connect("/tmp/fraud.db")
    c = conn.cursor()
    c.execute("SELECT crime_category, crime_type, description, risk_level, keywords FROM cyber_cases")
    cases = c.fetchall()
    conn.close()
    complaint_lower = complaint.lower()
    matches = []
    for case in cases:
        cat, ct, desc, risk, keywords = case
        keyword_list = keywords.lower().split()
        score = sum(1 for kw in keyword_list if kw in complaint_lower)
        if ct.lower() in crime_type.lower():
            score += 3
        if score > 0:
            matches.append({
                "crime_category": cat,
                "crime_type": ct,
                "description": desc,
                "risk_level": risk,
                "match_score": score
            })
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches[:3]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    complaint = data.get("complaint", "").strip()
    category = data.get("category", "General").strip()
    if not complaint:
        return jsonify({"error": "Please enter a complaint"}), 400
    try:
        analysis = analyze_with_groq(complaint, category)
        similar = find_similar_cases(complaint, analysis.get("crime_type", ""))
        conn = sqlite3.connect("/tmp/fraud.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO complaints
            (user_complaint, crime_category, crime_type, risk_score, summary, actions, prevention_tips, legal_sections, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint,
            analysis.get("crime_category"),
            analysis.get("crime_type"),
            analysis.get("risk_score"),
            analysis.get("summary"),
            json.dumps(analysis.get("immediate_actions", [])),
            json.dumps(analysis.get("prevention_tips", [])),
            json.dumps(analysis.get("legal_sections", [])),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "analysis": analysis, "similar_cases": similar})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history")
def history():
    conn = sqlite3.connect("/tmp/fraud.db")
    c = conn.cursor()
    c.execute("SELECT crime_category, crime_type, risk_score, summary, created_at FROM complaints ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"crime_category": r[0], "crime_type": r[1], "risk_score": r[2], "summary": r[3], "created_at": r[4]} for r in rows])

init_db()

if __name__ == "__main__":
    app.run(debug=True)
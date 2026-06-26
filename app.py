from flask import Flask, request, jsonify, render_template
from google import genai
import sqlite3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def init_db():
    conn = sqlite3.connect("database/fraud.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS fraud_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fraud_type TEXT,
            description TEXT,
            risk_level TEXT,
            keywords TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_complaint TEXT,
            fraud_type TEXT,
            risk_score INTEGER,
            summary TEXT,
            actions TEXT,
            prevention_tips TEXT,
            created_at TEXT
        )
    """)
    c.execute("SELECT COUNT(*) FROM fraud_cases")
    if c.fetchone()[0] == 0:
        dummy_cases = [
            ("OTP Scam", "Caller pretended to be from SBI and asked for OTP. Victim shared it and money was deducted.", "High", "otp bank call sbi share"),
            ("UPI Fraud", "Received a UPI collect request from unknown number saying it was for prize money.", "High", "upi collect request prize money"),
            ("Phishing", "Received email from fake Amazon saying account was suspended, clicked link and entered credentials.", "Medium", "email link click amazon credentials password"),
            ("KYC Scam", "Received WhatsApp message saying KYC update needed or account will be blocked. Shared Aadhaar.", "High", "kyc whatsapp aadhaar block update"),
            ("Identity Theft", "Someone used my PAN and Aadhaar to open a loan account without my knowledge.", "Critical", "pan aadhaar loan identity documents")
        ]
        c.executemany(
            "INSERT INTO fraud_cases (fraud_type, description, risk_level, keywords) VALUES (?,?,?,?)",
            dummy_cases
        )
    conn.commit()
    conn.close()

def analyze_with_gemini(complaint):
    prompt = f"""
You are a Cyber Fraud Investigation Assistant. Analyze the complaint below and return a JSON response only.

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
  "fraud_type": "Name of fraud type",
  "risk_score": 85,
  "summary": "2-3 sentence summary of what happened",
  "immediate_actions": ["Action 1", "Action 2", "Action 3"],
  "next_steps": ["Step 1", "Step 2"],
  "prevention_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

Complaint:
{complaint}
"""
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

def find_similar_cases(complaint, fraud_type):
    conn = sqlite3.connect("database/fraud.db")
    c = conn.cursor()
    c.execute("SELECT fraud_type, description, risk_level, keywords FROM fraud_cases")
    cases = c.fetchall()
    conn.close()
    complaint_lower = complaint.lower()
    matches = []
    for case in cases:
        ft, desc, risk, keywords = case
        keyword_list = keywords.lower().split()
        score = sum(1 for kw in keyword_list if kw in complaint_lower)
        if ft.lower() in fraud_type.lower():
            score += 3
        if score > 0:
            matches.append({
                "fraud_type": ft,
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
    if not complaint:
        return jsonify({"error": "Please enter a complaint"}), 400
    try:
        analysis = analyze_with_gemini(complaint)
        similar = find_similar_cases(complaint, analysis.get("fraud_type", ""))
        conn = sqlite3.connect("database/fraud.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO complaints 
            (user_complaint, fraud_type, risk_score, summary, actions, prevention_tips, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            complaint,
            analysis.get("fraud_type"),
            analysis.get("risk_score"),
            analysis.get("summary"),
            json.dumps(analysis.get("immediate_actions", [])),
            json.dumps(analysis.get("prevention_tips", [])),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
        return jsonify({
            "success": True,
            "analysis": analysis,
            "similar_cases": similar
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history")
def history():
    conn = sqlite3.connect("database/fraud.db")
    c = conn.cursor()
    c.execute("""
        SELECT fraud_type, risk_score, summary, created_at 
        FROM complaints ORDER BY id DESC LIMIT 10
    """)
    rows = c.fetchall()
    conn.close()
    return jsonify([{
        "fraud_type": r[0],
        "risk_score": r[1],
        "summary": r[2],
        "created_at": r[3]
    } for r in rows])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
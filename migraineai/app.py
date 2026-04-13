from flask import (Flask, render_template, request, jsonify,
                   session, redirect, url_for)
from functools import wraps
import hashlib
import os  # <--- Added this to read environment variables
import database as db
import model_engine as engine

app = Flask(__name__)

# Use an environment variable for the secret key, or a fallback for local dev
app.secret_key = os.environ.get("SECRET_KEY", "migraineai-secret-key-change-in-production")

db.init_db()

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    data = request.form
    ok, msg = db.create_user(
        name=data["name"], email=data["email"],
        password_hash=hash_pw(data["password"]),
        age=data.get("age"), gender=data.get("gender")
    )
    if ok:
        user = db.get_user_by_email(data["email"])
        session["user_id"]   = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("dashboard"))
    return render_template("register.html", error=msg)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = db.get_user_by_email(request.form["email"])
    if user and user["password_hash"] == hash_pw(request.form["password"]):
        session["user_id"]   = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Invalid email or password")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    uid         = session["user_id"]
    assessments = db.get_user_assessments(uid)
    symptom_sum = db.get_symptom_summary(uid)
    latest      = assessments[0] if assessments else None
    return render_template("dashboard.html",
        user_name         = session["user_name"],
        assessments       = assessments,
        symptom_sum       = symptom_sum,
        latest            = latest,
        total_assessments = len(assessments)
    )

@app.route("/assess")
@login_required
def assess():
    return render_template("assess.html")

@app.route("/result/<int:aid>")
@login_required
def result(aid):
    assessment, recs = db.get_assessment_with_recs(aid)
    if not assessment or assessment["user_id"] != session["user_id"]:
        return redirect(url_for("dashboard"))
    return render_template("result.html", a=assessment, recs=recs)

@app.route("/log")
@login_required
def log_page():
    logs = db.get_symptom_logs(session["user_id"])
    return render_template("log.html", logs=logs)

@app.route("/api/assess", methods=["POST"])
@login_required
def api_assess():
    data = request.json
    features = {
        "Age":               int(data.get("age", 30)),
        "Duration":          int(data.get("duration", 1)),
        "Frequency":         int(data.get("frequency", 1)),
        "Location":          int(data.get("location", 1)),
        "Character":         int(data.get("character", 1)),
        "Intensity":         int(data.get("intensity", 1)),
        "Nausea":            int(data.get("nausea", 0)),
        "Vomit":             int(data.get("vomit", 0)),
        "Phonophobia":       int(data.get("phonophobia", 0)),
        "Photophobia":       int(data.get("photophobia", 0)),
        "Visual":            int(data.get("visual", 0)),
        "Sensory":           int(data.get("sensory", 0)),
        "Dysphasia":         int(data.get("dysphasia", 0)),
        "Dysarthria":        int(data.get("dysarthria", 0)),
        "Vertigo":           int(data.get("vertigo", 0)),
        "Tinnitus":          int(data.get("tinnitus", 0)),
        "Hypoacusis":        int(data.get("hypoacusis", 0)),
        "Diplopia":          int(data.get("diplopia", 0)),
        "Defect":            int(data.get("defect", 0)),
        "Ataxia":            int(data.get("ataxia", 0)),
        "Conscience":        int(data.get("conscience", 0)),
        "Paresthesia":       int(data.get("paresthesia", 0)),
        "DPF":               int(data.get("dpf", 0)),
        "Sleep_Duration":    float(data.get("sleep_duration", 7)),
        "Sleep_Quality":     int(data.get("sleep_quality", 6)),
        "Physical_Activity": int(data.get("physical_activity", 50)),
        "Stress_Level":      int(data.get("stress_level", 4)),
        "BMI":               float(data.get("bmi", 22)),
        "BP_Systolic":       int(data.get("bp_systolic", 120)),
        "Heart_Rate":        int(data.get("heart_rate", 72)),
        "Daily_Steps":       int(data.get("daily_steps", 7000)),
        "Sleep_Disorder":    int(data.get("sleep_disorder", 0)),
    }
    result  = engine.predict(features)
    aid = db.save_assessment(
        user_id=session["user_id"],
        features=features,
        result={
            "predicted_type": result["predicted_type"],
            "risk_score":     result["risk_score"],
            "attack_prob":    result["attack_prob"],
            "chronic_risk":   result["chronic_risk"],
            "risk_category":  result["risk_category"],
        },
        recommendations=result["recommendations"]
    )
    result["assessment_id"] = aid
    return jsonify(result)

@app.route("/api/log", methods=["POST"])
@login_required
def api_log():
    data = request.json
    db.add_symptom_log(
        user_id      = session["user_id"],
        severity     = int(data.get("severity", 0)),
        duration_hrs = float(data.get("duration_hrs", 0)),
        triggers     = data.get("triggers", ""),
        medication   = data.get("medication", ""),
        notes        = data.get("notes", "")
    )
    return jsonify({"ok": True})

@app.route("/api/trends")
@login_required
def api_trends():
    return jsonify(db.get_trend_data(session["user_id"]))

@app.route("/api/history")
@login_required
def api_history():
    return jsonify(db.get_user_assessments(session["user_id"]))

# --- MODIFIED FOR DEPLOYMENT ---
if __name__ == "__main__":
    # Render and other hosts use the 'PORT' environment variable
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' is required to make the app reachable on the internet
    app.run(host='0.0.0.0', port=port)

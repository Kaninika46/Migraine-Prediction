"""
model_engine.py  —  Loads trained model + runs predictions
"""

import pickle
import numpy as np

with open("model/rf_model.pkl",    "rb") as f: _clf          = pickle.load(f)
with open("model/le_type.pkl",     "rb") as f: _le_type      = pickle.load(f)
with open("model/feature_cols.pkl","rb") as f: _feature_cols = pickle.load(f)


def predict(features: dict) -> dict:
    import pandas as _pd
    row   = _pd.DataFrame([[features.get(c, 0) for c in _feature_cols]], columns=_feature_cols)
    proba = _clf.predict_proba(row)[0]
    pred_idx       = int(np.argmax(proba))
    confidence     = float(proba[pred_idx])
    predicted_type = _le_type.classes_[pred_idx]

    score = 0
    neuro_cols = ["Visual","Sensory","Dysphasia","Dysarthria","Vertigo",
                  "Tinnitus","Hypoacusis","Diplopia","Defect","Ataxia",
                  "Conscience","Paresthesia"]
    score += min(sum(features.get(c, 0) for c in neuro_cols) * 3, 25)
    score += min(int(features.get("Frequency", 0)) * 2, 14)
    score += int(features.get("Intensity", 0)) * 3
    score += int(features.get("Duration",  0)) * 2

    stress     = float(features.get("Stress_Level",  5))
    sleep_dur  = float(features.get("Sleep_Duration",7))
    sleep_qual = float(features.get("Sleep_Quality", 6))
    bp         = float(features.get("BP_Systolic", 120))
    activity   = float(features.get("Physical_Activity", 50))

    score += round((stress / 8) * 15)
    if sleep_dur  < 6:  score += 8
    elif sleep_dur  < 7: score += 4
    if sleep_qual < 5:  score += 6
    elif sleep_qual < 7: score += 3
    if bp >= 140:        score += 8
    elif bp >= 130:      score += 4
    elif bp >= 120:      score += 2
    if activity < 30:    score += 5
    elif activity < 50:  score += 2
    if int(features.get("DPF",   0)) == 1: score += 5
    if int(features.get("Nausea",0)):       score += 3
    if int(features.get("Vomit", 0)):       score += 2

    sleep_disorder = int(features.get("Sleep_Disorder", 0))
    score += sleep_disorder * 3

    risk_score   = min(int(score), 100)
    attack_prob  = min(round(risk_score * 0.88), 95)
    freq         = int(features.get("Frequency", 0))
    chronic_risk = min(round(risk_score * 0.65 + freq * 3), 95)

    if risk_score < 30:   risk_category = "Low"
    elif risk_score < 55: risk_category = "Moderate"
    else:                 risk_category = "High"

    recs = []
    if stress     >= 6:  recs.append({"icon":"🧘","text":"High stress detected. Practice mindfulness or yoga for 15 min daily."})
    if sleep_dur  <  7 or sleep_qual < 6: recs.append({"icon":"😴","text":"Poor sleep pattern. Keep consistent sleep/wake times, avoid screens 1hr before bed."})
    if bp         >= 130: recs.append({"icon":"❤️","text":"Elevated blood pressure. Reduce sodium intake and consult a physician."})
    if activity   <  40:  recs.append({"icon":"🏃","text":"Low physical activity. Aim for 30 min aerobic exercise, 4 days/week."})
    if int(features.get("DPF",0)) == 1: recs.append({"icon":"🧬","text":"Family history of migraine. Schedule regular neurological check-ups."})
    if freq >= 5:         recs.append({"icon":"📅","text":"Frequent attacks. Keep a headache diary to identify patterns."})
    if sleep_disorder==1: recs.append({"icon":"🌙","text":"Insomnia noted. CBT-I (Cognitive Behavioural Therapy for Insomnia) is recommended."})
    if sleep_disorder==2: recs.append({"icon":"😮‍💨","text":"Sleep Apnea noted. Consider a sleep study and CPAP evaluation."})
    if int(features.get("Nausea",0)) or int(features.get("Vomit",0)):
        recs.append({"icon":"🥗","text":"Nausea present. Eat small regular meals, stay hydrated, avoid trigger foods."})
    if not recs:
        recs.append({"icon":"✅","text":"Your risk profile looks manageable. Keep up healthy lifestyle habits."})

    return {
        "predicted_type":  predicted_type,
        "confidence":      round(confidence * 100, 1),
        "risk_score":      risk_score,
        "attack_prob":     attack_prob,
        "chronic_risk":    chronic_risk,
        "risk_category":   risk_category,
        "recommendations": recs
    }
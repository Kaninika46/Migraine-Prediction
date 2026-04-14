# 🧠 MigraineAI — Personalized Risk Stratification System

> AI-Based Personalized Migraine Risk Stratification and Chronic Progression Monitoring System

**Course:** ABAI1010L — Foundations of AI Programming using Python  
**Institution:** Bennett University — School of Artificial Intelligence  
**Team:** Kaninika Giri  | Akshita Dey 
**Submitted to:** Dr. Shakshi Sharma  

---

## 🌐 Live Demo
👉 **[https://migraine-prediction-h7ke.onrender.com](https://migraine-prediction-h7ke.onrender.com)**

> ⚠️ First load may take 50 seconds (free tier spin-up). Please wait.

---

## 📌 Problem Statement
Migraine affects over **1 billion people** globally. Most existing apps only log symptoms. This system uses AI to **predict and prevent** migraine episodes by analyzing neurological symptoms, sleep patterns, and lifestyle factors together.

---

## 🤖 AI Model
| Property | Value |
|----------|-------|
| Algorithm | Random Forest Classifier |
| Number of Trees | 200 |
| Accuracy | 90% |
| Features Used | 32 |
| Train/Test Split | 80% / 20% |
| Target Classes | 7 migraine types |

---

## 📊 Datasets Used
| Dataset | Source | Records | Features |
|---------|--------|---------|---------|
| Migraine Classification | [Kaggle: ranzeet013](https://kaggle.com/datasets/ranzeet013/migraine-dataset) | 400 | 23 neurological |
| Sleep Health & Lifestyle | [Kaggle: uom190346a](https://kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset) | 374 | 13 lifestyle |

Both datasets are merged using **nearest-age join** (`pandas.merge_asof`) to create a unified 32-feature dataset.

---

## ⚙️ Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10, Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Database | SQLite3 |
| ML Model | Scikit-learn Random Forest |
| Charts | Chart.js |
| Model Saving | Pickle |
| Production Server | Gunicorn |
| Deployment | Render.com |
| Version Control | Git + GitHub |

---

## 🚀 Features
- ✅ User Registration & Login (SHA256 hashed passwords)
- ✅ 3-Step Risk Assessment Form (32 features)
- ✅ AI Migraine Type Prediction (7 types)
- ✅ Risk Score 0-100 (Low / Moderate / High)
- ✅ 30-day Attack Probability
- ✅ Chronic Progression Risk Score
- ✅ Personalised AI Recommendations
- ✅ Continuous Assessment Tracking
- ✅ Dashboard with Trend Charts
- ✅ Daily Symptom Diary
- ✅ SQLite Database Storage
- ✅ Live Deployed on Render
---
-  ## 📂 Project Structure

```text
├── data/               # Dataset files
├── model/              # Saved model files (.pkl / .h5)
├── static/             # CSS, JavaScript, and UI assets
├── templates/          # HTML templates for the web interface
├── app.py              # Main application entry point
├── database.py         # Database configuration and schemas
├── model_engine.py     # Logic for AI predictions and processing
├── train_model.py      # Script for training the ML model
├── Procfile            # Configuration for deployment (Render/Heroku)
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version specification
└── README.md           # Project documentation



## 📁 Project Structure

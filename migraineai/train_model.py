

import pandas as pd
import numpy as np
import pickle, os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# ── 1. LOAD ──────────────────────────────────────────────────────────────────
print("Loading datasets...")
migraine_df = pd.read_csv("data/migraine_data.csv")
sleep_df    = pd.read_csv("data/sleep_lifestyle.csv")

print(f"  Migraine dataset : {migraine_df.shape[0]} rows, {migraine_df.shape[1]} cols")
print(f"  Sleep dataset    : {sleep_df.shape[0]} rows, {sleep_df.shape[1]} cols")

# ── 2. CLEAN SLEEP DATASET ───────────────────────────────────────────────────
# Parse Blood Pressure → systolic / diastolic
sleep_df[["BP_Systolic","BP_Diastolic"]] = (
    sleep_df["Blood Pressure"]
    .str.split("/", expand=True)
    .astype(float)
)

# Encode categorical columns
sleep_df["Gender_enc"] = (sleep_df["Gender"] == "Male").astype(int)

bmi_map = {"Normal": 0, "Normal Weight": 0, "Overweight": 1, "Obese": 2}
sleep_df["BMI_enc"] = sleep_df["BMI Category"].map(bmi_map).fillna(0).astype(int)

disorder_map = {None: 0, "None": 0, float('nan'): 0,
                "Insomnia": 1, "Sleep Apnea": 2}
sleep_df["Disorder_enc"] = sleep_df["Sleep Disorder"].map(
    lambda x: 0 if pd.isna(x) or x == "None" else (1 if x == "Insomnia" else 2)
)

# Keep only the columns we'll merge
sleep_features = sleep_df[[
    "Age", "Sleep Duration", "Quality of Sleep",
    "Physical Activity Level", "Stress Level",
    "BMI_enc", "BP_Systolic", "Heart Rate",
    "Daily Steps", "Disorder_enc"
]].copy()

# Aggregate per age (multiple people can share the same age in sleep dataset)
sleep_agg = sleep_features.groupby("Age").mean().reset_index()
sleep_agg.columns = [
    "Age", "Sleep_Duration", "Sleep_Quality",
    "Physical_Activity", "Stress_Level",
    "BMI", "BP_Systolic", "Heart_Rate",
    "Daily_Steps", "Sleep_Disorder"
]

# ── 3. MERGE ─────────────────────────────────────────────────────────────────
# Nearest-age merge: for each migraine row, find the closest age in sleep_agg
migraine_df = migraine_df.sort_values("Age").reset_index(drop=True)
sleep_agg   = sleep_agg.sort_values("Age").reset_index(drop=True)

merged = pd.merge_asof(
    migraine_df,
    sleep_agg,
    on="Age",
    direction="nearest"
)

print(f"\nMerged dataset : {merged.shape[0]} rows, {merged.shape[1]} cols")
print("Missing values :\n", merged.isnull().sum()[merged.isnull().sum() > 0])

# Fill any remaining NaN with column medians
for col in merged.select_dtypes(include=[np.number]).columns:
    merged[col] = merged[col].fillna(merged[col].median())

# ── 4. ENCODE TARGET ─────────────────────────────────────────────────────────
le_type = LabelEncoder()
merged["Type_enc"] = le_type.fit_transform(merged["Type"])
print("\nMigraine types found:")
for i, cls in enumerate(le_type.classes_):
    print(f"  {i} → {cls}  ({(merged['Type']==cls).sum()} samples)")

# ── 5. FEATURES & TARGET ─────────────────────────────────────────────────────
FEATURE_COLS = [
    # from migraine dataset
    "Age", "Duration", "Frequency", "Location", "Character",
    "Intensity", "Nausea", "Vomit", "Phonophobia", "Photophobia",
    "Visual", "Sensory", "Dysphasia", "Dysarthria", "Vertigo",
    "Tinnitus", "Hypoacusis", "Diplopia", "Defect", "Ataxia",
    "Conscience", "Paresthesia", "DPF",
    # from sleep dataset (merged)
    "Sleep_Duration", "Sleep_Quality", "Physical_Activity",
    "Stress_Level", "BMI", "BP_Systolic", "Heart_Rate",
    "Daily_Steps", "Sleep_Disorder"
]

X = merged[FEATURE_COLS]
y = merged["Type_enc"]

# ── 6. TRAIN ─────────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining on {len(X_train)} samples, testing on {len(X_test)} samples...")

clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    random_state=42,
    n_jobs=-1
)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n✅ Accuracy: {acc*100:.1f}%")
print("\nClassification Report:")
print(classification_report(
    y_test, y_pred,
    target_names=le_type.classes_,
    zero_division=0
))

# Feature importance
fi = pd.Series(clf.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
print("Top 10 important features:")
print(fi.head(10).to_string())

# ── 7. SAVE ───────────────────────────────────────────────────────────────────
os.makedirs("model", exist_ok=True)
with open("model/rf_model.pkl",    "wb") as f: pickle.dump(clf,          f)
with open("model/le_type.pkl",     "wb") as f: pickle.dump(le_type,      f)
with open("model/feature_cols.pkl","wb") as f: pickle.dump(FEATURE_COLS, f)

print("\n✅ Saved: model/rf_model.pkl")
print("✅ Saved: model/le_type.pkl")
print("✅ Saved: model/feature_cols.pkl")
print("\nRun  python app.py  to start the Flask server.")
"""
STAT-654 Project: Performance Analysis of Ensemble Methods for
Hotel Booking Cancellation Prediction

Authors: Sai Nithin Reddy Maddi, Sujith Julakanti
Date   : March 2026

Dataset: Hotel Booking Demand (Kaggle)
  https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand

Usage:
  1. Download hotel_bookings.csv from Kaggle and place it in the same folder.
  2. Run:  python hotel_booking_analysis.py
"""

# ── Imports ─────────────────────────────────────────────────────────────────
import time
import warnings
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score, roc_curve,
)
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")
np.random.seed(42)

# ── 0. Configuration ─────────────────────────────────────────────────────────
DATA_FILE   = "hotel_bookings.csv"
OUTPUT_DIR  = "figures"
SAMPLE_SIZE = None          # set to e.g. 50_000 to speed up dev; None = full data
TEST_SIZE   = 0.20
CV_FOLDS    = 5
N_JOBS      = -1            # use all CPU cores

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Helper: pretty section headers ───────────────────────────────────────────
def section(title: str):
    bar = "=" * 60
    print(f"\n{bar}\n  {title}\n{bar}")


# ═══════════════════════════════════════════════════════════════════════════
# 1. DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════
section("1. Data Loading")

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"'{DATA_FILE}' not found.\n"
        "Download it from: https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand\n"
        "and place it in the same directory as this script."
    )

df = pd.read_csv(DATA_FILE)
if SAMPLE_SIZE:
    df = df.sample(SAMPLE_SIZE, random_state=42).reset_index(drop=True)

print(f"Dataset shape : {df.shape}")
print(f"Cancellation rate: {df['is_canceled'].mean():.2%}")
print("\nColumn dtypes:\n", df.dtypes.value_counts().to_string())


# ═══════════════════════════════════════════════════════════════════════════
# 2. EXPLORATORY DATA ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════
section("2. Exploratory Data Analysis")

# 2a. Target distribution
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

cancel_counts = df["is_canceled"].value_counts()
axes[0].bar(["Not Cancelled", "Cancelled"], cancel_counts.values,
            color=["steelblue", "tomato"], edgecolor="white")
axes[0].set_title("Booking Cancellation Distribution")
axes[0].set_ylabel("Count")
for i, v in enumerate(cancel_counts.values):
    axes[0].text(i, v + 200, f"{v:,}\n({v/len(df):.1%})", ha="center", fontsize=9)

# 2b. Cancellation by hotel type
hotel_cancel = df.groupby("hotel")["is_canceled"].mean() * 100
axes[1].bar(hotel_cancel.index, hotel_cancel.values,
            color=["steelblue", "tomato"], edgecolor="white")
axes[1].set_title("Cancellation Rate by Hotel Type")
axes[1].set_ylabel("Cancellation Rate (%)")
for i, v in enumerate(hotel_cancel.values):
    axes[1].text(i, v + 0.5, f"{v:.1f}%", ha="center", fontsize=10)

# 2c. Lead time distribution by cancellation
df[df["is_canceled"] == 0]["lead_time"].clip(0, 365).plot.hist(
    bins=40, alpha=0.6, color="steelblue", label="Not Cancelled", ax=axes[2])
df[df["is_canceled"] == 1]["lead_time"].clip(0, 365).plot.hist(
    bins=40, alpha=0.6, color="tomato", label="Cancelled", ax=axes[2])
axes[2].set_title("Lead Time Distribution by Cancellation")
axes[2].set_xlabel("Lead Time (days, clipped at 365)")
axes[2].legend()

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/eda_overview.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {OUTPUT_DIR}/eda_overview.png")

# 2d. Correlation heatmap (numeric features only)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
corr = df[numeric_cols].corr()
plt.figure(figsize=(12, 10))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=False, cmap="coolwarm",
            center=0, linewidths=0.4, cbar_kws={"shrink": 0.8})
plt.title("Correlation Matrix — Numeric Features")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/eda_correlation.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {OUTPUT_DIR}/eda_correlation.png")


# ═══════════════════════════════════════════════════════════════════════════
# 3. PREPROCESSING
# ═══════════════════════════════════════════════════════════════════════════
section("3. Preprocessing")

# 3a. Drop leaky / identifier columns
DROP_COLS = [
    "reservation_status",       # directly encodes the target
    "reservation_status_date",  # same reason
    "arrival_date_year",        # year alone not generalizable
    "company",                  # > 90% missing
    "agent",                    # many categories, high cardinality
]
df.drop(columns=[c for c in DROP_COLS if c in df.columns], inplace=True)

# 3b. Missing value handling
print("\nMissing values before treatment:")
print(df.isnull().sum()[df.isnull().sum() > 0].to_string())

df["children"].fillna(0, inplace=True)
df["country"].fillna("Unknown", inplace=True)
df.dropna(inplace=True)

print(f"\nShape after cleaning: {df.shape}")

# 3c. Feature engineering
df["total_nights"]    = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
df["total_guests"]    = df["adults"] + df["children"] + df["babies"]
df["arrival_month_n"] = pd.to_datetime(df["arrival_date_month"], format="%B").dt.month

# 3d. Encode categoricals
cat_cols = df.select_dtypes(include="object").columns.tolist()
print(f"\nEncoding {len(cat_cols)} categorical columns: {cat_cols}")

le = LabelEncoder()
for col in cat_cols:
    df[col] = le.fit_transform(df[col].astype(str))

# 3e. Train / test split
X = df.drop(columns=["is_canceled"])
y = df["is_canceled"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=42, stratify=y
)
print(f"\nTrain size: {len(X_train):,}  |  Test size: {len(X_test):,}")
print(f"Train cancellation rate: {y_train.mean():.2%}  |  Test: {y_test.mean():.2%}")

# 3f. Scale features (needed for Logistic Regression)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)


# ═══════════════════════════════════════════════════════════════════════════
# 4. MODEL TRAINING & HYPERPARAMETER TUNING
# ═══════════════════════════════════════════════════════════════════════════
section("4. Model Training & Hyperparameter Tuning")

cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=42)

# ── 4a. Logistic Regression ──────────────────────────────────────────────
print("\n[1/4] Logistic Regression ...")
lr_param_grid = {
    "C": [0.01, 0.1, 1.0, 10.0],
    "solver": ["lbfgs"],
    "max_iter": [1000],
}
lr_gs = GridSearchCV(
    LogisticRegression(random_state=42),
    lr_param_grid, cv=cv, scoring="f1", n_jobs=N_JOBS, refit=True, verbose=0
)
t0 = time.time()
lr_gs.fit(X_train_sc, y_train)
lr_train_time = time.time() - t0
print(f"   Best params : {lr_gs.best_params_}")
print(f"   CV F1       : {lr_gs.best_score_:.4f}")
print(f"   Training time: {lr_train_time:.1f}s")

# ── 4b. Decision Tree ───────────────────────────────────────────────────
print("\n[2/4] Decision Tree ...")
dt_param_grid = {
    "max_depth": [5, 10, 15, None],
    "min_samples_split": [2, 10, 20],
    "min_samples_leaf": [1, 5, 10],
    "criterion": ["gini", "entropy"],
}
dt_gs = GridSearchCV(
    DecisionTreeClassifier(random_state=42),
    dt_param_grid, cv=cv, scoring="f1", n_jobs=N_JOBS, refit=True, verbose=0
)
t0 = time.time()
dt_gs.fit(X_train, y_train)
dt_train_time = time.time() - t0
print(f"   Best params : {dt_gs.best_params_}")
print(f"   CV F1       : {dt_gs.best_score_:.4f}")
print(f"   Training time: {dt_train_time:.1f}s")

# ── 4c. Random Forest ───────────────────────────────────────────────────
print("\n[3/4] Random Forest ...")
rf_param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [10, 20, None],
    "min_samples_split": [2, 5],
    "max_features": ["sqrt", "log2"],
}
rf_gs = GridSearchCV(
    RandomForestClassifier(random_state=42, n_jobs=N_JOBS),
    rf_param_grid, cv=cv, scoring="f1", n_jobs=N_JOBS, refit=True, verbose=0
)
t0 = time.time()
rf_gs.fit(X_train, y_train)
rf_train_time = time.time() - t0
print(f"   Best params : {rf_gs.best_params_}")
print(f"   CV F1       : {rf_gs.best_score_:.4f}")
print(f"   Training time: {rf_train_time:.1f}s")

# ── 4d. Gradient Boosting ───────────────────────────────────────────────
print("\n[4/4] Gradient Boosting ...")
gb_param_grid = {
    "n_estimators": [100, 200],
    "learning_rate": [0.05, 0.1, 0.2],
    "max_depth": [3, 5, 7],
    "subsample": [0.8, 1.0],
}
gb_gs = GridSearchCV(
    GradientBoostingClassifier(random_state=42),
    gb_param_grid, cv=cv, scoring="f1", n_jobs=N_JOBS, refit=True, verbose=0
)
t0 = time.time()
gb_gs.fit(X_train, y_train)
gb_train_time = time.time() - t0
print(f"   Best params : {gb_gs.best_params_}")
print(f"   CV F1       : {gb_gs.best_score_:.4f}")
print(f"   Training time: {gb_train_time:.1f}s")


# ═══════════════════════════════════════════════════════════════════════════
# 5. EVALUATION
# ═══════════════════════════════════════════════════════════════════════════
section("5. Model Evaluation on Test Set")

models = {
    "Logistic Regression": (lr_gs.best_estimator_, X_test_sc, lr_train_time),
    "Decision Tree":       (dt_gs.best_estimator_, X_test,    dt_train_time),
    "Random Forest":       (rf_gs.best_estimator_, X_test,    rf_train_time),
    "Gradient Boosting":   (gb_gs.best_estimator_, X_test,    gb_train_time),
}

results = []
conf_matrices = {}
roc_data = {}

for name, (model, X_ev, train_t) in models.items():
    y_pred = model.predict(X_ev)
    y_prob = model.predict_proba(X_ev)[:, 1]

    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec  = recall_score(y_test, y_pred, zero_division=0)
    f1   = f1_score(y_test, y_pred, zero_division=0)
    auc  = roc_auc_score(y_test, y_prob)

    results.append({
        "Model":        name,
        "Accuracy":     acc,
        "Precision":    prec,
        "Recall":       rec,
        "F1-Score":     f1,
        "ROC-AUC":      auc,
        "Train Time(s)": train_t,
    })
    conf_matrices[name] = confusion_matrix(y_test, y_pred)
    roc_data[name] = roc_curve(y_test, y_prob)

results_df = pd.DataFrame(results).set_index("Model")
print("\n" + results_df.round(4).to_string())


# ── 5a. Metrics comparison bar chart ────────────────────────────────────
metrics = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
x = np.arange(len(metrics))
width = 0.20
colors = ["steelblue", "seagreen", "darkorange", "tomato"]

fig, ax = plt.subplots(figsize=(13, 5))
for i, (name, color) in enumerate(zip(results_df.index, colors)):
    vals = results_df.loc[name, metrics].values
    bars = ax.bar(x + i * width, vals, width, label=name, color=color, alpha=0.85,
                  edgecolor="white")

ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(metrics, fontsize=11)
ax.set_ylim(0.60, 1.02)
ax.set_ylabel("Score")
ax.set_title("Model Performance Comparison on Test Set", fontsize=13, fontweight="bold")
ax.legend(fontsize=9)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/metrics_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\nSaved: {OUTPUT_DIR}/metrics_comparison.png")


# ── 5b. ROC curves ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 6))
for (name, color) in zip(roc_data.keys(), colors):
    fpr, tpr, _ = roc_data[name]
    auc_val = results_df.loc[name, "ROC-AUC"]
    ax.plot(fpr, tpr, color=color, lw=2, label=f"{name} (AUC={auc_val:.3f})")
ax.plot([0, 1], [0, 1], "k--", lw=1)
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC Curves — All Models", fontsize=13, fontweight="bold")
ax.legend(loc="lower right", fontsize=9)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/roc_curves.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {OUTPUT_DIR}/roc_curves.png")


# ── 5c. Confusion matrices ──────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(11, 9))
axes = axes.flatten()
for ax, (name, cm) in zip(axes, conf_matrices.items()):
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["Not Cancelled", "Cancelled"],
                yticklabels=["Not Cancelled", "Cancelled"],
                cbar=False)
    ax.set_title(name, fontsize=11, fontweight="bold")
    ax.set_ylabel("Actual")
    ax.set_xlabel("Predicted")
plt.suptitle("Confusion Matrices", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/confusion_matrices.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {OUTPUT_DIR}/confusion_matrices.png")


# ── 5d. Training time comparison ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))
names = results_df.index.tolist()
times = results_df["Train Time(s)"].values
bar_colors = colors
bars = ax.barh(names, times, color=bar_colors, alpha=0.85, edgecolor="white")
for bar, t in zip(bars, times):
    ax.text(t + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{t:.1f}s", va="center", fontsize=9)
ax.set_xlabel("Total Training + Tuning Time (seconds)")
ax.set_title("Computational Cost: Training + Grid Search Time", fontsize=12, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/training_time.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {OUTPUT_DIR}/training_time.png")


# ═══════════════════════════════════════════════════════════════════════════
# 6. FEATURE IMPORTANCE & INTERPRETABILITY
# ═══════════════════════════════════════════════════════════════════════════
section("6. Feature Importance & Interpretability")

feature_names = X.columns.tolist()

def plot_feature_importance(importances, title, filename, top_n=20):
    indices = np.argsort(importances)[::-1][:top_n]
    top_features = [feature_names[i] for i in indices]
    top_vals     = importances[indices]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top_features[::-1], top_vals[::-1],
            color="steelblue", alpha=0.85, edgecolor="white")
    ax.set_xlabel("Feature Importance")
    ax.set_title(f"Top {top_n} Feature Importances — {title}",
                 fontsize=12, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/{filename}", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/{filename}")

# Decision Tree
plot_feature_importance(
    dt_gs.best_estimator_.feature_importances_,
    "Decision Tree", "fi_decision_tree.png"
)

# Random Forest
plot_feature_importance(
    rf_gs.best_estimator_.feature_importances_,
    "Random Forest", "fi_random_forest.png"
)

# Gradient Boosting
plot_feature_importance(
    gb_gs.best_estimator_.feature_importances_,
    "Gradient Boosting", "fi_gradient_boosting.png"
)

# Logistic Regression — absolute coefficient magnitudes
lr_coefs = np.abs(lr_gs.best_estimator_.coef_[0])
plot_feature_importance(lr_coefs, "Logistic Regression (|coef|)", "fi_logistic_regression.png")

# ── Side-by-side top-10 importance comparison ─────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, (name, model) in zip(axes, [
    ("Random Forest",     rf_gs.best_estimator_),
    ("Gradient Boosting", gb_gs.best_estimator_),
]):
    imp = model.feature_importances_
    idx = np.argsort(imp)[::-1][:10]
    ax.barh([feature_names[i] for i in idx][::-1],
            imp[idx][::-1], color="steelblue", alpha=0.85, edgecolor="white")
    ax.set_title(f"Top 10: {name}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Importance")
    ax.grid(axis="x", alpha=0.3)
plt.suptitle("Ensemble Methods — Feature Importance Comparison",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/fi_ensemble_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {OUTPUT_DIR}/fi_ensemble_comparison.png")


# ═══════════════════════════════════════════════════════════════════════════
# 7. SUMMARY TABLE
# ═══════════════════════════════════════════════════════════════════════════
section("7. Final Summary")

print("\n" + "─" * 72)
print(results_df[["Accuracy", "Precision", "Recall", "F1-Score",
                   "ROC-AUC", "Train Time(s)"]].round(4).to_string())
print("─" * 72)

best_model = results_df["F1-Score"].idxmax()
print(f"\nBest model by F1-Score: {best_model}  "
      f"(F1={results_df.loc[best_model,'F1-Score']:.4f}, "
      f"AUC={results_df.loc[best_model,'ROC-AUC']:.4f})")

# Save summary CSV
results_df.reset_index().to_csv(f"{OUTPUT_DIR}/results_summary.csv", index=False)
print(f"\nResults saved to: {OUTPUT_DIR}/results_summary.csv")
print("\nAll figures saved to:", OUTPUT_DIR)
print("\nDone.")

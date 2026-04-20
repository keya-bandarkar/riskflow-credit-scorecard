# XGBoost Model for Credit Scoring
import pandas as pd
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix, roc_curve
from scipy.stats import ks_2samp
import matplotlib.pyplot as plt
import seaborn as sns
import urllib.request
import warnings
warnings.filterwarnings('ignore')

# Apply aesthetics
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (10, 6)

print("Loading datasets...")
# Load German Credit Dataset
data_german = fetch_openml(name='credit-g', version=1, as_frame=True, parser='auto')
df_german = data_german.frame
df_german['target'] = df_german['class'].apply(lambda x: 0 if x == 'good' else 1).astype(int)
df_german.drop('class', axis=1, inplace=True)

# Load Australian Credit Dataset
url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/australian/australian.dat'
urllib.request.urlretrieve(url, 'australian.dat')
df_australian = pd.read_csv('australian.dat', sep=r'\s+', header=None, names=['target'] + [f'A{i}' for i in range(1,15)])
df_australian['target'] = df_australian['target'].astype(int)

# Rename columns to match German
column_mapping = {
    'A1': 'checking_status',
    'A2': 'duration',
    'A3': 'credit_history',
    'A4': 'purpose',
    'A5': 'credit_amount',
    'A6': 'savings_status',
    'A7': 'employment',
    'A8': 'installment_commitment',
    'A9': 'personal_status',
    'A10': 'other_parties',
    'A11': 'residence_since',
    'A12': 'property_magnitude',
    'A13': 'age',
    'A14': 'other_payment_plans',
    'target': 'target'
}
df_australian.rename(columns=column_mapping, inplace=True)

# Combine datasets
df = pd.concat([df_german, df_australian], ignore_index=True)
print(f"Combined Data Shape: {df.shape}")

# Preprocessing (simplified)
categorical_cols = df.select_dtypes(include=['category', 'object']).columns.tolist()
numerical_cols = df.select_dtypes(exclude=['category', 'object']).columns.tolist()
if 'target' in numerical_cols:
    numerical_cols.remove('target')

# Binning numerical variables
def auto_binning(df, col, bins=5):
    binned_col = pd.qcut(df[col], q=bins, duplicates='drop')
    return binned_col.astype(str)

df_binned = df.copy()
for col in numerical_cols:
    df_binned[col] = auto_binning(df_binned, col, bins=5)

# Fill missing
for col in df_binned.columns:
    if df_binned[col].isnull().any():
        df_binned[col] = df_binned[col].astype(str).fillna("Missing")

# WOE Transformation (simplified - using all features)
selected_features = [col for col in df_binned.columns if col != 'target']

def compute_woe_iv(df, feature, target):
    total_good = (df[target] == 0).sum()
    total_bad = (df[target] == 1).sum()
    grouped = df.groupby(feature).agg({target: ['count', 'sum']})
    grouped.columns = ['Total', 'Bad']
    grouped['Good'] = grouped['Total'] - grouped['Bad']
    grouped['Dist_Good'] = grouped['Good'] / total_good
    grouped['Dist_Bad'] = grouped['Bad'] / total_bad
    grouped['Dist_Good'] = np.where(grouped['Dist_Good'] == 0, 1e-4, grouped['Dist_Good'])
    grouped['Dist_Bad'] = np.where(grouped['Dist_Bad'] == 0, 1e-4, grouped['Dist_Bad'])
    grouped['WOE'] = np.log(grouped['Dist_Good'] / grouped['Dist_Bad'])
    grouped['IV'] = (grouped['Dist_Good'] - grouped['Dist_Bad']) * grouped['WOE']
    return grouped.reset_index()

woe_tables = {}
for col in selected_features:
    woe_tables[col] = compute_woe_iv(df_binned, col, 'target')

df_woe = df_binned[selected_features + ['target']].copy()
for col in selected_features:
    woe_map = dict(zip(woe_tables[col][col], woe_tables[col]['WOE']))
    df_woe[col] = df_woe[col].map(woe_map)

# Train-test split
X = df_woe[selected_features]
y = df_woe['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost
model = XGBClassifier(random_state=42, eval_metric='logloss')
model.fit(X_train, y_train)

# Evaluate
y_pred_prob = model.predict_proba(X_test)[:, 1]
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_pred_prob)
cm = confusion_matrix(y_test, y_pred)
fpr, tpr, _ = roc_curve(y_test, y_pred_prob)
ks_stat = ks_2samp(y_pred_prob[y_test == 0], y_pred_prob[y_test == 1]).statistic

print(f"XGBoost Results:")
print(f"Accuracy: {acc:.4f}")
print(f"AUC: {auc:.4f}")
print(f"Confusion Matrix:\n{cm}")
print(f"KS Statistic: {ks_stat:.4f}")

# Plot ROC
plt.figure()
plt.plot(fpr, tpr, label=f'AUC = {auc:.4f}')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - XGBoost')
plt.legend()
plt.savefig('xgboost_roc.png')
plt.close()

print("XGBoost model evaluation complete. ROC saved to 'xgboost_roc.png'")
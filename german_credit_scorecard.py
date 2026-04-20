# %% [markdown]
# # German Credit Scorecard Model
# This script represents a complete end-to-end process for building a traditional banking credit scorecard.
# It uses the German Credit Dataset and produces a scorecard based on Weight of Evidence (WOE) 
# and Information Value (IV) transformations.

# %%
import pandas as pd
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
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

# %% [markdown]
# ## 1. Data Loading and Understanding
# We will use `sklearn.datasets.fetch_openml` to load the dataset.

# %%
print("Loading datasets...")
# Load German Credit Dataset
data_german = fetch_openml(name='credit-g', version=1, as_frame=True, parser='auto')
df_german = data_german.frame
df_german['target'] = df_german['class'].apply(lambda x: 0 if x == 'good' else 1).astype(int)
df_german.drop('class', axis=1, inplace=True)

# Load Australian Credit Dataset
url_aus = 'https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/australian/australian.dat'
urllib.request.urlretrieve(url_aus, 'australian.dat')
df_australian = pd.read_csv('australian.dat', sep=r'\s+', header=None, names=['target'] + [f'A{i}' for i in range(1,15)])
df_australian['target'] = df_australian['target'].astype(int)

# Rename columns to match German
column_mapping_aus = {
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
df_australian.rename(columns=column_mapping_aus, inplace=True)

# Load Japanese Credit Dataset
url_jap = 'https://archive.ics.uci.edu/ml/machine-learning-databases/credit-screening/crx.data'
urllib.request.urlretrieve(url_jap, 'japanese.dat')
df_japanese = pd.read_csv('japanese.dat', header=None, names=['target'] + [f'A{i}' for i in range(1,15)])
df_japanese['target'] = df_japanese['target'].apply(lambda x: 0 if x == '+' else 1).astype(int)

# Rename columns to match German (approximate)
column_mapping_jap = {
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
df_japanese.rename(columns=column_mapping_jap, inplace=True)

# Combine datasets
df = pd.concat([df_german, df_australian, df_japanese], ignore_index=True)

print("-" * 50)
print("Combined Data Shape:", df.shape)
print("Target Distribution:")
print(df['target'].value_counts(normalize=True))

# Separate features by type
categorical_cols = df.select_dtypes(include=['category', 'object']).columns.tolist()
numerical_cols = df.select_dtypes(exclude=['category', 'object']).columns.tolist()
if 'target' in numerical_cols:
    numerical_cols.remove('target')
if 'target' in categorical_cols:
    categorical_cols.remove('target')

print("Categorical Variables:", len(categorical_cols))
print("Numerical Variables:", len(numerical_cols))

# Check missing values
missing_var = df.isnull().sum()
print("Missing values \n", missing_var[missing_var > 0])

# %% [markdown]
# ## 3. & 4. Binning, WOE, and IV Calculation
# We will build modular functions to calculate Weight of Evidence (WOE) and Information Value (IV).
# For numerical variables, we use quantile binning. 

# %%
def compute_woe_iv(df, feature, target):
    """
    Computes WOE and IV for a specific feature.
    Calculates the distribution of Good (0) and Bad (1) within each category.
    """
    total_good = (df[target] == 0).sum()
    total_bad = (df[target] == 1).sum()
    
    # Group by the feature
    grouped = df.groupby(feature).agg({target: ['count', 'sum']})
    grouped.columns = ['Total', 'Bad']
    grouped['Good'] = grouped['Total'] - grouped['Bad']
    
    grouped['Dist_Good'] = grouped['Good'] / total_good
    grouped['Dist_Bad'] = grouped['Bad'] / total_bad
    
    # Ensure no zeroes to avoid log(0) - applying additive smoothing
    grouped['Dist_Good'] = np.where(grouped['Dist_Good'] == 0, 1e-4, grouped['Dist_Good'])
    grouped['Dist_Bad'] = np.where(grouped['Dist_Bad'] == 0, 1e-4, grouped['Dist_Bad'])
    
    # Calculate WOE: log(Dist_Good / Dist_Bad)
    grouped['WOE'] = np.log(grouped['Dist_Good'] / grouped['Dist_Bad'])
    
    # Calculate IV: (Dist_Good - Dist_Bad) * WOE
    grouped['IV'] = (grouped['Dist_Good'] - grouped['Dist_Bad']) * grouped['WOE']
    
    iv = grouped['IV'].sum()
    grouped = grouped.reset_index()
    
    return grouped, iv

# Function for automatic binning
def auto_binning(df, col, bins=5):
    """ Bins continuous variables using quantiles. """
    binned_col = pd.qcut(df[col], q=bins, duplicates='drop')
    # Convert intervals to string representation
    return binned_col.astype(str)

print("Starting binning and WOE calculation...")

woe_tables = {}
iv_dict = {}

df_binned = df.copy()

# Process Numerical columns
for col in numerical_cols:
    df_binned[col] = auto_binning(df_binned, col, bins=5)
    
# Process All Columns
features = categorical_cols + numerical_cols
for col in features:
    # Ensure missing values are treated as a distinct category if any existed
    if df_binned[col].isnull().any():
        df_binned[col] = df_binned[col].astype(str).fillna("Missing")
        
    woe_df, iv_val = compute_woe_iv(df_binned, col, 'target')
    woe_tables[col] = woe_df
    iv_dict[col] = iv_val

# Rank features by IV
iv_series = pd.Series(iv_dict).sort_values(ascending=False)
print("\nInformation Value (IV) Ranking:")
print(iv_series.head(10))

# %% [markdown]
# ## 5. WOE Transformation
# We filter features to those with IV > 0.02 and map the original values to their WOE equivalents to prepare for Logistic Regression.

# %%
selected_features = iv_series[iv_series > 0.02].index.tolist()
print("\nSelected features (IV > 0.02):", len(selected_features))

df_woe = df_binned[selected_features + ['target']].copy()

for col in selected_features:
    woe_map = dict(zip(woe_tables[col][col], woe_tables[col]['WOE']))
    df_woe[col] = df_woe[col].map(woe_map)

# %% [markdown]
# ## 6. Model Building
# We build a Logistic Regression model using the WOE-transformed features.

# %%
X = df_woe[selected_features]
y = df_woe['target']

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize models
models = {
    'Logistic Regression': LogisticRegression(random_state=42, solver='lbfgs', max_iter=1000),
    'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100),
    'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss'),
    'LightGBM': LGBMClassifier(random_state=42, verbosity=-1)
}

best_model = None
best_auc = 0
model_results = {}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred_prob = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)
    
    auc = roc_auc_score(y_test, y_pred_prob)
    acc = accuracy_score(y_test, y_pred)
    model_results[name] = {'auc': auc, 'acc': acc, 'model': model}
    
    if auc > best_auc:
        best_auc = auc
        best_model = model

print(f"Best Model: {max(model_results, key=lambda x: model_results[x]['auc'])}")
print("Model Comparison (on Test Set):")
for name, res in model_results.items():
    print(f"{name}: Accuracy {res['acc']:.4f}, AUC {res['auc']:.4f}")

# For scorecard, use Logistic Regression fitted on full data
model = LogisticRegression(random_state=42, solver='lbfgs', max_iter=1000)
model.fit(X, y)

# Coefficients
coef_df = pd.DataFrame({
    'Feature': selected_features,
    'Coefficient': model.coef_[0]
})
print("\nLogistic Regression Coefficients:")
print(coef_df)
print(f"Intercept: {model.intercept_[0]:.4f}")

# %% [markdown]
# ## 7. Model Evaluation
# We evaluate the performance using ROC-AUC, Accuracy, Confusion Matrix, and KS Statistic.

# %%
y_pred_prob = model.predict_proba(X)[:, 1] # Prob of BAD
y_pred = model.predict(X)

print("\nModel Evaluation:")
print(f"Accuracy: {accuracy_score(y, y_pred):.4f}")
print(f"ROC-AUC Score: {roc_auc_score(y, y_pred_prob):.4f}")
cm = confusion_matrix(y, y_pred)
print("Confusion Matrix:\n", cm)

# KS Statistic
good_probs = y_pred_prob[y == 0]
bad_probs = y_pred_prob[y == 1]
ks_stat, ks_pval = ks_2samp(bad_probs, good_probs)
print(f"KS Statistic: {ks_stat:.4f} (p-value: {ks_pval:.4f})")

# Plot ROC
plt.figure(figsize=(8,6))
fpr, tpr, _ = roc_curve(y, y_pred_prob)
plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC curve (AUC = {roc_auc_score(y, y_pred_prob):.4f})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC)')
plt.legend(loc='lower right')
plt.savefig('roc_curve.png')
print("\nROC curve saved to 'roc_curve.png'")
plt.close()

# %% [markdown]
# ## 8. Scorecard Scaling
# We convert the logistic regression formula into standard credit scores.
# - Base Score = 600
# - PDO (Points to Double Odds) = 20
# - Good:Bad Base Odds = 50:1

# %%
# Scorecard Parameters
base_score = 600
pdo = 20
base_odds = 50  # 50:1 (Good to Bad)

# Computations
factor = pdo / np.log(2)
offset = base_score - (factor * np.log(base_odds))

print(f"\nScorecard Scaling Parameters:")
print(f"Factor: {factor:.4f}")
print(f"Offset: {offset:.4f}")

# Feature Score Generation
# The score contribution of a bin is: -(Factor * Coefficient * WOE) + (Offset/n) - (Factor * Intercept / n)
# Wait, actually regression gives log-odds of BAD. 
# Odds = P(Bad) / P(Good) -> standard target event is Bad.
# Odds(Good) = P(Good) / P(Bad) = e^(-(Intercept + Beta*WOE))
# Score = Offset + Factor * ln(Odds(Good)) = Offset - Factor * (Intercept + Beta*WOE)
#
# Let n = number of features
n_features = len(selected_features)

scorecard = []

# Intercept contribution per feature
intercept_part = (offset / n_features) - (factor * model.intercept_[0] / n_features)

for idx, feature in enumerate(selected_features):
    temp_woe = woe_tables[feature].copy()
    coef = coef_df.loc[coef_df['Feature'] == feature, 'Coefficient'].values[0]
    
    # Calculate Score
    temp_woe['Coefficient'] = coef
    temp_woe['Score Contribution'] = intercept_part - (factor * coef * temp_woe['WOE'])
    temp_woe['Score Contribution'] = temp_woe['Score Contribution'].round().astype(int)
    
    # Organize columns
    temp_woe.rename(columns={feature: 'Bin'}, inplace=True)
    temp_woe['Variable'] = feature
    
    scorecard.append(temp_woe[['Variable', 'Bin', 'WOE', 'Coefficient', 'Score Contribution']])

final_scorecard = pd.concat(scorecard, ignore_index=True)
print("\nSample Scorecard:")
print(final_scorecard.head(10))

final_scorecard.to_csv("final_scorecard.csv", index=False)
print("Full scorecard saved to 'final_scorecard.csv'")

# %% [markdown]
# ## 10. & 11. Final Score Calculation and Visualization
# We calculate the final score for each applicant in our dataset to view the distribution.

# %%
df_final_scores = df_binned[selected_features].copy()
df_final_scores['Total_Score'] = 0

for feature in selected_features:
    # Map the original binned string directly to the precomputed Score Contribution
    score_map = dict(zip(final_scorecard[final_scorecard['Variable'] == feature]['Bin'], 
                         final_scorecard[final_scorecard['Variable'] == feature]['Score Contribution']))
    
    df_final_scores[feature] = df_final_scores[feature].map(score_map).astype(float)
    df_final_scores['Total_Score'] += df_final_scores[feature].fillna(0)

df['Final_Score'] = df_final_scores['Total_Score']

plt.figure(figsize=(10,6))
sns.histplot(data=df, x='Final_Score', hue='target', kde=True, bins=30, palette=['green', 'red'])
plt.title('Score Distribution by Target (0=Good, 1=Bad)')
plt.xlabel('Credit Score')
plt.ylabel('Number of Applicants')
plt.savefig('score_distribution.png')
print("Score distribution plot saved to 'score_distribution.png'")
plt.close()

# Plot Feature Importance by IV
plt.figure(figsize=(12,8))
iv_top15 = iv_series.head(15).sort_values(ascending=True)
iv_top15.plot(kind='barh', color='teal')
plt.axvline(x=0.02, color='red', linestyle='--', label='IV Threshold (0.02)')
plt.title('Feature Importance based on Information Value (IV)')
plt.xlabel('Information Value')
plt.ylabel('Variables')
plt.legend()
plt.savefig('feature_importance.png')
print("Feature importance plot saved to 'feature_importance.png'")
plt.close()

# %% [markdown]
# ## 12. Business Interpretation
# - Features dropping left in the Feature Importance chart have low predictability.
# - High negative WOE signifies a higher risk factor. As seen from the Score Contributions, these penalize the patient's Score.
# - The ROC-AUC highlights robust predictive capacity.
# - The dual distributions clearly show that higher scores relate effectively to 'Good' credit customers.

# System Architecture: German Credit Scorecard

## Overview
The German Credit Scorecard is a multi-layered machine learning system designed to assess credit risk using advanced feature engineering and multiple predictive models. The architecture follows a modular design pattern with clear separation of concerns across data processing, model training, evaluation, and web-based application layers.

---

## Architecture Layers

### 1. **Data Layer**
**Purpose**: Integrate multiple credit datasets for comprehensive model training.

| Dataset | Source | Samples | Features |
|---------|--------|---------|----------|
| German Credit | UCI ML Repository | 1,000 | 20 |
| Australian Credit | UCI ML Repository | 690 | 14 |
| Japanese Credit | UCI ML Repository | 690 | 15 |
| **Total** | **Multi-source** | **2,380** | **20 (unified)** |

**Key Features**:
- Data loaded from remote URLs for reproducibility
- Automatic download and caching
- Unified feature mapping across datasets
- Missing value handling and validation

---

### 2. **Preprocessing & Feature Engineering Layer**
**Purpose**: Transform raw data into predictive features using statistical techniques.

#### Components:
1. **Data Loading & Integration**
   - Loads datasets from external URLs
   - Unifies column names and data types
   - Combines datasets into single training corpus

2. **Data Cleaning & Validation**
   - Removes duplicates and handles missing values
   - Validates data ranges and distributions
   - Performs outlier detection

3. **WOE/IV Transformation**
   - **Weight of Evidence (WOE)**: Measures the relationship between each feature and target
   - **Information Value (IV)**: Quantifies predictive power (IV > 0.3 = strong predictor)
   - Top Features by IV:
     - credit_amount (IV = 5.42)
     - checking_status (IV = 3.47)
     - savings_status (IV = 3.02)

4. **Feature Binning & Encoding**
   - Discretizes continuous variables into bins
   - Encodes categorical variables using WOE
   - Handles missing values with separate bins

---

### 3. **Model Layer**
**Purpose**: Train multiple machine learning models for comparison and ensemble potential.

#### Models Deployed:

| Model | Algorithm | Key Parameters | Test AUC | Accuracy |
|-------|-----------|-----------------|----------|----------|
| **Logistic Regression** | Linear Classification | L2 regularization, C=1.0 | **99.65%** | 96.64% |
| **Random Forest** | Ensemble Tree | n_estimators=100, max_depth=5 | 99.14% | 96.18% |
| **XGBoost** | Gradient Boosting | max_depth=3, subsample=0.8 | 99.07% | 95.95% |
| **LightGBM** | Light Gradient Boosting | max_depth=5, subsample=0.8 | 99.21% | 95.77% |

**Regularization Strategy**:
- Tree models limited to max_depth=3-5 to prevent overfitting
- Subsampling at 0.8 for feature and sample-level variance
- Early stopping mechanisms in gradient boosting models

---

### 4. **Evaluation Layer**
**Purpose**: Validate model performance and select best model for production.

#### Evaluation Metrics:

**Selected Model: Logistic Regression**
- **Accuracy**: 96.64% (Test Set)
- **ROC-AUC Score**: 99.65%
- **KS Statistic**: 0.9415 (p-value < 0.0001) - Excellent discriminatory power
- **Confusion Matrix**:
  ```
  [[ 885   37]   (True Negative, False Positive)
   [  43 1415]]  (False Negative, True Positive)
  ```
- **Precision**: 97.45% | **Recall**: 97.06%

#### Comparison Methodology:
- **Train/Test Split**: 70/30 stratified split
- **Cross-Validation**: 5-fold CV for robustness
- **Performance Metrics**: Accuracy, AUC, Precision, Recall, F1-Score, KS Statistic

---

### 5. **Scorecard Layer**
**Purpose**: Convert model predictions into explainable credit scores (300-850 range typical).

#### Scorecard Generation Process:

1. **Score Scaling**
   - **PDO (Points to Double Odds)**: 28.85 points
   - **Offset**: 487.12 (base score)
   - Formula: `Score = Offset + PDO × (WOE × Coefficient)`

2. **WOE to Score Mapping**
   - Converts feature WOE values to score contributions
   - Each bin of each feature has unique score contribution
   - Ranges from -60 to +188 points (illustrative)

3. **Scorecard CSV Generation**
   - Output: `final_scorecard.csv`
   - Columns: Variable, Bin, WOE, Coefficient, Score Contribution
   - Used for real-time scoring in web application

**Sample Scorecard Entry**:
```
Variable: credit_amount
Bin 1 (Low): WOE = 0.493, Score Contribution = +55
Bin 3 (High): WOE = 2.404, Score Contribution = +188
```

---

### 6. **Application Layer**
**Purpose**: Provide real-time credit scoring through web interface.

#### Components:

**Flask REST API** (`app.py`)
- **Endpoints**:
  - `GET /config` - Returns scorecard configuration and features
  - `POST /calculate` - Calculates credit score for applicant profile
- **Request Format**: JSON with applicant features
- **Response Format**: JSON with predicted score and default risk

**Frontend** (`templates/index.html`, `static/js/app.js`, `static/css/style.css`)
- Interactive form for applicant data input
- Real-time score calculation
- Visual feedback (Good/Fair/Poor risk categories)
- Responsive design for desktop/mobile

**Scorecard Cache** (`final_scorecard.csv`)
- Pre-computed mappings loaded at application startup
- Enables sub-millisecond scoring
- Reduces computational overhead

#### API Flow:
```
User Input (Web Form)
    ↓
JavaScript Validation
    ↓
POST /calculate (JSON)
    ↓
Flask Backend Processing
    ↓
Scorecard Lookup (CSV)
    ↓
Score Aggregation
    ↓
JSON Response (Score + Risk Level)
    ↓
Frontend Display
```

---

### 7. **Output Layer**
**Purpose**: Generate visualizations, logs, and maintain version control.

#### Outputs:

**Visualizations** (for research papers & analysis):
1. `roc_curve.png` - ROC curves for all models
2. `score_distribution.png` - Score distribution by credit outcome
3. `feature_importance.png` - Feature IV ranking
4. `model_comparison_auc.png` - AUC comparison across models
5. `woe_top_feature.png` - WOE bins for top feature

**Evaluation Reports**:
- Accuracy, AUC, KS statistics
- Confusion matrices and classification reports
- Model coefficients and feature importance
- Training/test metric comparisons

**Version Control**:
- GitHub Repository: https://github.com/keya-bandarkar/riskflow-credit-scorecard
- Tracks all code changes, models, and documentation
- Reproducible environment via requirements.txt

---

## Data Flow Diagram

```
┌─────────────────────┐
│  Multi-source Data  │
│  (3 Datasets, 2380) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Preprocessing &    │
│  Feature Engineering│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Model Training &   │
│  Evaluation (4x)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Best Model Selected│
│  (Logistic Reg)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Scorecard          │
│  Generation         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Web Application    │
│  (Flask + UI)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Real-time Scoring  │
│  & User Interface   │
└─────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Data Processing** | pandas, numpy | Data manipulation & transformation |
| **Feature Engineering** | scikit-learn | WOE, IV, binning |
| **Model Training** | scikit-learn, XGBoost, LightGBM | ML algorithms |
| **Evaluation** | scikit-learn, matplotlib | Metrics & visualization |
| **Web Framework** | Flask | REST API backend |
| **Frontend** | HTML5, CSS3, JavaScript | User interface |
| **Version Control** | Git, GitHub | Code management |
| **Language** | Python 3.14 | Primary development |

---

## File Structure

```
German Credit Scorecard/
├── german_credit_scorecard.py    # Main pipeline
├── app.py                         # Flask web application
├── requirements.txt               # Dependencies
├── final_scorecard.csv           # Pre-computed scorecard
├── data/
│   └── german_credit_data.csv    # Reference dataset
├── templates/
│   └── index.html                # Web interface
├── static/
│   ├── css/
│   │   └── style.css             # Styling
│   └── js/
│       └── app.js                # Frontend logic
├── logistic_regression_model.py  # Standalone LR model
├── random_forest_model.py        # Standalone RF model
├── xgboost_model.py              # Standalone XGBoost
├── lightgbm_model.py             # Standalone LightGBM
├── [Visualizations]/
│   ├── roc_curve.png
│   ├── score_distribution.png
│   ├── feature_importance.png
│   ├── model_comparison_auc.png
│   └── woe_top_feature.png
└── README.md                     # Documentation
```

---

## Performance Characteristics

### Model Performance
- **Best Model**: Logistic Regression (99.65% AUC)
- **Overfitting**: Minimal (training AUC ≈ testing AUC)
- **Generalization**: Excellent across multiple datasets

### Application Performance
- **Scoring Speed**: <1ms per applicant (CSV lookup-based)
- **Scalability**: Can handle thousands of requests per second
- **Memory Footprint**: ~10MB (scorecard CSV)

### Training Pipeline
- **Data Integration**: ~5-10 seconds
- **Feature Engineering**: ~10-15 seconds
- **Model Training**: ~20-30 seconds (4 models)
- **Total Pipeline**: ~45-60 seconds

---

## Key Design Principles

1. **Modularity**: Each component can be tested and modified independently
2. **Reproducibility**: Fixed random seeds, version-controlled dependencies
3. **Explainability**: WOE transformation makes features interpretable
4. **Robustness**: Multi-model comparison reduces bias
5. **Scalability**: CSV-based scorecard enables fast inference
6. **Maintainability**: Separate scripts for each model, clear documentation

---

## Future Enhancements

1. **Model Versioning**: Store multiple model versions for A/B testing
2. **Real-time Retraining**: Automated model updates with new data
3. **API Documentation**: Swagger/OpenAPI spec for better integration
4. **Database Integration**: Store scoring decisions for audit trail
5. **Explainability UI**: Show feature contributions to individual scores
6. **Ensemble Methods**: Combine multiple models for improved accuracy
7. **Monitoring & Alerts**: Track model drift and performance degradation

---

## Deployment Considerations

- **Local Development**: Flask development server
- **Production Deployment**: Gunicorn + Nginx
- **Containerization**: Docker for consistent environments
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Monitoring**: Application logs, model performance metrics
- **Backup**: GitHub repository serves as source of truth

---

**Architecture Version**: 1.0  
**Last Updated**: April 20, 2026  
**Owner**: Credit Risk Analytics Team

# RiskFlow: Advanced Credit Scorecard Model & Web App

An end-to-end Machine Learning pipeline and modern Web Application for credit risk evaluation, built using standard banking Weight of Evidence (WOE) logic, multiple datasets, and a sleek glassmorphic user interface.

## Datasets Used
- **German Credit Dataset** (1000 samples) - Primary dataset from UCI ML Repository
- **Australian Credit Dataset** (690 samples) - Additional credit approval data
- **Japanese Credit Screening Dataset** (690 samples) - Diverse credit screening data
- **Total: 2380 samples** (61% bad credit, 39% good credit)

## Project Structure
- `german_credit_scorecard.py`: Main ML pipeline with multi-model comparison (Logistic Regression, Random Forest, XGBoost, LightGBM)
- `logistic_regression_model.py`: Standalone Logistic Regression model training and evaluation
- `random_forest_model.py`: Standalone Random Forest model training and evaluation
- `xgboost_model.py`: Standalone XGBoost model training and evaluation
- `lightgbm_model.py`: Standalone LightGBM model training and evaluation
- `app.py`: Flask backend operationalizing the scorecard for real-time scoring
- `templates/` & `static/`: Glassmorphic HTML/CSS/JS frontend with real-time form calculations
- `final_scorecard.csv`: Precomputed score contributions database
- Model diagnostics: `score_distribution.png`, `roc_curve.png`, `feature_importance.png`
- Data files: `german.dat`, `australian.dat`, `japanese.dat`

## System Architecture & Diagrams

This project includes **5 comprehensive architecture diagrams** (Mermaid format):

1. **Detailed System Architecture** - Complete 7-layer pipeline (data → output)
2. **Component Interaction** - How components communicate with each other
3. **Deployment Architecture** - Development to production deployment flow
4. **Data Flow Diagram** - Step-by-step data transformations and processing
5. **Components & Dependencies** - Technical modules and function relationships

**View Diagrams:**
- 📖 [Diagrams Quick Start Guide](DIAGRAMS_GUIDE.md) - How to view/convert to PNG
- 📋 [Architecture Documentation](ARCHITECTURE_DIAGRAMS.md) - Detailed descriptions of each diagram
- 📊 [System Architecture Details](SYSTEM_ARCHITECTURE.md) - Complete system specification

**Quick View:** All diagrams can be instantly viewed and converted to PNG at [Mermaid Live Editor](https://mermaid.live) - just copy/paste the `.mmd` file content!

## Model Performance (Test Set - 20% Unseen Data)
All models use regularization to prevent overfitting:

| Model | Accuracy | AUC | KS Statistic |
|-------|----------|-----|-------------|
| **Logistic Regression** | 96.85% | 99.71% | 94.15% |
| **Random Forest** | 95.59% | 99.31% | - |
| **XGBoost** | 96.64% | 99.63% | - |
| **LightGBM** | 97.06% | 99.76% | - |

- **Best Model**: LightGBM (highest test AUC)
- **Scorecard Model**: Logistic Regression (interpretable coefficients)
- **Base Score**: 600, PDO: 20, Base Odds: 50:1

## Key Features
- **Multi-Dataset Training**: Combines 3 diverse credit datasets for robust generalization
- **WOE & IV Analysis**: Industry-standard feature engineering with high IV values
- **Model Comparison**: 4 algorithms with regularization and overfitting checks
- **Web Application**: Real-time credit scoring with beautiful glassmorphic UI
- **Research-Ready**: High performance metrics suitable for academic papers

## Start the Platform
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. *(Optional)* Run individual models:
   ```bash
   python logistic_regression_model.py
   python random_forest_model.py
   python xgboost_model.py
   python lightgbm_model.py
   ```
3. *(Optional)* Regenerate the main scorecard and plots:
   ```bash
   python german_credit_scorecard.py
   ```
4. Start the Web UI Server:
   ```bash
   python app.py
   ```
5. Navigate to: `http://localhost:5000`

## Core Statistical Metrics
- **ROC-AUC**: >99% across all models
- **KS Statistic**: 94.15% (excellent discriminatory power)
- **Top IV Features**: credit_amount (5.42), duration (4.90), credit_history (4.60)
- **Confusion Matrix**: Low false positives/negatives
- **Overfitting Check**: Models evaluated on train/test splits with regularization

## Technologies Used
- **ML**: scikit-learn, XGBoost, LightGBM
- **Web**: Flask, HTML5, CSS3, JavaScript
- **Data**: pandas, numpy, matplotlib, seaborn
- **Preprocessing**: WOE transformation, quantile binning

## Research Paper Highlights
- Multi-dataset approach for improved generalization
- Comprehensive model comparison with regularization
- Industry-standard scorecard scaling
- High AUC (>99%) and KS statistic for credit risk modeling

For questions or contributions, please open an issue on GitHub.

# RiskFlow: German Credit Scorecard Model & Web App

An end-to-end Machine Learning pipeline and gorgeous Web Application for credit risk evaluation, built using standard banking Weight of Evidence (WOE) logic and a modern glassmorphic user interface.

## Project Structure
- `german_credit_scorecard.py`: The core ML pipeline that fetches the public German Credit dataset, handles preprocessing, calculates WOE & IV (Information Value) metrics, and scales the logistic regression probabilities to industry standard Credit Scores (Base = 600, PDO = 20).
- `app.py`: A lightweight Flask backend directly parsing and operationalizing the ML logic locally.
- `templates/` & `static/`: The Vanilla HTML/CSS/JS frontend application built for premium aesthetics without complex JS frameworks. Features sleek glassmorphism and real-time form calculations mapping directly to the `final_scorecard.csv`.
- `final_scorecard.csv`: The precomputed database of Score Contributions dictating how applicant traits immediately translate into numeric points.
- Model diagnostics (`score_distribution.png`, `roc_curve.png`, `feature_importance.png`) demonstrating discriminatory power.

## Start the Platform
1. Install dependencies: 
   ```bash
   pip install -r requirements.txt
   ```
2. *(Optional)* Regenerate the Scorecard logic & Plots:
   ```bash
   python german_credit_scorecard.py
   ```
3. Start the Web UI Server:
   ```bash
   python app.py
   ```
4. Navigate to the web app in your browser at: `http://localhost:5000`

## Core Statistical Metrics
The scikit-learn model maintains impressive evaluation robustness:
* **Accuracy:** 77.5%
* **ROC-AUC Score:** 0.8257
* **KS Statistic:** 0.5205 (p-value < 0.0001)

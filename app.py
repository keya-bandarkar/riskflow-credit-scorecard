import os
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__)

# Load the scorecard mapping globally
try:
    SCORECARD_FILE = 'final_scorecard.csv'
    scorecard_df = pd.read_csv(SCORECARD_FILE)
    variables = scorecard_df['Variable'].unique().tolist()
    
    # Pre-compute form options safely matching string bins
    form_config = {}
    for var in variables:
        # Extract unique bins as strings to handle numeric edge cases
        bins = [str(b).strip() for b in scorecard_df[scorecard_df['Variable'] == var]['Bin'].unique()]
        form_config[var] = bins
        
except Exception as e:
    print(f"Error loading scorecard: {e}")
    scorecard_df = None
    form_config = {}
    variables = []

@app.route('/')
def home():
    """Serves the main frontend UI."""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Returns the dynamic form configuration based on scorecard bins."""
    return jsonify({'variables': variables, 'options': form_config})

@app.route('/api/calculate', methods=['POST'])
def calculate_score():
    """Calculates the score dynamically given applicant answers."""
    if scorecard_df is None:
        return jsonify({'error': 'Scorecard data not loaded'}), 500
        
    data = request.json
    total_score = 0
    breakdown = []
    
    # Process each variable
    for var in variables:
        user_val = data.get(var)
        
        # Skip if missing user input
        if user_val is None:
            continue
            
        user_val_str = str(user_val).strip()
        
        # Find matching row in scorecard dataframe
        row = scorecard_df[(scorecard_df['Variable'] == var) & (scorecard_df['Bin'].astype(str).str.strip() == user_val_str)]
        
        if not row.empty:
            pts = int(row.iloc[0]['Score Contribution'])
            total_score += pts
            breakdown.append({
                'variable': var,
                'value': user_val_str,
                'points': pts
            })
            
    return jsonify({
        'total_score': total_score,
        'breakdown': breakdown,
        'base_score': 600, # Example metadata fallback
    })

# Route to serve the generated python plot images from project root
@app.route('/images/<filename>')
def serve_image(filename):
    if filename.endswith('.png'):
        return send_from_directory('.', filename)
    return "Not Found", 404

if __name__ == '__main__':
    print("Starting Flask Server at http://localhost:5000")
    app.run(debug=True, port=5000)

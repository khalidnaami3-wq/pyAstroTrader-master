"""
AstroTrader Web API Server
Allows running predictions for any ticker through a web interface
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import pandas as pd
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).parent
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
OUTPUT_DIR = NOTEBOOKS_DIR / "output"

@app.route('/')
def index():
    return send_from_directory('.', 'astrotrader_web.html')

@app.route('/api/run-prediction', methods=['POST'])
def run_prediction():
    """Run AstroTrader prediction for a given ticker"""
    data = request.json
    ticker = data.get('ticker', '').upper().strip()
    api_key = data.get('apiKey', '').strip()
    
    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['ASSET_TO_CALCULATE'] = ticker
        env['ALPHAVANTAGE_KEY'] = api_key
        env['PYTHONPATH'] = f"{BASE_DIR};{NOTEBOOKS_DIR}"
        env['SWISSEPH_PATH'] = str(BASE_DIR / "pyastrotrader" / "swisseph")
        
        # Run the PowerShell script
        cmd = ['powershell', '-File', 'run_astro.ps1', '-Asset', ticker, '-ApiKey', api_key]
        
        process = subprocess.Popen(
            cmd,
            cwd=str(BASE_DIR),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(timeout=600)  # 10 minute timeout
        
        if process.returncode != 0:
            return jsonify({
                'error': f'Prediction failed: {stderr}',
                'stdout': stdout
            }), 500
        
        # Read the results
        results = read_prediction_results(ticker)
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'results': results,
            'message': f'Successfully generated predictions for {ticker}'
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Prediction timed out (>10 minutes)'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-results/<ticker>', methods=['GET'])
def get_results(ticker):
    """Get existing prediction results for a ticker"""
    ticker = ticker.upper().strip()
    
    try:
        results = read_prediction_results(ticker)
        if results:
            return jsonify({
                'success': True,
                'ticker': ticker,
                'results': results
            })
        else:
            return jsonify({
                'success': False,
                'message': f'No results found for {ticker}'
            }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/available-tickers', methods=['GET'])
def available_tickers():
    """List all tickers with existing predictions"""
    try:
        tickers = set()
        for file in OUTPUT_DIR.glob('*.Predict.Simplified.xlsx'):
            ticker = file.stem.split('.')[0]
            tickers.add(ticker)
        
        return jsonify({
            'success': True,
            'tickers': sorted(list(tickers))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def read_prediction_results(ticker):
    """Read prediction results from Excel file"""
    pred_file = OUTPUT_DIR / f"{ticker}.Predict.Simplified.xlsx"
    score_file = OUTPUT_DIR / f"{ticker}.score.price.change.txt"
    
    if not pred_file.exists():
        return None
    
    # Read predictions
    df = pd.read_excel(pred_file)
    predictions = []
    
    for _, row in df.iterrows():
        predictions.append({
            'date': row.get('CorrectedDate', ''),
            'value': float(row.get('PredictPriceChange', 0))
        })
    
    # Read model score if available
    model_score = None
    if score_file.exists():
        with open(score_file, 'r') as f:
            content = f.read().strip()
            if ':' in content:
                model_score = float(content.split(':')[1])
    
    return {
        'predictions': predictions,
        'model_score': model_score,
        'count': len(predictions)
    }

if __name__ == '__main__':
    print("Starting AstroTrader Web Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)

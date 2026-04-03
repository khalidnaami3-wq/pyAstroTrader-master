# AstroTrader

AstroTrader is a research project investigating the correlation between astrological events and stock market price fluctuations. This project uses machine learning (XGBoost) to analyze planetary positions and aspects to predict price trends.

> **⚠️ DISCLAIMER**: This is a research project for educational purposes only. Do NOT use these predictions for actual trading decisions. Past performance does not guarantee future results.

![](docs/jpmorgan.jpg)

## 🌟 New: Web Application

AstroTrader now includes a **fully automated web interface** for easy predictions!

### Quick Start - Web App

1. **Install Dependencies**:

   ```powershell
   pip install -r requirements.txt
   pip install flask flask-cors yfinance
   ```

2. **Start the Web Server**:

   ```powershell
   python astrotrader_server.py
   ```

3. **Open Your Browser**:
   - Navigate to: **http://localhost:5000**
   - Enter any stock ticker (AAPL, MSFT, TSLA, etc.)
   - Click "🚀 Run Prediction"
   - Wait 2-5 minutes for results

### Features

✅ **One-Click Predictions** - No manual commands needed  
✅ **Any Stock Ticker** - Supports stocks, ETFs, crypto (e.g., BTC-USD)  
✅ **Dual Data Sources** - Uses Yahoo Finance (free) or AlphaVantage  
✅ **Real-Time Progress** - Visual progress bar during processing  
✅ **Instant Results** - Predictions display automatically  
✅ **Beautiful UI** - Modern, responsive design

---

## 📊 Data Sources

AstroTrader supports **two data sources**:

### 1. Yahoo Finance (Recommended)

- ✅ **Free** - No API key required
- ✅ **No rate limits**
- ✅ **Reliable** - Works for most stocks
- ✅ **Automatic fallback** in web app

### 2. AlphaVantage

- Requires free API key from [alphavantage.co](https://www.alphavantage.co/support/#api-key)
- Rate limited (5 requests/minute, 500/day for free tier)
- Used as fallback if Yahoo Finance fails

---

## 🔧 Traditional CLI Usage

If you prefer command-line interface:

### Setup

```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install yfinance

# Create output directories
mkdir notebooks\input
mkdir notebooks\output
```

### Run Predictions

```powershell
# Using the automated script (recommended)
./run_astro.ps1 -Asset "AAPL" -ApiKey "YOUR_API_KEY"

# Or set environment variables
$Env:ASSET_TO_CALCULATE = "AAPL"
$Env:ALPHAVANTAGE_KEY = "YOUR_API_KEY"  # Optional with yfinance
./run_astro.ps1
```

### Manual Notebook Execution

```powershell
# Start Jupyter Lab
./start_notebooks.sh

# Or run notebooks via CLI
./run_notebooks.sh
```

---

## 📁 Project Structure

### Main Notebooks

1. **DownloadData.ipynb**  
   Downloads stock quotes for the specified asset and saves to CSV

2. **CreateModel.ipynb**

   - Calculates astrological indicators (planetary positions, aspects, transits)
   - Trains XGBoost model to detect correlations
   - Saves trained model to `notebooks/output/`

3. **Predict.ipynb**  
   Loads the trained model and generates predictions for upcoming trading days

### Python Modules

- **pyastrotrader/** - Core astrological computation library
  - Uses Swiss Ephemeris for accurate planetary calculations
  - `data_fetcher.py` - Flexible data fetching (YFinance/AlphaVantage)
- **astrotrader_server.py** - Flask API server for web interface
- **astrotrader_web.html** - Modern web UI

---

## 🎯 How It Works

### 1. Data Collection

- Downloads 20 years of historical stock data
- Supports: Stocks, ETFs, Crypto (via Yahoo Finance)

### 2. Astrological Analysis

Calculates for each trading day:

- **Planetary Positions** - Degrees in zodiac
- **Aspects** - Angular relationships between planets (conjunction, trine, square, etc.)
- **Transits** - Current planets vs. stock's "natal chart" (IPO date)

### 3. Machine Learning

- **Algorithm**: XGBoost (Gradient Boosting)
- **Features**: 100+ astrological indicators
- **Target**: Price change direction (+1, 0, -1)
- **Validation**: Train/test split with cross-validation

### 4. Predictions

- Generates 20-day forecast
- Outputs:
  - Price change predictions
  - Bullish/Bearish/Neutral signals
  - Model confidence scores
  - Feature importance rankings

---

## 📖 Background: Financial Astrology

### Why Astrology?

Nature uses planetary movements to mark seasons and biological cycles. Ancient civilizations used astrology to predict optimal planting times, enabling the agricultural revolution.

### Market Psychology

Stock prices reflect collective human psychology - fear and greed. Since human behavior has cyclical patterns influenced by natural rhythms (moon phases affecting crime rates, etc.), financial astrology explores whether planetary positions correlate with market sentiment.

### Historical Context

Many successful traders and bankers have studied astrology:

- J.P. Morgan: _"Millionaires don't use astrology, billionaires do"_
- W.D. Gann - Famous trader who used astrological cycles
- Numerous hedge funds employ "alternative data" including lunar cycles


---

## 🚀 Web App API Endpoints

If you want to integrate with the API directly:

### Run Prediction

```http
POST http://localhost:5000/api/run-prediction
Content-Type: application/json

{
  "ticker": "AAPL",
  "apiKey": "YOUR_KEY"  // Optional with yfinance
}
```

### Get Existing Results

```http
GET http://localhost:5000/api/get-results/AAPL
```

### List Available Tickers

```http
GET http://localhost:5000/api/available-tickers
```

---

## 📊 Output Files

All results saved to `notebooks/output/`:

- `{TICKER}_price_change.model` - Trained XGBoost model
- `{TICKER}.Predict.Simplified.xlsx` - Prediction summary
- `{TICKER}.Predict.xlsx` - Full predictions with all indicators
- `{TICKER}.Analisys.xlsx` - Complete historical analysis
- `{TICKER}.score.price.change.txt` - Model accuracy score
- `{TICKER}.features.price.change.txt` - Feature importance

---

## 🛠️ Requirements

- **Python**: 3.8+ (tested on 3.12)
- **OS**: Windows (PowerShell scripts), Linux/Mac (bash scripts)
- **Memory**: 4GB+ RAM recommended
- **Storage**: ~100MB per ticker analyzed

### Key Dependencies

- `pandas`, `numpy` - Data manipulation
- `xgboost` - Machine learning
- `pyswisseph` - Astrological calculations
- `yfinance` - Stock data (free)
- `flask` - Web server
- `openpyxl` - Excel file generation

---

## 🎨 Web Interface Screenshots

The web app features:

- 🎨 Modern gradient design
- 📊 Interactive prediction tables
- 📈 Real-time progress tracking
- 🎯 One-click ticker selection
- 📱 Responsive layout

---

## 🤝 Contributing

This is a research project. Contributions welcome:

- Additional astrological indicators
- Alternative ML models
- UI improvements
- Bug fixes

---

## 📝 License

This project is for educational and research purposes only.

---

## ⚠️ Final Warning

**DO NOT USE FOR ACTUAL TRADING**

This project explores correlations between astrological events and market movements as an academic exercise. Markets are influenced by countless factors including economics, politics, technology, and human psychology. No prediction method is 100% accurate.

Always:

- Do your own research
- Consult licensed financial advisors
- Never invest more than you can afford to lose
- Understand that past performance ≠ future results

---

**Happy Researching! 🌟📈**

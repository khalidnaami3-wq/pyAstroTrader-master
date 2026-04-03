param (
    [string]$Asset = "AAPL",
    [string]$ApiKey = "BQ7ESNRDESZ5G0DG"
)

$Env:ASSET_TO_CALCULATE = $Asset
$Env:ALPHAVANTAGE_KEY = "BQ7ESNRDESZ5G0DG"
$Env:PYTHONPATH = "$($PWD.Path);$($PWD.Path)\notebooks"
$Env:SWISSEPH_PATH = "$($PWD.Path)\pyastrotrader\swisseph"

Write-Host "Running AstroTrader for asset: $Asset" -ForegroundColor Cyan

$PythonExe = "$($PWD.Path)\.venv\Scripts\python.exe"
$Jupyter = "$($PWD.Path)\.venv\Scripts\jupyter.exe"

if (!(Test-Path $PythonExe)) {
    Write-Error "Virtual environment not found at .venv. Please run setup first."
    exit
}

cd notebooks

Write-Host "Step 1: Downloading Data..." -ForegroundColor Yellow
& $Jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute DownloadData.ipynb --to notebook --output-dir ./output

Write-Host "Step 2: Creating Model..." -ForegroundColor Yellow
& $Jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute CreateModel.price.change.ipynb --to notebook --output-dir ./output

Write-Host "Step 3: Generating Prediction..." -ForegroundColor Yellow
& $Jupyter nbconvert --ExecutePreprocessor.timeout=-1 --execute Predict.price.change.ipynb --to notebook --output-dir ./output

cd ..

Write-Host "Done! Results are in notebooks/output" -ForegroundColor Green

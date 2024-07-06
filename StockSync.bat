@echo off

echo 🚀 Starting StockSync initial Configuration... 

:: Check if the virtual environment directory exists
if exist venv (
    echo 📁 Virtual environment already exists. Activating...
) else (
    echo 📂 Creating virtual environment...
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate

:: Install dependencies
echo ⬇️ Installing dependencies...
pip install -r requirements.txt

:: Run the Flask application
echo 📈 Starting StockSync
set FLASK_APP=app.py
set FLASK_ENV=development
flask run

:: Deactivate the virtual environment after closing the app
deactivate

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import yfinance as yf
from sklearn.linear_model import LinearRegression
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId
import gunicorn

app = Flask(__name__)
app.secret_key = 'MYSECRETKEY'

# MongoDB configuration
client = MongoClient('mongodb+srv://deepraj21bera:KB6tvjYDWc7DJdJe@cluster0.tfauzjh.mongodb.net/canvas')
db = client['stock_app']
users_collection = db['users']
wishlist_collection = db['wishlist']

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_collection.find_one({"username": username}):
            flash('Username already exists. Please choose another one.', 'error')
            return redirect(url_for('register'))
        users_collection.insert_one({"username": username, "password": password})
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            session['user_id'] = str(user['_id'])
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        if user:
            username = user['username']
            wishlist = list(wishlist_collection.find({"user_id": session['user_id']}))
            default_ticker = 'AAPL'
            ticker_data = search_ticker_data(default_ticker)
            return render_template('dashboard.html', username=username, wishlist=wishlist, default_ticker=default_ticker, **ticker_data)
    return redirect(url_for('login'))

@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    if 'user_id' in session:
        user_id = session['user_id']
        ticker = request.json['ticker']
        if not wishlist_collection.find_one({"user_id": user_id, "ticker": ticker}):
            wishlist_collection.insert_one({"user_id": user_id, "ticker": ticker})
            return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/predict_price', methods=['POST'])
def predict_price():
    ticker = request.json['ticker']
    prediction = predict_next_day_price(ticker)
    return jsonify({'prediction': prediction})

def predict_next_day_price(ticker):
    data = yf.download(ticker, period='1mo', interval='1d')
    data['Date'] = data.index
    data['Date'] = data['Date'].map(lambda x: x.toordinal())
    X = np.array(data['Date']).reshape(-1, 1)
    y = data['Close'].values

    model = LinearRegression().fit(X, y)
    next_day = np.array([[X[-1, 0] + 1]])
    prediction = model.predict(next_day)
    return prediction[0]

@app.route('/search_ticker', methods=['POST'])
def search_ticker():
    ticker = request.json['ticker']
    ticker_data = search_ticker_data(ticker)
    if 'error' in ticker_data:
        return jsonify(ticker_data), 500
    return jsonify(ticker_data)

def search_ticker_data(ticker):
    try:
        data = yf.download(ticker, period='6mo', interval='1d')
        current_data = yf.Ticker(ticker).history(period='1d')

        if not current_data.empty:
            current_price = {
                'open': current_data['Open'].iloc[0],
                'high': current_data['High'].iloc[0],
                'low': current_data['Low'].iloc[0],
                'close': current_data['Close'].iloc[0],
            }
        else:
            current_price = {'open': None, 'high': None, 'low': None, 'close': None}

        predicted_price = predict_next_day_price(ticker)

        chart_data = {
            'x': [d.strftime('%Y-%m-%d') for d in data.index] if not data.empty else [],
            'open': data['Open'].tolist() if not data.empty else [],
            'high': data['High'].tolist() if not data.empty else [],
            'low': data['Low'].tolist() if not data.empty else [],
            'close': data['Close'].tolist() if not data.empty else []
        }

        return {
            'chart_data': chart_data,
            'current_price': current_price,
            'predicted_price': predicted_price
        }
    except Exception as e:
        print(f"Error fetching data for ticker {ticker}: {e}")
        return {'error': 'Failed to fetch data'}

if __name__ == '__main__':
    app.run(debug=True)

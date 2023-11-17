from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import requests
import mysql.connector

app = Flask(__name__)

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://Samkelisiwe:S@mkelisiwe_8696@localhost/Fitness'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Disable tracking modifications for performance

db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
# Secret key for sessions
app.secret_key = 'your_secret_key'

# Weather API configuration
weather_api_key = '8db317108df44280fca955d52a99348f'
weather_api_base_url = 'http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={8db317108df44280fca955d52a99348f}'

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = sha256_crypt.encrypt(request.form['password'])

        new_user = User(name=name, email=email, password=password)

        flash('You are now registered and can log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_candidate = request.form['password']

        cursor = mysql.connection.cursor()
        result = cursor.execute("SELECT * FROM users WHERE email = %s", [email])

        if result > 0:
            data = cursor.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['name'] = data['name']
                flash('You are now logged in.', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cursor.close()
        else:
            error = 'Email not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

# User dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'logged_in' in session:
        if request.method == 'POST':
            city = request.form['city']
            weather_data = get_weather(city)
            return render_template('dashboard.html', username=session['name'], weather=weather_data)
        else:
            # Render the dashboard page without weather data if it's a GET request
            return render_template('dashboard.html', username=session['name'], weather=None)
    else:
        return redirect(url_for('login'))

# Get weather data from OpenWeatherMap API
def get_weather(city):
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric'  # Use 'imperial' for Fahrenheit
    }

    response = requests.get(weather_api_base_url, params=params)
    data = response.json()

    temperature = data['main']['temp']
    weather_description = data['weather'][0]['description']

    return {
        'temperature': temperature,
        'description': weather_description,
    }

if __name__ == '__main__':
    app.run(debug=True)

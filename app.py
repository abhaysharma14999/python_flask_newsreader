import pyttsx3
import json
import time
import requests
import threading
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'Abhay'  # Change this to a random secret key

continue_reading = False
interval = 0

def get_news():
    # Replace 'YOUR_NEWS_API_KEY' with your actual News API key
    api_key = 'c2baff50d94c4e5190017479a1b2f9e8\n'
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    response = requests.get(url)
    data = response.json()

    # Check if the "articles" key exists in the API response
    if 'articles' in data:
        return data['articles']
    else:
        raise Exception('Error: Unable to fetch news articles.')

def speak_news(news):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)  # Adjust the speech rate as needed

    for article in news:
        if not continue_reading:
            break
        title = article['title']
        description = article['description']
        engine.say(title)
        engine.say(description)
        engine.runAndWait()

def start_reading_thread():
    global continue_reading
    try:
        interval_val = interval
        if interval_val <= 0:
            raise ValueError

        continue_reading = True
        while continue_reading:
            news = get_news()
            speak_news(news)
            time.sleep(interval_val)
    except ValueError:
        pass
    except Exception as e:
        pass

@app.route('/', methods=['GET', 'POST'])
def home():
    global interval
    if request.method == 'POST':
        interval_str = request.form.get('interval')
        try:
            interval = int(interval_str)
            if interval <= 0:
                raise ValueError

            t = threading.Thread(target=start_reading_thread)
            t.start()

            flash(f'News reader started with an update interval of {interval} seconds.', 'success')
            return redirect(url_for('home'))
        except ValueError:
            flash('Please enter a valid positive integer for the interval.', 'error')

    return render_template('home.html', interval=interval, continue_reading=continue_reading)

@app.route('/stop')
def stop_reading():
    global continue_reading
    continue_reading = False
    flash('News reader stopped.', 'info')
    return redirect(url_for('home'))

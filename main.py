from flask import Flask, request, redirect, render_template
import string
import random
import sqlite3

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SERVER_NAME'] = 'localhost:5000'

# Create a connection to the database
conn = sqlite3.connect('urls.db')
cursor = conn.cursor()

# Create a table to store the URLs
cursor.execute('''CREATE TABLE IF NOT EXISTS urls
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                long_url TEXT,
                short_url TEXT)''')
conn.commit()

# Function to generate a unique short URL
def generate_short_url():
    # Get a list of all the characters that can be used in the short URL
    chars = string.ascii_letters + string.digits
    # Generate a random 6-character string
    short_url = ''.join(random.choice(chars) for _ in range(6))
    # Check if the short URL is already in use
    cursor.execute('SELECT * FROM urls WHERE short_url = ?', (short_url,))
    row = cursor.fetchone()
    if row:
        # If the short URL is already in use, generate a new one
        return generate_short_url()
    else:
        return short_url

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the long URL from the form
        long_url = request.form['long_url']
        # Generate a unique short URL
        short_url = generate_short_url()
        # Insert the URL into the database
        cursor.execute('INSERT INTO urls (long_url, short_url) VALUES (?, ?)', (long_url, short_url))
        conn.commit()
        # Render the results page with the short URL
        return render_template('results.html', short_url=short_url)
    else:
        # Render the home page
        return render_template('home.html')

# Route for the short URLs
@app.route('/<short_url>')
def redirect_url(short_url):
    # Get the long URL from the database
    cursor.execute('SELECT long_url FROM urls WHERE short_url = ?', (short_url,))
    row = cursor.fetchone()
    if row:
        # If the short URL is in the database, redirect to the long URL
        long_url = row[0]
        return redirect(long_url)
    else:
        # If the short URL is not in the database, return a 404 error
        return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()

from flask import Flask, render_template, request, send_file, session
from flask_session import Session  # for saving session data
from tempfile import mkdtemp  # for creating temporary directory for storing session data
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from io import BytesIO

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Use filesystem-based session storage
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def create_url(search_term, page_number):
    base_url = "https://mikroelectron.com/Home/Search/"
    return f"{base_url}{search_term}/?page={page_number}"

def extract_prices(price_string):
    matches = re.findall(r'(\d+\.?\d*)', price_string)
    prices = [float(match) for match in matches]
    return prices[0] if prices else None

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_term = request.form['search_term']
        num_pages = int(request.form['num_pages'])
        price_list = []
        original_title_list = []
        for page_number in range(1, num_pages + 1):
            url = create_url(search_term, page_number)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            prices = soup.find_all('span', {'class': 'title-price PriceTitle'})
            titles = soup.find_all('h4', {'class': 'title-price tooltips'})
            for price, title in zip(prices, titles):
                extracted_price = extract_prices(price.text.strip())
                price_list.append(extracted_price)
                original_title_list.append(title.get('data-original-title', ''))

        df = pd.DataFrame({
            'Original Title': original_title_list,
            'Price': price_list,
        })

        session['df'] = df.to_dict(orient='records')

        return render_template('results.html',  table=df.to_html(classes='data', header="true"), titles=df.columns.values)

    return render_template('index.html')

@app.route('/download', methods=['GET'])
def download():
    df = pd.DataFrame(session.get('df'))
    buf_str = BytesIO()
    df.to_csv(buf_str, index=False)
    buf_str.seek(0)
    return send_file(buf_str,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='results.csv')


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True,port=5000)

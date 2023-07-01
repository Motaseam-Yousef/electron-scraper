from flask import Flask, render_template, request, send_file
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

app = Flask(__name__)

def create_url(search_term, page_number):
    base_url = "https://mikroelectron.com/Home/Search/"
    return f"{base_url}{search_term}/?page={page_number}"

def extract_prices(price_string):
    # Find all occurrences of a pattern in the string
    matches = re.findall(r'(\d+\.?\d*)', price_string)
    
    # Convert the matched strings to floats
    prices = [float(match) for match in matches]

    # Return the first price only
    return prices[0] if prices else None

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_term = request.form['search_term']
        num_pages = int(request.form['num_pages'])

        # Prepare lists to store the data
        price_list = []
        original_title_list = []

        # Loop through each page
        for page_number in range(1, num_pages + 1):
            url = create_url(search_term, page_number)

            # Make the HTTP request
            response = requests.get(url)

            # Create a BeautifulSoup object and specify the parser
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the elements
            prices = soup.find_all('span', {'class': 'title-price PriceTitle'})
            titles = soup.find_all('h4', {'class': 'title-price tooltips'})

            # Iterate over each group of elements and append them to the lists
            for price, title in zip(prices, titles):
                extracted_price = extract_prices(price.text.strip())
                price_list.append(extracted_price)
                original_title_list.append(title.get('data-original-title', ''))

        # Create a DataFrame from the lists
        df = pd.DataFrame({
            'Original Title': original_title_list,
            'Price': price_list,
        })

        # Save the DataFrame to a CSV file
        df.to_csv('results.csv', index=False)
        
        # Then return the csv file as a download
        return send_file('results.csv', as_attachment=True)

    # render a form to get user input
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
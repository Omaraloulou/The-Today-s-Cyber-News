import os
import requests
import datetime
import pandas as pd
from bs4 import BeautifulSoup
import webbrowser
import pyfiglet
from colorama import Fore
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk

# Download NLTK data
nltk.download('punkt')

# Display styled text
styled_text = pyfiglet.figlet_format("THE TODAY'S CYBER NEWS ")
print(Fore.BLUE + styled_text)

# List of URLs to scrape
urls_list = [
    "https://cybersecuritynews.com/",
    "https://www.darkreading.com/",
]

def get_date():
    return datetime.date.today().strftime("%Y-%m-%d")

def output_file_path():
    return os.path.dirname(os.path.abspath(__file__))

# Send request and parse HTML content
def fetch_html(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'lxml')

# Extract summary using Sumy
def get_article_summary(article_url):
    parser = HtmlParser.from_url(article_url, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")

    summary = summarizer(parser.document, 2)  # Summarize to 2 sentences
    return ' '.join([str(sentence) for sentence in summary])

# Extract news from cybersecuritynews.com
def extract_news_cybersecuritynews(site):
    news = {}
    articles = site.find_all('div', {'class': 'item-details'})
    for article in articles:
        title = article.contents[1].find('a').text.strip()
        link = article.contents[1].find('a').get('href')
        date_str = article.contents[3].find('time').text.strip()
        news_date = datetime.datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
        if news_date == get_date():
            summary = get_article_summary(link)
            news[title] = (link, summary)
    return news

# Extract news from darkreading.com
def extract_news_darkreading(site):
    news = {}
    articles = site.find_all('a', {'class': 'ListPreview-Title'})
    for article in articles:
        title = article.text.strip()
        link = article.get('href')
        if link and not link.startswith('http'):
            link = f"https://www.darkreading.com{link}"
        summary = get_article_summary(link)
        news[title] = (link, summary)
    return news

# Function to save news as an HTML file
def save_news_to_html(news):
    data_list = [
        [title, f'<a href="{link}" style="color: blue; text-decoration: underline;" target="_blank">{link}</a>', summary]
        for title, (link, summary) in news.items()
    ]
    df = pd.DataFrame(data_list, columns=["Title", "Link", "Summary"])
    df.index += 1

    html_table = df.to_html(escape=False, classes='styled-table')
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {{
        background: linear-gradient(to bottom, #b4faeb, #b4faeb);
        color: black;
        font-family: Times New Roman, serif;
    }}
    .styled-table {{
        width: 100%;
        border-collapse: separate;
        font-size: 1em;
        font-family: serif;
        min-width: 400px;
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.15);
        background-color: transparent;
    }}
    .styled-table thead th {{
        padding: 14px 17px;
        text-align: middle;
        border-bottom: 5px solid #ddd;
        border-bottom-color: #82f5dc;
        background-color: transparent;
        color: black;
    }}
    .styled-table tbody td {{
        padding: 15px 10px;
        text-align: left;
        border-bottom: 1px solid #ddd;
        background-color: transparent;
        color: black;
    }}
    .styled-table tbody tr:hover {{
        background-color: #82f5dc;
    }}
    .styled-table tbody tr.active-row {{
        font-weight: bold;
        color: white;
    }}
    h1 {{
        text-align: center;
        margin-top: 25px;
    }}
    </style>
    </head>
    <body>
    <h1>The Today's Cyber News</h1>
    <br>
    <table class="styled-table">
    <thead>
    <tr>
    <th>Title</th>
    <th>Link</th>
    <th>Summary</th>
    </tr>
    </thead>
    <tbody>
    {''.join(f"<tr><td>{title}</td><td>{link}</td><td>{summary}</td></tr>" for title, link, summary in data_list)}
    </tbody>
    </table>
    </body>
    </html>
    '''

    file_path = os.path.join(output_file_path(), "security_news_report.html")
    with open(file_path, "w") as file:
        file.write(html_content)

    # Open the file in the default web browser
    webbrowser.open(f"file://{file_path}")

# Main function to orchestrate the scraping and saving process
def main():
    news = {}
    for url in urls_list:
        site = fetch_html(url)
        if "cybersecuritynews.com" in url:
            news.update(extract_news_cybersecuritynews(site))
        elif "darkreading.com" in url:
            news.update(extract_news_darkreading(site))
    save_news_to_html(news)

# Entry point of the script
if __name__ == "__main__":
    main()

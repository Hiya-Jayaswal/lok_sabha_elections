import pandas as pd
import bs4 as BeautifulSoup
import requests

print("hello")

url = "https://results.eci.gov.in/PcResultGenJune2024/index.htm"

respone = requests.get(url)

my_data = []

soup = BeautifulSoup(html_doc, 'html.parser')
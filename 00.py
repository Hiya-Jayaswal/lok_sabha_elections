import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize the WebDriver (this example uses Chrome)
driver = webdriver.Chrome()

# URL of the main page
url = 'https://results.eci.gov.in/PcResultGenJune2024/index.htm'

# Open the URL
driver.get(url)

# Wait for the page to load and for the table to be present
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'table'))
)

# Parse the page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Function to scrape data from the table
def scrape_table(soup):
    table = soup.find('table', {'class': 'table'})
    rows = table.find_all('tr')
    
    data = []
    for row in rows[1:]:  # Skip the header row
        cols = row.find_all('td')
        cols = [col.text.strip() for col in cols]
        data.append(cols)
    
    return data

# Scrape the initial table
data = scrape_table(soup)

# Find links to other pages (e.g., state-wise results)
# This example assumes there are links to other pages you want to scrape
links = driver.find_elements(By.XPATH, "//a[contains(@href, 'state')]")

for link in links:
    link.click()
    
    # Wait for the page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'table'))
    )
    
    # Parse the new page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Scrape the table data
    data.extend(scrape_table(soup))
    
    # Go back to the main page
    driver.back()

# Create a DataFrame from the data
df = pd.DataFrame(data, columns=['Party', 'Won', 'Leading', 'Total'])

# Save the DataFrame to a CSV file
df.to_csv('lok_sabha_elections_extended.csv', index=False)

# Print the entire DataFrame
print(df.to_string(index=False))

# Convert 'Won', 'Leading', and 'Total' columns to numeric
df['Won'] = pd.to_numeric(df['Won'], errors='coerce')
df['Leading'] = pd.to_numeric(df['Leading'], errors='coerce')
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')

# Calculate the total number of seats
total_seats = df['Won'].sum()
print(f"The total number of seats in the parliamentary elections is {total_seats}.")

# List to hold insights
insights = []

# Insight 1: Party with the most seats won
most_seats = df.loc[df['Won'].idxmax()]
insights.append(f"The party with most seats is {most_seats['Party']} with {most_seats['Won']} seats.")

# Insight 2: Party with the highest total (won + leading)
highest_total = df.loc[df['Total'].idxmax()]
insights.append(f"The party with the highest total (won + leading) is {highest_total['Party']} with {highest_total['Total']} seats.")

# Insight 3: Number of parties with more than 10 seats
parties_more_than_10 = df[df['Won'] > 10].shape[0]
insights.append(f"There are {parties_more_than_10} parties with more than 10 seats.")

# Insight 4: Total seats won by the top 3 parties
top_3_parties = df.nlargest(3, 'Won')
total_seats_top_3 = top_3_parties['Won'].sum()
insights.append(f"The total seats won by the top 3 parties are {total_seats_top_3}.")

# Insight 5: Average seats won by all parties
average_seats_won = df['Won'].mean()
insights.append(f"The average seats won by all parties are {average_seats_won:.2f}.")

# Insight 6: Parties with no seats won
no_seats = df[df['Won'] == 0].shape[0]
insights.append(f"There are {no_seats} parties with no seats won.")

# Insight 7: Total number of parties contesting
total_parties = df.shape[0]
insights.append(f"The total number of parties contesting the election is {total_parties}.")

# Insight 8: Party with the smallest number of seats won
least_seats = df[df['Won'] > 0].nsmallest(1, 'Won')
insights.append(f"The party with the smallest number of seats won is {least_seats.iloc[0]['Party']} with {least_seats.iloc[0]['Won']} seats.")

# Insight 9: Proportion of seats won by the largest party
proportion_largest_party = (most_seats['Won'] / total_seats) * 100
insights.append(f"The proportion of seats won by the largest party is {proportion_largest_party:.2f}%.")

# Insight 10: Parties with more seats leading than won
more_leading_than_won = df[df['Leading'] > df['Won']].shape[0]
insights.append(f"There are {more_leading_than_won} parties with more seats leading than won.")

# Print the insights
for i, insight in enumerate(insights, 1):
    print(f"Insight {i}: {insight}")

# Save the insights to a text file
with open('lok_sabha_elections.txt', 'w') as f:
    for i, insight in enumerate(insights, 1):
        f.write(f"Insight {i}: {insight}\n")

# Close the driver
driver.quit()

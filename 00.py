import requests
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
driver = webdriver.Chrome()

def scrape_table(soup):
    table = soup.find('table', {'class': 'table'})
    rows = table.find_all('tr')
    
    data = []
    for row in rows[1:]:  
        cols = row.find_all('td')
        cols = [col.text.strip() for col in cols]
        data.append(cols)
    
    return data

# Function to scrape data from the party-wise results table
def scrape_party_wise_table(soup):
    table = soup.find('table', {'class': 'table'})
    if not table:
        return []  # Return empty list if table not found
    
    rows = table.find_all('tr')
    
    data = []
    for row in rows[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) >= 3:  # Ensure there are at least 3 columns
            party = cols[0].text.strip()
            seats = cols[1].text.strip()
            total_votes = cols[2].text.strip()  # Assuming this is the total votes column
            data.append([party, seats, total_votes])
    
    return data

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

# Save the DataFrame to a CSV file for the main page
df.to_csv('lok_sabha_elections_extended_main.csv', index=False)

# Convert 'Won', 'Leading', and 'Total' columns to numeric
df['Won'] = pd.to_numeric(df['Won'], errors='coerce')
df['Leading'] = pd.to_numeric(df['Leading'], errors='coerce')
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')

# Calculate the total number of seats
total_seats = df['Won'].sum()
print(f"The total number of seats in the parliamentary elections is {total_seats}.")

# Display the main results table
print("\nMain Results Table:")
print(df)

# List to hold insights
insights = []

# Insight 1: Party with the most seats won
if not df.empty:
    most_seats = df.loc[df['Won'].idxmax()]
    insights.append(f"The party with most seats is {most_seats['Party']} with {most_seats['Won']} seats.")

# Insight 2: Party with the highest total (won + leading)
if not df.empty:
    highest_total = df.loc[df['Total'].idxmax()]
    insights.append(f"The party with the highest total (won + leading) is {highest_total['Party']} with {highest_total['Total']} seats.")

# Insight 3: Number of parties with more than 10 seats
parties_more_than_10 = df[df['Won'] > 10].shape[0]
insights.append(f"There are {parties_more_than_10} parties with more than 10 seats.")

# Insight 4: Total seats won by the top 3 parties
if not df.empty:
    top_3_parties = df.nlargest(3, 'Won')
    total_seats_top_3 = top_3_parties['Won'].sum()
    insights.append(f"The total seats won by the top 3 parties are {total_seats_top_3}.")

# Insight 5: Average seats won by all parties
average_seats_won = df['Won'].mean() if not df.empty else 0
insights.append(f"The average seats won by all parties are {average_seats_won:.2f}.")

# Insight 6: Parties with no seats won
no_seats = df[df['Won'] == 0].shape[0]
insights.append(f"There are {no_seats} parties with no seats won.")

# Insight 7: Total number of parties contesting
total_parties = df.shape[0]
insights.append(f"The total number of parties contesting the election is {total_parties}.")

# Insight 8: Party with the smallest number of seats won
least_seats = df[df['Won'] > 0].nsmallest(1, 'Won') if not df.empty else pd.DataFrame(columns=['Party', 'Won'])
if not least_seats.empty:
    insights.append(f"The party with the smallest number of seats won is {least_seats.iloc[0]['Party']} with {least_seats.iloc[0]['Won']} seats.")

# Insight 9: Proportion of seats won by the largest party
if not df.empty and total_seats > 0:
    proportion_largest_party = (most_seats['Won'] / total_seats) * 100
    insights.append(f"The proportion of seats won by the largest party is {proportion_largest_party:.2f}%.")

# Insight 10: Parties with more seats leading than won
more_leading_than_won = df[df['Leading'] > df['Won']].shape[0]
insights.append(f"There are {more_leading_than_won} parties with more seats leading than won.")

# Visit the Party-wise Results Page
party_wise_url = 'https://results.eci.gov.in/PcResultGenJune2024/partywiseresult-S24.htm'
driver.get(party_wise_url)

# Wait for the page to load and for the table to be present
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'table'))
)

# Parse the page with BeautifulSoup
soup_party_wise = BeautifulSoup(driver.page_source, 'html.parser')

# Scrape the party-wise results table
data_party_wise = scrape_party_wise_table(soup_party_wise)

# Create a DataFrame for party-wise results
df_party_wise = pd.DataFrame(data_party_wise, columns=['Party', 'Seats', 'Total Votes'])

# Convert 'Seats' and 'Total Votes' columns to numeric
df_party_wise['Seats'] = pd.to_numeric(df_party_wise['Seats'], errors='coerce')
df_party_wise['Total Votes'] = pd.to_numeric(df_party_wise['Total Votes'], errors='coerce')

# Display the party-wise results table
print("\nUttar Pradesh Results Table:")
print(df_party_wise)

# Save party-wise results to CSV
df_party_wise.to_csv('lok_sabha_party_wise_results.csv', index=False)

# Insight 11: Party with the most seats in the party-wise results
if not df_party_wise.empty:
    most_seats_party_wise = df_party_wise.loc[df_party_wise['Seats'].idxmax()]
    insights.append(f"The party with most seats in party-wise results is {most_seats_party_wise['Party']} with {most_seats_party_wise['Seats']} seats.")

# Insight 12: Number of parties with more than 5 seats in party-wise results
parties_more_than_5_party_wise = df_party_wise[df_party_wise['Seats'] > 5].shape[0]
insights.append(f"There are {parties_more_than_5_party_wise} parties with more than 5 seats in party-wise results.")

#Insight14
if not df_party_wise.empty:
    highest_votes_party = df_party_wise.loc[df_party_wise['Total Votes'].idxmax()]
    insights.append(f"The party with the highest votes in party-wise results is {highest_votes_party['Party']} ")

for i, insight in enumerate(insights, 1):
    print(f"Insight {i}: {insight}")

with open('lok_sabha_elections_insights.txt', 'w') as f:
    for i, insight in enumerate(insights, 1):
        f.write(f"Insight {i}: {insight}\n")

plt.figure(figsize=(12, 8))
sns.barplot(x='Party', y='Won', data=df, palette= ['#ADC89B'])
plt.title('Seats Won by Each Party')
plt.xticks(rotation=90)
plt.xlabel('Party')
plt.ylabel('Seats Won')
plt.tight_layout()
plt.savefig('seats_won_by_party.png')
plt.show()

plt.figure(figsize=(8, 8))
plt.pie(top_3_parties['Won'], labels=top_3_parties['Party'], autopct='%1.1f%%', startangle=140, colors= ['#FE9494', '#459AD8', '#F3DC8B'])
plt.title('Proportion of Seats Won by Top 3 Parties')
plt.tight_layout()
plt.savefig('proportion_seats_top_3.png')
plt.show()

driver.quit()

from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from playwright_stealth import stealth_sync
# Launch headless browser with Playwright
from fake_useragent import UserAgent
import re
import logging
import time
import random
from utils import send_msg
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MAL_USERNAME = os.getenv('MAL_USERNAME')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CREDENTIALS_FILENAME = os.getenv('CREDENTIALS_FILENAME')


def sanitize(filename):
    # Remove invalid characters for Windows file names
    return re.sub(r'[<>:"/\\|?*]', '', filename)



def extract_last_figure(soup):
    # Extract figure names and links
    figures = []
    for a_tag in soup.find_all("a", class_="anchor"):
        name = a_tag.img["alt"] if a_tag.img and "alt" in a_tag.img.attrs else None
        link = 'https://myfigurecollection.net'+a_tag["href"] if "href" in a_tag.attrs else None
        if name and link:
            figures.append({"Name": name, "Link": link})

    # Create a pandas DataFrame
    figures_df = pd.DataFrame(figures)
    return figures_df.iloc[0]



def get_mal_list():
    anime_data = []
    # Launch headless browser with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Use headless=True to avoid GUI
        page = browser.new_page()

        # Open the HTML file
        page.goto(f'https://myanimelist.net/animelist/{MAL_USERNAME}')

        # Wait for the page to load (adjust the selector to match the content)
        page.wait_for_selector('.list-table')  # This waits until the table is rendered

        # Get the page content after JavaScript execution
        rendered_html = page.content()

        
        soup = BeautifulSoup(rendered_html, 'html.parser')

        # Continue with extracting the data as you did before
        

        # Locate the table containing anime details
        table = soup.find('table', {'class': 'list-table'})
        if table:
            rows = table.find_all('tr', {'class': 'list-table-data'})
            for row in rows:
                anime_title = row.find('td', class_='data title clearfix').find('a').text.strip()

                anime_score = row.find('td', class_='data score').find('span', class_='score-label').text.strip()
            
                # anime_progress = row.find('td', class_='data progress').find('div', class_='progress-52215').text.strip()
    

                anime_data.append({
                    'Title': anime_title,
                    'Score': anime_score
                    # 'Progress': anime_progress
                })

        browser.close()
    
    # Convert the list of dictionaries into a pandas DataFrame
    return pd.DataFrame(anime_data)





def get_mfc_page(anime_code):

    result = pd.DataFrame()

    ua = UserAgent()


    header = {
        'User-Agent': ua.chrome,
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Use headless=True to avoid GUI
        page = browser.new_page(java_script_enabled = True)
        page.set_extra_http_headers(header)
        stealth_sync(page)

        # Open the HTML file
        page.goto(f'https://myfigurecollection.net/?_tb=item&orEntries%5B%5D={anime_code}&rootId=0', referer=f"https://myfigurecollection.net/entry/{anime_code}")

        # Get the page content after JavaScript execution
        rendered_html = page.content()

        # Now parse the rendered HTML with BeautifulSoup
        
        soup = BeautifulSoup(rendered_html, 'html.parser')

        formatted_html = soup.prettify()

        # Locate the table containing anime details
        table = soup.find('div', {'class': 'results'})
        if table:
            # Pretty-print the HTML content
            formatted_html = table.prettify()

            # Extract figure names and links
            figures = []
            for a_tag in table.find_all("a", class_="anchor"):
                name = a_tag.img["alt"] if a_tag.img and "alt" in a_tag.img.attrs else None
                link = 'https://myfigurecollection.net'+a_tag["href"] if "href" in a_tag.attrs else None
                if name and link:
                    figures.append({"Name": name, "Link": link})

            result = pd.DataFrame(figures)


        browser.close()
    return result

def update_top_anime():
    gc = gspread.service_account(filename=f'credentials/{CREDENTIALS_FILENAME}')
    sh = gc.open('mal-to-mfc')
    worksheet = sh.get_worksheet(0)
    df_sheet = pd.DataFrame(worksheet.get_all_records())

    # Ensure 'Last Updated' column exists
    if 'Last Updated' not in df_sheet.columns:
        df_sheet['Last Updated'] = ""

    df = get_mal_list()
    df['Score'] = pd.to_numeric(df['Score'], errors="coerce")
    best_anime = df[df['Score'] > 7]
    
    # Filter titles in df that are not already in df_sheet
    new_titles = best_anime[~best_anime['Title'].isin(df_sheet['MyAnimeList'])]

    # Create new rows with empty columns and today's date
    yesterday = (datetime.now() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    # Create new rows with empty columns and yesterday's date
    new_rows = pd.DataFrame({
        "MyAnimeList": new_titles['Title'],
        "Score": new_titles['Score'],
        "id1": "",
        "id2": "",
        "id3": "",
        "id4": "",
        "id5": "",
        "id6": "",
        "Last Figure (id1)": "",
        "Last Figure (id2)": "",
        "Last Figure (id3)": "",
        "Last Figure (id4)": "",
        "Last Figure (id5)": "",
        "Last Figure (id6)": "",
        "Last Updated": yesterday,
    })

    # Append new rows to df_sheet
    df_sheet = pd.concat([df_sheet, new_rows], ignore_index=True)
    worksheet.update([df_sheet.columns.values.tolist()] + df_sheet.values.tolist())


    return df_sheet


def main():
    logger.info('Starting')
    # Initialize SMS message content
    new_figures_notifications = []
    missing_ids_notifications = []

    # Keep track of scraped IDs to avoid duplicates
    scraped_ids = set()

    # Update top anime list and get updated DataFrame
    df_sheet = update_top_anime()

    # Filter rows older than today
    today = datetime.now().strftime("%Y-%m-%d")
    df_sheet['Last Updated'] = pd.to_datetime(df_sheet['Last Updated'], errors='coerce')
    # Replace NaT values with yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    df_sheet['Last Updated'].fillna(yesterday, inplace=True)
    rows_to_scrape = df_sheet[df_sheet['Last Updated'] < today]
    logger.info(rows_to_scrape)
    # Process each anime row
    for idx, row in rows_to_scrape.iterrows():
        anime_name = sanitize(row['MyAnimeList'])

        # Check if both IDs are missing
        if not row['id1'] and not row['id2'] and not row['id3'] and not row['id4'] and not row['id5'] and not row['id6']:
            missing_ids_notifications.append(anime_name)
            continue  # Skip to next row

        anime_updates = []  # Track updates for this anime

        for id_col, last_fig_col in [
            ('id1', 'Last Figure (id1)'),
            ('id2', 'Last Figure (id2)'),
            ('id3', 'Last Figure (id3)'),
            ('id4', 'Last Figure (id4)'),
            ('id5', 'Last Figure (id5)'),
            ('id6', 'Last Figure (id6)')
        ]:
            if row[id_col]:
                anime_id = row[id_col]

                # Skip if ID has already been scraped
                if anime_id in scraped_ids:
                    logger.info("ID %s already scraped. Skipping.", anime_id)
                    continue

                try:
                    logger.info("Fetching figures for %s (ID: %s)", anime_name, anime_id)
                    res = get_mfc_page(anime_id)

                    if not res.empty:
                        last_stored_figure = row.get(last_fig_col, "")
                        new_figures = []

                        # Collect all figures up to the stored last figure
                        for _, figure in res.iterrows():
                            if figure['Name'] == last_stored_figure:
                                break
                            new_figures.append({"Name": figure['Name'], "Link": figure['Link']})

                        if new_figures:
                            logger.info("New figures found for %s (ID: %s): %d", anime_name, anime_id, len(new_figures))
                            anime_updates.extend(new_figures)

                            # Update the last figure in the sheet
                            df_sheet.at[idx, last_fig_col] = res.iloc[0]['Name']  # Update to the latest figure

                        # Mark this ID as scraped
                        scraped_ids.add(anime_id)

                except Exception as e:
                    logger.error("Error fetching figures for %s (ID: %s): %s", anime_name, anime_id, e)

                # Add a random sleep to avoid detection
                sleep_duration = random.uniform(0, 2)  # Random duration between 1 and 5 seconds
                logger.info("Sleeping for %.2f seconds...", sleep_duration)
                time.sleep(sleep_duration)

        # If there are updates for this anime, format them into a notification
        if anime_updates:
            notification = f"Anime: {anime_name}\n" + "\n".join(
                [f"- {fig['Name']} ({fig['Link']})" for fig in anime_updates]
            )
            new_figures_notifications.append(notification)

        # Update the last updated date for this row
        df_sheet.at[idx, 'Last Updated'] = today
    df_sheet = df_sheet.fillna('')
    # Update the Google Sheet
    gc = gspread.service_account(filename=f'credentials/{CREDENTIALS_FILENAME}')
    sh = gc.open('mal-to-mfc')
    worksheet = sh.get_worksheet(0)
    df_sheet['Last Updated'] = df_sheet['Last Updated'].dt.strftime('%Y-%m-%d')  # Convert to string format
    df_sheet = df_sheet.fillna('')
    worksheet.update([df_sheet.columns.values.tolist()] + df_sheet.values.tolist())


    # Send or print the SMS messages
    if new_figures_notifications:
        for notification in new_figures_notifications:
            print(notification)
            send_msg(notification, subject="New Figures Found")
            time.sleep(1)  # Pause for 1 second between messages
    else:
        logger.info("No new figures found.")

    if missing_ids_notifications:
        for missing_id in missing_ids_notifications:
            send_msg(f"Missing ID for: {missing_id}", subject="Missing MFC ID")
            time.sleep(1)  # Pause for 1 second between messages
    else:
        logger.info("No missing IDs found.")
    



if __name__ == '__main__':
    main()
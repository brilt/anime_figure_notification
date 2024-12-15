# Anime Figure Notification Bot  

A Python bot that fetches anime figures from [MyFigureCollection](https://myfigurecollection.net/) and updates data from your [MyAnimeList](https://myanimelist.net/) account. It sends notifications about new figures and alerts for missing IDs via Telegram.  

---

## Features  

- Syncs anime list from MyAnimeList (MAL).  
- Automatically includes only anime scored **8 and above** on your MAL list.  
- Allows adding non-anime elements like **Hatsune Miku** directly to the spreadsheet for figure tracking.  
- Scrapes figure information from MyFigureCollection (MFC).  
- Updates a Google Sheet with figure data.  
- Sends notifications via Telegram for new figures or missing IDs.  
- Prevents duplicate scraping by keeping track of already-seen MFC figure IDs during a session.  

---

## Project Structure  

```
anime_figure_notification/  
├── bot.py               # Telegram bot commands  
├── main.py              # Core logic for scraping and updates  
├── requirements.txt     # Required Python dependencies  
├── utils.py             # Utility functions (e.g., sending Telegram messages)  
├── credentials/         # Contains the Google API credentials  
│   └── credentials.json  
```  

---

## Spreadsheet Structure  

The spreadsheet tracks anime and related figure information sourced from **MyAnimeList (MAL)** and **MyFigureCollection (MFC)**. Below is a detailed explanation of the columns:  

| **Column**                | **Purpose**                                                                                                                                                                 |  
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|  
| **MyAnimeList**           | Contains the title of the anime, sourced from the user’s MyAnimeList account. Automatically includes only anime titles scored **8 and above**.                              |  
| **Score**                 | The user’s rating for the anime (e.g., 1-10), as recorded in their MyAnimeList account. This column is automatically filled by the bot.                                      |  
| **id1, id2, id3, id4, id5, id6** | Contains MFC entry IDs. These IDs are extracted from the **URL of the figure page** on MyFigureCollection. Each ID corresponds to a figure listing for the anime or entry. The multiple ID columns allow tracking of anime with multiple entries on MFC, such as anime with multiple seasons or spin-offs. |  
| **Last Figure (id1), Last Figure (id2), Last Figure (id3), etc.** | Tracks the most recent figure found for the respective MFC ID. Prevents duplicate notifications for already processed figures.           |  
| **Last Updated**          | Records the last date when the anime’s associated MFC IDs were checked for updates. Figures are only checked if the date in this column is older than the current date.     |  

### Adding Non-Anime Elements  
You can also track non-anime characters like **Hatsune Miku** or similar franchises by directly adding their names and IDs to the spreadsheet. For example:  

| **MyAnimeList**   | **Score** | **id1** |  
|--------------------|-----------|---------|  
| Hatsune Miku       | 10        | 1590    |  

The bot treats these entries the same as anime titles, sending notifications when new figures are found.  

---

## How the Bot Handles MFC IDs  

- **Multiple IDs for a Single Anime**:  
  Some anime, especially those with multiple seasons or spin-offs, may have multiple MFC IDs. For example, each season of an anime may have its own separate entry on MyFigureCollection. The spreadsheet accommodates this by allowing multiple ID columns (`id1`, `id2`, etc.), so figures for all related MFC entries can be tracked.  

- **Avoiding Duplicate Scraping**:  
  The bot keeps track of already-seen figure IDs during a scraping session. If an MFC page with a specific ID has already been processed, it will not be scraped again during the same session. This ensures efficiency and prevents duplicate notifications for the same figures.  

---

## Setup  

### Prerequisites  

1. **Python 3.10+**: Make sure Python is installed. You can download it [here](https://www.python.org/).  
2. **Playwright**: Required for web scraping.  
3. **Google Sheets API**: A valid service account JSON file from a GCP project.  
4. **Telegram Bot**: Create a bot and obtain its token. Follow this [guide](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot) to setup your Telegram bot.  

---

### Installation  

1. **Clone the Repository**  
   ```bash  
   git clone https://github.com/brilt/anime_figure_notification.git  
   cd anime_figure_notification  
   ```  

2. **Install Dependencies**  
   Use `pip` to install the required Python libraries:  
   ```bash  
   pip install -r requirements.txt  
   ```  

3. **Setup Playwright**  
   Install the necessary browsers for Playwright:  
   ```bash  
   playwright install  
   ```  

4. **Configure Environment Variables**  
   Create a `.env` file in the project root with the following content:  
   ```env  
   MAL_USERNAME=YourMyAnimeListUsername  
   TELEGRAM_BOT_TOKEN=YourTelegramBotToken  
   TELEGRAM_CHAT_ID=YourTelegramChatID  
   CREDENTIALS_FILENAME=FilenameOfJSONCredentials  
   ```  

5. **Add Google Sheets Credentials**  
   Place your service account JSON file in the `credentials/` folder. Update its filename in `.env`.  

---

### Usage  

1. **Run the Telegram Bot**  
   Start the bot:  
   ```bash  
   python bot.py  
   ```  

   Telegram Commands:  
   - `/start` - Initialize the bot.  
   - `/getid` - Retrieve your Telegram chat ID.  

2. **Scrape and Update Data**  
   Run the main script manually (optional):  
   ```bash  
   python main.py  
   ```  

---

## Contributing  

Feel free to submit issues or contribute improvements via pull requests.  

---

## License  

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.  

---
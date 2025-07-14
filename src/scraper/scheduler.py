import asyncio
import argparse
from .telegram_scraper import TelegramScraper

def main():
    parser = argparse.ArgumentParser(description='Ethiopian Medical Telegram Scraper')
    parser.add_argument('--days-back', type=int, default=1, 
                        help='Days back to scrape (default: yesterday)')
    args = parser.parse_args()

    scraper = TelegramScraper()
    asyncio.run(scraper.run(args.days_back))

if __name__ == "__main__":
    main()
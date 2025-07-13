import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv
from .utils import ensure_directory_exists, sanitize_channel_name

load_dotenv()

class TelegramScraper:
    def __init__(self):
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.session_name = os.getenv('SESSION_NAME')
        self.phone = os.getenv('PHONE')
        self.channels = os.getenv('CHANNELS').split(',')
        self.image_channels = os.getenv('IMAGE_CHANNELS').split(',')
        self.client = None
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger('telegram_scraper')
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('logs/scraper.log')
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(file_format)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    async def start_client(self):
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.start(phone=self.phone)
        self.logger.info("Telegram client initialized")

    async def scrape_channel(self, channel, target_date):
        try:
            self.logger.info(f"Starting scrape: {channel}")
            messages = []
            entity = await self.client.get_entity(channel)
            
            async for message in self.client.iter_messages(entity, offset_date=target_date):
                if message.date.date() != target_date.date():
                    break
                
                # Download images for medical channels
                image_path = None
                if channel in self.image_channels and isinstance(message.media, MessageMediaPhoto):
                    image_path = await self.download_image(message, target_date, channel)
                
                messages.append({
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'text': message.text,
                    'media': bool(message.media),
                    'image_path': image_path,
                    'channel': channel
                })
            
            return messages
        except FloodWaitError as e:
            wait_time = e.seconds
            self.logger.warning(f"Rate limited. Waiting {wait_time} seconds")
            await asyncio.sleep(wait_time)
            return await self.scrape_channel(channel, target_date)
        except Exception as e:
            self.logger.error(f"Scrape failed for {channel}: {str(e)}", exc_info=True)
            return []

    async def download_image(self, message, target_date, channel):
        try:
            date_str = target_date.strftime('%Y-%m-%d')
            sanitized_channel = sanitize_channel_name(channel)
            image_dir = f"data/raw/telegram_images/{date_str}/{sanitized_channel}"
            ensure_directory_exists(image_dir)
            
            image_path = f"{image_dir}/{message.id}.jpg"
            await message.download_media(file=image_path)
            self.logger.info(f"Downloaded medical image: {image_path}")
            return image_path
        except Exception as e:
            self.logger.error(f"Image download failed: {str(e)}")
            return None

    async def run(self, days_back=1):
        await self.start_client()
        target_date = datetime.utcnow() - timedelta(days=days_back)
        date_str = target_date.strftime('%Y-%m-%d')
        
        for channel in self.channels:
            try:
                messages = await self.scrape_channel(channel, target_date)
                if messages:
                    self.save_messages(messages, channel, date_str)
                    self.logger.info(f"Saved {len(messages)} messages from {channel}")
                else:
                    self.logger.info(f"No messages found for {channel} on {date_str}")
            except Exception as e:
                self.logger.error(f"Channel processing failed: {channel} - {str(e)}")
        
        await self.client.disconnect()

    def save_messages(self, messages, channel, date_str):
        sanitized_channel = sanitize_channel_name(channel)
        dir_path = f"data/raw/telegram_messages/{date_str}/{sanitized_channel}"
        ensure_directory_exists(dir_path)
        
        file_path = f"{dir_path}/messages.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Messages saved to {file_path}")
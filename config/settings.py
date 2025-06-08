import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id_str) for id_str in os.getenv("ADMIN_IDS", "").split(",") if id_str]
DB_URL = os.getenv("DB_URL", "sqlite:///finance.db")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
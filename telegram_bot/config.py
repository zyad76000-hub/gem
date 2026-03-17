import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "6159178791:AAHkx_JEgIT1TBYUGInjw8xjBl3oegs_558")
# تحويل قائمة معرفات الأدمن إلى أرقام
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]
MAX_DOWNLOADS_PER_USER = int(os.getenv("MAX_DOWNLOADS", "50"))

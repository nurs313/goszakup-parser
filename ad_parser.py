import requests
from bs4 import BeautifulSoup
import telegram
import time
import json
import os
from urllib.parse import urljoin
import asyncio

# Настройки
SITE_URL = "https://goszakup.gov.kz/ru/search/lots?filter%5Bname%5D=&filter%5Bnumber%5D=&filter%5Bnumber_anno%5D=&filter%5Benstru%5D=&filter%5Bstatus%5D%5B%5D=360&filter%5Bcustomer%5D=&filter%5Bamount_from%5D=100000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Bmonth%5D=&filter%5Bplan_number%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bstart_date_to%5D=&filter%5Byear%5D=&filter%5Bitogi_date_from%5D=&filter%5Bitogi_date_to%5D=&filter%5Bstart_date_from%5D=&filter%5Bmore%5D=&smb="
BOT_TOKEN = os.getenv("BOT_TOKEN", "7927707474:AAG0jX3r_575FuUVIBWdFUGWQwFJYjlKlGY")
CHAT_ID = os.getenv("CHAT_ID", "5309614527")
DATA_FILE = "seen_ads.json"

# Инициализация Telegram-бота
bot = telegram.Bot(token=BOT_TOKEN)

# Функции для работы с файлом
def load_seen_ads():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return set(json.load(f))
    print(f"{time.ctime()}: Файл {DATA_FILE} не найден, начинаем с пустого списка")
    return set()

def save_seen_ads(seen_ads):
    with open(DATA_FILE, 'w') as f:
        json.dump(list(seen_ads), f)
    print(f"{time.ctime()}: Сохранено {len(seen_ads)} объявлений в {DATA_FILE}")

# Функция парсинга объявлений
def parse_ads():
    try:
        print(f"{time.ctime()}: Выполняется запрос к {SITE_URL}")
        response = requests.get(SITE_URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        ad_links = [urljoin(SITE_URL, a['href']) for a in soup.select(SELECTOR)]
        print(f"{time.ctime()}: Найдено {len(ad_links)} ссылок")
        return set(ad_links)
    except Exception as e:
        print(f"{time.ctime()}: Ошибка при парсинге: {e}")
        return set()

# Асинхронная функция отправки уведомления
async def send_notification(link):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=f"Новое объявление: {link}")
        print(f"{time.ctime()}: Отправлено уведомление: {link}")
    except Exception as e:
        print(f"{time.ctime()}: Ошибка при отправке уведомления: {e}")

# Проверка новых объявлений
async def check_new_ads():
    print(f"{time.ctime()}: Проверка новых объявлений...")
    seen_ads = load_seen_ads()
    current_ads = parse_ads()
    new_ads = current_ads - seen_ads
    if new_ads:
        print(f"{time.ctime()}: Найдено {len(new_ads)} новых объявлений")
        for ad in new_ads:
            await send_notification(ad)
            seen_ads.add(ad)
        save_seen_ads(seen_ads)
    else:
        print(f"{time.ctime()}: Новых объявлений нет")
    return seen_ads  # Возвращаем для сохранения в репозитории

# Главная функция
if __name__ == "__main__":
    print(f"{time.ctime()}: Парсер запущен...")
    asyncio.run(check_new_ads())

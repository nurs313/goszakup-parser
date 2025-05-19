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
SELECTOR = 'a[href^="/ru/announce/index/"]'
BOT_TOKEN = os.getenv("BOT_TOKEN", "7927707474:AAG0jX3r_575FuUVIBWdFUGWQwFJYjlKlGY")
CHAT_ID = os.getenv("CHAT_ID", "5309614527")
DATA_FILE = "seen_ads.json"

# Инициализация Telegram-бота
print(f"{time.ctime()}: Инициализация бота...")
try:
    bot = telegram.Bot(token=BOT_TOKEN)
    print(f"{time.ctime()}: Бот успешно инициализирован")
except Exception as e:
    print(f"{time.ctime()}: Ошибка инициализации бота: {e}")

# Функции для работы с файлом
def load_seen_ads():
    print(f"{time.ctime()}: Проверка наличия {DATA_FILE}")
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                ads = set(json.load(f))
                print(f"{time.ctime()}: Загружено {len(ads)} объявлений из {DATA_FILE}")
                return ads
        except json.JSONDecodeError as e:
            print(f"{time.ctime()}: Ошибка чтения {DATA_FILE}: {e}. Начинаем с пустого списка")
            return set()
    print(f"{time.ctime()}: Файл {DATA_FILE} не найден, начинаем с пустого списка")
    return set()

def save_seen_ads(seen_ads):
    print(f"{time.ctime()}: Попытка сохранить {len(seen_ads)} объявлений в {DATA_FILE}")
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(list(seen_ads), f, indent=2)
        print(f"{time.ctime()}: Успешно сохранено {len(seen_ads)} объявлений в {DATA_FILE}")
        with open(DATA_FILE, 'r') as f:
            print(f"{time.ctime()}: Содержимое {DATA_FILE}: {f.read()}")
        if os.path.exists(DATA_FILE):
            print(f"{time.ctime()}: Файл {DATA_FILE} подтверждён в директории")
        else:
            print(f"{time.ctime()}: Файл {DATA_FILE} НЕ найден после сохранения")
    except Exception as e:
        print(f"{time.ctime()}: Ошибка при сохранении {DATA_FILE}: {e}")

# Функция парсинга объявлений
def parse_ads():
    print(f"{time.ctime()}: Проверка SELECTOR: {SELECTOR}")
    try:
        print(f"{time.ctime()}: Выполняется запрос к {SITE_URL}")
        response = requests.get(SITE_URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        ad_links = [urljoin(SITE_URL, a['href']) for a in soup.select(SELECTOR)]
        print(f"{time.ctime()}: Найдено {len(ad_links)} ссылок: {ad_links[:5]}")
        return set(ad_links)
    except Exception as e:
        print(f"{time.ctime()}: Ошибка при парсинге: {e}")
        return set()

# Асинхронная функция отправки уведомления
async def send_notification(link):
    print(f"{time.ctime()}: Отправка уведомления: {link}")
    try:
        await bot.send_message(chat_id=CHAT_ID, text=f"Новое объявление: {link}")
        print(f"{time.ctime()}: Успешно отправлено уведомление: {link}")
    except Exception as e:
        print(f"{time.ctime()}: Ошибка при отправке уведомления: {e}")

# Проверка новых объявлений
async def check_new_ads():
    print(f"{time.ctime()}: Проверка новых объявлений...")
    seen_ads = load_seen_ads()
    print(f"{time.ctime()}: Текущее количество seen_ads: {len(seen_ads)}")
    current_ads = parse_ads()
    print(f"{time.ctime()}: Текущее количество current_ads: {len(current_ads)}")
    new_ads = current_ads - seen_ads
    if new_ads:
        print(f"{time.ctime()}: Найдено {len(new_ads)} новых объявлений")
        for ad in new_ads:
            await send_notification(ad)
            seen_ads.add(ad)
    else:
        print(f"{time.ctime()}: Новых объявлений нет")
    print(f"{time.ctime()}: Перед сохранением seen_ads: {len(seen_ads)} объявлений")
    save_seen_ads(seen_ads)
    return seen_ads

# Главная функция
if __name__ == "__main__":
    print(f"{time.ctime()}: Парсер запущен...")
    try:
        asyncio.run(check_new_ads())
        print(f"{time.ctime()}: Парсер завершил работу")
    except Exception as e:
        print(f"{time.ctime()}: Ошибка выполнения парсера: {e}")

import requests
from bs4 import BeautifulSoup
import time

# НАЛАШТУВАННЯ
TOKEN = "9257801183:AAHfb3NeFt5hfIAnxjpj9S5gotrCyuq7tLI"
CHAT_ID = "9257801183"
URL = "https://bezsvitla.com.ua/chernihivska-oblast/cherha-4-2"

# Змінна для збереження попереднього стану
last_schedule = ""

def send_telegram_message(text):
    """Відправка повідомлення в Telegram"""
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(telegram_url, json=payload)
    except Exception as e:
        print(f"Помилка відправки в Telegram: {e}")

def get_schedule():
    """Парсинг графіка з сайту bezsvitla.com.ua"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Шукаємо блок із графіком
        # Зазвичай інтервали знаходяться у відповідних контейнерах або текстах
        text_content = soup.get_text()
        
        # Витягуємо ключовий блок графіка (проста очистка для порівняння)
        # На сайті інтервали відображаються у форматі HH:MM – HH:MM
        import re
        intervals = re.findall(r'\d{2}:\d{2}\s*–\s*\d{2}:\d{2}', text_content)
        
        if intervals:
            # Прибираємо дублікати, зберігаючи порядок
            seen = set()
            clean_intervals = [x for x in intervals if not (x in seen or seen.add(x))]
            return "\n".join([f"⏰ {i}" for i in clean_intervals])
        
        return None
    except Exception as e:
        print(f"Помилка під час парсингу: {e}")
        return None

def main():
    global last_schedule
    send_telegram_message("🤖 <b>Бот моніторингу черги 4.2 запущено!</b>\nЯ сповіщу вас, як тільки графік зміниться.")
    
    while True:
        current_schedule = get_schedule()
        
        if current_schedule:
            # Якщо графік змінився або це перший запуск
            if current_schedule != last_schedule:
                last_schedule = current_schedule
                msg = f"⚡ <b>ОНОВЛЕНО ГРАФІК (Черга 4.2)</b>\n\n{current_schedule}\n\n🔗 <a href='{URL}'>Переглянути на сайті</a>"
                send_telegram_message(msg)
                print("Оновлення надіслано в Telegram!")
        
        # Перевіряти кожні 15 хвилин (900 секунд)
        time.sleep(900)

if __name__ == "__main__":
    main()
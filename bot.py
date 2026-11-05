import requests
from bs4 import BeautifulSoup
import re

TOKEN = "9257801183:AAHfb3NeFt5hfIAnxjpj9S5gotrCyuq7tLI"
CHAT_ID = "8613036126"
URL = "https://bezsvitla.com.ua/chernihivska-oblast/cherha-4-2"

def send_telegram_message(text):
    telegram_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(telegram_url, json=payload)
    except Exception as e:
        print(f"Помилка: {e}")

def main():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(URL, headers=headers, timeout=15)
        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.text, "html.parser")
        text_content = soup.get_text()
        intervals = re.findall(r'\d{2}:\d{2}\s*–\s*\d{2}:\d{2}', text_content)
        
        if intervals:
            seen = set()
            clean_intervals = [x for x in intervals if not (x in seen or seen.add(x))]
            current_schedule = "\n".join([f"⏰ {i}" for i in clean_intervals])
            
            # Відправляємо свіжий графік
            msg = f"⚡ <b>АКТУАЛЬНИЙ ГРАФІК (Черга 4.2)</b>\n\n{current_schedule}\n\n🔗 <a href='{URL}'>Переглянути на сайті</a>"
            send_telegram_message(msg)
    except Exception as e:
        print(f"Помилка парсингу: {e}")

if __name__ == "__main__":
    main()

import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN", "9257801183:AAHfb3NeFt5hfIAnxjpj9S5gotrCyuq7tLI")

# Указываем список ID получателей через запятую (в виде чисел или строк)
# Например: ["123456789", "987654321", "112233445"]
CHAT_IDS = ["757987493", "1941981584"]

URL = "https://bezsvitla.com.ua/chernihivska-oblast/cherha-3-2"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_current_date_ukr():
    months = {
        1: "січня", 2: "лютого", 3: "березня", 4: "квітня",
        5: "травня", 6: "червня", 7: "липня", 8: "серпня",
        9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"
    }
    now = datetime.now()
    return f"{now.day} {months[now.month]}"

def check_schedule():
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка загрузки: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    result_lines = []
    
    time_pattern = re.compile(r'(\d{2}:\d{2})\s*[\-–—]\s*(\d{2}:\d{2})')

    for element in soup.find_all(True):
        text = element.get_text(" ", strip=True)
        match = time_pattern.search(text)
        
        if match and len(text) < 35:
            interval = f"{match.group(1)} - {match.group(2)}"
            
            parent = element.find_parent()
            classes = " ".join(element.get("class", []))
            parent_classes = " ".join(parent.get("class", [])) if parent else ""
            combined_classes = (classes + " " + parent_classes).lower()
            
            is_off = any(c in combined_classes for c in ["off", "red", "danger", "disable", "outage", "no-light"])
            
            full_html = str(parent).lower() if parent else str(element).lower()
            if "вимк" in full_html or "нема" in full_html or "class=\"off" in full_html:
                is_off = True

            status_text = "немає світла" if is_off else "є світло"
            line = f"{interval} — {status_text}"
            
            if line not in result_lines and not any(interval in existing for existing in result_lines):
                result_lines.append(line)

    if result_lines:
        date_str = get_current_date_ukr()
        message = "⚡ <b>ГРАФІК СВІТЛА (Черга 3.2)</b>"
        message += f"\n <b>Дата: {date_str}</b>"
        message += "\n\n" + "\n".join(result_lines)
        message += f"\n\n🔗 <a href='{URL}'>Переглянути на сайті</a>"
        
        # Запускаем рассылку по всем ID из списка
        send_telegram_to_all(message)
    else:
        print("Не удалось найти интервалы расписания.")

def send_telegram_to_all(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for chat_id in CHAT_IDS:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        res = requests.post(url, json=payload)
        print(f"Отправка для {chat_id}: статус {res.status_code}")

if __name__ == "__main__":
    check_schedule()

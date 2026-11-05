import os
import re
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("BOT_TOKEN", "9257801183:AAHfb3NeFt5hfIAnxjpj9S5gotrCyuq7tLI")
CHAT_ID = os.getenv("CHAT_ID", "8613036126")


URL = "https://bezsvitla.com.ua/chernihivska-oblast/cherha-4-2"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_schedule():
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка загрузки: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    outage_lines = []
    
    time_pattern = re.compile(r'(\d{2}:\d{2})\s*[\-–—]\s*(\d{2}:\d{2})')

    for element in soup.find_all(['div', 'li', 'span', 'p']):
        text = element.get_text(" ", strip=True)
        match = time_pattern.search(text)
        
        if match and len(text) < 30:
            interval = f"{match.group(1)} - {match.group(2)}"
            
            elem_str = str(element).lower()
            parent_str = str(element.parent).lower() if element.parent else ""
            combined = elem_str + " " + parent_str
            
            # Определяем статус отключения
            is_outage = False
            if any(k in combined for k in ["off", "red", "danger", "no-light", "disable", "outage"]):
                is_outage = True
            elif "rgb(40" in combined or "fill=\"#28" in combined or "green" in combined:
                is_outage = False
            else:
                if "вимк" in combined or "нема" in combined or "off" in combined:
                    is_outage = True

            # Добавляем в список ТОЛЬКО если это отключение света
            if is_outage:
                line = f"❌ {interval}"
                if line not in outage_lines and not any(interval in existing for existing in outage_lines):
                    outage_lines.append(line)

    if outage_lines:
        message = "⚡ <b>ГОДИНИ ВІДКЛЮЧЕННЯ (Черга 4.2)</b>\n\n"
        message += "\n".join(outage_lines)
        message += f"\n\n🔗 <a href='{URL}'>Переглянути на сайті</a>"
        send_telegram(message)
    else:
        # Если отключений нет, сообщаем об этом
        message = "⚡ <b>Графік для Черги 4.2:</b>\n\n💡 Наразі відключень за цією чергою немає!"
        message += f"\n\n🔗 <a href='{URL}'>Переглянути на сайті</a>"
        send_telegram(message)

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    res = requests.post(url, json=payload)
    print("Статус отправки:", res.status_code, res.text)

if __name__ == "__main__":
    check_schedule()

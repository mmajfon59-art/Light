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
    result_lines = []
    
    # Ищем все блоки, которые похожи на строки расписания (содержат время вида ЧЧ:ММ - ЧЧ:ММ)
    time_pattern = re.compile(r'\d{2}:\d{2}\s*[\-–—]\s*\d{2}:\d{2}')

    for element in soup.find_all(True):
        text = element.get_text(strip=True)
        match = time_pattern.search(text)
        
        if match and len(text) < 30:
            interval = match.group(0).replace("–", "-").replace("—", "-")
            
            # Ищем родительский контейнер строки, чтобы проверить наличие класса/индикатора цвета
            container = element.find_parent(['div', 'li', 'tr'])
            container_html = str(container).lower() if container else str(element).lower()
            
            # На сайте bezsvitla активный свет (есть) обычно имеет зеленый цвет или класс on/has-light/success
            # Отключение (нет света) — red/off/danger/disable
            if any(k in container_html for k in ["off", "red", "danger", "no-light", "disable", "outage"]):
                icon = "❌"
            elif any(k in container_html for k in ["on", "success", "green", "has-light", "active"]):
                icon = "💡"
            else:
                # Если явного класса нет, проверяем по наличию SVG/иконок внутри
                if "rgb(40" in container_html or "#28" in container_html or "green" in container_html:
                    icon = "💡"
                else:
                    icon = "❌" # по умолчанию для неактивных интервалов
            
            line = f"{icon} {interval}"
            if line not in result_lines and not any(interval in existing for existing in result_lines):
                result_lines.append(line)

    if result_lines:
        message = "⚡ <b>АКТУАЛЬНИЙ ГРАФІК (Черга 4.2)</b>\n\n"
        message += "\n".join(result_lines)
        message += f"\n\n🔗 <a href='{URL}'>Переглянути на сайті</a>"
        send_telegram(message)
    else:
        print("Не удалось найти интервалы.")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True  # убирает большое превью сайта с картинкой-молнией
    }
    res = requests.post(url, json=payload)
    print("Статус отправки в Telegram:", res.status_code, res.text)

if __name__ == "__main__":
    check_schedule()

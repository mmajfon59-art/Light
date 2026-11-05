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
    
    time_pattern = re.compile(r'(\d{2}:\d{2})\s*[\-–—]\s*(\d{2}:\d{2})')

    for element in soup.find_all(['div', 'li', 'span', 'p']):
        text = element.get_text(" ", strip=True)
        match = time_pattern.search(text)
        
        if match and len(text) < 30:
            interval = f"{match.group(1)} - {match.group(2)}"
            
            # Проверяем структуру контейнера строки графика
            container = element.find_parent(['div', 'li', 'tr'])
            container_html = str(container).lower() if container else str(element).lower()
            
            # Ищем маркеры света (зеленый цвет, класс on, success или наличие лампочки)
            is_light = False
            if any(k in container_html for k in ["on", "success", "green", "has-light", "active", "rgb(40", "#28"]):
                is_light = True
            elif any(k in container_html for k in ["off", "red", "danger", "no-light", "disable", "outage", "rgb(217", "#e"]):
                is_light = False
            else:
                # Если явных классов нет, по умолчанию считаем по наличию текста отключения
                if "вимк" in container_html or "нема" in container_html:
                    is_light = False
                else:
                    is_light = True  # Если сомнения — считаем, что свет есть, пока не доказано обратное

            status_text = "є світло" if is_light else "немає світла"
            line = f"{interval} — {status_text}"
            
            if line not in result_lines and not any(interval in existing for existing in result_lines):
                result_lines.append(line)

    if result_lines:
        message = "⚡ <b>ГРАФІК СВІТЛА (Черга 4.2)</b>\n\n"
        message += "\n".join(result_lines)
        message += f"\n\n🔗 <a href='{URL}'>Переглянути на сайті</a>"
        send_telegram(message)
    else:
        print("Не удалось найти интервалы расписания.")

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

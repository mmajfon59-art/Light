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
    
    # Регулярное выражение для поиска времени (например, 00:00 - 02:30 или 00:00 – 02:30)
    time_pattern = re.compile(r'(\d{2}:\d{2})\s*[\-–—]\s*(\d{2}:\d{2})')

    # Ищем элементы, которые похожи на строки расписания
    for element in soup.find_all(['div', 'li', 'span', 'p']):
        text = element.get_text(" ", strip=True)
        match = time_pattern.search(text)
        
        # Проверяем, что строка короткая и содержит именно временной интервал
        if match and len(text) < 30:
            interval = f"{match.group(1)} - {match.group(2)}"
            
            # Анализируем классы и содержимое элемента на предмет статуса отключения
            elem_str = str(element).lower()
            parent_str = str(element.parent).lower() if element.parent else ""
            combined = elem_str + " " + parent_str
            
            # На сайте bezsvitla отключения отмечены красными элементами или классами off/red/danger
            # Свет — зелеными или on/success
            if any(k in combined for k in ["off", "red", "danger", "no-light", "disable", "outage"]):
                icon = "❌"
            elif any(k in combined for k in ["on", "success", "green", "has-light", "active"]):
                icon = "💡"
            else:
                # Дополнительная проверка по графическим индикаторам внутри строки
                if "rgb(40" in combined or "fill=\"#28" in combined or "green" in combined:
                    icon = "💡"
                else:
                    # Если явного указания нет, проверяем по сопутствующему тексту
                    if "вимк" in combined or "нема" in combined or "off" in combined:
                        icon = "❌"
                    else:
                        icon = "💡"

            line = f"{icon} {interval}"
            if line not in result_lines and not any(interval in existing for existing in result_lines):
                result_lines.append(line)

    if result_lines:
        message = "⚡ <b>АКТУАЛЬНИЙ ГРАФІК (Черга 4.2)</b>\n\n"
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

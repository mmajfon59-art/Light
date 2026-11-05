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
    
    # Регулярное выражение для поиска интервалов времени (например, 00:00 - 02:30)
    time_pattern = re.compile(r'\d{2}:\d{2}\s*[\-–—]\s*\d{2}:\d{2}')

    # Находим все теги, содержащие время
    for element in soup.find_all(True):
        text = element.get_text(strip=True)
        match = time_pattern.search(text)
        
        # Если элемент содержит только интервал времени (без лишнего длинного текста)
        if match and len(text) < 25:
            interval = match.group(0).replace("–", "-").replace("—", "-")
            
            # Анализируем HTML-разметку элемента и его родителей
            html_chunk = str(element) + str(element.parent)
            html_chunk_lower = html_chunk.lower()
            
            # Проверяем на наличие иконки выключения / красного цвета
            if any(k in html_chunk_lower for k in ["off", "red", "danger", "no-light", "без", "light-off", "0.5"]):
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
        print("ОШИБКА: Не удалось собрать строки интервалов.")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    res = requests.post(url, json=payload)
    print("Статус отправки в Telegram:", res.status_code, res.text)

if __name__ == "__main__":
    check_schedule()

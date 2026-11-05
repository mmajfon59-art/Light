import os
import re
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")
CHAT_ID = os.getenv("CHAT_ID", "ВАШ_CHAT_ID")

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
    
    # Пытаемся найти дату на странице (обычно отображается в заголовках или блоках истории/статуса)
    date_str = ""
    date_elem = soup.find(string=re.compile(r'\d{1,2}\s+(січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)', re.I))
    if date_elem:
        date_str = date_elem.strip()

    # Ищем все элементы, содержащие временные интервалы
    time_pattern = re.compile(r'\d{2}:\d{2}\s*[\-–—]\s*\d{2}:\d{2}')

    for element in soup.find_all(True):
        text = element.get_text(strip=True)
        match = time_pattern.search(text)
        
        if match and len(text) < 35:
            interval = match.group(0).replace("–", "-").replace("—", "-")
            
            # Проверяем атрибуты и классы элемента или его соседей на предмет света/отключения
            parent = element.parent
            combined_html = (str(element) + str(parent)).lower()
            
            # На сайте bezsvitla блоки со светом содержат зеленые индикаторы / классы
            # Отключения содержат стили с красным цветом или классы off/red
            if any(cls in combined_html for cls in ["off", "red", "danger", "no-light", "disable"]):
                icon = "❌"
            elif any(cls in combined_html for cls in ["on", "success", "green", "has-light", "active"]):
                icon = "💡"
            else:
                # Анализируем наличие стилей цвета внутри тега (например, SVG пути или цвета фона)
                if "rgb(40" in combined_html or "fill=\"#28" in combined_html or "green" in combined_html:
                    icon = "💡"
                elif "rgb(217" in combined_html or "red" in combined_html or "fill=\"#e" in combined_html:
                    icon = "❌"
                else:
                    # Если явно не определился цвет, проверяем текст рядом
                    if "є світло" in combined_html or "вимкнено" not in combined_html:
                        icon = "💡"
                    else:
                        icon = "❌"

            line = f"{icon} {interval}"
            if line not in result_lines and not any(interval in existing for existing in result_lines):
                result_lines.append(line)

    # Если стандартный поиск не вывел строки, делаем поиск по строковым фрагментам времени на странице
    if not result_lines:
        for div in soup.find_all('div'):
            t = div.get_text(" ", strip=True)
            if time_pattern.search(t) and len(t) < 50:
                if "❌" in t or "off" in str(div).lower():
                    icon = "❌"
                else:
                    icon = "💡"
                m = time_pattern.search(t)
                if m:
                    line = f"{icon} {m.group(0)}"
                    if line not in result_lines:
                        result_lines.append(line)

    # Формируем сообщение
    header = "⚡ <b>АКТУАЛЬНИЙ ГРАФІК (Черга 4.2)</b>"
    if date_str:
        header += f"\n📅 <i>{date_str}</i>"

    if result_lines:
        message = header + "\n\n" + "\n".join(result_lines)
        message += f"\n\n🔗 <a href='{URL}'>Переглянути на сайті</a>"
        send_telegram(message)
    else:
        print("Не удалось извлечь график.")

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

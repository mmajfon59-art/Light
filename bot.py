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
    
    # Поиск даты на странице
    date_str = ""
    month_names = r'(січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)'
    date_pattern = re.compile(r'(\d{1,2}\s+' + month_names + r')', re.I)
    
    for tag in soup.find_all(['h1', 'h2', 'h3', 'div', 'span', 'p']):
        t = tag.get_text(strip=True)
        m = date_pattern.search(t)
        if m and len(t) < 30:
            date_str = m.group(1)
            break

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
        message = "⚡ <b>ГРАФІК СВІТЛА (Черга 4.2)</b>"
        if date_str:
            message += f"\n📅 <b>Дата: {date_str}</b>"
        message += "\n\n" + "\n".join(result_lines)
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

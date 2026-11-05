import os
import requests
from bs4 import BeautifulSoup

# Данные для Telegram
TOKEN = os.getenv("BOT_TOKEN", "9257801183:AAHfb3NeFt5hfIAnxjpj9S5gotrCyuq7tLI")
CHAT_ID = os.getenv("CHAT_ID", "8613036126")

URL = "https://bezsvitla.com.ua/chernihivska-oblast/cherha-4-2"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_schedule():
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка загрузки страницы: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Находим все блоки с временными интервалами
    # На bezsvitla.com.ua интервалы обычно находятся в элементах с классами статусов
    text_lines = ["⚡ <b>АКТУАЛЬНИЙ ГРАФІК (Черга 4.2)</b>\n"]
    
    # Ищем строки графика (контейнеры интервалов)
    items = soup.find_all("div", class_=lambda c: c and ("schedule" in c or "item" in c or "row" in c or "flex" in c))
    
    # Резервный парсинг по тексту, если структуры разметки меняются
    found_any = False
    
    # Проход по элементам разметки страницы
    for el in soup.find_all(['div', 'li', 'p']):
        text = el.get_text(strip=True)
        # Ищем совпадения временных интервалов формата 00:00 - 02:30
        if "–" in text or "-" in text:
            # Определение статуса по классам или вложенным SVG/иконкам
            html_str = str(el).lower()
            
            # Проверяем признаки отсутствия или наличия света
            if "off" in html_str or "no-light" in html_str or "red" in html_str or "без" in html_str:
                icon = "❌"
            elif "on" in html_str or "has-light" in html_str or "green" in html_str or "є" in html_str:
                icon = "💡"
            else:
                continue

    # Формируем универсальный парсинг конкретно под структуры bezsvitla
    # Если парсер сложный — собираем текстовые блоки родительских тегов
    schedule_blocks = soup.select('div[class*="schedule"], div[class*="interval"], div[class*="item"]')
    
    result_lines = []
    for block in schedule_blocks:
        t = block.get_text(" ", strip=True)
        if any(char.isdigit() for char in t) and ":" in t:
            # Анализируем цвет / класс иконки или контейнера
            cls = str(block.get("class", [])).lower()
            inner = str(block).lower()
            
            if "red" in inner or "off" in inner or "danger" in inner or "outage" in inner:
                status = "❌"
            else:
                status = "💡"
            
            if t not in result_lines:
                result_lines.append(f"{status} {t}")

    # Если точечный селектор не сработал — базовое сопоставление по тегам SVG/классам
    if not result_lines:
        # Прямой разбор элементов списка
        for row in soup.find_all(True, class_=True):
            classes = " ".join(row.get("class", []))
            txt = row.get_text(strip=True)
            if len(txt) >= 11 and ":" in txt and ("-" in txt or "–" in txt):
                if "off" in classes or "red" in classes or "disable" in classes:
                    icon = "❌"
                else:
                    icon = "💡"
                line = f"{icon} {txt}"
                if line not in result_lines and len(txt) < 20:
                    result_lines.append(line)

    if result_lines:
        message = "⚡ <b>АКТУАЛЬНИЙ ГРАФІК (Черга 4.2)</b>\n\n" + "\n".join(result_lines)
        message += f"\n\n🔗 <a href='{URL}'>Переглянути на сайті</a>"
        send_telegram(message)
    else:
        print("Не удалось распарсить график, проверяем структуру...")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    res = requests.post(url, json=payload)
    print("Ответ Telegram:", res.status_code, res.text)

if __name__ == "__main__":
    check_schedule()

import requests
from bs4 import BeautifulSoup
import csv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://old.mospolytech.ru"
ENDPOINT = "https://mospolytech.ru/postupayushchim/priem-v-universitet/rating-abiturientov/fio_list_curl.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": BASE_URL,
}

PAYLOAD = {
    "select1": "000000058_01",
    "specCode": "2.3.8.",
    "eduForm": "Очная",
    "eduFin": "Полное возмещение затрат",
    "f": "1",
}


def get_rating_html():
    try:
        response = requests.post(
            ENDPOINT,
            data=PAYLOAD,
            headers=HEADERS,
            timeout=15,
            verify=False,
        )
        response.raise_for_status()
        response.encoding = "utf-8"

        if response.text == "!error!":
            print("Сервер вернул ошибку: !error!")
            return None

        return response.text

    except requests.exceptions.RequestException as e:
        print("Ошибка запроса:", e)
        return None


def parse_table(html):
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="check")  # именно эта таблица с данными

    if not table:
        print("Таблица не найдена в ответе")
        print("Ответ сервера:", html[:500])
        return None, None

    # Заголовки из <td> в первой строке (там нет <th>)
    header_row = table.find("tr")
    headers = [td.get_text(strip=True) for td in header_row.find_all("td")]

    rows = []
    for tr in table.find_all("tr")[1:]:  # пропускаем заголовок
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if cells:
            rows.append(cells)

    return headers, rows


def save_to_csv(headers, rows, filename="rating.csv"):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)
    print(f"Сохранено в {filename} ({len(rows)} строк)")


if __name__ == "__main__":
    print("Отправляю запрос...")
    html = get_rating_html()

    if not html:
        exit()

    headers, rows = parse_table(html)

    if rows:
        print(f"Найдено строк: {len(rows)}")
        save_to_csv(headers, rows)
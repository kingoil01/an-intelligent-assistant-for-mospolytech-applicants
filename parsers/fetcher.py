import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def sync_fetch_rating(select1, spec_code, edu_form, edu_fin):
    page_url = "https://mospolytech.ru/postupayushchim/priem-v-universitet/rating-abiturientov/"
    post_url = "https://mospolytech.ru/postupayushchim/priem-v-universitet/rating-abiturientov/fio_list_curl.php"

    payload = {
        "select1": select1,
        "specCode": spec_code,
        "eduForm": edu_form,
        "eduFin": edu_fin,
        "f": "1",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Origin": "https://mospolytech.ru",
        "Referer": page_url,
    }

    session = requests.Session()

    # Сначала открываем страницу, чтобы получить cookies
    session.get(
        page_url,
        headers=headers,
        timeout=15,
        verify=False,
    )

    # Потом делаем POST запрос к таблице
    response = session.post(
        post_url,
        data=payload,
        headers=headers,
        timeout=15,
        verify=False,
    )

    response.encoding = "utf-8"
    html = response.text

    print("SERVER RESPONSE:", html[:300])

    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="check")

    if not table:
        raise RuntimeError("Таблица не найдена")

    rows = []

    for tr in table.find_all("tr")[1:]:
        tds = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(tds) >= 3:
            try:
                place = int(tds[0])
                code = int(tds[2])
                rows.append((code, place))
            except ValueError:
                continue

    return rows

import asyncio

async def fetch_rating(select1, spec_code, edu_form, edu_fin):
    return await asyncio.to_thread(
        sync_fetch_rating,
        select1,
        spec_code,
        edu_form,
        edu_fin,
    )
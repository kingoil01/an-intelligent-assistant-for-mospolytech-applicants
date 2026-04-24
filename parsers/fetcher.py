import aiohttp
from bs4 import BeautifulSoup

async def fetch_rating(qs: str):
    url = "https://mospolytech.ru/postupayushchim/priem-v-universitet/rating-abiturientov/fio_list_curl.php"

    payload = {
        "qs": qs
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, ssl=False) as resp:
            html = await resp.text()

    soup = BeautifulSoup(html, "lxml")

    rows = []

    table = soup.find("table", class_="check")
    if not table:
        return []

    for tr in table.find_all("tr")[1:]:
        tds = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(tds) >= 3:
            try:
                place = int(tds[0])
                code = int(tds[2])
                rows.append((code, place))
            except:
                continue

    return rows
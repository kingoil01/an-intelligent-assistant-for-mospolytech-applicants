import aiosqlite
import asyncio
import aiohttp
from bs4 import BeautifulSoup

DB_PATH = "bot.db"

ENDPOINT = "https://mospolytech.ru/postupayushchim/priem-v-universitet/rating-abiturientov/fio_list_curl.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://mospolytech.ru",
}


async def fetch_html(session: aiohttp.ClientSession, payload: dict) -> str | None:
    try:
        async with session.post(
            ENDPOINT,
            data=payload,
            headers=HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
            ssl=False,
        ) as response:
            response.raise_for_status()
            text = await response.text(encoding="utf-8")
            return None if text == "!error!" else text
    except aiohttp.ClientError as e:
        print(f"Ошибка запроса: {e}")
        return None


def parse_places(html: str) -> dict[int, int]:
    """Возвращает {unique_code: place}"""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="check")

    if not table:
        return {}

    places = {}
    for tr in table.find_all("tr")[1:]:  # пропускаем заголовок
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) < 3:
            continue
        try:
            place = int(cells[0])       # столбец №
            unique_code = int(cells[2]) # столбец "Уникальный код"
            places[unique_code] = place
        except ValueError:
            continue

    return places


async def get_competitions(db: aiosqlite.Connection) -> list[dict]:
    """Получаем все конкурсные группы из БД"""
    async with db.execute(
        "SELECT id, name, select1, spec_code, edu_form, edu_fin FROM competitions"
    ) as cursor:
        rows = await cursor.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "select1": row[2],
            "spec_code": row[3],
            "edu_form": row[4],
            "edu_fin": row[5],
        }
        for row in rows
    ]


async def update_places(db: aiosqlite.Connection, competition_id: int, places: dict[int, int]):
    """Обновляем current_place у абитуриентов этой конкурсной группы"""
    async with db.execute(
        "SELECT id, unique_code FROM applicants WHERE competition_id = ?",
        (competition_id,),
    ) as cursor:
        applicants = await cursor.fetchall()

    for applicant_id, unique_code in applicants:
        if unique_code in places:
            await db.execute(
                """UPDATE applicants
                   SET current_place = ?, place_updated_at = datetime('now')
                   WHERE id = ?""",
                (places[unique_code], applicant_id),
            )

    await db.execute(
        "UPDATE competitions SET last_updated = datetime('now') WHERE id = ?",
        (competition_id,),
    )


async def refresh_all():
    """Главная функция — тянет данные по всем конкурсным группам и обновляет БД"""
    async with aiosqlite.connect(DB_PATH) as db:
        competitions = await get_competitions(db)

        if not competitions:
            print("Нет конкурсных групп в БД")
            return

        async with aiohttp.ClientSession() as session:
            for competition in competitions:
                print(f"Обновляю: {competition['name']}")

                payload = {
                    "select1": competition["select1"],
                    "specCode": competition["spec_code"],
                    "eduForm": competition["edu_form"],
                    "eduFin": competition["edu_fin"],
                    "f": "1",
                }

                html = await fetch_html(session, payload)
                if not html:
                    print(f"  Не удалось получить данные")
                    continue

                places = parse_places(html)
                print(f"  Найдено абитуриентов: {len(places)}")

                await update_places(db, competition["id"], places)
                await db.commit()

        print("Обновление завершено")


async def get_place(tg_user_id: int) -> list[dict]:
    """Получить текущие места пользователя — вызывать из бота"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT c.name, a.unique_code, a.current_place, a.place_updated_at
               FROM subscriptions s
               JOIN applicants a ON s.applicant_id = a.id
               JOIN competitions c ON a.competition_id = c.id
               WHERE s.tg_user_id = ? AND s.notifications_enabled = 1""",
            (tg_user_id,),
        ) as cursor:
            rows = await cursor.fetchall()

    return [
        {
            "competition": row[0],
            "unique_code": row[1],
            "place": row[2],
            "updated_at": row[3],
        }
        for row in rows
    ]


if __name__ == "__main__":
    asyncio.run(refresh_all())
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_html(url):
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "ru-RU,ru;q=0.9"}
    try:
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.text
    except requests.exceptions.RequestException as e:
        print("Ошибка:", e)
        return None

def get_subjects_from_html(html, target_code, target_prof):
    # ускоряем за счет lxml
    soup = BeautifulSoup(html, "lxml")

    # CSS-селектор сразу фильтрует строки с нужными td
    rows = soup.select("tr:has(td[itemprop='eduCode']):has(td[itemprop='eduProf'])")
    subjects = []

    for row in rows:
        code_cell = row.find("td", itemprop="eduCode")
        prof_cell = row.find("td", itemprop="eduProf")

        code = code_cell.text.strip()
        prof = prof_cell.text.strip()
        print(f"Проверяю: {code} | {prof}")

        if code == target_code and target_prof.lower() in prof.lower():
            print(f"\nНАЙДЕНО: {code} | {prof}\n")
            rpd_block = row.find("td", itemprop="educationRpd")

            if rpd_block:
                for a in rpd_block.find_all("a"):
                    text = a.get_text(strip=True)
                    if text:
                        subjects.append(text)
            break  # останавливаемся после первого совпадения
    return subjects

def save_to_file(subjects, code, prof):
    filename = f"{code}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Программа: {code}\n")
        f.write(f"Профиль: {prof}\n\n")
        f.write("Дисциплины:\n")

        for i, s in enumerate(subjects, 1):
            f.write(f"{i}. {s}\n")

    print(f"\nСохранено в {filename}")

if __name__ == "__main__":
    url = "https://mospolytech.ru/sveden/education/eduop/"

    code = input("Введите код программы: ") 
    prof = input("Введите название профиля: ")

    html = get_html(url)

    if not html:
        print("Не удалось получить страницу")
        exit()

    subjects = get_subjects_from_html(html, code, prof)

    if subjects:
        save_to_file(subjects, code, prof)
    else:
        print("Ничего не найдено")
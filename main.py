import os
import sys
from os.path import splitext
import requests
from bs4 import BeautifulSoup
from transliterate import translit
from pdfminer import high_level
import re
import json

UPLOAD_URL = "https://se.math.spbu.ru/post_theses"
TEXT_PATH = "./report/text/"
SLIDES_PATH = "./report/slides/"
SUPERVISOR_REVIEW_PATH = "./report/review/"

SUPERVISORS = (
    'Кириленко',
    'Баклановский',
    'Литвинов',
    'Подкопаев',
    'Пименов',
    'Немешев',
    'Григорьев',
    'Булычев',
    'Монькин',
    'Лазарева',
    'Губанов',
    'Сартасов',
    'Брыксин'
)

# Download files?
download = False


def download_file(uri, safe_filename, save_path="./report/"):
    # Skip if download == false
    if not download:
        print("Download flag if False")
        return

    r = requests.get(uri, allow_redirects=True)
    open(safe_filename, 'wb').write(r.content)
    try:
        os.rename(safe_filename, save_path + safe_filename)
    except FileExistsError:
        print("File already exists " + safe_filename)
        os.remove(safe_filename)
    else:
        print("Downloaded " + safe_filename)


def get_2017_reports():
    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2017'

    response = session.get(url)

    if response.status_code != 200:
        print("Response status " + str(response.status_code))
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Найдем таблицы содержащие курсовые работы
    tables = soup.select(".listing")

    # Разберем первую таблицу, бакалавры 371 группы
    for row in tables[0].find_all('tr'):
        cols = row.find_all('td')
        if len(cols) != 3:
            print("Error while parsing cols in table")
            continue

        author = cols[0].text
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = cols[1].text

        # находим ссылки на текст слайды и рецензию
        anchors = cols[2].find_all('a')

        # Скачиваем текст
        text_uri = anchors[0].get('href')
        extension = splitext(text_uri)[1]
        text_filename = author_en + "_Bachelor_Report_2017_text" + extension
        print("Download text: " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Скачиваем слайды
        slides_uri = anchors[1].get('href')
        extension = splitext(slides_uri)[1]
        slides_filename = author_en + "_Bachelor_Report_2017_slides" + extension
        print("Download slides: " + slides_filename)
        download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Скачиваем отзыв
        supervisor_review_uri = anchors[2].get('href')
        extension = splitext(supervisor_review_uri)[1]
        supervisor_review_filename = author_en + "_Bachelor_Report_2017_supervisor_review" + extension
        print("Download supervisor review: " + supervisor_review_filename)
        download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Достаем имя научника
        text_pdf = high_level.extract_text('report/text/' + text_filename)
        supervisor_re = re.search(r"Научный руководитель:.*\n+(.+)", text_pdf)[1]
        supervisor = ''

        for supervisor_string in SUPERVISORS:
            tmp = re.search(supervisor_string, supervisor_re)
            if str(tmp) != "None":
                supervisor = tmp[0]
                break
        if supervisor == '':
            print("Error while parsing supervisor")
            continue

        print("Supervisor: " + supervisor)

        thesis_info = {'type_id': 2, 'course_id': 2, 'name_ru': name, 'author': author,
                       'supervisor': supervisor, 'publish_year': 2017,
                       'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        report_text = "report/text/" + text_filename
        presentation = "report/slides/" + slides_filename
        supervisor_review = "report/review/" + supervisor_review_filename

        files = [
            ('thesis_text', (report_text, open(report_text, 'rb'), 'application/octet')),
            ('presentation', (presentation, open(presentation, 'rb'), 'application/octet')),
            ('supervisor_review', (supervisor_review, open(supervisor_review, 'rb'), 'application/octet')),
            ('thesis_info', ('thesis_info', json.dumps(thesis_info), 'application/json')),
        ]

        r = requests.post(UPLOAD_URL, files=files, allow_redirects=False)
        print(str(r.content, 'utf-8'))

    # Разберем вторую таблицу, бакалавры 344 группы
    for row in tables[1].find_all('tr'):
        cols = row.find_all('td')
        if len(cols) != 4:
            print("Error while parsing cols in table")
            continue

        author = cols[0].text
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = cols[1].text

        # находим ссылки на текст слайды и рецензию
        anchors = cols[3].find_all('a')

        # Скачиваем текст
        text_uri = anchors[0].get('href')
        extension = splitext(text_uri)[1]
        text_filename = author_en + "_Bachelor_Report_2017_text" + extension
        print("Download text: " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Скачиваем слайды
        slides_uri = anchors[1].get('href')
        extension = splitext(slides_uri)[1]
        slides_filename = author_en + "_Bachelor_Report_2017_slides" + extension
        print("Download slides: " + slides_filename)
        download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Скачиваем отзыв
        supervisor_review_uri = ''
        supervisor_review_filename = ''
        if len(anchors) > 2:
            supervisor_review_uri = anchors[2].get('href')
            extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = author_en + "_Bachelor_Report_2017_supervisor_review" + extension
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Достаем имя научника
        supervisor_re = cols[2].text
        supervisor = ''

        for supervisor_string in SUPERVISORS:
            tmp = re.search(supervisor_string, supervisor_re)
            if str(tmp) != "None":
                supervisor = tmp[0]
                break
        if supervisor == '':
            print("Error while parsing supervisor")
            continue

        print("Supervisor: " + supervisor)

        thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                       'supervisor': supervisor, 'publish_year': 2017,
                       'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        report_text = "report/text/" + text_filename
        presentation = "report/slides/" + slides_filename
        supervisor_review = "report/review/" + supervisor_review_filename

        files = [
            ('thesis_text', (report_text, open(report_text, 'rb'), 'application/octet')),
            ('presentation', (presentation, open(presentation, 'rb'), 'application/octet')),
            ('thesis_info', ('thesis_info', json.dumps(thesis_info), 'application/json')),
        ]
        if len(anchors) > 2:
            files.append(('supervisor_review', (supervisor_review, open(supervisor_review, 'rb'), 'application/octet')))

        r = requests.post(UPLOAD_URL, files=files, allow_redirects=False)
        print(str(r.content, 'utf-8'))

if __name__ == '__main__':
    get_2017_reports()

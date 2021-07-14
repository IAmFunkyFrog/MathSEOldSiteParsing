# Заметка: как мне удалось выяснить, группы x7x - програмные инженеры, а группы x4x - матобесы

import os
import sys
from os.path import splitext
import requests
from bs4 import BeautifulSoup
from transliterate import translit
from pdfminer import high_level
import re
import json
import docx

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
    'Брыксин',
    'Амелин',
    'Иноземцев',
    'Давыденко',
    'Невоструев',
    'Нестеров',
    'Вахитов',
    'Новиков',
    'Романовский',
    'Чурилин',
    'Коновалов',
    'Малов',
    'Маров',
    'Дымникова',
    'Чурилин',
    'Николенко',
    'Смирнов',
    'Терехов'
)

# Флаг скачки файлов с сайта
download = False

# Флаг загрузки файлов на сайт
UPLOAD_FLAG = True


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


def get_supervisor_from_text(text):
    print("Text of work " + text)
    try:
        supervisor_re = re.search(r".{250}Научный\sруководитель.{250}", text)[0]
    except TypeError:
        print("Error with parsing text file")
        return ''
    supervisor = ''
    print("String that must contain supervisor: " + supervisor_re)
    for supervisor_string in SUPERVISORS:
        tmp = re.search(supervisor_string, supervisor_re)
        if str(tmp) != "None":
            supervisor = tmp[0]
            break
    return supervisor


def get_supervisor_from_file(path):
    text_extension = splitext(path)[-1]
    text_of_work = ''
    if text_extension.find('.pdf', 0) > -1:
        text_of_work = high_level.extract_text(path)
    elif text_extension.find('.doc', 0) > -1 or text_extension.find('.docx', 0) > -1:
        document = docx.Document(path)
        for paragraph in document.paragraphs:
            text_of_work = text_of_work + paragraph.text + ' '
    text_of_work = text_of_work.replace('\n', ' ')
    return get_supervisor_from_text(text_of_work)


def upload_on_site(thesis_info, text_filename, slides_filename='', supervisor_review_filename=''):
    if not UPLOAD_FLAG:
        print("Upload on site disabled")
        return

    report_text = "report/text/" + text_filename
    files = [
        ('thesis_text', (report_text, open(report_text, 'rb'), 'application/octet')),
        ('thesis_info', ('thesis_info', json.dumps(thesis_info), 'application/json')),
    ]

    if slides_filename != '':
        presentation = "report/slides/" + slides_filename
        files.append(('presentation', (presentation, open(presentation, 'rb'), 'application/octet')))

    if supervisor_review_filename != '':
        supervisor_review = "report/review/" + supervisor_review_filename
        files.append(('supervisor_review', (supervisor_review, open(supervisor_review, 'rb'), 'application/octet')))

    r = requests.post(UPLOAD_URL, files=files, allow_redirects=False)
    print(str(r.content, 'utf-8'))


def get_text_filename(author_en, year, extension):
    return author_en + "_Bachelor_Report_" + str(year) + "_text" + extension

def get_slides_filename(author_en, year, extension):
    return author_en + "_Bachelor_Report_" + str(year) + "_slides" + extension

def get_supervisor_review_filename(author_en, year, extension):
    return author_en + "_Bachelor_Report_" + str(year) + "_supervisor_review" + extension


def get_2017_reports():
    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2017'
    year = 2017

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
        text_extension = splitext(text_uri)[1]
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Download text: " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Скачиваем слайды
        slides_uri = anchors[1].get('href')
        slides_extension = splitext(slides_uri)[1]
        slides_filename = get_slides_filename(author_en, year, slides_extension)
        print("Download slides: " + slides_filename)
        download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Скачиваем отзыв
        supervisor_review_uri = anchors[2].get('href')
        supervisor_review_extension = splitext(supervisor_review_uri)[1]
        supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
        print("Download supervisor review: " + supervisor_review_filename)
        download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Достаем имя научника
        supervisor = get_supervisor_from_file(TEXT_PATH + text_filename)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue

        print("Supervisor: " + supervisor)

        # Генерируем метаинформацию и загружаем

        thesis_info = {'type_id': 2, 'course_id': 2, 'name_ru': name, 'author': author,
                       'supervisor': supervisor, 'publish_year': year,
                       'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

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
        text_extension = splitext(text_uri)[1]
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Download text: " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Скачиваем слайды
        slides_uri = anchors[1].get('href')
        slides_extension = splitext(slides_uri)[1]
        slides_filename = get_slides_filename(author_en, year, slides_extension)
        print("Download slides: " + slides_filename)
        download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Скачиваем отзыв
        supervisor_review_filename = ''
        if len(anchors) > 2:
            supervisor_review_uri = anchors[2].get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Достаем имя научника
        supervisor = get_supervisor_from_text(cols[2].text)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue

        print("Supervisor: " + supervisor)

        # Генерируем метаинформацию и загружаем

        thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                       'supervisor': supervisor, 'publish_year': year,
                       'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)


def get_2016_reports():
    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2016'
    year = 2016

    response = session.get(url)

    if response.status_code != 200:
        print("Response status " + str(response.status_code))
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")

    # Найдем таблицы содержащие курсовые работы
    tables = soup.select(".listing")

    # Разберем первую таблицу, магистры 546 группа
    for row in tables[0].find_all('tr'):
        cols = row.find_all('td')
        if len(cols) != 3:
            print("Error while parsing cols in table")
            continue

        author = cols[0].text
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = cols[1].text

        # находим ссылки на текст
        anchors = cols[2].find_all('a')

        # Скачиваем текст
        text_uri = anchors[0].get('href')
        text_extension = splitext(text_uri)[1]
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Download text: " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Достаем имя научника
        supervisor = get_supervisor_from_file(TEXT_PATH + text_filename)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue

        print("Supervisor: " + supervisor)

        report_text = "report/text/" + text_filename

        thesis_info = {'type_id': 2, 'course_id': 3, 'name_ru': name, 'author': author,
                       'supervisor': supervisor, 'publish_year': year,
                       'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename)

    # Разберем вторую таблицу, бакалавры 371 группа
    for row in tables[1].find_all('tr'):
        cols = row.find_all('td')
        if len(cols) != 3:
            print("Error while parsing cols in table")
            continue

        author = cols[0].text
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = cols[1].text

        # находим ссылки на текст слайды и рецензию
        anchors = cols[2].find_all('a')

        if len(anchors) == 0:
            print("error while finding anchor to report")
            continue

        # Скачиваем текст
        text_uri = anchors[0].get('href')
        text_extension = splitext(text_uri)[1]
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Download text: " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Скачиваем слайды
        slides_uri = anchors[1].get('href')
        slides_extension = splitext(slides_uri)[1]
        slides_filename = get_slides_filename(author_en, year, slides_extension)
        print("Download slides: " + slides_filename)
        download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Скачиваем отзыв
        supervisor_review_filename = ''
        if len(anchors) > 2:
            supervisor_review_uri = anchors[2].get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Достаем имя научника
        supervisor = get_supervisor_from_file(TEXT_PATH + text_filename)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue

        print("Supervisor: " + supervisor)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 2, 'name_ru': name, 'author': author,
                       'supervisor': supervisor, 'publish_year': year,
                       'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

    # Разберем третью таблицу, бакалавры 344 группа
    for row in tables[2].find_all('tr'):
        cols = row.find_all('td')
        if len(cols) != 3:
            print("Error while parsing cols in table")
            continue

        author = cols[0].text
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = cols[1].text

        # находим ссылки на текст слайды и рецензию
        anchors = cols[2].find_all('a')

        if len(anchors) == 0:
            print("error while finding anchor to report")
            continue

        # Скачиваем текст
        text_uri = anchors[0].get('href')
        text_extension = splitext(text_uri)[1]
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Download text: " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Скачиваем слайды
        slides_uri = anchors[1].get('href')
        slides_extension = splitext(slides_uri)[1]
        slides_filename = get_slides_filename(author_en, year, slides_extension)
        print("Download slides: " + slides_filename)
        download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Скачиваем отзыв
        supervisor_review_filename = ''
        if len(anchors) > 2:
            supervisor_review_uri = anchors[2].get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Достаем имя научника
        supervisor = get_supervisor_from_file(TEXT_PATH + text_filename)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue

        print("Supervisor: " + supervisor)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                       'supervisor': supervisor, 'publish_year': year,
                       'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

def get_2015_fall():
    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/autumn-2015/magistracy-564'
    year = 2015

    response = session.get(url)

    if response.status_code != 200:
        print("Response status " + str(response.status_code))
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")
    spans = soup.select('.summary')

    # Переберем всех магистров 546 группы
    for span in spans:
        anchor = span.find('a')
        splited_author_and_theme = anchor.text.split('. ')
        author = splited_author_and_theme[0]
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = splited_author_and_theme[1]

        # Находим текст
        response = session.get(anchor.get("href"))

        if response.status_code != 200:
            print("Response status " + str(response.status_code))
            sys.exit(0)

        text_soup = BeautifulSoup(response.text, "lxml")
        anchors_to_text = text_soup.find_all('a')
        text_filename = ''
        for a in anchors_to_text:
            if a.text.find(author, 0) > -1:
                text_extension = splitext(a.text)[1].replace('\n', '')
                text_filename = get_text_filename(author_en, year, text_extension)
                print("Download " + text_filename)
                download_file(a.get('href'), text_filename, TEXT_PATH)
                break

        if text_filename == '':
            print("Error while parsing text filename")
            continue

        # Находим имя научника
        supervisor = get_supervisor_from_file(TEXT_PATH + text_filename)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue

        print("Supervisor: " + supervisor)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 3, 'name_ru': name, 'author': author,
                       'supervisor': supervisor, 'publish_year': year,
                       'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename)
        

if __name__ == '__main__':
    get_2015_fall()
    #get_2016_reports()
    #get_2017_reports()

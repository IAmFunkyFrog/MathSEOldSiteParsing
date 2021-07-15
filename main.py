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
TEXT_PATH = "/media/stepan-trefilov/Share/report/text/"
SLIDES_PATH = "/media/stepan-trefilov/Share/report/slides/"
SUPERVISOR_REVIEW_PATH = "/media/stepan-trefilov/Share/report/review/"

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
    'Терехов',
    'Лазарева',
    'Вояковская',
    'Праздников',
    'Граничин',
    'Мордвинов',
    'Боташ',
    'Шалымов',
    'Васильев',
    'Анисимов',
    'Пахомов',
    'Граничин',
    'Королёв',
    'Козлов',
    'Медведев',
    'Куралёнок',
    'Щитинин',
    'Платонов',
    'Оносовский',
    'Вяххи',
    'Семихатский',
    'Соломатов',
    'Данильченко',
    'Петров',
    'Зеленчук',
    'Николаев',
    'Абусалимов',
    'Белогрудов'
)

# Флаг скачки файлов с сайта
download = False

# Флаг загрузки файлов на сайт
UPLOAD_FLAG = False


def download_file(uri, safe_filename, save_path="./report/"):
    # Skip if download == false
    if not download:
        print("Download flag if False")
        return

    r = requests.get(uri, allow_redirects=True)
    open(save_path + safe_filename, 'wb').write(r.content)
    print("Downloaded " + safe_filename)


def rename_file(old_filename, new_filename):
    print("Renaming " + old_filename + " to " + new_filename)
    os.rename(old_filename, new_filename)


def get_supervisor_from_text(text):
    try:
        supervisor_re = re.search(r".{0,250}[Нн]аучный\sруководитель.{0,250}", text)[0]
    except TypeError:
        supervisor_re = text
        print("Error with parsing text")
    supervisor = ''
    print("String that must contain supervisor: " + supervisor_re)
    for supervisor_string in SUPERVISORS:
        if supervisor_re.find(supervisor_string, 0) > -1:
            supervisor = supervisor_string
            break
    return supervisor


def get_supervisor_from_file(path):
    text_extension = splitext(path)[-1]
    text_of_work = ''
    if text_extension.find('.pdf', 0) > -1:
        text_of_work = high_level.extract_text(path)
    elif text_extension.find('.doc', 0) > -1 or text_extension.find('.docx', 0) > -1:
        try:
            document = docx.Document(path)
        except KeyError:
            print("Ошибка парсинга doc")
            return ''
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


def get_2015_spring():
    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/spring-2015/list'
    year = 2015

    response = session.get(url)

    if response.status_code != 200:
        print("Response status " + str(response.status_code))
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")
    uls = soup.find('h3', text='344 группа').parent.find_all('ul')

    # Парсинг 344 группы
    for li in uls[0].find_all('li'):
        surname = li.find('b').text.split('.')[-1].replace(' ', '')

        anchors = li.find_all('a')
        # Достаем научника
        supervisor = get_supervisor_from_text(li.text)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue
        print("Supervisor " + supervisor)

        # Достаем текст
        text_anchor = li.find('a', text='Отчёт')
        text_uri = text_anchor.get('href')
        text_extension = splitext(text_uri)[-1]
        text_tmp_name = get_text_filename(surname, year, text_extension)
        print("Download tmp text: " + text_tmp_name)
        download_file(url + "/" + text_uri, text_tmp_name, TEXT_PATH)

        # Достаем имя студента из текста
        text_of_work = ''
        if text_extension.find('.pdf', 0) > -1:
            text_of_work = high_level.extract_text(TEXT_PATH + text_tmp_name)
        elif text_extension.find('.doc', 0) > -1 or text_extension.find('.docx', 0) > -1:
            document = docx.Document(TEXT_PATH + text_tmp_name)
            for paragraph in document.paragraphs:
                text_of_work = text_of_work + paragraph.text + ' '
        text_of_work.replace('\n', ' ')
        author_re = re.search(re.compile(surname + "\s+\w+\s+\w+\s"), text_of_work)
        if author_re is None:
            print("Error while parsing author name")
            continue

        author = author_re[0].replace('\n', '')
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = re.search(re.compile(surname + "\s+(.+)\("), li.text)[1]

        print("Removing tmp text " + text_tmp_name)
        os.remove(TEXT_PATH + text_tmp_name)
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Downloading text " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Достаем слайды
        slides_anchor = li.find('a', text='Презентация')
        slides_filename = ''
        if slides_anchor is not None:
            slides_uri = slides_anchor.get('href')
            slides_extension = splitext(slides_uri)[1]
            slides_filename = get_slides_filename(author_en, year, slides_extension)
            print("Download slides: " + slides_filename)
            download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Достаем отзыв научника
        supervisor_review_anchor = li.find('a', text='Отзыв')
        supervisor_review_filename = ''
        if supervisor_review_anchor is not None:
            supervisor_review_uri = supervisor_review_anchor.get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                      'supervisor': supervisor, 'publish_year': year,
                      'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

    # Парсинг 371 группы
    for li in uls[1].find_all('li'):
        surname = li.find('b').text.split('.')[-1].replace(' ', '')

        anchors = li.find_all('a')
        # Достаем научника
        supervisor = get_supervisor_from_text(li.text)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue
        print("Supervisor " + supervisor)

        # Достаем текст
        text_anchor = li.find('a', text='Отчёт')
        text_uri = text_anchor.get('href')
        text_extension = splitext(text_uri)[-1]
        text_tmp_name = get_text_filename(surname, year, text_extension)
        print("Download tmp text: " + text_tmp_name)
        download_file(url + "/" + text_uri, text_tmp_name, TEXT_PATH)

        # Достаем имя студента из текста
        text_of_work = ''
        if text_extension.find('.pdf', 0) > -1:
            text_of_work = high_level.extract_text(TEXT_PATH + text_tmp_name)
        elif text_extension.find('.doc', 0) > -1 or text_extension.find('.docx', 0) > -1:
            document = docx.Document(TEXT_PATH + text_tmp_name)
            for paragraph in document.paragraphs:
                text_of_work = text_of_work + paragraph.text + ' '
        text_of_work.replace('\n', ' ')
        author_re = re.search(re.compile(surname + "\s+\w+\s+\w+\s"), text_of_work)
        if author_re is None:
            print("Error while parsing author name")
            continue

        author = author_re[0].replace('\n', '')
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = re.search(re.compile(surname + "\s+(.+)\("), li.text)[1]

        print("Removing tmp text " + text_tmp_name)
        os.remove(TEXT_PATH + text_tmp_name)
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Downloading text " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Достаем слайды
        slides_anchor = li.find('a', text='Презентация')
        slides_filename = ''
        if slides_anchor is not None:
            slides_uri = slides_anchor.get('href')
            slides_extension = splitext(slides_uri)[1]
            slides_filename = get_slides_filename(author_en, year, slides_extension)
            print("Download slides: " + slides_filename)
            download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Достаем отзыв научника
        supervisor_review_anchor = li.find('a', text='Отзыв')
        supervisor_review_filename = ''
        if supervisor_review_anchor is not None:
            supervisor_review_uri = supervisor_review_anchor.get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 2, 'name_ru': name, 'author': author,
                      'supervisor': supervisor, 'publish_year': year,
                      'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

def get_2014():
    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/2014/list'
    year = 2014

    response = session.get(url)

    if response.status_code != 200:
        print("Response status " + str(response.status_code))
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")
    uls = soup.find('h3', text='344 группа').parent.find_all('ul')

    # Парсинг 344 группы
    for li in uls[0].find_all('li'):
        surname = li.find('b').text.split('.')[-1].replace(' ', '')

        anchors = li.find_all('a')
        # Достаем научника
        supervisor = get_supervisor_from_text(re.search(r"\((.+)\)", li.text)[1])

        if supervisor == '':
            print("Error while parsing supervisor")
            continue
        print("Supervisor " + supervisor)

        # Достаем текст
        text_anchor = li.find('a', text='Отчёт')
        text_uri = text_anchor.get('href')
        text_extension = splitext(text_uri)[-1]
        text_tmp_name = get_text_filename(surname, year, text_extension)
        print("Download tmp text: " + text_tmp_name)
        download_file(url + "/" + text_uri, text_tmp_name, TEXT_PATH)

        # Достаем имя студента из текста
        author = li.find('b').text.lstrip()
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = re.search(r"\s+(.+)\(", li.text)[1]

        print("Removing tmp text " + text_tmp_name)
        os.remove(TEXT_PATH + text_tmp_name)
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Downloading text " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Достаем слайды
        slides_anchor = li.find('a', text='Презентация')
        slides_filename = ''
        if slides_anchor is not None:
            slides_uri = slides_anchor.get('href')
            slides_extension = splitext(slides_uri)[1]
            slides_filename = get_slides_filename(author_en, year, slides_extension)
            print("Download slides: " + slides_filename)
            download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Достаем отзыв научника
        supervisor_review_anchor = li.find('a', text='Отзыв')
        supervisor_review_filename = ''
        if supervisor_review_anchor is not None:
            supervisor_review_uri = supervisor_review_anchor.get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                      'supervisor': supervisor, 'publish_year': year,
                      'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

    # Парсинг 371 группы
    for li in uls[1].find_all('li'):
        surname = li.find('b').text.split('.')[-1].replace(' ', '')

        anchors = li.find_all('a')
        # Достаем научника
        supervisor = get_supervisor_from_text(re.search(r"\((.+)\)", li.text)[1])

        if supervisor == '':
            print("Error while parsing supervisor")
            continue
        print("Supervisor " + supervisor)

        # Достаем текст
        text_anchor = li.find('a', text='Отчёт')
        text_uri = text_anchor.get('href')
        text_extension = splitext(text_uri)[-1]
        text_tmp_name = get_text_filename(surname, year, text_extension)
        print("Download tmp text: " + text_tmp_name)
        download_file(url + "/" + text_uri, text_tmp_name, TEXT_PATH)

        # Достаем имя студента из текста
        author = li.find('b').text.lstrip()
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = re.search(r"\s+(.+)\(", li.text)[1]

        print("Removing tmp text " + text_tmp_name)
        os.remove(TEXT_PATH + text_tmp_name)
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Downloading text " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Достаем слайды
        slides_anchor = li.find('a', text='Презентация')
        slides_filename = ''
        if slides_anchor is not None:
            slides_uri = slides_anchor.get('href')
            slides_extension = splitext(slides_uri)[1]
            slides_filename = get_slides_filename(author_en, year, slides_extension)
            print("Download slides: " + slides_filename)
            download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Достаем отзыв научника
        supervisor_review_anchor = li.find('a', text='Отзыв')
        supervisor_review_filename = ''
        if supervisor_review_anchor is not None:
            supervisor_review_uri = supervisor_review_anchor.get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 2, 'name_ru': name, 'author': author,
                      'supervisor': supervisor, 'publish_year': year,
                      'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

    # Парсинг 444 группы
    for li in uls[2].find_all('li'):
        surname = li.find('b').text.split('.')[-1].replace(' ', '')

        anchors = li.find_all('a')
        # Достаем научника
        supervisor = get_supervisor_from_text(re.search(r"\((.+)\)", li.text)[1])

        if supervisor == '':
            print("Error while parsing supervisor")
            continue
        print("Supervisor " + supervisor)

        # Достаем текст
        text_anchor = li.find('a', text='Отчёт')
        text_uri = text_anchor.get('href')
        text_extension = splitext(text_uri)[-1]
        text_tmp_name = get_text_filename(surname, year, text_extension)
        print("Download tmp text: " + text_tmp_name)
        download_file(url + "/" + text_uri, text_tmp_name, TEXT_PATH)

        # Достаем имя студента из текста
        author = li.find('b').text.lstrip()
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = re.search(r"\s+(.+)\(", li.text)[1]

        print("Removing tmp text " + text_tmp_name)
        os.remove(TEXT_PATH + text_tmp_name)
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Downloading text " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Достаем слайды
        slides_anchor = li.find('a', text='Презентация')
        slides_filename = ''
        if slides_anchor is not None:
            slides_uri = slides_anchor.get('href')
            slides_extension = splitext(slides_uri)[1]
            slides_filename = get_slides_filename(author_en, year, slides_extension)
            print("Download slides: " + slides_filename)
            download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Достаем отзыв научника
        supervisor_review_anchor = li.find('a', text='Отзыв')
        supervisor_review_filename = ''
        if supervisor_review_anchor is not None:
            supervisor_review_uri = supervisor_review_anchor.get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                      'supervisor': supervisor, 'publish_year': year,
                      'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)


def get_2013():
    session = requests.session()
    url = 'https://oops.math.spbu.ru/SE/YearlyProjects/2013/list'
    year = 2013

    response = session.get(url)

    if response.status_code != 200:
        print("Response status " + str(response.status_code))
        sys.exit(0)

    soup = BeautifulSoup(response.text, "lxml")
    uls = soup.find('h3', text='341 группа').parent.find_all('ul')

    # Парсинг 341 группы
    for li in uls[0].find_all('li'):
        surname = li.find('b').text.split('.')[-1].replace(' ', '')

        anchors = li.find_all('a')

        # Достаем текст
        text_anchor = li.find('a', text='Отчёт')
        text_uri = text_anchor.get('href')
        text_extension = splitext(text_uri)[-1]
        text_tmp_name = get_text_filename(surname, year, text_extension)
        print("Download tmp text: " + text_tmp_name)
        download_file(url + "/" + text_uri, text_tmp_name, TEXT_PATH)

        # Достаем имя студента из текста
        author = li.find('b').text.lstrip()
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = re.search(re.compile(author + "\s+(.+)"), li.text)[1]
        print("Work name " + name)

        print("Removing tmp text " + text_tmp_name)
        if download:
            os.remove(TEXT_PATH + text_tmp_name)
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Downloading text " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Достаем научника
        supervisor = get_supervisor_from_file(TEXT_PATH + text_filename)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue
        print("Supervisor " + supervisor)

        # Достаем слайды
        slides_anchor = li.find('a', text='Презентация')
        slides_filename = ''
        if slides_anchor is not None:
            slides_uri = slides_anchor.get('href')
            slides_extension = splitext(slides_uri)[1]
            slides_filename = get_slides_filename(author_en, year, slides_extension)
            print("Download slides: " + slides_filename)
            download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Достаем отзыв научника
        supervisor_review_anchor = li.find('a', text='Отзыв')
        supervisor_review_filename = ''
        if supervisor_review_anchor is not None:
            supervisor_review_uri = supervisor_review_anchor.get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                      'supervisor': supervisor, 'publish_year': year,
                      'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

        # Парсинг 344 группы
        for li in uls[1].find_all('li'):
            surname = li.find('b').text.split('.')[-1].replace(' ', '')

            anchors = li.find_all('a')
            # Достаем текст
            text_anchor = li.find('a', text='Отчёт')
            text_uri = text_anchor.get('href')
            text_extension = splitext(text_uri)[-1]
            text_tmp_name = get_text_filename(surname, year, text_extension)
            print("Download tmp text: " + text_tmp_name)
            download_file(url + "/" + text_uri, text_tmp_name, TEXT_PATH)

            # Достаем имя студента из текста
            author = li.find('b').text.lstrip()
            author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
            name = re.search(re.compile(author + "\s+(.+)"), li.text)[1]
            print("Work name " + name)

            print("Removing tmp text " + text_tmp_name)
            if download:
                os.remove(TEXT_PATH + text_tmp_name)
            text_filename = get_text_filename(author_en, year, text_extension)
            print("Downloading text " + text_filename)
            download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

            # Достаем научника
            supervisor = get_supervisor_from_file(TEXT_PATH + text_filename)

            if supervisor == '':
                print("Error while parsing supervisor")
                continue
            print("Supervisor " + supervisor)

            # Достаем слайды
            slides_anchor = li.find('a', text='Презентация')
            slides_filename = ''
            if slides_anchor is not None:
                slides_uri = slides_anchor.get('href')
                slides_extension = splitext(slides_uri)[1]
                slides_filename = get_slides_filename(author_en, year, slides_extension)
                print("Download slides: " + slides_filename)
                download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

            # Достаем отзыв научника
            supervisor_review_anchor = li.find('a', text='Отзыв')
            supervisor_review_filename = ''
            if supervisor_review_anchor is not None:
                supervisor_review_uri = supervisor_review_anchor.get('href')
                supervisor_review_extension = splitext(supervisor_review_uri)[1]
                supervisor_review_filename = get_supervisor_review_filename(author_en, year,
                                                                            supervisor_review_extension)
                print("Download supervisor review: " + supervisor_review_filename)
                download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

            # Генерируем метаинформацию и загружаем
            thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                           'supervisor': supervisor, 'publish_year': year,
                           'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

            upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

    # Парсинг 361 группы
    for li in uls[2].find_all('li'):
        surname = li.find('b').text.split('.')[-1].replace(' ', '')

        anchors = li.find_all('a')
        # Достаем текст
        text_anchor = li.find('a', text='Отчёт')
        text_uri = text_anchor.get('href')
        text_extension = splitext(text_uri)[-1]
        text_tmp_name = get_text_filename(surname, year, text_extension)
        print("Download tmp text: " + text_tmp_name)
        download_file(url + "/" + text_uri, text_tmp_name, TEXT_PATH)

        # Достаем имя студента из текста
        author = li.find('b').text.lstrip()
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = re.search(re.compile(author + "\s+(.+)"), li.text)[1]
        print("Work name " + name)

        print("Removing tmp text " + text_tmp_name)
        if download:
            os.remove(TEXT_PATH + text_tmp_name)
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Downloading text " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Достаем научника
        supervisor = get_supervisor_from_file(TEXT_PATH + text_filename)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue
        print("Supervisor " + supervisor)

        # Достаем слайды
        slides_anchor = li.find('a', text='Презентация')
        slides_filename = ''
        if slides_anchor is not None:
            slides_uri = slides_anchor.get('href')
            slides_extension = splitext(slides_uri)[1]
            slides_filename = get_slides_filename(author_en, year, slides_extension)
            print("Download slides: " + slides_filename)
            download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Достаем отзыв научника
        supervisor_review_anchor = li.find('a', text='Отзыв')
        supervisor_review_filename = ''
        if supervisor_review_anchor is not None:
            supervisor_review_uri = supervisor_review_anchor.get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Генерируем метаинформацию и загружаем
        # TODO: попросить у зеленчука добавить 361 группу в бд и поменять course_id
        thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                      'supervisor': supervisor, 'publish_year': year,
                      'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)

    # Парсинг 445 группы
    for li in uls[3].find_all('li'):
        surname = li.find('b').text.split('.')[-1].replace(' ', '')

        anchors = li.find_all('a')
        # Достаем текст
        text_anchor = li.find('a', text='Отчёт')
        text_uri = text_anchor.get('href')
        text_extension = splitext(text_uri)[-1]
        text_tmp_name = get_text_filename(surname, year, text_extension)
        print("Download tmp text: " + text_tmp_name)
        download_file(url + "/" + text_uri, text_tmp_name, TEXT_PATH)

        # Достаем имя студента из текста
        author = li.find('b').text.lstrip()
        author_en = translit(author, 'ru', reversed=True).replace(" ", "_")
        name = re.search(re.compile(author + "\s+(.+)"), li.text)[1]
        print("Work name " + name)

        print("Removing tmp text " + text_tmp_name)
        if download:
            os.remove(TEXT_PATH + text_tmp_name)
        text_filename = get_text_filename(author_en, year, text_extension)
        print("Downloading text " + text_filename)
        download_file(url + "/" + text_uri, text_filename, TEXT_PATH)

        # Достаем научника
        supervisor = get_supervisor_from_file(TEXT_PATH + text_filename)

        if supervisor == '':
            print("Error while parsing supervisor")
            continue
        print("Supervisor " + supervisor)

        # Достаем слайды
        slides_anchor = li.find('a', text='Презентация')
        slides_filename = ''
        if slides_anchor is not None:
            slides_uri = slides_anchor.get('href')
            slides_extension = splitext(slides_uri)[1]
            slides_filename = get_slides_filename(author_en, year, slides_extension)
            print("Download slides: " + slides_filename)
            download_file(url + "/" + slides_uri, slides_filename, SLIDES_PATH)

        # Достаем отзыв научника
        supervisor_review_anchor = li.find('a', text='Отзыв')
        supervisor_review_filename = ''
        if supervisor_review_anchor is not None:
            supervisor_review_uri = supervisor_review_anchor.get('href')
            supervisor_review_extension = splitext(supervisor_review_uri)[1]
            supervisor_review_filename = get_supervisor_review_filename(author_en, year, supervisor_review_extension)
            print("Download supervisor review: " + supervisor_review_filename)
            download_file(url + "/" + supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

        # Генерируем метаинформацию и загружаем
        thesis_info = {'type_id': 2, 'course_id': 1, 'name_ru': name, 'author': author,
                      'supervisor': supervisor, 'publish_year': year,
                      'secret_key': 'e789ec3741a6bd9f2d18c2dd6c074dda'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)


if __name__ == '__main__':
    get_2013()
    # get_2014()
    # get_2015_spring()
    # get_2015_fall()
    # get_2016_reports()
    # get_2017_reports()

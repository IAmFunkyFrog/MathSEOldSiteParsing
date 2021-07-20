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
    'Белогрудов',
    'Суворов',
    'Минкин',
    'Бугайченко',
    'Полозов',
    'Осечкина',
    'Дыдычкин'
)

# Флаг скачки файлов с сайта
download = True

# Флаг загрузки файлов на сайт
UPLOAD_FLAG = True


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
            print("Error while parsing .doc")
            return ''
        except ValueError:
            print("Error while parsing .doc - it is not .doc or .docx")
            return ''
        except:
            print("Error while parsing .doc - Mb file is corrupted")
            return ''
        for paragraph in document.paragraphs:
            text_of_work = text_of_work + paragraph.text + ' '
    text_of_work = text_of_work.replace('\n', ' ')
    return get_supervisor_from_text(text_of_work)


def upload_on_site(thesis_info, text_filename, slides_filename='', supervisor_review_filename=''):
    print(thesis_info)

    if not UPLOAD_FLAG:
        print("Upload on site disabled")
        return

    report_text = TEXT_PATH + text_filename
    files = [
        ('thesis_text', (report_text, open(report_text, 'rb'), 'application/octet')),
        ('thesis_info', ('thesis_info', json.dumps(thesis_info), 'application/json')),
    ]

    if slides_filename != '':
        presentation = SLIDES_PATH + slides_filename
        files.append(('presentation', (presentation, open(presentation, 'rb'), 'application/octet')))

    if supervisor_review_filename != '':
        supervisor_review = SUPERVISOR_REVIEW_PATH + supervisor_review_filename
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
                       'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                       'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                       'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                       'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                       'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                       'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                      'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                      'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
        name = re.search(re.compile(author + "\s+(.+)\("), li.text)[1]

        print("Removing tmp text " + text_tmp_name)
        if download:
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
                      'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
        name = re.search(re.compile(author + "\s+(.+)\("), li.text)[1]

        print("Removing tmp text " + text_tmp_name)
        if download:
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
                      'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
        name = re.search(re.compile(author + "\s+(.+)\("), li.text)[1]

        print("Removing tmp text " + text_tmp_name)
        if download:
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
                      'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                      'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                           'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
        thesis_info = {'type_id': 2, 'course_id': 100500, 'name_ru': name, 'author': author,
                      'supervisor': supervisor, 'publish_year': year,
                      'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

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
                      'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'}

        upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)


def upload_one_report(thesis_info, text_uri, slides_uri = '', supervisor_review_uri = ''):
    if text_uri == '':
        print("Invalid text_uri")
        return

    year = thesis_info['publish_year']
    author = thesis_info['author']
    author_en = translit(author, 'ru', reversed=True).replace(" ", "_")

    text_extension = '.' + text_uri.split('.')[-1]
    text_filename = get_text_filename(author_en, year, text_extension)
    download_file(text_uri, text_filename, TEXT_PATH)

    slides_filename = ''
    if slides_uri != '':
        slides_extension = slides_uri.split('.')[-1]
        slides_filename = get_slides_filename(author_en, year, text_extension)
        download_file(slides_uri, slides_filename, SLIDES_PATH)
    supervisor_review_filename = ''
    if supervisor_review_uri != '':
        supervisor_review_extension = supervisor_review_uri.split('.')[-1]
        supervisor_review_filename = get_supervisor_review_filename(author_en, year, text_extension)
        download_file(supervisor_review_uri, supervisor_review_filename, SUPERVISOR_REVIEW_PATH)

    upload_on_site(thesis_info, text_filename, slides_filename, supervisor_review_filename)



# скрипт загрузки проблемных работ, которые не удалось просто распарсить
def bruteforce_2012():
    # 2012 год
    # 341 группа
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Разработка 3D пиксельного движка', 'author': 'Осипов Никита Алексеевич',
         'supervisor': 'Оносовский', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/341_Osipov_report.doc',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/341_Osipov_review.pdf'
    )
    # 345 группа
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Фреймворки юнит-тестирования для С++',
         'author': 'Бажутин Михаил Сергеевич',
         'supervisor': 'Литвинов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Bazhutin_report.doc',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Bazhutin_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': '. Разработка 3D пиксельного графического движка',
         'author': 'Байцерова Юлия Сергеевна',
         'supervisor': 'Оносовский', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Baytserova_report.docx',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Baytserova_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Baytserova_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Терминальный Android-клиент для распределенных приложений на базе платформы Ubiq Mobile',
         'author': 'Бумаков Никита Вячеславович',
         'supervisor': 'Оносовский', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Bumakov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Bumakov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Bumakov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Статический анализ кода языка Ruby',
         'author': 'Денисов Юрий Борисович',
         'supervisor': 'Ушаков', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Denison_report.doc',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Denison_review.png'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Визуальный язык задания ограничений на модели в QReal',
         'author': 'Дерипаска Анна Олеговна',
         'supervisor': 'Литвинов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Deripaska_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Deripaska_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Deripaska_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Структура хранения индексов закэшированных страйпов и ссылок на них',
         'author': 'Дудин виктор Дмитриевич',
         'supervisor': 'Короткевич', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Dudin_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Dudin_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Dudin_review.jpg'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Разработка средства проверки корректности адресов возврата на платформе S2E',
         'author': 'Евард Вадим Евгеньевич',
         'supervisor': 'Зеленчук', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Evard_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Evard_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Evard_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Реализация механизмов виртуальной памяти для x86 архитектуры в ОСРВ Embox',
         'author': 'Ефимов Глеб Дмитриевич',
         'supervisor': 'Бондарев', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Efimov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Efimov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Efimov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Определение расстояния между точкой и множеством, представленным бинарной диаграммой решений',
         'author': 'Зубаревич Дмитрий Александрович',
         'supervisor': 'Бугайченко', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Zubarevich_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Zubarevich_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Zubarevich_review.docx'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Алгоритмы расчета RAID 6',
         'author': 'Калмук Александр Игоревич',
         'supervisor': 'Короткевич', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Kalmuk_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Kalmuk_review.jpg'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Инструмент для оценки алгоритмов дедупликации',
         'author': 'Кладов Алексей Александрович',
         'supervisor': 'Луцив', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Kladov_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Kladov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Трассировки ОСРВ Embox',
         'author': 'Крамар Алина Сергеевна',
         'supervisor': 'Бондарев', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Kramar_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Kramar_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Поддержка механизма рефакторингов в metaCASE-системе QReal',
         'author': 'Кузенкова Анастасия Сергеевна',
         'supervisor': 'Литвинов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Kuzenkova_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Kuzenkova_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Реализация алгоритмов расчета RAID 6 с использованием встроенных функций SSE',
         'author': 'Макулов Рустам Наилевич',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Makulov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Makulov_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Makulov_review.jpg'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Переиспользование кода в визуальных языках программирования',
         'author': 'Нефёдов Ефим Андреевич',
         'supervisor': 'Литвинов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Nefedov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Nefedov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Nefedov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Исследование и тестирование семплирующего метода профайлинга на примере профилировщика производительности Intel VTune Amplifier XE 2011',
         'author': 'Одеров Роман Сергеевич',
         'supervisor': 'Баклановский', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Oderov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Oderov_presentation.pptx',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Средства описания генераторов кода для предметно-ориентированных решений в metaCASE-средстве QReal',
         'author': 'Подкопаев Антон Викторович',
         'supervisor': ' Брыксин', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Podkopaev_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Podkopaev_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Podkopaev_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Интерпретация метамоделей в metaCASE-системе QReal',
         'author': 'Птахина Алина Ивановна',
         'supervisor': 'Литвинов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Ptakhina_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Ptakhina_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Ptakhina_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Модуль сбора информации о производительности процессоров Intel с использованием PMU для профайлера ядра ОС MS WS2008R2',
         'author': 'Серко Сергей Анатольевич',
         'supervisor': 'Баклановский', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Serko_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Serko_presentation.pdf',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Юзабилити в проекте QReal:Robots',
         'author': 'Соковикова Наталья Алексеевна',
         'supervisor': 'Литвинов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Sokovikova_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Sokovikova_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Sokovikova_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Исследование эффективности дедупликации с использованием цепочек преобразований при помощи разработанного инструментального средства',
         'author': 'Соса Укатерина Андреевна',
         'supervisor': 'Луцив', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Sosa_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Sosa_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Архитектура и прототипирование metaCASE-системы',
         'author': 'Таран Кирилл Сергеевич',
         'supervisor': 'Брыксин', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Taran_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Taran_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Taran_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Алгоритмы расчёта RAID 6',
         'author': 'Тюшев Кирилл Игоревич',
         'supervisor': 'Короткевич', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Tyushev_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Tyushev_review.jpg'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Реализация уровня изоляции Read Committed для древовидных структур данных',
         'author': 'Федотовский Павел Валерьевич',
         'supervisor': 'Чернышев', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Fedotovskij_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Fedotovskij_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Fedotovskij_review.docx'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Выделение научных сообществ на основе анализа библиографических данных',
         'author': 'Филатов Владимир Константинович',
         'supervisor': 'Суворов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Filatov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Ibragimov_Filatov_presentation.pdf',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Сравнение распределителей памяти для многопоточного обработчика транзакций',
         'author': 'Чередник Кирилл Евгеньевич',
         'supervisor': 'Смирнов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Cherednik_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/345/345_Cherednik_review.doc'
    )
    # 361 группа
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Поисковые алгоритмы на блоке графического процессора',
         'author': 'Алексеев Илья Владимирович',
         'supervisor': 'Губанов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Alekseev_report.docx',
        slides_uri='',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Разработка редактора диаграмм для облачной технологии создания мобильных приложений',
         'author': 'Белокуров Дмитрий Николаевич',
         'supervisor': 'Брыксин', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Belokurov_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Belokurov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Обзор реализации механизма циклической разработки диаграмм классов и программного кода в современных UML-средствах',
         'author': '',
         'supervisor': 'Кознов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Стабилизация показаний G-сенсора при помощи камеры',
         'author': 'Говейнович Сергей Геннадьевич',
         'supervisor': 'Оносовский', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Goveynovich_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Goveynovich_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Разработка сети простых вычислительных процессоров и фильтра в рамках студенческого проекта МПВ',
         'author': '',
         'supervisor': 'Кривошеин', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Zabranskiy_review.docx'
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Разработка трехмерного игрового движка для игры под Android',
         'author': 'Зольников Павел Евгеньевич',
         'supervisor': 'Оносовский', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Zolnikov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Zolnikov_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Zolnikov_review.docx'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Создание подсистемы управления рисками: разработка бизнес-логики подсистемы',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Выделение научных сообществ на основе анализа библиографических данных',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Анализ тональности текста',
         'author': 'Калмыков Алексей Владимирович',
         'supervisor': 'Губанов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Kalmykov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Kalmykov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Kalmykov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Создание информационной подсистемы для распределенной подготовки стартапа',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': ' Реализация эвристик языка ДРАКОН в metaCASE-средстве QReal',
         'author': 'Колантаевская Анна Сергеевна',
         'supervisor': 'Брыксин', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Kolantaevskaya_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Kolantaevskaya_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': ' Тиражирование мобильных приложений для платформы iOS и Android',
         'author': 'Коршаков Степан Андреевич',
         'supervisor': 'Сабашный', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Korshakov_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Korshakov_review.doc'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Оценка сайта на наличие нежелательного контента',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Разработка интерфейса программирования приложений и добавление скриптовой функциональности для ПО криминалистического анализа',
         'author': 'Макеев Давид Александрович',
         'supervisor': 'Губанов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Makeev_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Makeev_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Выделение человека на изображении',
         'author': 'Монькин Александр Александрович',
         'supervisor': 'Петров', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Monkin_S_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Monkin_S_review.jpeg'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Вычисление объема трехмерного объекта в задаче планирования хирургической операции',
         'author': 'Монькин Сергей Александрович',
         'supervisor': 'Петров', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Monkin_S_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Monkin_S_review.jpeg'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Трехмерная модель робота в QReal:Robots',
         'author': 'Павлов Сергей Николаевич',
         'supervisor': 'Брыксин', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Pavlov_report.pdf',
        slides_uri='',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Выделение групп пользователей в социальных сетях',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Реализация модулей ввода/вывода ПВП в связке с ядром DSP48E в рамках проекта МПВ',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Верификация дизассемблера x86-64',
         'author': 'Тенсин Егор Дмитриевич',
         'supervisor': 'Баклановский', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Tensin_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/361/361_Tensin_presentation.pdf',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Разработка модуля памяти для многоядерного потокового вычислителя',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': ' Транслятор микрокода для многоядерного потокового вычислителя',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Создание подсистемы управления рисками: разработка архитектуры подсистемы',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Создание генератора GLR трансляторов для .NET',
         'author': 'Авдюхин Дмитрий Алексеевич',
         'supervisor': 'Кириленко', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Avdyukhin_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Avdyukhin_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Организация надежных соединений через виртуальные каналы',
         'author': 'Бурдун Егор Федорович',
         'supervisor': 'Бондарев', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Burdun_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Burdun_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Алгоритм построения оценок весов интентов для многозначных запросов',
         'author': 'Григорьев Артем Валерьевич',
         'supervisor': 'Грауэр', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Grigoriev_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Grigoriev_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Grigoriev_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Обучение информатике в школах и ВУЗах на примере ОСРВ Embox',
         'author': 'Дзендик Дарья Анатольевна',
         'supervisor': 'Бондарев', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Dzendzik_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Dzendzik_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Dzendzik_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Распознавание языка жестов на видео потоке',
         'author': 'Землянская Светлана Андреевна',
         'supervisor': 'Граничин', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Zemlyanskaya_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Zemlyanskaya_presentation.ppt',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Zemlyanskaya_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Генерация кода для платформы Ubiq Mobile',
         'author': 'Иванов Всеволод Юрьевич',
         'supervisor': 'Литвинов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Ivanov_report.docx',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Ivanov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Программная платформа для встраиваемых решений',
         'author': 'Козлов Антон Павлович',
         'supervisor': 'Бондарев', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Kozlov_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Kozlov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Повышение прозрачности сайта госзакупок РФ',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    )  # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Оптимизация вычислений за счет эффективных структур данных в ОС Embox',
         'author': 'Мальковский Николай Владимирович',
         'supervisor': 'Бондарев', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Malkovsky_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Malkovsky_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Malkovsky_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Механизм автоматической генерации мигратора базы данных информационной системы при изменениях модели предметной области',
         'author': 'Михайлов Дмитрий Петрович',
         'supervisor': 'Нестеров', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Mikhaylov_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Mikhaylov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Реализация настраиваемого графического представления элемента на диаграмме в QReal',
         'author': 'Мордвинов Дмитрий Александрович',
         'supervisor': 'Брыксин', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Mordvinov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Mordvinov_presentation.ppt',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Mordvinov_review.doc'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Реализация алгоритма Semi-Global Matching',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Статическая верификация для языка HaSCoL',
         'author': 'Найданов Дмитрий Геннадьевич',
         'supervisor': 'Медведев', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Naydanov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Naydanov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Naydanov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Реализация поддержки диалектов в YaccConstructor/YARD',
         'author': '',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Восстановление адресного пространства процесса из расширенного образа памяти на платформе Windows',
         'author': 'Овчинников Антон Андреевич',
         'supervisor': 'Губанов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Ovchinnikov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Ovchinnikov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Ovchinnikov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Разработка системы для мониторинга и анализа ботнетов, распространяемых через веб приложения',
         'author': 'Перевалова Марина Андреевна',
         'supervisor': 'Зеленчук', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Perevalova_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Perevalova_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Задача верификации лица на основе 3D модели',
         'author': 'Петров Николай Сергеевич',
         'supervisor': '', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Petrov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Petrov_presentation.ppt',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Petrov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Средства создания визуальных интерпретаторов диаграмм в системе QReal',
         'author': 'Поляков Владимир Александрович',
         'supervisor': 'Брыксин', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Polyakov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Polyakov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Polyakov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': ' Восстановление адресного пространства процесса из образа памяти с использованием файла подкачки на платформе Linux',
         'author': 'Свидерский Павел Юрьевич',
         'supervisor': 'Ãóáàíîâ', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Sviderski_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Sviderski_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Построение трёхмерной модели головы на основе трёхмерных анатомических признаков',
         'author': 'Серебряков Сергей Николаевич',
         'supervisor': 'Петров', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Serebryakov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Serebryakov_presentation.ppt',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Serebryakov_review.jpg'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Инструмент анализа пользовательских логов поисковых систем',
         'author': 'Солозобов Андрей Сергеевич',
         'supervisor': 'Грауэр', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Solozobov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Solozobov_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Solozobov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Система мониторинга веб-сервисов',
         'author': 'Фефелов Алексей Андреевич',
         'supervisor': 'Строкан', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Fefelov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Fefelov_review.pdf',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': '3D Registration',
         'author': 'Фоменко Екатерина Сергеевна',
         'supervisor': 'Пименов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Fomenko_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Fomenko_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Проектирование и реализация облачной metaCASE системы',
         'author': 'Чижова Надежда Александровна',
         'supervisor': 'Литвинов', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Chizhova_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Chizhova_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Chizhova_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Практическая оценка качества различных средств HLS при синтезе из SystemC',
         'author': 'Шеин Роман Евгеньевич',
         'supervisor': 'Салищев', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Shein_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Shein_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': 'Автоматическое тестирование верстки web-интерфейсов',
         'author': 'Шувалов Иннокентий Петрович',
         'supervisor': 'Ерошенко', 'publish_year': 2012,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Shuvalov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Shuvalov_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2012/YearlyProjects/2012/445/445_Shuvalov_review.pdf'
    )


def bruteforce_2011():
    # 345 группа
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Синтаксический анализатор языка С',
         'author': 'Авдюхин Дмитрий Алексеевич',
         'supervisor': 'Кириленко', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Avdyukhin_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Avdyukhin_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Avdyukhin_review.odt'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Организация надёжных соединений через виртуальные каналы',
         'author': 'Бурдун Фёдор Викторович',
         'supervisor': 'Бондарев', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Burdun_report.pdf',
        slides_uri='',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Burdun_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Замена цвета выбранного элемента одежды в видеопотоке',
         'author': 'Григорьев Артем Валерьевич',
         'supervisor': 'Жуков', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Grigoryev_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Grigoryev_presentation.ppt',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Grigoryev_review.doc'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Графическая подсистема ОСРВ Embox для роботов LEGO Mindstorms NXT 2.0',
         'author': 'Дзендзик Дарья Анатольевна',
         'supervisor': 'Бондарев', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Dzendzik_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Dzendzik_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Dzendzik_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Фрактальный анализ рынка',
         'author': 'Землянская Светлана Андреевна',
         'supervisor': 'Ширяев', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Zemlyanskaya_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Zemlyanskaya_presentation.ppt',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Zemlyanskaya_review.jpg'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Алгоритмы вытеснения кэша. Применение алгоритмов в СХД и поиск возможностей их оптимизации для современных приложений.',
         'author': 'Колобов Роман Евгеньевич',
         'supervisor': 'Платонов', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Kolobov_report.doc',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Kolobov_presentation.odp',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Помехоустойчивое свёрточное кодирование',
         'author': 'Коноплёв Юрий Михайлович',
         'supervisor': 'Татищев', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Konoplyov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Konoplyov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Konoplyov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Оптимизация потоков для операционной системы Embox',
         'author': 'Мальковский Николай Владимирович',
         'supervisor': 'Бондарев', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Malkovsky_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Malkovsky_presentation.pdf',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Разработка декомпилятора языка Java SE 6',
         'author': 'Михайлов Дмитрий Петрович',
         'supervisor': 'Шафиров', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Mikhailov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Mikhailov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Mikhailov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Применение алгоритмов SuperResolution к лицам',
         'author': '',
         'supervisor': 'Пименов', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Создание средств визуального сравнения моделей в QReal',
         'author': 'Мордвинов Дмитрий Александрович',
         'supervisor': 'Брыксин', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Mordvinov_report.docx',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Mordvinov_presentation.ppt',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Аппаратное ускорение задачи выравнивания строк на языке HaSCoL',
         'author': 'Найданов Дмитрий Геннадьевич',
         'supervisor': 'Медведев', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Naydanov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Naydanov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Naydanov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Предметно-ориентированное моделирование приложений для платформы Android',
         'author': 'Никонова Ольга Анатольевна',
         'supervisor': 'Брыксин', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Nikonova_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Nikonova_presentation.ppt',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Nikonova_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Внедрение шифрования в систему хранения данных высокой производительности',
         'author': 'Овчинников Антон Андреевич',
         'supervisor': 'Ершов', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Ovchinnikov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Ovchinnikov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Ovchinnikov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Определение положения камеры относительно плоского маркера',
         'author': '',
         'supervisor': 'Вахитов', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    ) # Не хватает отчества на сайте
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Разработка визуального интерпретатора моделей в системе QReal',
         'author': 'Поляков Владимир Александрович',
         'supervisor': 'Брыксин', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Polyakov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Polyakov_presentation.ppt',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Polyakov_review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Обнаружение узлов в сети',
         'author': 'Свидерский Павел Юрьевич',
         'supervisor': 'Смирнов', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Svidersky_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Svidersky_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Svidersky_review.doc'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Восстановление положения объекта известной формы по зашумлённым наблюдениям с помощью видеокамеры',
         'author': 'Серебряков Сергей Николаевич',
         'supervisor': 'Вахитов', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Serebryakov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Serebryakov_presentation.ppt',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345-Serebryakov-review.pdf'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Алгоритмы детектирующие и исправляющие ошибки в системах хранения данных уровня RAID 6',
         'author': 'Солозобов Андрей Сергеевич',
         'supervisor': 'Шевяков', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Solozobov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Solozobov_presentation.pdf',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Solozobov_review.jpg'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Инструменты анализа данных метилирования генов в цепочке ДНК',
         'author': 'Фоменко Екатерина Сергеевна',
         'supervisor': 'Вяххи', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Fomenko_report.doc',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Fomenko_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Fomenko_review.doc'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Библиотека алгоритмов поиска подстрок в тексте с препроцессингом в применении к биоинформатике',
         'author': 'Чижова Надежда Александровна',
         'supervisor': 'Вяххи', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Chizhova_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Chizhova_presentation.pptx',
        supervisor_review_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Chizhova_review.doc'
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Реализация конфигурируемого аппаратного блока для вычисления быстрого преобразования Фурье переменной длины по смешанному основанию с использованием HLS',
         'author': 'Шеин Роман Евгеньевич',
         'supervisor': 'Салищев', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Shein_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Shein_presentation.pdf',
        supervisor_review_uri=''
    )
    upload_one_report(
        {'type_id': 2, 'course_id': 1, 'name_ru': 'Восстановление смазанных или размытых зашумлённых изображений',
         'author': 'Шувалов Иннокентий Петрович',
         'supervisor': 'Вахитов', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Shuvalov_report.pdf',
        slides_uri='https://oops.math.spbu.ru/SE/YearlyProjects/2011/YearlyProjects/2011/345/345_Shuvalov_presentation.odp',
        supervisor_review_uri=''
    )
    # 361 группа
    upload_one_report(
        {'type_id': 2, 'course_id': 100500, 'name_ru': '',
         'author': '',
         'supervisor': '', 'publish_year': 2011,
         'secret_key': '7fa15fc01c79c7378910cd7c6ee6e0f9'},
        text_uri='',
        slides_uri='',
        supervisor_review_uri=''
    )

if __name__ == '__main__':
    bruteforce_2011()
    # bruteforce_2012()
    # get_2013() пока нельзя запускать, надо дождаться добавления нового направления в бд
    # get_2014()
    # get_2015_spring()
    # get_2015_fall()
    # get_2016_reports()
    # get_2017_reports()

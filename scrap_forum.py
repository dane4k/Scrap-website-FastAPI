from sqlalchemy.orm import sessionmaker

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging

from crud import *

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

url = 'https://forum.criminal.ist/'
user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/111.0.0.0 Safari/537.36'}


def get_soup_response(link: str) -> BeautifulSoup | None:
    try:
        response = requests.get(link, headers=user_agent)
        soup = BeautifulSoup(response.text, 'html.parser')
        logging.info(f"Fetched data from {link}")
        return soup
    except requests.RequestException as e:
        logging.error(f"Error while getting info from {link}: {str(e)}")
        return None


def get_boards(link) -> list:
    boards_lst = []
    soup = get_soup_response(link)
    boards = soup.find_all(class_='up_contain')  # разделы
    for board in boards:  # обходим разделы
        board_url = board.find('a').get('href')
        boards_lst.append(board_url)
    logging.info(f"Got all boards list")
    return boards_lst


def get_pages_amount(board: str) -> int:
    board_pages_soup = get_soup_response(board)
    a_nav_page = board_pages_soup.find_all('a', class_='nav_page')
    nav_pages_links = list(set([el.get('href') for el in a_nav_page if 'board' in el.get('href')]))
    if nav_pages_links:
        endings = [int(el[-2]) for el in nav_pages_links]
        total_pages = int(max(endings) / 2 + 1)
    else:
        total_pages = 1
    logging.info(f"Got number of pages for {board}")

    return total_pages


def get_threads(boards_lst: list) -> list:
    threads = []
    subthreads = []

    for board in boards_lst:
        total_pages = get_pages_amount(board)
        for page_number in range(1, total_pages + 1):
            if len(threads) >= 3:  # ограничиваю
                return threads
            page_soup = get_soup_response(f'{board[:-2]}.{(page_number - 1) * 20}')
            page = page_soup.find_all(class_='windowbg')
            if not page:  # если в разделе есть подразделы
                sub_soup = get_soup_response(url)
                sub_page = sub_soup.find_all(class_='up_contain')
                for element in sub_page:
                    subthreads.append(element.find('a').get('href'))
                break
            for element in page:
                thread = element.find('a').get('href')
                thread_normalized = thread[:37] + thread[80:]
                threads.append(thread_normalized)

    for subthread in subthreads:
        threads.append(subthread)
    logging.info(f"Got all threads urls from forum")
    return threads


def insert_threads_data(threads: list):
    for thread in threads:
        post_soup = get_soup_response(thread)
        post_message = " ".join(post_soup.find(class_='post').get_text().split())
        thread_title = post_soup.find(id='top_subject').get_text().strip()
        thread_id = int(float(thread.split('=')[1]))
        add_object(Theme(id_=thread_id, name=thread_title, text=post_message), session)
        logging.info(f"Added theme with id: {thread_id} to Theme table")

    logging.info(f"Filled the Theme table")


def get_thread_pages_amount(topic: str) -> int:
    thread_pages_soup = get_soup_response(topic)
    a_nav_page = thread_pages_soup.find_all('a', class_='nav_page')
    lst = []
    for el in a_nav_page:
        try:
            lst.append(int(el.get_text()))
        except ValueError:
            pass
    if lst:
        logging.info(f"Got number of pages for {topic}. It consists of {max(lst)} pages")
        return max(lst)
    else:
        logging.info(f"Got number of pages for {topic}. It consists of 1 page")
        return 0


def insert_comments_and_authors_data(threads: list):
    comments_ids = set()
    author_ids = set()
    for thread in threads:
        total_pages = get_thread_pages_amount(thread)
        topic_id = int(float(thread.split('=')[1]))
        for page_number in range(1, total_pages + 1):
            post_soup = get_soup_response(f'{thread[:-2]}.{(page_number - 1) * 20}')
            comments_blocks = post_soup.find_all(class_='windowbg')
            for comment in comments_blocks[1:]:
                comment_id = int(comment.get('id').split('msg')[-1])
                comment_author_id = int(comment.find('a').get('href').split('=')[-1])
                try:
                    quote_id = int(comment.find('cite').find('a').get('href').split('=')[-1])
                except AttributeError:
                    quote_id = -1
                comment_text = comment.find(class_='inner').get_text().strip()
                if 'Цитата' in comment_text:
                    comment_text = comment_text.split(':')[-1][2:].strip()

                comment_date = comment.find(class_='smalltext').get_text()
                if 'Сегодня' in comment_date:
                    today = datetime.today()
                    time_parts = comment_date.split("в")
                    time_part = time_parts[1].strip()
                    time_obj = datetime.strptime(time_part, "%H:%M")
                    comment_date = datetime.combine(today, time_obj.time()).strftime("%d.%m.%Y, %H:%M")
                elif 'Вчера' in comment_date:
                    ystrd = datetime.today() - timedelta(days=1)
                    time_parts = comment_date.split("в")
                    time_part = time_parts[1].strip()
                    time_obj = datetime.strptime(time_part, "%H:%M")
                    comment_date = datetime.combine(ystrd, time_obj.time()).strftime("%d.%m.%Y, %H:%M")
                else:
                    try:
                        comment_date_obj = datetime.strptime(comment_date, '%Y-%m-%d %H:%M:%S')
                        comment_date = comment_date_obj.strftime('%d.%m.%Y, %H:%M')
                    except ValueError:
                        comment_date = datetime.strptime(comment_date, '%d.%m.%Y, %H:%M').strftime('%d.%m.%Y, %H:%M')

                date_format = '%d.%m.%Y, %H:%M'
                comment_date = datetime.strptime(str(comment_date), date_format)
                try:
                    comment_likes = int(comment.find_all('a')[-1].get_text().split()[0])
                except Exception:
                    comment_likes = 0

                comment_author_nickname = comment.find('a').get_text()
                if not (comment_id in comments_ids):
                    add_object(Comment(id_=comment_id, theme_id=topic_id, author_id=comment_author_id,
                                       author_name=comment_author_nickname, quote_id=quote_id, text=comment_text,
                                       created=comment_date, likes=comment_likes), session)
                    logging.info(f"Added comment with id: {comment_id} to the Comment table")
                    comments_ids.add(comment_id)
                if not (comment_author_id in author_ids):
                    add_object(Author(id_=comment_author_id, nickname=comment_author_nickname), session)
                    logging.info(f"Added author with id: {comment_author_id} to the Author table")
                    author_ids.add(comment_author_id)

    logging.info(f"Filled the Author and Comment tables")


if __name__ == '__main__':
    engine = create_engine('sqlite:///database.db')
    Base.metadata.create_all(engine)

    session = sessionmaker(bind=engine)()

    boards_list = get_boards(url)  # nado
    threads_list = get_threads(boards_list)  # nado
    insert_threads_data(threads_list)
    insert_comments_and_authors_data(threads_list)

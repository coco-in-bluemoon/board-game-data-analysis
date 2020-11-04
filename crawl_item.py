import json
import math
import os
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm


def initialize_webdriver():
    # Headless Chrome Options
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')

    driver = webdriver.Chrome('./driver/chromedriver', options=options)

    return driver


def get_filenames(base_directory='./data/games'):
    files = os.listdir(base_directory)
    files = sorted(files, key=lambda x: int(re.search(r'[0-9]+', x).group()))
    return files


def update_file(file, driver):
    file_no = re.search(r'[0-9]+', file).group()

    file_input_path = os.path.join('./data/games', file)

    fin = open(file_input_path)

    SAVE_INTERVAL = 2

    json_data = json.load(fin)
    for page in sorted(json_data.keys(), key=lambda x: int(x)):
        updated_items = {page: list()}
        for idx, item in enumerate(json_data[page]):
            item_no = idx+1

            # Check if there is savefile
            item_no_for_savefile =\
                math.ceil(item_no / SAVE_INTERVAL) * SAVE_INTERVAL
            file_output_path =\
                f'./data/ratings/ratings_' +\
                f'{file_no}_{page}_{item_no_for_savefile}.json'

            if os.path.exists(file_output_path):
                continue

            update_item(item, driver)
            updated_items[page].append(item)

            if (not item_no % SAVE_INTERVAL) or\
                    (item_no == len(json_data[page])):
                fout = open(file_output_path, 'w')
                json.dump(updated_items, fout)
                fout.close()
                updated_items = {page: list()}

    fin.close()


def crawl_additional_feature(item, driver):
    link = item['link']

    year = re.search(r'[0-9]+', item['year']).group()
    item['year'] = year

    game_id = re.search('/([0-9]+)/', link).group(1)
    item['id'] = game_id

    title = item['title']

    print(f'[ ] Craw Additional Features: {title}')

    driver.get(link)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    labels = ['player_number', 'playtime', 'age', 'complexity']
    soup_information = soup.select(
        'li.gameplay-item .gameplay-item-primary:nth-child(1)'
    )
    for idx, information in enumerate(soup_information):
        information = information.text.strip()
        information = re.sub(r'[\s]', '', information)
        information = re.search(r'([0-9][0-9\+\–\.]*)', information).group()

        label = labels[idx]
        item[label] = information

    selector_type = '.game-description-classification li:nth-child(1) \
        .feature-description > span'
    soup_type = soup.select(selector_type)

    types = list()
    for information in soup_type:
        information = information.text.strip()
        information = re.sub(',', '', information)
        types.append(information)
    item['type'] = types

    print(f'[*] Craw Additional Features: {title}')


def crawl_rating_feature(item, driver):
    link = item['link']
    title = item['title']

    print(f'[ ] Craw Rating Features: {title}')

    link_rating = f'{link}/ratings'
    driver.get(link_rating)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    soup_num_ratings = soup.select_one('strong.ng-binding')
    num_ratings = soup_num_ratings.text.strip()
    num_ratings = re.sub(',', '', num_ratings)
    ITEM_PER_PAGE = 50
    num_pages = math.ceil(int(num_ratings) / ITEM_PER_PAGE)

    if num_ratings == '999999':
        raise ValueError

    ratings = list()
    for page in tqdm(range(1, num_pages+1)):
        link_rating = f'{link_rating}?pageid={page}'
        driver.get(link_rating)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        soup_ratings = soup.select('.summary-rating-item')
        for soup_rating in soup_ratings:
            soup_rating_number =\
                soup_rating.select_one('.summary-item-callout')      
            rating_number = soup_rating_number.text.strip()
            rating_number = re.sub(r'\s', '', rating_number)

            soup_user = soup_rating.select_one('.comment-header-title a')
            user = soup_user.text.strip()

            soup_review = soup_rating.select_one('.comment-body span')
            review = soup_review.text.strip()
            review = re.sub('[\s]{2,}', ' ', review)

            rating = {
                'rating': rating_number,
                'user': user
            }            
            if review:
                rating['review'] = review

            ratings.append(rating)

    item['rating'] = ratings
    print(f'[*] Craw Rating Features: {title}')


def update_item(item, driver):
    crawl_additional_feature(item, driver)
    try:
        crawl_rating_feature(item, driver)
    except ValueError:
        print('***** ValueError: Restart Rating Feature Crawling *****')
        crawl_rating_feature(item, driver)


if __name__ == "__main__":
    driver = initialize_webdriver()
    files = get_filenames(base_directory='./data/games')

    for file in files:
        print(f'[ ] Update {file}')
        update_file(file, driver)
        print(f'[*] Update {file}\n')

    driver.close()

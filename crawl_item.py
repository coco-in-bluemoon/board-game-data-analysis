import json
import math
import os
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from tqdm import tqdm


def crawl_board_game(item, driver):
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

    labels = ['players', 'playtime', 'age', 'complexity']
    soup_information = soup.select(
        'li.gameplay-item .gameplay-item-primary:nth-child(1)'
    )
    for idx, information in enumerate(soup_information):
        information = information.text.strip()
        information = re.sub(r'[\s]', '', information)
        information = re.search(r'([0-9][0-9\+\–\.]+)', information).group()

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

            ratings.append(review)

    item['rating'] = ratings
    print(f'[*] Craw Rating Features: {title}')
    return item


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument('disable-gpu')

    driver = webdriver.Chrome('./driver/chromedriver', options=options)

    files = sorted(
        os.listdir('./data/games'),
        key=lambda x: int(re.search(r'[0-9]+', x).group())
    )

    for filename in files:
        print(f'{filename}에 데이터를 추가하고 rating을 수집합니다.')
        filename_input = os.path.join('./data/games', filename)
        fin = open(filename_input, 'r')
        json_data = json.load(fin)

        updated_data = dict()
        partition = 0
        for idx, page in enumerate(sorted(json_data.keys())):
            updated_data['page'] = list()
            for item in json_data[page]:
                item_updated = crawl_board_game(item, driver)
                updated_data['page'].append(item_updated)

            if (idx % 4 == 0) or (idx == len(json_data.keys()) - 1):
                filename_output = f'./data/ratings/ratings_{page+1}_{partition+1}.json'
                fout = open(filename_output, 'w')
                json.dump(updated_data, fout)
                fout.close()
                partition += 1
                updated_data = dict()

        fin.close()

    driver.close()

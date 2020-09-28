from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import requests


base_url = 'https://boardgamegeek.com'


def crawl_game(page=1):
    borad_game_url = f'{base_url}/browse/boardgame/page/{page}'
    response = requests.get(borad_game_url)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    board_games = {f'{page}': list()}

    for item in soup.select('#collectionitems #row_'):
        game = dict()

        rank = item.select_one('.collection_rank').text.strip()
        game['rank'] = rank

        link = item.select_one('.collection_thumbnail a').get('href')
        link = base_url + link
        game['link'] = link

        try:
            thumbnail = item.select_one('.collection_thumbnail img').get('src')
            game['thumbnail'] = thumbnail
        except AttributeError:
            pass

        title = item.select_one('.collection_objectname a').text.strip()
        game['title'] = title

        try:
            year = item.select_one('.collection_objectname span').text.strip()
            game['year'] = year
        except AttributeError:
            pass

        try:
            description =\
                item.select_one('.collection_objectname p').text.strip()
            game['description'] = description
        except AttributeError:
            pass

        ratings = item.select('.collection_bggrating')
        assert len(ratings) == 3
        geek_rating, avg_rating, num_voters =\
            [rating.text.strip() for rating in ratings]
        game['geek_rating'] = geek_rating
        game['avg_rating'] = avg_rating
        game['num_voters'] = num_voters

        board_games[f'{page}'].append(game)

    return board_games


if __name__ == "__main__":
    P = 1208
    games = dict()
    file_no = 10
    for page in tqdm(range(901, P+1)):
        game = crawl_game(page=page)
        games.update(game)

        if not page % 100 or page == P:
            file_name = f'./data/games_{file_no}.json'
            with open(file_name, 'w') as f:
                json.dump(games, f)
            print(f'{page} 페이지까지의 게임 정보를 JSON 파일 {file_name} 저장하였습니다.')
            games = dict()
            file_no += 1

import json
import os

import pandas as pd


working_directory = os.getcwd()
filenames = list()
for no in range(2, 25, 2):
    filename =\
        os.path.join(working_directory, f'data/ratings/ratings_1_1_{no}.json')
    filenames.append(filename)

rating_df_full = pd.DataFrame(columns=['user', 'game', 'rating'])
for filename in filenames:
    users = list()
    games = list()
    ratings = list()

    f = open(filename, 'r')
    json_data = json.load(f)

    for game_info in json_data['1']:
        game = game_info['title']

        for rating_info in game_info['rating']:
            rating = rating_info['rating']
            user = rating_info['user']

            if rating:
                users.append(user)
                games.append(game)
                ratings.append(rating)

    f.close()
    rating_df = pd.DataFrame(
        {'user': users, 'game': games, 'rating': ratings},
        columns=['user', 'game', 'rating']
    )
    rating_df_full = rating_df_full.append(rating_df, ignore_index=True)


rating_df_full.drop_duplicates(['user', 'game', 'rating'], inplace=True)
rating_df_full = rating_df_full.pivot(
    index='user', columns='game', values='rating'
)
rating_df_full.to_csv('./data/rating_matrix.csv')

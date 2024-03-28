'''
DS 4300 Spring 2024
Kaydence Lin, Kaito, Yidi
HW 5: Song Recommendation
filename: spotify_cypher_cleaner.py
Get the song samples from csv, compute Euclidean Distance, and transform to easily import into cypher
'''

import pandas as pd
import math
from scipy.spatial import distance

def main():
    spotify = pd.read_csv('spotify.csv').drop_duplicates(subset=['track_name'], ignore_index=True)

    # print(spotify.head())
    print(spotify.columns)

    # 'Is This It'
    album = input('Enter album name: ')
    while(len(spotify[(spotify['album_name'] == album)]) == 0):
        album = input('Enter album name: ')

    # Trim off un-needed columns
    spotify = spotify[['artists','album_name','track_name','popularity','danceability','energy','loudness',
                       'speechiness','acousticness','instrumentalness','liveness','valence','tempo','track_genre']]

    # Strokes and non-Strokes
    choice = spotify[spotify['album_name']==album].reset_index(drop=True)
    genre_count = choice.groupby('track_genre').size().reset_index(name='count').sort_values('count', ascending=False).reset_index(drop=True)
    genres = set(choice['track_genre'])
    artist = set(choice['artists'])

    print(artist)
    print(genre_count)

    recom = spotify[~spotify['artists'].isin(artist) & spotify['track_genre'].isin(genres)]
    recom_pool = []
    base = genre_count.loc[0,'count']
    top = recom[recom['track_genre'] == genre_count.loc[0, 'track_genre']].shape[0]
    recom_pool.append(recom[recom['track_genre']==genre_count.loc[0,'track_genre']])

    for i in range(1,genre_count.shape[0]):
        recom_pool.append(recom[recom['track_genre']==genre_count.loc[i,'track_genre']].sample(math.floor(genre_count.loc[i,'count'] / base * top)))

    recom = pd.concat(recom_pool).reset_index(drop=True)

    print(recom.groupby('track_genre').size().reset_index(name='count'))

    # pre-concat transform
    limit = recom.shape[0]
    recom_col = ['recom_' + s for s in list(recom.columns)]
    recom = recom.loc[recom.index.repeat(choice.shape[0])].set_axis(recom_col, axis=1).reset_index(drop=True)
    stacked_choice = pd.concat([choice] * limit).reset_index(drop=True)

    # print(recom)
    # print(stacked_choice['track_name'].head(20))

    # concatenate Strokes and non-Strokes
    cypher_csv = pd.concat([stacked_choice, recom], axis=1).reset_index(drop=True)

    # assign euclidean distance
    features = ['popularity','danceability','energy','loudness','speechiness','acousticness','instrumentalness','liveness','valence','tempo']
    recom_features = ['recom_' + f for f in features]
    cypher_csv['euclidean_distance'] = [distance.euclidean(cypher_csv.loc[i,features], cypher_csv.loc[i,recom_features]) for i in range(cypher_csv.shape[0])]

    # print(cypher_csv)
    # print(cypher_csv.columns)
    print(cypher_csv[['track_name','recom_track_name','euclidean_distance']].head(20))

    # save to csv
    cypher_csv.to_csv('spotify_cypher.csv', index=False)

if __name__ == "__main__":
    main()

"""
Module containing utility functions for calculating various metrics and
performing common operations on Pandas dataframes.

Note - module currently assumes the standard df column names.
Consider changing this later.
"""

import pandas as pd
import numpy as np

def sparsity(df):
    """
    Returns the sparsity of the dataframe.
    Sparsity is defined as the percentage of non-zero elements in a
    songs-playlist matrix.
    """
    return float(df.shape[0])*100/float(len(df.spotify_id.unique()) * len(df.playlist_id.unique()))


def plot_value_occurences(column, df):
    """
    Plots the value count (histogram) for the specified column on the specified DF.

    Arguments:
        - column - name of column of interest
        - df - Pandas DF of interest
    """
    value_counts = pd.value_counts(df[column])

    plt.figure(figsize=(12,10))

    plt.xlabel(column)
    plt.ylabel(f"{column} Occurences")

    plt.plot(value_counts.values, marker="x")
    plt.show()


def cold_start_indxs(df, song_threshold=2, return_playlist=False, reverse=False):
    """
    Returns the *index* for all playlists which do not have the threshold number of songs.
    The default behaviour is to return the playlists which do not have *at least*
    the threshold number of songs.

    Arguments:
        - df - Pandas DF of interest
        - song_threshold - threshold number of songs
        - return_playlist - *also* returns an array playlist_id which do not meet the
        condition
        - reverse - condition flip. Instead of finding all playlists which do have
        less than the threshold number of songs, condition flips to find the playlist
        which have more than the threshold number of songs.

    Returns:
        - *index* array of all playlists which do not meet the condition
        - If return_playlist, then also returns array of playlist_ids which do
        not meet the condition
    """
    value_counts = pd.value_counts(df.playlist_id)
    if reverse:
        playlists = value_counts[value_counts>song_threshold].index.values
    else:
        playlists = value_counts[value_counts<song_threshold].index.values

    if return_playlist:
        return df[df.playlist_id.isin(playlists)].index, playlists
    else:
        return df[df.playlist_id.isin(playlists)].index


def withold_songs(df, withold_split=(0.2,0.2)):
    """
    Removes a certain proportion of songs from a certain proportion of playlists in DF.

    Arguments:
        - df - standard cleaned_data DF
        - withold_split - tuple. First value = fraction of playlists to split.
        Second value = fraction of songs to remove from said playlists.

    Returns:
        - df with songs excluded
        - pd Series wrapping a dictionary of playlist and num_songs excluded.
        key = playlist; value = list of spotify IDs excluded.

    Note - the withold split is the target split; the exact split will vary slightly.
    This is to avoid splits creating empty playlists.
    """

#     Songs in each playlist
    playlist_vc = pd.value_counts(df.playlist_id)

#     Number of songs potentially excluded from each playlist
    split = playlist_vc.apply(lambda vc: round(vc*withold_split[1]))

#     Filter out playlists with a 0 split and which leave no songs in remaining playlist
    split = split[(split>0) & (playlist_vc>split)]

#     Sample valid playlists
    split = split.sample(frac=withold_split[0])

    indxs_to_drop = []

#     Dictionary for storing spotify IDs of songs excluded from each playlist
    excluded = defaultdict(list)

    for playlist_id, num_songs_excl in split.items():
        temp_excl_df = df[df.playlist_id==playlist_id].sample(num_songs_excl)

        excluded[playlist_id] += [row.spotify_id for _, row in temp_excl_df.iterrows()]

        indxs_to_drop += list(temp_excl_df.index.values)

    return df.drop(indxs_to_drop, axis=0), pd.Series(excluded)

def tester(x):
    print(x)

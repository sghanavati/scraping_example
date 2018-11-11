#!/usr/bin/python

import sys
from copy import deepcopy
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import urllib
import os

from christie_scraper import scraper, read_ivr_training_data, save_ivr_training_data


def calc_avg_price_of_similars(artist, X, all_objects, MONTH):
    month_objs = all_objects.loc[all_objects['month'] == MONTH][
        ['lot_num', 'sold_price_usd', 'height_cm', 'length_cm']]

    month_artist_infos = all_objects.loc[(all_objects['artist'] == artist) & (all_objects['month'] == MONTH)][
        ['artist', 'lot_num', 'month', 'title', 'sold_price_usd', 'height_cm', 'length_cm']]
    month_prices = []
    month_lots = []
    for i in range(month_artist_infos.shape[0]):
        # print("\n", month_artist_infos.iloc[i].lot_num, " : ", month_artist_infos.iloc[i].height_cm, "  ", month_artist_infos.iloc[i].length_cm)
        try:
            h = float(month_artist_infos.iloc[i].height_cm)
            w = float(month_artist_infos.iloc[i].length_cm)
        except:
            h = 10e10
            w = 10e10

        for j in range(month_objs.shape[0]):
            try:
                sim_h = float(month_objs.iloc[j].height_cm)
                sim_w = float(month_objs.iloc[j].length_cm)
            except:
                sim_h = -10e10
                sim_w = -10e10

            if (sim_h >= (h - X) and sim_h <= (h + X) and sim_w >= (w - X) and sim_w <= (w + X)):
                if month_objs.iloc[j].lot_num not in month_lots:
                    month_lots.append(month_objs.iloc[j].lot_num)
                    month_prices.append(float(month_objs.iloc[j].sold_price_usd))
                    # print(" ** ", month_objs.iloc[j].lot_num, " : ", month_objs.iloc[j].height_cm, "  ", month_objs.iloc[j].length_cm, float(month_objs.iloc[j].sold_price_usd))
    return np.mean(month_prices)

def calc_price_growth(old_price, new_price):
    return 100.0*(new_price - old_price)/old_price


def find_intersecting_artist(all_objects):
    a1 = np.array(all_objects.loc[all_objects['month'] == '14November2017'].artist)
    a2 = np.array(all_objects.loc[all_objects['month'] == '28February2018'].artist)

    common_artists = list(set(a1).intersection(a2))
    print("There are ", len(common_artists), " common artists")
    return common_artists
    
def get_data(basedir, scraped_path):
    LotUrlFile1 = basedir + "/resources/feb17/lot301"  # LOT 431, 434 were widthrawn
    LotUrlFile2 = basedir + "/resources/feb17/lot435"  # to LOT 544

    LotUrlFile3 = basedir + "/resources/march18/lot401"  # lot 513 and 521 was withdrawn so it won't be found
    LotUrlFile4 = basedir + "/resources/march18/lot514"
    LotUrlFile5 = basedir + "/resources/march18/lot523"  # to lot 627

    pd1 = scraper(LotUrlFile1)
    pd2 = scraper(LotUrlFile2)
    pd3 = scraper(LotUrlFile3)
    pd4 = scraper(LotUrlFile4)
    pd5 = scraper(LotUrlFile5)

    all_data = pd.concat([
        pd.DataFrame(pd1).reset_index(drop=True),
        pd.DataFrame(pd2).reset_index(drop=True),
        pd.DataFrame(pd3).reset_index(drop=True),
        pd.DataFrame(pd4).reset_index(drop=True),
        pd.DataFrame(pd5).reset_index(drop=True)
    ])
    save_ivr_training_data(all_data, scraped_path)

def run(X):     #similar objects: height +/-X and width +/-X
    print("X is ", X)
    X = float(X)
    basedir = os.path.abspath(os.path.dirname(__file__))
    scraped_path = os.path.abspath(os.path.dirname(__file__)) + "/feb17_march18.csv"
    month1 = '14November2017'
    month2 = '28February2018'

    if not os.path.exists(scraped_path):
        get_data(basedir, scraped_path)

    all_objects = read_ivr_training_data(scraped_path)

    common_artists = find_intersecting_artist(all_objects)

    results = []
    
    for artist in common_artists:
        # print(" ** ", artist)
        result = {'artist':artist}
        feb_price = calc_avg_price_of_similars(artist, X, all_objects, month1)
        march_price = calc_avg_price_of_similars(artist, X, all_objects, month2)
        growth = calc_price_growth(feb_price, march_price)
        result['feb_price'] = feb_price
        result['march_price'] = march_price
        result['growth'] = growth
        print(result)
        results.append(result)


if __name__ == '__main__':
    run(sys.argv[1])
    #TODO: 1.read both dates into a pandas framework (month, lot num, artist, born death, title,
    # sold price, estimation price, image, medium, size WxH, convert gbp to usd  (artist signature, year painted, provenance))
    #TODO: 2.find common artist who sold on both days  list(set(list1).intersection(list2))
    #TODO: 3.for those find similar objs in each month
    #TODO: 4.calc avg price of each month + growth and print nicely


    # 1. save first lot, then while next lot is not empty wget
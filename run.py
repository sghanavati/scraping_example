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




def find_similar_objects(all_objects, X):
    lot_pairs = []
    lot_id_list = all_objects.lot_id.list()
    lot_id_list_copy = deepcopy(lot_id_list)

    for i in range(len(lot_id_list)):
        this_lot_id = all_objects.iloc[i].lot_id
        this_width = all_objects.iloc[i].width
        this_height = all_objects.iloc[i].height
        lot_id_list_copy.remove(this_lot_id)
        for lot_id in lot_id_list_copy:
            if (all_objects.loc['lot_id'==lot_id].width >= (this_width - X) or
               all_objects.loc['lot_id' == lot_id].width <= (this_width + X) or
               all_objects.loc['lot_id' == lot_id].height >= (this_height - X) or
               all_objects.loc['lot_id' == lot_id].height <= (this_height + X) ) :
                lot_pairs.append(tuple((this_lot_id, lot_id)))
    return lot_pairs

def calc_price_growth(old_price, new_price):
    return 100.0*(new_price - old_price)/old_price


def find_intersecting_artist(all_objects):
    a1 = np.array(all_objects.loc[all_pd['month'] == '14November2017'].artist)
    a2 = np.array(all_objects.loc[all_pd['month'] == '28February2018'].artist)

    common_artists = list(set(a1).intersection(a2))
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
    save_ivr_training_data(all_data, data_path)

def run(X):     #similar objects: height +/-X and width +/-X
    basedir = os.path.abspath(os.path.dirname(__file__))
    scraped_path = os.path.abspath(os.path.dirname(__file__)) + "/feb17_march18.csv"
    # get_data(basedir, scraped_path)

    all_objects = read_ivr_training_data(scraped_path)
    print(all_objects.columns)
    print(all_objects.shape)

    common_artists = find_intersecting_artist(all_objects)

    all_objects.loc[all_objects['artist'] == common_artists[0]][
        ['artist', 'month', 'title', 'sold_price_usd', 'height_cm', 'length_cm']]
    
    for artist in common_artists:
        feb_artist_Ws = all_objects.loc[all_objects['artist'] == artist][
        ['artist', 'month', 'title', 'sold_price_usd', 'height_cm', 'length_cm']]

    '''
    lot_pairs = find_similar_objects(all_objects, X)


    for obj in all_objects:
        nov17_prices = []
        march18_prices = []

        #TODO: 1.calc each month price average
        nov17_price = np.avg(nov17_prices)
        march18_price = np.avg(march18_prices)


        #TODO: beautify the output
        print(obj.artist_name, obj.height, obj.width, calc_price_growth(nov17_price, march18_price), '%',
              ' Avg ', nov17_price, ' Avg ', march18_price)
    '''


if __name__ == '__main__':
    run(sys.argv[1])
    #TODO: 1.read both dates into a pandas framework (month, lot num, artist, born death, title,
    # sold price, estimation price, image, medium, size WxH, convert gbp to usd  (artist signature, year painted, provenance))
    #TODO: 2.find common artist who sold on both days  list(set(list1).intersection(list2))
    #TODO: 3.for those find similar objs in each month
    #TODO: 4.calc avg price of each month + growth and print nicely


    # 1. save first lot, then while next lot is not empty wget
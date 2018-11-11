import pandas as pd
from bs4 import BeautifulSoup
import re
import urllib
import os

#TODO function gets origial LotUrlFile and return pandas framework
# Average: 1 GBP = 1.3831 USD  on 28 Feb 2018
conversion_rate = 1.3831

basedir = os.path.abspath(os.path.dirname(__file__)) + "/resources/"


def scraper(LotUrlFile):
    # the fields we're scraping
    locations = []
    months = []
    lot_nums = []
    artists = []
    born_deaths = []
    titles = []
    estimated_prices = []
    sold_prices = []
    sold_price_usds = []
    image_urls = []
    image_paths = []
    descriptions = []
    artist_signatures = []
    mediums = []
    height_cms = []
    length_cms = []
    year_printeds = []
    provenances = []

    do_continue = True
    while(do_continue):
        soup = BeautifulSoup(open(LotUrlFile), "html.parser")
        print(" ***** ", LotUrlFile)

        locations.append( soup.find('p', {'class':"sale-header--location"}).text)
        month = soup.find('p', {'class':"sale-header--date"}).text.replace(' ','')
        months.append(month)
        if not os.path.exists(basedir + month):
            os.makedirs(basedir + month)

        lot_num = soup.find('span', {'id':"main_center_0_lblLotNumber"}).text.replace(' ','')
        lot_nums.append(lot_num)

        #NOTE: the next lot id of Lot 430 in Nov17 was wrong => manually saved
        nextLotUrl = soup.find('a', {'id':"main_center_0_lnkNextLot"})['href']
        if (nextLotUrl.endswith("intObjectID=") or "intObjectID=&" in nextLotUrl):
            do_continue = False
        else:
            LotUrlFile = basedir + month + "/NextLotof" + lot_num
            if not os.path.exists(LotUrlFile):
                urllib.request.urlretrieve( nextLotUrl, LotUrlFile)

        if (((lot_num=='512' or lot_num=='519') and month=='28February2018') or
            (lot_num=='430' and month=='14November2017')):
            do_continue = False


        artist_years = soup.find('span', {'id':"main_center_0_lblLotPrimaryTitle"}).text
        artists.append( artist_years[0 : artist_years.find(' (')])
        born_deaths.append( artist_years[artist_years.find('(')+1 : artist_years.find(')')] )
        titles.append( soup.find('h2', {'id':"main_center_0_lblLotSecondaryTitle"}).text)
        estimated_prices.append( soup.find('span', {'id':"main_center_0_lblPriceEstimatedPrimary"}).text)
        sold_price = soup.find('p', {'id':"main_center_0_lblPriceRealizedPrimary"}).text.replace(',','')
        sold_prices.append(sold_price)
        sold_price = sold_price.replace(' ','')
        #convert GBP to USD
        sold_price_usd = 0
        if "USD" in sold_price:
            sold_price_usd = int(sold_price.replace('USD', ''))
        elif "GBP" in sold_price:
            sold_price_usd = int(conversion_rate*int(sold_price.replace('GBP', '')))
        sold_price_usds.append(sold_price_usd)


        image_url_t = str(soup.find('ul', {'id':"main_center_0_imgCarouselMain"}))
        image_url = re.findall('(src="https://www.christies.com/img/LotImages/.*.jpg)',image_url_t)[0].replace('src="','')
        image_urls.append(image_url)
        image_path = basedir + month + "/Lot" + lot_num + ".jpg"
        if not os.path.exists(image_path):
            urllib.request.urlretrieve( image_url, image_path)
        image_paths.append("./resources/"+ month + "/Lot" + lot_num + ".jpg")

        description = str(soup.find('span', {'id':"main_center_0_lblLotDescription"})).split('<br/>')
        descriptions.append(description)

        artist_signatures.append( description[2].replace('\n',''))
        mediums.append( description[3].replace('\n',''))

        try:
            height = list(set([el if 'Height' in el else 0 for el in description]))
            height.remove(0)
            height = height[0].replace(' ','')
            height = height.replace('\n', '')
            height = height.replace('Height:','')
            height_cm = re.findall('\(.*cm.*\)', height)[0]
            height_cm = height_cm.replace('(','')
            height_cm = height_cm.replace('cm.)','')
            height_cm = height_cm.replace('cm)', '')

            length = list(set([el if 'Length' in el else 0 for el in description]))
            length.remove(0)
            length = length[0].replace(' ','')
            length = length.replace('\n', '')
            length = length.replace('Length:','')
            length_cm = re.findall('\(.*cm.*\)', length)[0]
            length_cm = length_cm.replace('(','')
            length_cm = length_cm.replace('cm.)','')
            length_cm = length_cm.replace('cm)', '')
        except:
            size_list = [re.findall('\(.*cm.*\)', el) for el in description]
            for el in size_list:
                if el != []:
                    size = el
            size = size[0].replace('\n', '')
            size = size.replace(' ', '')
            size_cm = re.findall('\(.*cm.*\)', size)[0]
            x = size_cm.find('x')
            height_cm = size_cm[1:x]
            length_cm = size_cm[x+1:size_cm.find('cm')]


        height_cms.append(height_cm)
        length_cms.append(length_cm)
        year_printed = description[-2].replace('\n','')
        if 'cm.' in year_printed:
            year_printed = ''
        year_printeds.append(year_printed)
        provenances.append( soup.find('p', {'id':"main_center_0_lblLotProvenance"}).text)


    scraped_res = pd.concat([
        pd.Series(locations),
        pd.Series(months),
        pd.Series(lot_nums),
        pd.Series(artists),
        pd.Series(born_deaths),
        pd.Series(titles),
        pd.Series(estimated_prices),
        pd.Series(sold_prices),
        pd.Series(sold_price_usds),
        pd.Series(image_urls),
        pd.Series(image_paths),
        pd.Series(descriptions),
        pd.Series(artist_signatures),
        pd.Series(mediums),
        pd.Series(height_cms),
        pd.Series(length_cms),
        pd.Series(year_printeds),
        pd.Series(provenances)
    ], axis=1)

    scraped_res.columns = ['location', 'month', 'lot_num'
        , 'artist', 'born_death', 'title'
        , 'estimated_price', 'sold_price', 'sold_price_usd'
        , 'image_url', 'image_path', 'description'
        , 'artist_signature', 'medium'
        , 'height_cm', 'length_cm'
        , 'year_printed', 'provenance'
         ]

    return scraped_res


def read_ivr_training_data(data_path):
    scraped_data = pd.read_table(
        data_path,
        sep="\t",
        header=0)
    return scraped_data


def save_ivr_training_data(scraped_data, data_path):
    scraped_data.to_csv(data_path,
                           sep="\t",
                           index = False        #don't write row index
                           )
    return



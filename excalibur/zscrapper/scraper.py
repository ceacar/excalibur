#!/usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import ssl
import json
import os
from urllib.request import Request, urlopen
import time
import excalibur
import pathlib
import random


class ZillowScraper:
    def __init__(self):
        # For ignoring SSL certificate errors
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.url_base = 'http://www.zillow.com'
        self.cache_path = './scrap_cache'

    def soupify(self, url):
        # Input from user
        # url is ('Zillow House Listing Url- ')

        # Making the website believe that you are accessing it using a mozilla browser
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        # Creating a BeautifulSoup object of the html page for easy extraction of data.
        soup = BeautifulSoup(webpage, 'html.parser')
        return soup

    def _get_building_url(self, url):
        soup = self.soupify(url)
        cards = soup.find_all('a', attrs={'class': 'unit-card-link'}, href=True)
        urls = []
        for card in cards:
            urls.append(self.url_base + card['href'])
        return urls

    def scrap_building(self, url_to_scrap):
        """
        takes only webpage has buildingId
        https://www.zillow.com/b/4725-40th-st-sunnyside-ny-5YDFHW/
        """
        json_list = []
        for url in self._get_building_url(url_to_scrap):
            print(f"scrapping {url}")
            json_list.append(self.scrap_with_cache(url))
        return json_list

    def random_sleep(self):
        time_to_sleep = random.randint(2, 20)
        print("sleeping for {}".format(time_to_sleep))
        time.sleep(time_to_sleep)

    def scrap(self, url):
        # Input from user
        # url is ('Zillow House Listing Url- ')

        soup = self.soupify(url)
        self.html = soup.prettify('utf-8')
        self.property_json = {}
        self.property_json['Details_Broad'] = {}
        self.property_json['Address'] = {}

        # Extract Title of the property listing
        for title in soup.findAll('title'):
            self.property_json['Title'] = title.text.strip()
            break

        for meta in soup.findAll('meta', attrs={'name': 'description'}):
            self.property_json['Detail_Short'] = meta['content'].strip()

        for div in soup.findAll('div', attrs={'class': 'character-count-truncated'}):
            self.property_json['Details_Broad']['Description'] = div.text.strip()

        for (i, script) in enumerate(soup.findAll('script', attrs={'type': 'application/ld+json'})):
            if i == 0:
                json_data = json.loads(script.text)
                # self.property_json['Details_Broad']['Number of Rooms'] = json_data['numberOfRooms']
                self.property_json['livingArea'] = json_data['floorSize']['value']
                self.property_json['streetAddress'] = json_data['address']['streetAddress']
                self.property_json['city'] = json_data['address']['addressLocality']
                self.property_json['state'] = json_data['address']['addressRegion']
                self.property_json['zipcode'] = json_data['address']['postalCode']
            if i == 1:
                json_data = json.loads(script.text)
                self.property_json['price'] = json_data['offers']['price']
                # self.property_json['Image'] = json_data['image']
                break
        self.random_sleep()
        return self.property_json

    def scrap_no_price(self, url):
        # Input from user
        # url is ('Zillow House Listing Url- ')
        """
        {'Details_Broad': {},
        'Address': {},
        'Title': '4112 53rd St APT 3C, Woodside, NY 11377 | Zillow',
        'price': 243592,
        'address': '4112 53rd St APT 3C',
        'city': 'Woodside',
        'state': 'NY',
        'livingArea': 400,
        'homeType': 'MULTI_FAMILY',
        'lotSize': None,
        'zestimate': 243592}
        """

        soup = self.soupify(url)
        self.html = soup.prettify('utf-8')
        self.property_json = {}
        self.property_json['Details_Broad'] = {}
        self.property_json['Address'] = {}

        # Extract Title of the property listing
        for title in soup.findAll('title'):
            self.property_json['Title'] = title.text.strip()
            break

        # for meta in soup.findAll('meta', attrs={'name': 'description'}):
        #     self.property_json['Detail_Short'] = meta['content'].strip()
        # for div in soup.findAll('div', attrs={'class': 'character-count-truncated'}):
        #     self.property_json['Details_Broad']['Description'] = div.text.strip()
        # temp_list[2] has the price
        for (i, script) in enumerate(soup.findAll('script', attrs={'type': 'application/json'})):
            try:
                json_data = json.loads(script.text)
                sub_str = json_data['apiCache']
                sub_str_json_obj = json.loads(sub_str)

                # sub_str_json_obj['OffMarketSEORenderQuery{"zpid":2086730412}']['property']['price']
                """
                dict_keys([
                'VariantQuery{"zpid":245449686}',
                'ForSaleDoubleScrollFullRenderQuery{
                    "zpid":245449686,"contactFormRenderParameter":{
                        "zpid":245449686,"platform":"desktop","isDoubleScroll":true
                    }
                }'])
                """
                for key in sub_str_json_obj.keys():
                    price = ""
                    try:
                        propty = sub_str_json_obj[key]['property']
                        price = propty['price']
                        address = propty['streetAddress']
                        city = propty['city']
                        state = propty['state']
                        live_area = propty['livingArea']
                        home_type = propty['homeType']
                        lot_size = propty['lotSize']
                        zestimate = propty['zestimate']
                        self.property_json['price'] = price
                        self.property_json['address'] = address
                        self.property_json['city'] = city
                        self.property_json['state'] = state
                        self.property_json['livingArea'] = live_area
                        self.property_json['homeType'] = home_type
                        self.property_json['lotSize'] = lot_size
                        self.property_json['zestimate'] = zestimate
                        time.sleep(3)
                        return self.property_json
                    except Exception:
                        # except Exception as e:
                        # print('skipped key {} {}'.format(key, e))
                        pass
                break
            except Exception as e:
                print('skipping {} {}, {}'.format(i, script, e))
        time.sleep(1.5)
        return self.property_json

    def scrap_with_error_handling(self, url):
        """
        we scrap this url, it may error out, then we try with another scrap
        """

        # try:
        #     json_obj = self.scrap(url)
        #     return json_obj
        # except Exception:
        #     json_obj = self.scrap_no_price(url)
        #     return json_obj
        # raise Exception("no suitable scrap can be used")
        try:
            json_obj = self.scrap_no_price(url)
            return json_obj
        except Exception:
            print('Error scrapping {}'.format(url))

    def scrap_with_cache(self, url):
        file_name = excalibur.hash_utility.md5_string(url.encode())
        pathlib.Path(self.cache_path).mkdir(parents=True, exist_ok=True)
        full_file_path = self.cache_path + '/' + file_name
        if os.path.exists(full_file_path) and os.stat(full_file_path).st_size > 0:
            print('reading from cache: {}'.format(full_file_path))
            # file exists, we have scrapped this url before
            with open(full_file_path, 'r') as f:
                return json.load(f)
        else:
            returned_json_obj = self.scrap_with_error_handling(url)
            with open(full_file_path, 'w') as f:
                json.dump(returned_json_obj, f)
            return returned_json_obj

    def write_to_output(self):
        with open('data.json', 'w') as outfile:
            json.dump(self.property_json, outfile, indent=4)

        with open('output_file.html', 'wb') as file:
            file.write(self.html)


if __name__ == "__main__":
    zls = ZillowScraper()
    url = input('Enter Zillow House Listing Url- ')
    zls.scrap(url)
    zls.write_to_output()
    print('----------Extraction of data is complete. Check json file.----------')

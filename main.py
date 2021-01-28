# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 11:02:06 2020

@author: OHyic

"""
from GoogleImageScraper_Efficient import GoogleImageScraper
from screeninfo import get_monitors
import os
import shutil
import time
webdriver_path = os.getcwd()+"\\webdriver\\chromedriver.exe"

def checkdirexist(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        os.mkdir(path)
    else:
        os.mkdir(path)

#add new search key into array ["cat","t-shirt","apple","orange","pear","fish"]
search_keys= ["green trouser portrait 2020"]

number_of_images = 10

width_screen, height_screen = get_monitors()[0].width,get_monitors()[0].height
print(width_screen,height_screen)
min_resolution=(0,0)
max_resolution=(width_screen,height_screen)

if __name__ == '__main__':
    for search_key in search_keys:
        image_path = os.getcwd() + "\\photos\\" +search_key +"\\"
        checkdirexist(image_path)
        t = time.time()
        #image_scrapper = GoogleImageScraper(webdriver_path,image_path,search_key,number_of_images,width_screen,height_screen)
        #image_scrapper = GoogleImageScraper(webdriver_path,image_path,search_key,number_of_images,width_screen,height_screen,similar_images = True, link_similar_image="https://static.zara.net/photos///contents/mkt/spots/ss21-north-new-in-man/subhome-xmedia-03//w/1900/img-large-landscape-513a9b3af139cdc88ef8cb6ea3c9907c_0.jpg?ts=1611344365227")
        image_scrapper = GoogleImageScraper(webdriver_path, image_path, search_key, number_of_images, width_screen,
                                            height_screen)
        image_urls,image_halts = image_scrapper.find_image_urls()
        print(len(image_urls), len(image_halts))
        print(image_urls)
        if len(image_halts)==0:
            image_halts = ["image" + str(idx) for idx in range(len(image_urls))]
        print("Time consumed finding urls", time.time()-t)
        image_scrapper.download_urls(image_urls,image_halts,4)
        print("Time for downloading urls", time.time() - t)

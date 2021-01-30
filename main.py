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
import webbrowser

webdriver_path = os.getcwd()+"\\webdriver\\chromedriver.exe"

def checkdirexist(path):
    if os.path.exists(path):
        shutil.rmtree(path)
        os.mkdir(path)
    else:
        os.mkdir(path)

search_keys= ["blue trouser 2020"]

number_of_images = "all"
#number_of_images = 20

width_screen, height_screen = get_monitors()[0].width,get_monitors()[0].height
min_resolution=(0,0)
max_resolution=(width_screen,height_screen)


if __name__ == '__main__':
    for search_key in search_keys:
        image_path = os.getcwd() + "\\photos\\" +search_key +"\\"
        checkdirexist(image_path)
        t = time.time()
        print("Parsing first %s images of '%s' in google images" %(number_of_images,search_key))
        print("Saving in '%s' \n" % (image_path))
        image_scrapper = GoogleImageScraper(webdriver_path, image_path, search_key, number_of_images, width_screen,
                                            height_screen, color="blue", shape="tall",photo_type="photo", headless=True)
        image_urls,image_halts = image_scrapper.find_image_urls()
        if len(image_halts)==0:
            image_halts = ["image" + str(idx) for idx in range(len(image_urls))]
        print("Time consumed finding urls", time.time()-t)
        image_scrapper.download_urls(image_urls,image_halts,2)
        print("\nTime taken by the entire process %s.%s minutes" % (str(round((time.time() - t)/60)),str(round((time.time() - t)%60))))
        # if you want to open dirs in which pictures are saved!
        #webbrowser.open(image_path)

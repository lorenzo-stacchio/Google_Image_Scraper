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

number_of_images = 100

width_screen, height_screen = get_monitors()[0].width,get_monitors()[0].height
print(width_screen,height_screen)
min_resolution=(0,0)
max_resolution=(width_screen,height_screen)

if __name__ == '__main__':
    for search_key in search_keys:
        image_path = os.getcwd() + "\\photos\\" +search_key +"\\"
        checkdirexist(image_path)
        t = time.time()
        image_scrapper = GoogleImageScraper(webdriver_path,image_path,search_key,number_of_images,width_screen,height_screen)
        image_urls,image_halts = image_scrapper.find_image_urls()
        # image_urls = ["https://i.pinimg.com/originals/03/e3/2d/03e32d71bcf2f3c6ecb7ee1456043e9c.jpg","https://i.pinimg.com/236x/57/bd/49/57bd49c042c24b228f408e327ccdc9e9.jpg",
        #               "https://i.pinimg.com/236x/eb/e3/46/ebe346d7b096ec3ad2ef72efb3dde724--olive-pants-olive-jacket.jpg ","https://i.pinimg.com/236x/d0/bf/25/d0bf252c171c65adb44fe1c8df3778e9--olive-chinos-olive-pants.jpg ",
        #               "https://i.pinimg.com/236x/d0/bf/25/d0bf252c171c65adb44fe1c8df3778e9--olive-chinos-olive-pants.jpg "]
        # image_halts = ["Hunter_green_and_Olive_pants_ideas_olive_pants_fall_outfits_fashion","Best_Men's_Green_and_Olive_Pants_ideas_olive_pants_olive_chinos_mens_outfits", "Best_Men's_Green_and_Olive_Pants_ideas_olive_pants_olive_chinos_mens_outfits",
        #                "Pantone_Was_Spot_on_With_Its_Spring_2020_Color_Predictions_Who_What_Wear","Pantone_Was_Spot_on_With_Its_Spring_2020_Color_Predictions_Who_What_Wear"]
        print(len(image_urls), len(image_halts))
        print("Time consumed finding urls", time.time()-t)
        image_scrapper.download_urls(image_urls,image_halts)
        print("Time for downloading urls", time.time() - t)

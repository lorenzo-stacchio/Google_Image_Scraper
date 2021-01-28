# -*- coding: utf-8 -*-
from multiprocessing.context import Process
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from bs4 import BeautifulSoup
import multiprocessing as mp
from urllib import request as ulreq


class GoogleImageScraper():

    def __init__(self,webdriver_path,image_path, search_key,number_of_images, screen_width, screen_height,color=None,transparent= None, black_white = None, headless=False):
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.list_of_possible_colors = ["green", "yellow", "orange", "red", "white", "teal", "blue", "purple", "pink", "gray",
                                  "black", "brown"]
        self.transparent_code = "trans"
        self.black_white = "gray"
        self.headless = headless
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.bad_chars_list = ["|", ",", "-", ";", "?", "!", "(", ")", "/", ":",".", "\\","\"" ]
        self.url = "https://www.google.com/search?q=%s&tbm=isch&hl=it&tbs&rlz=1C1UEAD_itIT929IT929&sa=X&ved=0CAEQpwVqFwoTCIDosdGzt-4CFQAAAAAdAAAAABAC&biw=%s&bih=%s"%(search_key,self.screen_width, self.screen_height)
        print(self.url)
        if color in self.list_of_possible_colors:
            self.url = self.url.replace("tbs", "tbs=ic:specific%2Cisc:" + str(color))
        elif transparent:
            self.url = self.url.replace("tbs", "tbs=ic:trans")
        elif black_white:
            self.url = self.url.replace("tbs", "tbs=ic:gray")


    def adjust_string_path(self, alt_image):
        for bad_char in self.bad_chars_list:
            alt_image = alt_image.replace(bad_char, "")
        alt_image = " ".join(alt_image.split())
        alt_image = alt_image.replace(" ", "_")
        return alt_image

    def get_url_image_from_dedicated_google_url(self, url):
        assert url  # url must be not None
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        images = soup.findAll('img')  # there are two images tags, the second one contains the good url
        return images[1]['src']  # return its source

    def adjust_url(self,url):
        test_image = [1 if format in url else 0 for format in [".jpg", ".png", ".jpeg"]]
        if "lh3.googleusercontent.com" in url:
            url += "=w1000"
        elif sum(test_image) > 0:
            extension = [".jpg", ".png", ".jpeg"][test_image.index(1)]
            url = url.split(extension)[0] + extension  # remove bad queries from link
        return url

    def init_driver(self):
        # custom options
        options = Options()
        if (self.headless):
            # options.add_argument("--start-maximized")
            options.add_argument('--headless')
        prefs = {'profile.default_content_setting_values': {'cookies': 2,
                                                            'plugins': 2, 'popups': 2, 'geolocation': 2,
                                                            'notifications': 2, 'auto_select_certificate': 2,
                                                            'fullscreen': 2,
                                                            'mouselock': 2, 'mixed_script': 2,
                                                            'protocol_handlers': 2,
                                                            'media_stream_mic': 2, 'media_stream_camera': 2,
                                                            'media_stream': 2,
                                                            'ppapi_broker': 2, 'automatic_downloads': 2,
                                                            'midi_sysex': 2,
                                                            'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                            'metro_switch_to_desktop': 2,
                                                            'protected_media_identifier': 2, 'app_banner': 2,
                                                            'site_engagement': 2,
                                                            'durable_storage': 2}}
        options.add_experimental_option('prefs', prefs)
        # options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        ####################################################
        return webdriver.Chrome(self.webdriver_path, chrome_options=options)


    def find_image_urls(self):
        print("GoogleImageScraper Notification: Scraping for image link... Please wait.")
        image_urls=[]
        image_halts = []
        driver = self.init_driver()
        driver.set_window_position(int((self.screen_width)*0.83/2), 0) # *0.9 is to struggle against selenium sizing vs windows sizing problems
        driver.set_window_size(int((self.screen_width)*0.83/2), int(self.screen_height)*0.85)
        driver.get(self.url)
        # Goes down until we reach the end
        last_height = driver.execute_script("return document.body.scrollHeight")
        end_reached = False
        while(not end_reached):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                driver.find_element_by_xpath("//input[@value='Mostra altri risultati']").click()
            except Exception as _:
                pass
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                end_reached = True
            else:
                last_height = new_height
        print("----PARSING LINKS TO HTML PAGE FOR SINGLE IMAGES----")
        a_images = {idx+1: el for idx, el in enumerate(driver.find_elements_by_xpath('//*[@id="islrg"]/div[1]/div/a[1]'))}
        num_of_images_found = len(a_images)
        print(str(num_of_images_found))
        for indx in range(1, num_of_images_found):
            try:
                # print("INDICE ATTUALE", indx-1)
                imgurl = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (
                    str(indx)))  # con questo arrivi a cliccare all'immagine numero n
                imgurl.click()
            except Exception as _:
                pass
        time.sleep(1)
        for indx in range (1,num_of_images_found):
            try:
                imgurl = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (
                    str(indx)))  # con questo arrivi a cliccare all'immagine numero n
                google_url= driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[%s]/a[1]' % (str(indx))).get_attribute("href")
                url = self.get_url_image_from_dedicated_google_url(google_url)
                url = self.adjust_url(url)
                image_urls.append(url)
                image_halts.append(self.adjust_string_path(imgurl.get_attribute("alt")))  # append image alt
            except Exception as _:
                pass
        driver.close()
        return image_urls,image_halts


    def download_single_image(self, image_path, urls_part, alts_part, partition_id):
        for url, alt in zip(urls_part,alts_part):
            try:
                opener = ulreq.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5')]
                ulreq.install_opener(opener)
                print(url)
                print(image_path + str(partition_id) + "___" + alt + "___" + str(time.time_ns()) + ".jpg")
                ulreq.urlretrieve(url, image_path + str(partition_id) + "___" + alt + "___" + str(time.time_ns()) + ".jpg")
            except Exception as e:
                print(e)


    def download_urls(self,image_urls,image_halts, workers = mp.cpu_count()):
        assert workers>0
        assert len(image_urls) == len(image_halts)

        if workers==1:
            self.download_single_image(self.image_path, image_urls,image_halts, 0)
        else:
            partitions = mp.cpu_count()
            processes = []
            parts_size = int(len(image_urls)/(partitions))
            rest = round(len(image_urls)%partitions)
            for idx in range(partitions):
                start = idx*parts_size
                if idx == partitions-1:# this is last
                    end = start + parts_size + rest
                else:
                    end = start + parts_size
                print(start,end)
                p = Process(target=self.download_single_image, args=(self.image_path, image_urls[start:end],image_halts[start:end],idx))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()
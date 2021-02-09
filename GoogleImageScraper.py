# -*- coding: utf-8 -*-
"""

@author: Lorenzo Stacchio

"""
from multiprocessing.context import Process
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from bs4 import BeautifulSoup
import multiprocessing as mp
from urllib import request as ulreq
import socket
import json
import time
from alive_progress import alive_bar


class GoogleImageScraper():
    
    def __init__(self,webdriver_path,image_path,type_browser="chrome", number_of_images=10,search_key=None, screen_width=1920, screen_height=1080,similar_images = False, link_similar_image=None,color=None, shape=None, photo_type=None,headless=True):
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.headless = headless
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = color
        self.shape = shape
        self.photo_type = photo_type
        self.similar_image = similar_images
        self.link_similar_image = link_similar_image
        self.type_browser = type_browser
        #self.url = "https://www.google.com/search?q=%s&tbm=isch&hl=it&tbs&rlz=1C1UEAD_itIT929IT929&sa=X&ved=0CAEQpwVqFwoTCIDosdGzt-4CFQAAAAAdAAAAABAC&biw=%s&bih=%s"%(search_key,self.screen_width, self.screen_height)
        self.base_url = "https://www.google.com/search?q=%s&tbm=isch&hl=it&tbs&rlz=1C1UEAD_itIT929IT929&sa=X&ved=0CAEQpwVqFwoTCIDosdGzt-4CFQAAAAAdAAAAABAC&biw=%s&bih=%s"%(search_key,self.screen_width, self.screen_height)
        # Init all this variables with init_parameters()
        self.time_wait_between_dowloads,self.time_wait_between_scrolling,self.timeout_for_download_images = None,None,None 
        # color variables 
        self.color_list,self.colorized, self.black_and_white, self.transparent = None,None,None,None
        self.shapes,self.photo_types = None,None
        self.chars_to_clean_urls = None # chars to replace in urls
        # Load configs and parse arguments
        config_dict = self.load_config()
        self.init_parameters(config_dict)
        self.driver = self.init_driver()
        self.url = self.parse_arguments()

    def load_config(self):
        with open("config.json", "r") as configs:
            config_file = ''.join(configs.readlines())
            config_dict = json.loads(config_file)
            return config_dict

    # TODO: IMPLEMENTARE RICERCA PER PAESE
    def init_parameters(self, config_dict):
        socket.setdefaulttimeout(config_dict["time"]["timeout_for_download_images"]) #set time limit to download
        self.time_wait_between_dowloads = config_dict["time"]["timeout_for_download_images"]
        self.time_wait_between_scrolling = config_dict["time"]["time_wait_between_scrolling"]
        self.timeout_for_download_images = config_dict["time"]["timeout_for_download_images"]
        self.color_list = config_dict["image_params"]["colors"]["normal"]
        self.colorized = config_dict["image_params"]["colors"]["colorized"]
        self.transparent = config_dict["image_params"]["colors"]["trasparent_code"]
        self.black_and_white = config_dict["image_params"]["colors"]["black_and_white"]
        self.shapes = config_dict["image_params"]["shapes"]
        self.photo_types = config_dict["image_params"]["type_of_image"]
        self.chars_to_clean_urls = config_dict["chars_to_clean_urls"]


    def parse_arguments(self):
        color_params_parsing = ""
        # PARSE FOR FIRST SIMILAR
        if self.similar_image: # other type of research
            url = "https://www.google.it/searchbyimage?image_url=%s&encoded_image=&image_content=&filename=&hl=it"%(self.link_similar_image)
            return self.get_url_similar_images_google(url)
        else: # NORMAL SEARCH
            # tra un parametro e l'altro ci va la virgola ---> &tbs=ic:color,iar:t
            # parsing color
            color_string = None
            if self.color in self.color_list:
                color_string = "ic:specific%2Cisc:" + str(self.color)
                #self.url = self.url.replace("tbs", "tbs=ic:specific%2Cisc:" + str(self.color))
            elif self.color == self.colorized:
                color_string = "ic:" + self.colorized
            elif self.color == self.transparent:
                color_string = "ic:" + self.transparent
                #self.url = self.url.replace("tbs", "tbs=ic:trans")
            elif self.color == self.black_and_white:
                color_string = "ic:" + self.black_and_white
                #self.url = self.url.replace("tbs", "tbs=ic:gray")
            # parsing shape
            shape_string = None
            if self.shape in self.shapes.keys():
                shape_string = "iar:" + self.shapes[self.shape]
            # parsing photo type
            photo_type_string = None
            if self.photo_type in self.photo_types.keys():
                photo_type_string = "itp:" + self.photo_types[self.photo_type]
            #itp
            final_string_filter = "tbs=" + ','.join([filter  for filter in [color_string,shape_string,photo_type_string] if filter])
            return self.base_url.replace("tbs", str(final_string_filter))

    def get_url_similar_images_google(self,url):
        #TO DO
        assert url  # url must be not None
        self.driver.get(url)
        source = self.driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        link_similar_images = soup.findAll("a", class_= "ekf0x hSQtef")
        return "https://www.google.com/" + link_similar_images[0]['href'] #add prefix basing on href value


    def get_url_image_from_dedicated_google_url(self, url):
        assert url  # url must be not None
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        images = soup.findAll('img')  # there are two images tags, the second one contains the good url
        return images[1]['src']  # return its source


    def adjust_string_path(self, alt_image):
        for bad_char in self.chars_to_clean_urls:
            alt_image = alt_image.replace(bad_char, "")
        alt_image = " ".join(alt_image.split())
        alt_image = alt_image.replace(" ", "_")
        return alt_image


    def get_original_urls_from_list_of_links(self, link_similar_images_list):
        image_urls = []
        with alive_bar(total=self.number_of_images, title="Fetching urls") as bar:
            for idx,link in enumerate(link_similar_images_list):
                bar()
                try:
                    if link.has_attr('href') and "/imgres?imgurl=" in link['href']:
                        url = "https://www.google.com/" + link['href']
                        url = self.get_url_image_from_dedicated_google_url(url)
                        url = self.adjust_url(url)
                        image_urls.append(url)
                except Exception as _:
                    pass # bad url
        return image_urls


    def adjust_url(self,url):
        test_image = [1 if format in url else 0 for format in [".jpg", ".png", ".jpeg"]]
        if "lh3.googleusercontent.com" in url:
            url += "=w1000"
        elif sum(test_image) > 0:
            extension = [".jpg", ".png", ".jpeg"][test_image.index(1)]
            url = url.split(extension)[0] + extension  # remove bad queries from link
        return url


    def get_all_original_urls_from_page(self, html_page, num_of_images_found, workers = mp.cpu_count()):
        # This will create a list of buyers:
        image_urls = []
        soup = BeautifulSoup(html_page, "html.parser")
        link_similar_images = soup.findAll("a", class_="wXeWr islib nfEiy mM5pbd")[:num_of_images_found]
        print(len(link_similar_images))
        image_urls = self.get_original_urls_from_list_of_links(link_similar_images)
        return image_urls


    def init_driver(self):
        # custom options
        options = Options()
        if (self.headless):
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
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("excludeSwitches", ["enable-logging"]) #silent selenium
        if self.type_browser=="chrome":
            return webdriver.Chrome(self.webdriver_path, chrome_options=options)
        else:
            return webdriver.Firefox(executable_path=self.webdriver_path)


    def find_image_urls(self):
        image_halts = []
        self.driver.set_window_position(int((self.screen_width)*0.83/2), 0) # *0.9 is to struggle against selenium sizing vs windows sizing problems
        self.driver.set_window_size(int((self.screen_width)*0.83/2), int(self.screen_height)*0.85)
        self.driver.get(self.url)
        # Goes down until we reach the end
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        end_reached = False
        print("\n----BROWSING----")
        while(not end_reached):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                self.driver.find_element_by_xpath("//input[@value='Mostra altri risultati']").click()
            except Exception as _:
                pass
            time.sleep(self.time_wait_between_scrolling)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                end_reached = True
            else:
                last_height = new_height
        print("\n----PARSING LINKS TO HTML PAGE FOR SINGLE IMAGES----")
        a_images = {idx+1: el for idx, el in enumerate(self.driver.find_elements_by_xpath('//*[@id="islrg"]/div[1]/div/a[1]'))}
        num_of_images_found = len(a_images)
        print("Images found %s in '%s' search"% (str(num_of_images_found), str(self.search_key)))

        if self.number_of_images=="all":
            self.number_of_images = num_of_images_found
        elif self.number_of_images> num_of_images_found:
            # check number of images to download is less than images found otherwise put max limit
            self.number_of_images = num_of_images_found

        print("\n----CLICKING ON %s IMAGE TO RETRIEVE URLS----" % (str(self.number_of_images)))
        with alive_bar(total=self.number_of_images, title="Clicking on image") as bar:
            for indx in range(1, self.number_of_images + 1):
                bar()
                try:
                    imgurl = self.driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (
                        str(indx)))  # con questo arrivi a cliccare all'immagine numero n
                    imgurl.click()
                    image_halts = imgurl["alt"]
                except Exception as _:
                    pass
        time.sleep(self.time_wait_between_scrolling)
        print("\n----FETCHING URLS----")
        image_urls = self.get_all_original_urls_from_page(self.driver.page_source, self.number_of_images)
        self.driver.close()
        return image_urls,image_halts

    @staticmethod
    def download_single_image(image_path, urls_part, alts_part, timeout, partition_id):
        with alive_bar(total=len(urls_part), title="Process %s downloading images" %(str(partition_id))) as bar:
            for url, alt in zip(urls_part, alts_part):
                bar()
                try:
                    opener = ulreq.build_opener()
                    opener.addheaders = [('User-agent',
                                          "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3")]
                    ulreq.install_opener(opener)
                    request = ulreq.urlopen(url, timeout=timeout)
                    with open(image_path + str(partition_id) + "___" + alt + "___" + str(time.time_ns()) + ".jpg",
                              'wb') as f:
                            f.write(request.read())
                except Exception as e:
                    bar.text("%s in Process %s" % (e,str(partition_id)))


    def download_urls(self,image_urls,image_halts, workers = mp.cpu_count()):
        print("\n----Downloading URLS----")
        assert workers>0
        assert len(image_urls) == len(image_halts)
        if workers==1:
            self.download_single_image(self.image_path, image_urls,image_halts, self.timeout_for_download_images,0)
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
                p = Process(target=self.download_single_image, args=(self.image_path, image_urls[start:end],image_halts[start:end],self.timeout_for_download_images,idx))
                p.start()
                print("Process %s started"%(idx))
                processes.append(p)
            for p in processes:
                p.join()
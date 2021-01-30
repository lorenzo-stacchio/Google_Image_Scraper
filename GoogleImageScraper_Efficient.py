# -*- coding: utf-8 -*-
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

class GoogleImageScraper():
    
    def __init__(self,webdriver_path,image_path, search_key,number_of_images, screen_width, screen_height,similar_images = False, link_similar_image=None,color=None, headless=True):
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.headless = headless
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.color = color
        self.similar_image = similar_images
        self.link_similar_image = link_similar_image
        #self.url = "https://www.google.com/search?q=%s&tbm=isch&hl=it&tbs&rlz=1C1UEAD_itIT929IT929&sa=X&ved=0CAEQpwVqFwoTCIDosdGzt-4CFQAAAAAdAAAAABAC&biw=%s&bih=%s"%(search_key,self.screen_width, self.screen_height)
        self.url = "https://www.google.com/search?q=%s&tbm=isch&hl=it&tbs&rlz=1C1UEAD_itIT929IT929&sa=X&ved=0CAEQpwVqFwoTCIDosdGzt-4CFQAAAAAdAAAAABAC&biw=%s&bih=%s"%(search_key,self.screen_width, self.screen_height)
        print(self.url)
        # Init all this variables with init_parameters()
        self.time_wait_between_dowloads,self.time_wait_between_scrolling,self.timeout_for_download_images = None,None,None 
        # color variables 
        self.color_list, self.black_and_white, self.transparent = None,None,None 
        self.chars_to_clean_urls = None # chars to replace in urls
        # Load configs and parse arguments
        config_dict = self.load_config()
        self.init_parameters(config_dict)
        self.parse_arguments()
        self.driver = self.init_driver()

    def load_config(self):
        with open("config.json", "r") as configs:
            config_file = ''.join(configs.readlines())
            config_dict = json.loads(config_file)
            return config_dict

    def init_parameters(self, config_dict):
        print(config_dict)
        socket.setdefaulttimeout(config_dict["time"]["timeout_for_download_images"]) #set time limit to download
        self.time_wait_between_dowloads = config_dict["time"]["timeout_for_download_images"]
        self.time_wait_between_scrolling = config_dict["time"]["time_wait_between_scrolling"]
        self.timeout_for_download_images = config_dict["time"]["timeout_for_download_images"]
        self.color_list = config_dict["image_params"]["colors"]["normal"]
        self.transparent = config_dict["image_params"]["colors"]["trasparent_code"]
        self.black_and_white = config_dict["image_params"]["colors"]["black_and_white"]
        self.chars_to_clean_urls = config_dict["chars_to_clean_urls"]

    def parse_arguments(self):
        color_params_parsing = ""
        if self.color in self.color_list:
            self.url = self.url.replace("tbs", "tbs=ic:specific%2Cisc:" + str(self.color))
        elif self.color == self.transparent:
            self.url = self.url.replace("tbs", "tbs=ic:trans")
        elif self.color == self.black_and_white:
            self.url = self.url.replace("tbs", "tbs=ic:gray")
        elif self.similar_image: # other type of research
            self.url = "https://www.google.it/searchbyimage?image_url=%s&encoded_image=&image_content=&filename=&hl=it"%(link_similar_image)
            self.url = self.get_url_similar_images_google(self.url)

    def adjust_string_path(self, alt_image):
        for bad_char in self.chars_to_clean_urls:
            alt_image = alt_image.replace(bad_char, "")
        alt_image = " ".join(alt_image.split())
        alt_image = alt_image.replace(" ", "_")
        return alt_image

    def get_url_similar_images_google(self,url):
        #TO DO
        assert url  # url must be not None
        self.driver.get(url)
        source = self.driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        link_similar_images = soup.findAll("a", class_= "ekf0x hSQtef")
        self.driver.close()
        return "https://www.google.com/" + link_similar_images[0]['href'] #add prefix basing on href value


    def get_url_image_from_dedicated_google_url(self, url):
        assert url  # url must be not None
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        images = soup.findAll('img')  # there are two images tags, the second one contains the good url
        return images[1]['src']  # return its source

    @staticmethod
    def get_original_urls_from_list_of_links(self, link_similar_images_list):
        image_urls = []
        for link in link_similar_images_list:
            try:
                if link.has_attr('href') and "/imgres?imgurl=" in link['href']:
                    url = "https://www.google.com/" + link['href']
                    url = self.get_url_image_from_dedicated_google_url(url)
                    url = self.adjust_url(url)
                    image_urls.append(url)
            except Exception as e:
                print(e)
        return image_urls

    def get_all_original_urls_from_page(self, html_page, num_of_images_found, workers = mp.cpu_count()):
        # This will create a list of buyers:
        image_urls = []
        soup = BeautifulSoup(html_page, "html.parser")
        link_similar_images = soup.findAll("a", class_="wXeWr islib nfEiy mM5pbd")[:num_of_images_found]
        print(len(link_similar_images))
        if workers==1:
            image_urls = self.get_original_urls_from_list_of_links(self, link_similar_images)
        else:
            partitions = workers
            processes = []
            parts_size = int(len(link_similar_images)/(partitions))
            rest = round(len(link_similar_images)%partitions)
            for idx in range(partitions):
                start = idx*parts_size
                if idx == partitions-1:# this is last
                    end = start + parts_size + rest
                else:
                    end = start + parts_size
                print("Partition fetching urls", start,end)
                p = Process(target=self.get_original_urls_from_list_of_links, args=(self, link_similar_images[start:end]))
                p.start()
                print("Process %s started fetching urls"%(idx))
                processes.append(p)
            for p in processes:
                p.join()

        # for link in link_similar_images[:num_of_images_found]:
        #     try:
        #         if link.has_attr('href') and "/imgres?imgurl=" in link['href']:
        #             url = "https://www.google.com/" + link['href']
        #             url = self.get_url_image_from_dedicated_google_url(url)
        #             url = self.adjust_url(url)
        #             image_urls.append(url)
        #     except Exception as e:
        #         print(e)
        return image_urls

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
        return webdriver.Chrome(self.webdriver_path, chrome_options=options)


    def find_image_urls(self):
        print("GoogleImageScraper Notification: Scraping for image link... Please wait.")
        image_halts = []
        self.driver.set_window_position(int((self.screen_width)*0.83/2), 0) # *0.9 is to struggle against selenium sizing vs windows sizing problems
        self.driver.set_window_size(int((self.screen_width)*0.83/2), int(self.screen_height)*0.85)
        self.driver.get(self.url)
        # Goes down until we reach the end
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        end_reached = False
        print("----BROWSING----")
        while(not end_reached):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                self.driver.find_element_by_xpath("//input[@value='Mostra altri risultati']").click()
            except Exception as _:
                pass
            time.sleep(2)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                end_reached = True
            else:
                last_height = new_height
        print("----PARSING LINKS TO HTML PAGE FOR SINGLE IMAGES----")
        a_images = {idx+1: el for idx, el in enumerate(self.driver.find_elements_by_xpath('//*[@id="islrg"]/div[1]/div/a[1]'))}
        num_of_images_found = len(a_images)
        print("Images found:", str(num_of_images_found))

        if self.number_of_images=="all":
            self.number_of_images = num_of_images_found
        elif self.number_of_images> num_of_images_found:
            # check number of images to download is less than images found otherwise put max limit
            self.number_of_images = num_of_images_found

        print("----CLICKING ON IMAGE TO RETRIEVE URLS----")
        for indx in range(1, self.number_of_images):
            try:
                imgurl = self.driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (
                    str(indx)))  # con questo arrivi a cliccare all'immagine numero n
                imgurl.click()
                image_halts = imgurl["alt"]
            except Exception as _:
                pass
        time.sleep(2)
        print("----FETCHING URLS----")
        image_urls = self.get_all_original_urls_from_page(self.driver.page_source, self.number_of_images)
        self.driver.close()
        return image_urls,image_halts

    @staticmethod
    def download_single_image(image_path, urls_part, alts_part, timeout, partition_id):
        for url, alt in zip(urls_part, alts_part):
            try:
                opener = ulreq.build_opener()
                opener.addheaders = [('User-agent',
                                      "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3")]
                ulreq.install_opener(opener)
                print("Process P downloading ", url)
                # print(image_path + str(partition_id) + "___" + alt + "___" + str(time.time_ns()) + ".jpg")
                request = ulreq.urlopen(url, timeout=timeout)
                with open(image_path + str(partition_id) + "___" + alt + "___" + str(time.time_ns()) + ".jpg",
                          'wb') as f:
                    try:
                        f.write(request.read())
                    except:
                        print("error downloading", url)
                # ulreq.urlretrieve(url, image_path + str(partition_id) + "___" + alt + "___" + str(time.time_ns()) + ".jpg")
            except Exception as e:
                print(e, "in Process", str(partition_id))


    def download_urls(self,image_urls,image_halts, workers = mp.cpu_count()):
        print("----Downloading URLS----")
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
                print("Partition", start,end)
                p = Process(target=self.download_single_image, args=(self.image_path, image_urls[start:end],image_halts[start:end],self.timeout_for_download_images,idx))
                p.start()
                print("Process %s started"%(idx))
                processes.append(p)
            for p in processes:
                p.join()
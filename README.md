# Google_Image_Scraper
This is a simple and almost efficient way to download all **high quality** images retrieved by single and multi-search on [google images](https://www.google.com/imghp) in python bypassing google api. Of course, given recent updates in html and javascript code provided by google you can't expect to retrieve all the images in one second using this language and without using google api, but in a reasonable time. 

# How it works
The implementation is based mostly on [selenium](https://selenium-python.readthedocs.io/) library (:heart:) for python 3 and takes some intuitions from [Yandex Images Download
](https://github.com/bobokvsky/yandex-images-download). In particular, this scraper is organized in three steps:

* It scrolls down the entire google image search. This is made to avoid slowness in next steps but also to count the total number of image found;
* It click an all the images found, to retrieve origin urls.
* It parse all the found urls and download images through them. 

# TODO
* Cmd like commands with argument parsing
* Documentation
* Add remainings possible google image search options
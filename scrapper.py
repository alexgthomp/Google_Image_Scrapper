import os
import requests
from bs4 import BeautifulSoup
import urllib
import re
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print("Found: {} search results. Extracting links from {}:{}".format(number_results,results_start,number_results))
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print("Found: {} image links, done!".format(len(image_urls)))
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls


def persist_image(image_output:str,url:str):
    try:
        urllib.request.urlretrieve(url, image_output)
        print("SUCCESS - saved {} - as {}".format(url,image_output))
    except Exception as e:
        print("ERROR - Could not save {} - {}".format(url,e))


def search_and_download(search_term:str,driver_path:str,target_folder:str,number_images=5):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument('--no-sandbox')

    search_term_formatted = re.sub(r"\s+", "", search_term, flags=re.UNICODE)
    
    with webdriver.Chrome(chrome_options=chrome_options, executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5)
        
    for idx, elem in enumerate(res):
        out_put_path = target_folder + search_term_formatted + "_" + str(idx) + ".jpg"
        persist_image(out_put_path,elem)

def main():
    if len(sys.argv) == 5:
        print("Beginning Scrapper .... ")
        search_term = sys.argv[1]
        driver_path = sys.argv[2]
        target_folder = sys.argv[3]
        number_images = int(sys.argv[4])
        search_and_download(search_term,driver_path,target_folder,number_images)
    else:
      print("Incorrect arguments, Example: python scrapper.py search_term driver_path target_folder number_images")

if __name__ == "__main__":
    main()

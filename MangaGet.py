import sys, os, time, urllib, urllib.request, shutil, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import staleness_of
#from selenium.webdriver.common.keys import Keys

def new_chrome_browser(logFile):
    try:
        browser = webdriver.Chrome()
        return browser
    except:
        writeLog(logFile, "[ERROR] Failed to load chrome webdriver")
        writeLog(logFile, sys.exc_info()[0])
        sys.exit()

def open_site(browser, url, logFile):
    browser.get(url)

def reverse_array(arr, logFile):
    length = len(arr)
    if length > 1:
        p2 = length - 1
        mid_point = len(arr) // 2
        for p1 in range(0, mid_point):
            temp = arr[p2]
            arr[p2] = arr[p1]
            arr[p1] = temp
            p2 -= 1
    else:
        writeLog(logFile, "reverse_array() ERROR: cannot reverse empty array")
        writeLog(logFile, sys.exc_info()[0])

def sleep(sec, logFile):
    str_sec = str(sec)
    writeLog(logFile, "Sleeping for " + str_sec + " seconds...")
    sys.stdout.flush()
    time.sleep(sec)

def writeLog(logFile, text):
    print(str(text))
    flush()
    logFile.write(str(text) + "\n")
    logFile.flush()
    os.fsync(logFile.fileno())

def flush():
    sys.stdout.flush()

def main(argv):

    ## TODO Code review + Proper error checking for everything + Restructure code

    ## TODO validate url
    if len(argv) != 1:
        print("File usage: python MangaGet.py URL")
        sys.exit()
    else:
        root_url = argv[0]

    ## TODO find safer way to determine name of manga: user input?
    index = root_url.rfind('/') + 1
    manga_name = root_url[index:]

    chapter_urls = []
    chapter_titles = []
    image_sources = []

    ## Make new directory
    if not os.path.exists(manga_name):
        os.makedirs(manga_name)

    log = manga_name + "\\" + "Log.txt"
    logFile = open(log, "w")

    writeLog(logFile, "Root_url: " + root_url)
    writeLog(logFile, manga_name + " manga directory created")

    ## Open webdriver
    chrome_browser = new_chrome_browser(logFile)

    ## Load root url
    try:
        open_site(chrome_browser, root_url, logFile)
    except:
        logFile.write("[ERROR] Failed to load url\n")
        writeLog(logFile, sys.exc_info()[0])
        sys.exit()

    writeLog(logFile, "Manga root url loaded")

    wait = WebDriverWait(chrome_browser, 60)
    wait.until(EC.presence_of_element_located((By.XPATH, '//table[@class="listing"]//a[@href]')))
    #sleep(10, logFile)

    ## Gets manga chapter urls
    for url in chrome_browser.find_elements_by_xpath('//table[@class="listing"]//a[@href]'):
        chapter_urls.append(url.get_attribute('href'))
        chapter_titles.append(url.get_attribute('title')) # unused
        #writeLog(logFile, url.get_attribute('href'))
        #writeLog(logFile, url.get_attribute('title'))

    writeLog(logFile, "Manga urls and chapters loaded")

    reverse_array(chapter_urls, logFile)
    reverse_array(chapter_titles, logFile)

    ## Iterate through each chapter url
    num_chapters = len(chapter_urls)
    for i in range(0, num_chapters):

        ## Make chapter directory
        dir = manga_name + "/" + manga_name + " Chapter " + str(i+1)
        if not os.path.exists(dir):
            os.makedirs(dir)
            writeLog(logFile, "===========================================")
            writeLog(logFile, dir + " directory created")

        ## Load chapter url
        writeLog(logFile, "Loading " + manga_name + " chapter " + str(i+1) + " url...")

        open_site(chrome_browser, chapter_urls[i], logFile)
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="divImage"]//img[@src]')))

        # try:
        #     chrome_browser.set_page_load_timeout(60)
        # except:
        #     print("error!")
        # old_page = chrome_browser.find_element_by_id("divImage")
        # wait.until(EC.staleness_of(old_page))

        writeLog(logFile, "Chapter " + str(i+1) + " url loaded")

        ## Get image sources urls
        writeLog(logFile, "Retrieving image source url(s)...")
        html_src = BeautifulSoup(chrome_browser.page_source, "html.parser")

        for script in html_src.find_all("script"):
            if "googleusercontent" in str(script):
                urls = re.findall(r'(https?://\S+)', str(script))

        for img_src in urls:
            if "googleusercontent" in img_src:
                valid_img_src = str.replace(img_src, ";", "&")
                image_sources.append(valid_img_src)

        # writeLog(logFile, html_src.prettify())
        # for src in html_src.find_all(attrs={"id":"divImage"}):
        #     for link in src.find_all("img"):
        #         image_sources.append(link.get("src"))
        #         print(link.get("src"))

       # for image in chrome_browser.find_elements_by_xpath('//div[@id="divImage"]//img[@src]'):
       # print("html src: " + str(image.get_attribute('src')))
       #     flush()
       #     image_sources.append(image.get_attribute('src'))

        writeLog(logFile, "Image source url(s) retrieved")

        x = 0
        for src in image_sources:
            writeLog(logFile, src)
            x += 1

        writeLog(logFile, "Number of image sources: " + str(x))

        image_count = len(image_sources)
        ## Save the images
        for x in range(0, image_count):

            image_name = manga_name + " ch " + str(i+1) + " - " + str(x) + ".png"
            p_image_source = image_sources[x]
            p_url = urlparse(p_image_source)

            if p_url.scheme != "http" and p_url.scheme != "https":
                p_image_source += "https://"

            print("[CHECK] img src: " + p_image_source)
            urllib.request.urlretrieve(p_image_source, image_name)

            if os.path.isfile(image_name) is False :
                writeLog(logFile, "[ERROR] Failed to retrieve " + image_name)

            shutil.move(image_name, dir) # move image to respective directory
            writeLog(logFile, image_name + " saved")

        writeLog(logFile, "Images saved")

        ## Reset and repeat (get next url)
        image_sources[:] = []

    chrome_browser.close()
    logFile.close()

if __name__ == "__main__":
    main(sys.argv[1:])

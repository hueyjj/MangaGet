import sys, os, time, urllib, urllib.request, shutil, re, lxml
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
    sys.stdout.write(str(text) + "\n")
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

    ## Gets manga chapter urls

    for url in chrome_browser.find_elements_by_xpath('//table[@class="listing"]//a[@href]'):
        chapter_urls.append(url.get_attribute('href'))
        chapter_titles.append(url.get_attribute('title')) # unused

    writeLog(logFile, "Manga urls and chapters loaded")

    reverse_array(chapter_urls, logFile)
    reverse_array(chapter_titles, logFile)

    ## Iterate through each chapter url

    formats = ['.jpg', '.png', '.jpeg', '.gif', '.tif']
    num_chapters = len(chapter_urls)
    for i in range(0, num_chapters):

        ## Make chapter directory
        writeLog(logFile, "===========================================")
        dir = manga_name + "/" + manga_name + " Chapter " + str(i+1)
        if not os.path.exists(dir):
            os.makedirs(dir)
            writeLog(logFile, dir + " directory created")

        ## Load chapter url

        writeLog(logFile, "Loading " + manga_name + " chapter " + str(i+1) + " url...")

        for attempt in range(10):
            try:
                open_site(chrome_browser, chapter_urls[i], logFile)
                #wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="divImage"]]')))
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'script')))
                writeLog(logFile, "Chapter " + str(i+1) + " url loaded")
            except:
                continue
            else:
                break
        else:
            writeLog(logFile, "[ERROR] Unable to load Chapter " + str(i+1) + " url")
            continue

        ## Get image sources urls

        writeLog(logFile, "Retrieving image source url(s)...")

        html_src = BeautifulSoup(chrome_browser.page_source, "lxml")
        urls = []
        image_sources = []

        for javascript in html_src.find_all("script"):
            for ext in formats:
                if ext in str(javascript):
                    urls = re.findall(r'(https?://\S+)', str(javascript))
                    for img_src in urls:
                        for ext_t in formats:
                            if ext_t in img_src:
                                valid_img_src = str.replace(img_src, ";", "&")
                                image_sources.append(valid_img_src)

        if len(image_sources) == 0:
            writeLog(logFile, "[ERROR] No image urls found")
            sys.exit()

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

        # x = 0
        # for src in image_sources:
        #     writeLog(logFile, src)
        #     x += 1
 
        writeLog(logFile, "Number of image sources: " + str(len(image_sources)))


        ## Load each image source urls

        image_count = len(image_sources)

        for x in range(0, image_count):

            image_name = manga_name + " ch " + str(i+1) + " - " + str(x) + ".png"
            p_image_source = image_sources[x]
            p_url = urlparse(p_image_source)

            if p_url.scheme != "http" and p_url.scheme != "https":
                p_image_source = "https://" + p_image_source

            ## Retrieve and save image

            try:
                r = urllib.request.Request(p_image_source)
                with urllib.request.urlopen(r) as response:
                    f = open(image_name, "wb")
                    f.write(response.read())
                    f.close()
            except:
                try:
                    writeLog(logFile, "[WARNING] " + image_name + " might be corrupted")
                    writeLog(logFile, "Trying to retrieve " + image_name + " again...")
                    r = urllib.request.Request(p_image_source)
                    with urllib.request.urlopen(r) as response:
                        f = open(image_name, "wb")
                        f.write(response.read())
                        f.close()
                except:
                    writeLog(logFile, "Trying again (3rd time) but with different method...")
                    try:
                        urllib.request.urlretrieve(p_image_source, image_name)
                    except:
                        writeLog(logFile, "[ERROR] Failed to retrieve " + image_name)

            if os.path.isfile(image_name) is True:
                file_info = os.stat(image_name)
                file_size = file_info.st_size

                if file_size is 0:
                    writeLog(logFile, "[ERROR] Bad file. Failed to save " + image_name)
                else:
                    shutil.move(image_name, dir) # move image to respective directory
                    writeLog(logFile, image_name + " saved")
            else:
                writeLog(logFile, "[ERROR] " + image_name + " does not exist")


        ## Reset and repeat (get next chapter url)

    chrome_browser.close()
    logFile.close()

if __name__ == "__main__":
    main(sys.argv[1:])

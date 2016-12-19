import sys, os, time, urllib, urllib.request, shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.keys import Keys

def new_chrome_browser(logFile):
    try:
        browser = webdriver.Chrome()
        return browser
    except:
        writeLog(logFile, "[ERROR] Failed to load chrome webdriver")
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

def sleep(sec, logFile):
    str_sec = str(sec)
    writeLog(logFile, "Sleeping for " + str_sec + " seconds...")
    sys.stdout.flush()
    time.sleep(sec)

def writeLog(logFile, text):
    print(text)
    flush()
    logFile.write(text + "\n")
    logFile.flush()
    os.fsync(logFile.fileno())

def flush():
    sys.stdout.flush()

def main(argv):

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
    try:
        chrome_browser = new_chrome_browser(logFile)
    except:
        writeLog(logFile, "[ERROR] Failed to load chrome webdriver\n")
        sys.exit()

    ## Load root url
    try:
        open_site(chrome_browser, root_url, logFile)
    except:
        logFile.write("[ERROR] Failed to load url\n")

    writeLog(logFile, "Manga root url loaded")

    wait = WebDriverWait(chrome_browser, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//table[@class="listing"]//a[@href]')))
    #sleep(10, logFile)

    ## Gets manga chapter urls
    for url in chrome_browser.find_elements_by_xpath('//table[@class="listing"]//a[@href]'):
        chapter_urls.append(url.get_attribute('href'))
        chapter_titles.append(url.get_attribute('title')) # unused
        writeLog(logFile, url.get_attribute('href'))
        writeLog(logFile, url.get_attribute('title'))

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

        ## Open chapter url
        try:
            writeLog(logFile, "Loading " + manga_name + " chapter " + str(i+1) + " url...")
            open_site(chrome_browser, chapter_urls[i], logFile)
            writeLog(logFile, "Chapter " + str(i+1) + " url loaded")

            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="divImage"]//img[@src]')))
            #sleep(4, logFile)

            ## Get image sources urls
            writeLog(logFile, "Retrieving image source url(s)...")
            try:
                for image in chrome_browser.find_elements_by_xpath('//div[@id="divImage"]//img[@src]'):
                    image_sources.append(image.get_attribute('src'))
            except:
                writeLog(logFile, "[ERROR] Failed to find image source url(s)")
                sys.exit()

            writeLog(logFile, "Image source url(s) retrieved")

            image_count = len(image_sources)

            ## Save the images
            for x in range(0, image_count):
                try:
                    image_name = manga_name + " ch " + str(i+1) + " - " + str(x) + ".png"
                    urllib.request.urlretrieve(image_sources[x], image_name)
                    shutil.move(image_name, dir) # move image to respective directory
                    writeLog(logFile, image_name + " saved")
                except:
                    writeLog(logFile, "[ERROR] Failed to save " + image_name + ". Failed URL: " +
                             image_sources[x]);

            writeLog(logFile, "Images saved")
        except:
            writeLog(logFile, "[ERROR] Failed to load url OR\n"+
                     "Failed to retrieve image from image source urls OR\n"
                     "Failed to save image to disk")

        ## Reset and repeat (get next url)
        image_sources[:] = []

    chrome_browser.close()
    logFile.close()

if __name__ == "__main__":
    main(sys.argv[1:])

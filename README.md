# MangaGet
MangaGet is a crawler that scrapes the images from the manga site, Kissmanga.

# Requirements
Python 3

Selenium

Urllib

Beautifulsoup

lxml

Chrome webdriver

# Running
File usage: python MangaGet.py URL

Example: python MangaGet.py http://kissmanga.com/manga/Naruto

# Remarks
Tested on Win 7 64 bit with Python 3 and on ~140Mb/s DL speed.

Need testing on lower speed network.

**DO NOT** attempt to use PhantomJS or any headless drivers unless you know what you are doing.

   reason: any attempts to run MangaGet with PhantomJS (default settings) will result in a ban (uknown what type of ban) by Kissmanga. Running MangaGet with Chrome webdriver should be fine.

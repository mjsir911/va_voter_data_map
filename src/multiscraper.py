#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from scraper import *
from selenium.webdriver.support.ui import Select
import time

__appname__     = ""
__author__      = "Marco Sirabella"
__copyright__   = ""
__credits__     = ["Marco Sirabella"]  # Authors and bug reporters
__license__     = "GPL"
__version__     = "1.0"
__maintainers__ = "Marco Sirabella"
__email__       = "msirabel@gmail.com"
__status__      = "Prototype"  # "Prototype", "Development" or "Production"
__module__      = ""

#year = 2016
#f = os.fork()
#while f != 0 and year > 1900:
#    time.sleep(1)
#    year -= 1
#    f = os.fork()

#valid_years = list(years(init()))
browser = init()
valid_years = [int(year.get_attribute('innerHTML')) for year in
    browser.find_element_by_css_selector(
        '#SearchYearFrom'
    ).find_elements_by_css_selector('option')
]


def process_one_year(which_year):
    driver = init()
    for year in years(driver, which_year):
        for i in pages(driver):
            for row in driver.find_elements_by_css_selector(
                    'tr.election_item'
            ):
                getCSV(row)


from multiprocessing import Pool
import logging
import timeit
logger = logging.getLogger()
timer = timeit.Timer()
starttime = timer.timer()

max_pool_count = 4
{
    8: 522.168079962008,
    4: 678.5831731929939,
    2: 904.9906527489948,
    1 :1634.690616922002
}
p = Pool(max_pool_count)
valid_years = valid_years
pool_args = [valid_years[i::max_pool_count] for i in range(max_pool_count)]
p.map(process_one_year, pool_args)
endtime = timer.timer()
logging.debug('time taken to process: {}'.format(endtime - starttime))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import selenium.webdriver
from selenium.webdriver.support.ui import Select
import PIL.Image
import urllib.request
import io
import os
import logging

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


DRIVER_PATH = 'include/phantomjs/phantomjs'
URL = 'http://historical.elections.virginia.gov'
DATA_DIR = 'data/'
logger = logging.Logger('root')
logging.basicConfig(level=logging.INFO)


def debug(driver):
    PIL.Image.open(io.BytesIO(driver.get_screenshot_as_png())).show()


def init():
    if os.path.exists(DRIVER_PATH):
        driver = selenium.webdriver.PhantomJS(DRIVER_PATH)
        logging.info('Using local installation of phantomjs')
    else:
        driver = selenium.webdriver.PhantomJS()
        logging.info('Using default installation of phantomjs')
    driver.get(URL)
    logging.info(f'Going to page `{URL}`')
    return driver


def curl(url):
    """
    http://stackoverflow.com/questions/7243750/download-file-from-web-in-python-3
    """
    logger.debug(f'Downloading {url}')
    response = urllib.request.urlopen(url)
    filename = response.headers.get('Content-disposition')
    filename = filename[filename.find('=') + 1:]
    data = response.read()
    return {filename: data}


downloadURL = URL + '/elections/download/'


def getCSV(tablerow):
    tr_id = tablerow.get_attribute('id')
    tr_id = tr_id.replace('election-id-', '')
    assert tr_id.isdigit()
    url = downloadURL + tr_id
    name, contents = list(curl(url).items())[0]
    with open(DATA_DIR + name, 'wb') as fp:
        logging.info(f'Writing file {name}')
        fp.write(contents)


def years(driver, years=None):
    if years is None:
        years = [
            year.get_attribute('innerHTML') for year in
            driver.find_element_by_css_selector(
                '#SearchYearFrom'
            ).find_elements_by_css_selector('option')
        ]
    else:
        years = list(map(str, years))
        assert all(map(lambda s: s.isdigit(), years))
    for year in years:
        year_from = driver.find_element_by_css_selector('#SearchYearFrom')
        year_to   = driver.find_element_by_css_selector('#SearchYearTo')
        dropdowns = year_from, year_to
        for dd in dropdowns:
            select = Select(dd)
            select.select_by_value(year)

        # Click on search button
        driver.find_element_by_css_selector(
            '#search_form_elections>div>#SearchIndexForm>div>input.splashy.tan'
        ).click()
        logging.info(
            f'Clicking on search button to get all results from year {year}'
        )
        yield year
        logging.info('Going back to search screen')
        driver.back()


def pages(driver):
    old = False
    new = True
    # maxcount = int(driver.find_element_by_css_selector('''#search_results_table_wrapper >
            # div.fg-toolbar.ui-toolbar.ui-widget-header.ui-corner-bl.ui-corner-br.ui-helper-clearfix
            # > div.dataTables_info''').get_attribute('innerHTML')[-10:].replace('items', ''))
    while old != new:
        print(old == new)
        old = driver.find_element_by_css_selector('body').get_attribute(
            'innerHTML'
        )
        logging.info('Fetching new page')
        driver.find_element_by_css_selector(
            '#search_results_table_next'
        ).click()
        counter = driver.find_element_by_css_selector(
                '''#search_results_table_paginate > span >
                a.fg-button.ui-button.ui-state-default.ui-state-disabled'''
        ).get_attribute('innerHTML')
        # yield int(counter), maxcount
        yield int(counter)
        new = driver.find_element_by_css_selector('body').get_attribute(
            'innerHTML'
        )


if __name__ == '__main__':
    browser = init()
    for year in years(browser, [2014, 2013]):
        for i in pages(browser):
            print(year, i)
            for row in browser.find_elements_by_css_selector('tr.election_item'):
                getCSV(row)

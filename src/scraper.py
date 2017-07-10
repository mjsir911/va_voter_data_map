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
logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.INFO)


def debug(driver):
    PIL.Image.open(io.BytesIO(driver.get_screenshot_as_png())).show()


def init():
    if os.path.exists(DRIVER_PATH):
        driver = selenium.webdriver.PhantomJS(DRIVER_PATH)
        logger.info('Using local installation of phantomjs')
    else:
        driver = selenium.webdriver.PhantomJS()
        logger.info('Using default installation of phantomjs')
    driver.get(URL)
    logger.info('Going to page `{URL}`'.format(URL=URL))
    return driver


def curl(url):
    """
    http://stackoverflow.com/questions/7243750/download-file-from-web-in-python-3
    """
    logger.debug('Downloading {url}'.format(url=url))
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
    logger.debug("Election id %i", tr_id)
    url = downloadURL + tr_id
    name, contents = list(curl(url).items())[0]
    with open(DATA_DIR + name, 'wb') as fp:
        logger.debug('Writing file {}'.format(DATA_DIR + name))
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
        logger.info(
            'Clicking on search button to get all results from year '
            '{year}'.format(year=year)
        )
        yield year
        logger.info('Going back to search screen')
        driver.back()


def pages(driver):
    old = False
    new = True
    while old != new:
        old = driver.find_element_by_css_selector('body').get_attribute(
            'innerHTML'
        )
        counter = driver.find_element_by_css_selector(
            '''#search_results_table_paginate > span >
            a.fg-button.ui-button.ui-state-default.ui-state-disabled'''
        ).get_attribute('innerHTML')
        yield int(counter)
        logger.info('Fetching new page')
        driver.find_element_by_css_selector(
            '#search_results_table_next'
        ).click()
        new = driver.find_element_by_css_selector('body').get_attribute(
            'innerHTML'
        )


if __name__ == '__main__':
    browser = init()
    for year in years(browser, [2016]):
        for i in pages(browser):
            print(year, i)
            for row in browser.find_elements_by_css_selector(
                    'tr.election_item'
            ):
                tr_id = row.get_attribute('id')
                tr_id = tr_id.replace('election-id-', '')
                assert tr_id.isdigit()
                print(tr_id)

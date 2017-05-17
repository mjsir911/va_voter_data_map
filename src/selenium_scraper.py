#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib.request
from selenium import webdriver

__appname__     = ""
__author__      = "phufford"
__copyright__   = ""
__credits__     = ["phufford", "Marco Sirabella"]  # Authors and bug reporters
__license__     = "GPL"
__version__     = "1.0"
__maintainers__ = "Marco Sirabella"
__email__       = "msirabel@gmail.com"
__status__      = "Prototype"  # "Prototype", "Development" or "Production"
__module__      = ""

#path_to_chromedriver = './chromedriver'
driver = 'phantomjs-2.1.1-linux-x86_64/bin/phantomjs' # Default aptitude path
#browser = webdriver.PhantomJS(executable_path = driver)
browser = webdriver.PhantomJS()
url = 'http://historical.elections.virginia.gov'
browser.get(url)

def build_search_link(year, office_id):
    return url + '/elections/search/year_from:' + year + '/year_to:' + year + '/office_id:' + office_id

def get_csv_municipality_link(election_id):
    return url + '/elections/download/' + election_id + '/precincts_include:0/'

def get_csv_precinct_link(election_id):
    return url + '/elections/download/' + election_id + '/precincts_include:1/'

def download_csv(url, filename):
    print("downloading " + url)
    csv_file = open(filename + '.csv', 'wb')
    response = urllib.request.urlopen(url)
    csv_file.write(response.read())
    csv_file.close()
    print('response' + str(response))

def get_filename(election_row, election_id):
    filename = []
    for election_discriptor in election_row.find_elements_by_css_selector('td')[0:4]:
        filename.append(election_discriptor.text)
    return "_".join("-".join(filename).split(" "))

search_links = []
for office in browser.find_elements_by_css_selector("#SearchOfficeId optgroup option"):
    office.click()
    for year in browser.find_elements_by_css_selector("#SearchYearFrom option"):
        if year.text:
            search_link = build_search_link(year.text, office.get_property("value"))
            search_links.append(search_link)
print(search_links)

for link in search_links:
    browser.get(link)
    try:
        show_all = browser.find_element_by_xpath('//*[@id="search_results_table_length"]/label/select/option[4]')
    except:
        continue
    show_all.click()
    for election in browser.find_elements_by_css_selector('#search_results_table tbody tr'):
        election_id = election.get_property('id').split('-')[-1]
        if election_id:
            print(election_id)
            municipality_url = get_csv_municipality_link(election_id)
            precinct_url = get_csv_precinct_link(election_id)
            filename = get_filename(election, election_id)
            download_csv(precinct_url, filename + "-by_precinct")
            download_csv(municipality_url, filename + "-by_municipality")
            download_csv(municipality_url)


"""
        browser.find_element_by_xpath('//*[@id="SearchIndexForm"]/div[53]/input').click()
        browser.find_element_by_xpath('//*[@id="search_results_table_length"]/label/select/option[4]').click()
"""

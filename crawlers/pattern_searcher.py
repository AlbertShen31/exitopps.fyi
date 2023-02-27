# -*- coding: utf-8 -*-

#! /usr/bin/python

import sys

import time
import argparse
import requests

from util import *
from os.path import exists
from random import randint
from bs4 import BeautifulSoup

# TODO: implement bookmark feature (and overwrite results)

# bookmark of where you left off. Format: <index>, <google search page>
BOOKMARK_FILE = './data/_bookmark.csv'

# the number of max requests that can be made in a single session
MAX_REQUESTS = randint(25, 50)

REQUESTS_SO_FAR = 0

# a list of search patterns
SEARCH_PATTERNS  = [
    "site:rocketreach.co facebook software engineer",
    "site:rocketreach.co apple software engineer",
    "site:rocketreach.co amazon software engineer",
    "site:rocketreach.co microsoft software engineer",
    "site:rocketreach.co google software engineer",
]

def sleepForRandomInterval(low, high):
    """ input: range of seconds to randomly sleep for """
    random_sec = randint(low, high)
    print(f"sleeping for {random_sec}...")
    time.sleep(random_sec)

def isSlug(url_string):
    return u'›' in url_string

def appendOutputToFile(output, file_name):
    with open(file_name, 'a') as f:
        for url in output:
            f.write(url.strip() + '\n')

def updateBookmarkPosition(search_idx, page_idx):
    with open(BOOKMARK_FILE, 'r+') as f:
        data = f.read()
        f.seek(0)
        f.write(str(search_idx) + ',' + str(page_idx))
        f.truncate() 

def googleSearch(args, search_idx, page_idx, search_string):
    """ input: search query string
        output: a list of urls to visit
    """

    # search google for the search_string
    headers = {
        'user-agent': getRandomUserAgent(),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://www.google.com/'
    }
    url = "https://www.google.com/search?q=" + search_string
    url = url + "&num=100"
    page = requests.get(url, headers=headers).content
    parsed_page = BeautifulSoup(page, 'html.parser')

    # iterate through pages in results by checking for a next btn
    n = page_idx
    while True:
        try:
            
            if args.debug:
                print(page)

            # add all results on current page to response
            links = [x.text.strip() for x in parsed_page.find_all('span')]
            
            # get urls from the links 
            urls = list(set(url for url in links if isSlug(url)))
            urls = [url.split(u'›')[1].strip() for url in urls]
            print("found " + str(len(urls)) + " urls on the page:")
            print(urls)

            # if there are no urls, we are probably on a captcha;
            # so sleep for a very long time
            if len(urls) > 0:
                # write new urls to file
                appendOutputToFile(urls, args.output)

                # go to the next page and bookmark position
                n += 1
                updateBookmarkPosition(search_idx, n)
                page = requests.get(url + '&start=' + str(n*100), headers=headers).content
                parsed_page = BeautifulSoup(page, 'html.parser')

                # on last page, exit while True loop if no next buton
                if not parsed_page.find_all(id='pnnext'):
                    break
            else:
                sleepForRandomInterval(555, 1200)
                print("issueing a random google search...")
                issueRandomGoogleSearch()
                sleepForRandomInterval(1800, 3600)

        except Exception as e:
            print(e)
            break

        headers['user-agent'] = getRandomUserAgent()
        sleepForRandomInterval(27, 365)

def run(args):
    
    # retrieve bookmark from previous run
    if not exists(BOOKMARK_FILE):
        search_idx, page_idx = 0, 0 
        with open(BOOKMARK_FILE, 'w') as f:
            f.write(str(search_idx) + ',' + str(page_idx)) 
    else:
        with open(BOOKMARK_FILE, 'r') as f:
            search_idx, page_idx = f.readline().split(',')
            search_idx = int(search_idx.strip())
            page_idx  = int(page_idx.strip())

    print(f"Resuming search from pattern: {search_idx} and page: {page_idx}")
    
    # make a google search for search query
    for idx, search_string in enumerate(SEARCH_PATTERNS[search_idx:]):

        if args.debug:
            print("\n>>Searching for:{}".format(search_string))
        googleSearch(args, idx, page_idx, search_string)

        sleepForRandomInterval(27, 365)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', help='display debugging output while running')
    parser.add_argument('--output', '-o', default='./data/urls.csv', type=str, help='specify where to write (append) output')
    args = parser.parse_args()
    run(args)



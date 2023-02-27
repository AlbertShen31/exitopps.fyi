#! /usr/bin/python

import sys
import json
import time
import argparse
import requests

from util import *
from os.path import exists
from random import randint

# Google APi key
API_KEY = "API_KEY"

# Google Search Endpoint
API_ENDPOINT = 'https://www.googleapis.com/customsearch/v1'

# a list of search patterns
SEARCH_PATTERNS  = {
    'facebook': "site:rocketreach.co facebook software engineer",
    'apple': "site:rocketreach.co apple software engineer",
    'amazon': "site:rocketreach.co amazon software engineer",
    'microsoft': "site:rocketreach.co microsoft software engineer",
    'google': "site:rocketreach.co google software engineer",
}

def appendOutputToFile(output, file_name):
    with open(file_name, 'a') as f:
        f.write(output.strip() + '\n')

def googleSearch(args, search_string):
    """ input: search query string
        output: a list of urls to visit
    """
    for i in range(0, 100, 10):
        print("Parsing search results from page " + str(i))
        # search google for the search_string
        params = {
            'key': API_KEY,
            'cx': 'f32dae071a62b00f3',
            'q': search_string,
            'start': i, 
        }
        response = requests.get(API_ENDPOINT, params=params)
        response = response.json()

        output = [x['htmlFormattedUrl'].strip() for x in response['items']]
        output = '\n'.join(output)

        print("=====> output")
        print(output)
        appendOutputToFile(output, args.output)


def run(args):
    
    if not args.company in SEARCH_PATTERNS:
        raise Exception("provided company is not valid")

    # make a google search for search query
    search_string = SEARCH_PATTERNS[args.company]

    if args.debug:
        print("\n>>Searching for:{}".format(search_string))
    googleSearch(args, search_string)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', help='display debugging output while running')
    parser.add_argument('--output', '-o', default='./data/urls.csv', type=str, help='specify where to write (append) output')
    parser.add_argument('--company', '-c', type=str, choices=['apple', 'amazon', 'google', 'microsoft', 'facebook'], help='specify a company')
    args = parser.parse_args()
    run(args)



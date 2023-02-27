#! /usr/bin/python

import sys
import json
import traceback
import time
import argparse
import requests
from random import randint

from util import *
from os.path import exists
from random import randint
from bs4 import BeautifulSoup

COMPANIES = [
    'Facebook',
    'Microsoft',
    'Amazon',
    'Apple',
    'Google',
]

def sleepForRandomInterval(low, high):
    """ input: range of seconds to randomly sleep for """
    random_sec = randint(low, high)
    print(f"sleeping for {random_sec}...")
    time.sleep(random_sec)

def appendOutputToFile(output_line, file_name):
    with open(file_name, 'a') as f:
        f.write(output_line.strip() + '\n')

def formatCompanyLi(li_tag):
    """ input: beautifulsoup li tag for a single company 
        output: tuple of (title, company)
    """
    try:
        company, title = None, None
        try:
            company = li_tag.find('a').text.strip()
            title = li_tag.text.strip().split('@')[0]
            return (title, company)
        except:
            traceback.print_exc()

        if not company:
            company = li_tag.text.strip().split('@')[1]
            title = li_tag.text.strip().split('@')[0]
        return (title, company)
    except:
        return None

def parseUrl(args, url):
    """ input: a rocketreach url
        output: a parsed csv file of results
    """
    headers = {
        'user-agent': getRandomUserAgent(),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://www.google.com/'
    }

    page = requests.get(url, headers=headers)
    # if args.debug:
    #     print(page.content)
    time.sleep(2)
    soup = BeautifulSoup(page.content, 'html.parser')

    companies = []

    # parse out companies in the visible section
    visible_cos = []
    try:
        visible_cos = soup.find('ul', {'id': 'see-more-jobs-anchor'})
        visible_cos = visible_cos.find_all('li')
    except Exception as e:
        traceback.print_exc()

    # parse out companies in the "See More" section (initially hidden)
    invisible_cos = []
    try:
        
        joblists = soup.find_all('div', {'class': 'rr-see-more-items-list jobs'})[0]
        invisible_cos = joblists.find_all('ul')[1]
        invisible_cos = invisible_cos.find_all('li')
        
    except:
        traceback.print_exc()

    companies = visible_cos + invisible_cos
    companies = [formatCompanyLi(c) for c in companies]
    companies = [c for c in companies if c]
    companies.reverse()
    output_lines = []

    # output a graph edge for each connection in the list
    if not companies:
        return
    else:
        output_line = ','.join([url, '_university_', '_university_', companies[0][0], companies[0][1]])
        output_lines.append(output_line)
    if len(companies) <= 1:
        return
    else:
        for i in range(1, len(companies)):
            output_line = ','.join([url, companies[i-1][0], companies[i-1][1], companies[i][0], companies[i][1]])
            output_lines.append(output_line)

    output_lines = [o for o in output_lines if o]
    for output_line in output_lines:
        if args.debug:
            print(output_line)
        appendOutputToFile(output_line, args.output)

def convertLineToUrl(line):
    url = line.strip()
    if 'rocketreach.co' not in url:
        url = 'https://rocketreach.co/' + url
    if not url.startswith('https://'):
        url = 'https://' + url
    return url

def run(args):
    with open(args.input) as infile:
        for line in infile:
            url = convertLineToUrl(line)
            if args.debug:
                print("\n>>Parsing:{}".format(url))
            
            try:
                parseUrl(args, url)
            except Exception as e:
                traceback.print_exc()
            sleepForRandomInterval(21, 518)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', help='display debugging output while running')
    parser.add_argument('--input', '-i', default='./data/urls.csv', type=str, help='specify where urls input is')
    parser.add_argument('--output', '-o', default='./data/results_exitgraph.tsv', type=str, help='specify where to write (append) output')
    args = parser.parse_args()
    run(args)



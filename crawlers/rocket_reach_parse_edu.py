#! /usr/bin/python

import sys
import json
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
        f.write('\t'.join(output_line).strip() + '\n')

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
    soup = BeautifulSoup(page.content, 'html.parser')

    # parse out college and major
    try:
        education = soup.find('ul', {'id': 'see-more-education-anchor'})
        education = education.findChild().text.strip()
        education = education.split('Degree')
        college, major = education[0].strip(), education[-1].strip()
    except Exception as e:
        education, major = None, None

    # parse out FAANG company and index
    try:
        jobs = soup.find('div', {'class': 'rr-see-more-items-list jobs'})
        jobs = jobs.get_text()
        current_job = None
        for company in COMPANIES:
            if company in jobs:
                current_job = company 
                break

        output_line = [url, str(college), str(current_job), str(major)]
    except:
        return

    if args.debug:
        print(output_line)
        appendOutputToFile(output_line, args.output)
    else:
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
            parseUrl(args, url)
            sleepForRandomInterval(27, 365)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', help='display debugging output while running')
    parser.add_argument('--input', '-i', default='./data/urls.csv', type=str, help='specify where urls input is')
    parser.add_argument('--output', '-o', default='./data/results.tsv', type=str, help='specify where to write (append) output')
    args = parser.parse_args()
    run(args)



import sys
import argparse
import csv
import os
import re
	
COLLEGE_FILE = './colleges.tsv'
PARSED_FILE = './parsed.tsv'
unclassified = []
colleges = {}

def parse(line):
    if line == "":
        return

    url, college, company, major = line.split('\t')
    college = re.sub(r"[^a-zA-Z]","",college).lower()

    if company == "None":
        return

    for i in colleges.keys():
        if i in college:
            if company in colleges[i]:
                colleges[i][company].append(major)
            else:
                colleges[i][company] = [major]
            return
    unclassified.append(url + " " + college)
    

def appendOutputToFile(output_line, file_name):
    with open(file_name, 'a') as f:
        f.write('\t'.join(output_line).strip() + '\n')

def run(args):
    with open(COLLEGE_FILE, 'r') as f:
        for line in f:
            for i in line.split('\t'):
                temp = re.sub(r"[^a-zA-Z]","",i).lower()
                if '[' not in temp and temp != '':
                    colleges[temp] = {}

    with open(PARSED_FILE, 'r') as f:
        for line in f:
            parse(line)

    #TODO String similarity for remaining
    for i in unclassified:
        print(i + "\n")

    #Clear file before appending
    os.remove("../website/landingpage/data/counts.tsv")

    for i in colleges.keys():
        for j in colleges[i].keys():
            appendOutputToFile([i,j,str(len(colleges[i][j]))], "../website/landingpage/data/counts.tsv")


#TODO combine keys for colleges with multiple names(Use first column as base)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', help='display debugging output while running')
    parser.add_argument('--output', '-o', default='./data/urls.csv', type=str, help='specify where to write (append) output')
    args = parser.parse_args()
    run(args)

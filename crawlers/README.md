## SETUP (if first time)
`cd ~/Projects/exitopps/crawlers/ && python3 -m venv exitopps_crawlers`
`source exitopps_crawlers/bin/activate`

(Install Requirements)
`pip install -r requirements.txt`

Create a data directory
`cd ~Projects/exitopps/crawlers && mkdir data`

## ACTIVATE (when developing)
`source exitopps_crawlers/bin/activate`

## RUN URL SEARCHER
this command produces a file called data/urls.csv which contains rocket-reach slugs
`python pattern_searcher.py`

## RUN rocket_reach_parse_edu
this command produces a file called college_histogram.csv which contains counts on company destinations for different colleges
`python rocket_reach_parse_edu.py`

the format of the output will look like this:
```
college \t company \t prev_company \t major
harvard university  \t facebook \t amazon \t computer science, anthropology
harvard university, \t facebook \t ibm \t computer science
...
```

## RUN rocket_reach_parse_exitgraph
this command produces a file which contains exit opps per company
`python rocket_reach_parse_exitgraph.py`

the format of the output will look like this:
```
```

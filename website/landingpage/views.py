# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import os
import math

from django.shortcuts import render
from django.views import generic
from django.conf import settings

from .models import Post

from plotly.offline import plot
from plotly.graph_objs import Scatter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from user_agents import parse

import numpy as np
import pandas as pd
import re
import networkx as nx
import random

from pyvis.network import Network

def index(request):
    college_plot, company = collegePlot(request)

    exitPlot(request)
    
    return render(request, "index.html", context={'college_plot': college_plot, 'company_name': company})


def collegePlot(request):
    colleges = []
    companies = []
    counts = []

    dataPath = os.path.join(os.path.dirname(__file__), "data/counts.tsv")

    # for path in [collegePath, companyPath, dataPath]:
    with open(dataPath, 'r') as file:
        csvreader = csv.reader(file, delimiter = "\t")

        for row in csvreader:
            colleges.append(row[0])
            companies.append(row[1])
            counts.append(int(row[2]))

    data = {} # {company: [[], count, other_count}
    specs = []
    titles = []

    for i in range(len(companies)):
        if companies[i] not in data:
            data[companies[i]] = [[],[],0]
        if counts[i] <= 1:
            data[companies[i]][2] += 1
        else:
            data[companies[i]][0].append(colleges[i])
            data[companies[i]][1].append(counts[i])    
    
    # agg. "Other" counts
    for i, comp in enumerate(data):
        data[comp][0].append("Other")
        data[comp][1].append(data[comp][2])


    # render pie charts
    for company in data:
        specs.append([{"type": "pie"}])
        titles.append(company)

    # render table
    specs.append([{"type": "table"}])
    titles.append("Table")    

    # get selected chart
    chart_type = request.GET.get('chart_type', 'pie')
    company = request.GET.get('company', 'Facebook')

    fig = None
    if chart_type == 'pie':
        fig = go.Figure(
            data = go.Pie(
                labels=data[company][0], 
                values=data[company][1],
            )
        )
    elif chart_type == 'table':
        fig = go.Figure(
            data = go.Table(header=dict(values=['College', 'Company', 'Count']), 
                cells=dict(values=[colleges,companies,counts]))
        )
    else:
        raise Exception("Invalid Chart / Company Value specified")

    # set dimensions based on device
    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_str)

    width, height = 1000, 500
    chart_margins = dict(t=50, b=50, l=50, r=50)

    if user_agent.is_mobile:
        width, height = 350, 450
        chart_margins = dict(t=20, b=20, l=20, r=20)
        fig.update_traces(textposition='inside')
    elif user_agent.is_tablet:
        width, height = 800, 500

    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'width': width,
        'height': height,
        'showlegend': not user_agent.is_mobile,
        'legend':dict(
            title_font_family="Sans-Serif",
            font=dict(
                family="Sans-Serif",
                size=13,
                color='white'
            ),
            bgcolor="#007D8E",
            bordercolor="#007D8E",
            borderwidth=2,
            y=0.94
        ),
        'uniformtext_minsize': 12,
        'uniformtext_mode': 'hide',
        'margin': chart_margins,
    })

    return plot(fig, output_type='div', show_link=False, link_text=""), company



def exitPlot(request):
    #Read Data
    data=[]
    company = request.GET.get('company', 'Facebook')
    # data = [["Google","Facebook"],["Google","Facebook"],["Apple","Facebook"],["Microsoft","Facebook"], ["Facebook","Google"],["Facebook","Amazon"]]
    exclude = ["_university_"]
    university = ["university", "college", "institute", "school"]

    dataPath = os.path.join(os.path.dirname(__file__), "data/results_exitgraph.tsv")
    with open(dataPath, 'r') as file:
        csvreader = csv.reader(file, delimiter = "\t")

        for row in csvreader:
            
            for i in university:
                if i in row[2].lower():
                    row[2] = "University"

                if i in row[4].lower():
                    row[4] = "University"

            if (row[2] not in exclude and row[4] not in exclude) and row[2] != row[4]:
                data.append([row[2], row[4]])

    defaultSize = 25
    sizeMultiplier = 2.5
    radius = 400

    exit_graph = Network(width="100%", bgcolor="#D9EDDF", directed=True)
    exit_graph.inherit_edge_colors(False)
    exit_graph.set_edge_smooth('dynamic')
    exit_graph.add_node(company, label=company, x=0, y=0, color="#13D098")

    leftNodes = {}
    rightNodes = {}
    edges={}

    for i in data:
        first, second = i
        if first == company:
            nodeLabel = "R_" + second
            exit_graph.add_node(nodeLabel, label=second, title=second, size=defaultSize, color="#007D8E")
            rightNodes[nodeLabel] = rightNodes.get(nodeLabel, 0) + 1
            if (company+":"+nodeLabel) not in edges:
                print(company+":"+nodeLabel)
                exit_graph.add_edge(company, nodeLabel, title=company+":"+nodeLabel, arrowStrikethrough=False)
            edges[company+":"+nodeLabel] = edges.get(company+":"+nodeLabel, 0) + 1
        elif second == company:
            nodeLabel = "L_" + first
            exit_graph.add_node(nodeLabel, label=first, title=first, size=defaultSize, color="#007D8E")
            leftNodes[nodeLabel] = leftNodes.get(nodeLabel, 0) + 1
            if (nodeLabel+":"+company) not in edges:
                exit_graph.add_edge(nodeLabel, company, title=nodeLabel+":"+company, arrowStrikethrough=False)
            edges[nodeLabel+":"+company] = edges.get(nodeLabel+":"+company, 0) + 1

    company_count = len(leftNodes) + len(rightNodes)
    exit_graph.get_node(company)["size"] = defaultSize + (company_count * sizeMultiplier)
    exit_graph.get_node(company)["title"] = company + ": " + str(company_count)
    exit_graph.get_node(company)["fixed"] = {"x": True, "y": True}
    exit_graph.get_node(company)["font"] = {"size": max(40, company_count)}

    if (company_count > 50):
        radius = 800

    for e in exit_graph.get_edges():
        label = e["title"]
        e["title"] = edges[label]
        e["width"] = 10
        e["color"] = "#007d8e5b"


    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_str)

    leftPoints = nodeArcXY(len(leftNodes), radius, True)
    rightPoints = nodeArcXY(len(rightNodes), radius)
    
    if user_agent.is_mobile:
        leftPoints = nodeArcXY(len(leftNodes), radius, True, vertical=3)
        rightPoints = nodeArcXY(len(rightNodes), radius, vertical=3)

    i=0
    for l in leftNodes.keys():
        n = exit_graph.get_node(l)
        n["title"] = n["label"] + ": " + str(leftNodes[l])
        n["fixed"] = {"x": True, "y": False}
        n["font"] = {"size": 20}
        n["size"] += leftNodes[l] * sizeMultiplier
        x,y = leftPoints[i]
        n["x"] = x
        n["y"] = y
        i+=1
    
    
    i=0
    for r in rightNodes.keys():
        n = exit_graph.get_node(r)
        n["title"] = n["label"] + ": " + str(rightNodes[r])
        n["fixed"] = {"x": True, "y": False}
        n["font"] = {"size": 20}
        n["size"] += rightNodes[r] * sizeMultiplier
        x,y = rightPoints[i]
        n["x"] = x
        n["y"] = y
        i+=1
    
    exit_graph.barnes_hut(gravity=-2000,
        central_gravity=0.3,
        spring_length=250,
        spring_strength=0.001,
        damping=0.09,
        overlap=0.7)

    exit_graph.save_graph(str(settings.BASE_DIR)+'/templates/pvis_graph_file.html')

#Return (x,y) values along an arc for points split into 
#vertical=1 default setting for desktop vertical=2 for more vertical arc for mobile screens
def nodeArcXY(size, radius, left=False, vertical=1):
    points = []

    if size <= 1 and left:
        return [(-radius,0)]
    elif size <= 1 and not left:
        return [(radius,0)]

    startAngle=math.pi/4
    arcSize=math.pi/2

    if left:
        startAngle = math.pi*5/4

    count = min(10, size)
    for i in range(size):
        arcNum = i//count
        place = i%count
        angle = startAngle - (arcSize/(count-1)*place) + (random.randint(-20,20) * math.pi/100) 
        x = math.cos(angle) * (radius + (150/vertical*arcNum)) 
        y = math.sin(angle) * (radius + (150*arcNum))
        points.append((x,y))

    return points

class Privacy(generic.TemplateView):
    template_name = 'privacy.html'









#from plotly.offline import plot
#from plotly.graph_objs import Scatter
#import plotly.graph_objects as go
import plotly.express as px

def display_test():
    test = plot([Scatter(x=[1, 2, 3], y=[3, 1, 6])], output_type='div')
    return test

def BMI(weight, height_string):
    height_string = height_string.rstrip("''")
    height_split = height_string.split("'")
    height = (int(height_split[0])*12) + int(height_split[1])
    bmi = (703*weight)/(height*height)
    return bmi

def weight_display(user_info):
    weights = []
    date = []
    count = 0
    for entry in user_info:
        weights.append(entry.weight)
        date.append(count)
        count = count+1
    fig = px.line(x=date, y=weights, title="Weight")
    fig.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="Weight")
    graph = fig.to_html()
    return graph

def height_display(user_info):
    heights = []
    date = []
    count = 0
    for entry in user_info:
        heights.append(entry.height)
        date.append(count)
        count = count+1
    fig = px.line(x=date, y=heights, title="Height")
    fig.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="Height")
    graph = fig.to_html()
    return graph

def bmi_display(user_info):
    bmi = []
    date= []
    count = 0
    for entry in user_info:
        bmi.append(BMI(entry.weight, entry.height))
        date.append(count)
        count = count+1
    
    fig = px.line(x=date, y=bmi, title="BMI")
    fig.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="BMI")
    graph = fig.to_html()
    return graph
import plotly.express as px
import math
import datetime

def BMI(weight, height_string):
    height_string = height_string.rstrip("''")
    height_split = height_string.split("'")
    height = (int(height_split[0])*12) + int(height_split[1])
    bmi = (703*weight)/(height*height)
    return bmi

def BMR(entry, weight):
    lean = 1
    genderNum = 1
    if entry.gender == "male":
        genderNum = 1
        if entry.age >= 28:
            lean = .85
        elif entry.age >= 21:
            lean = .9
        elif entry.age >= 15:
            lean = .95
    if entry.gender == "female":
        genderNum = .9
        if entry.age >= 38:
            lean = .85
        elif entry.age >= 29:
            lean = .9
        elif entry.age >= 19:
            lean = .95
    return 1.55*((weight/2.2)*genderNum*24*lean)
    

def weight_display(user_info):
    weights = []
    date = []
    for entry in user_info:
        weights.append(entry.weight)
        date.append(entry.date)
    fig = px.line(x=date, y=weights, title="Weight")
    fig.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="Weight")
    graph = fig.to_html()
    return graph

def height_display(user_info):
    heights = []
    date = []
    for entry in user_info:
        heights.append(entry.height)
        print(entry.date)
        date.append(entry.date)
    fig = px.line(x=date, y=heights, title="Height")
    fig.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="Height")
    graph = fig.to_html()
    return graph

def bmi_display(user_info):
    bmi = []
    date= []
    for entry in user_info:
        bmi.append(BMI(entry.weight, entry.height))
        date.append(entry.date)
    
    fig = px.line(x=date, y=bmi, title="BMI")
    fig.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="BMI")
    graph = fig.to_html()
    return graph

def calorie_display(user_info):
    calories = []
    date = []
    for entry in user_info:
        if entry.calories is not None:
            calories.append(entry.calories)
        else:
            bmr = BMR(entry, entry.weight)
            calories.append(bmr)
        date.append(entry.date)
    fig = px.line(x=date, y=calories, title="Calories")
    fig.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="Calories")
    graph = fig.to_html()
    return graph

def estimate_BMI(user_info, calorie_intake):
    bmi = []
    bmr = 0
    date = []
    weights = []
    weight = user_info[-1].weight
    start = user_info[-1].date
    extra_calories = 0
    for entry in calorie_intake:
        bmr = BMR(user_info[-1], weight)
        extra_calories = entry - bmr
        weight += extra_calories/3500
        weights.append(weight)
        bmi.append(BMI(weight, user_info[-1].height))
        date.append(start)
        start += datetime.timedelta(days=1)

    fig = px.line(x=date, y=bmi, title="BMI")
    fig.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="BMI")
    graph1 = fig.to_html()

    fig = px.line(x=date, y=weights, title="Weight")
    fig.update_layout(title_x=0.5, xaxis_title="Date", yaxis_title="Weight")
    graph2 = fig.to_html()
    return graph1, graph2

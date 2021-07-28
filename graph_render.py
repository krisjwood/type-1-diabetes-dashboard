import pygal 
import processing as p
import datetime as dt
import sqlite3 as sql


# Graphs for Overview
def past_1h():
    # Fetch current timeframe
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    sql_q = '''SELECT bg FROM glucosedata ORDER BY id DESC LIMIT 12'''
    temp = cursor.execute(sql_q)

    past_1h_bg = []
    for x in temp:
        past_1h_bg.append(x[0])

    past_1h_bg.reverse()

    # Render graph
    line_chart = pygal.Line()
    line_chart.title = 'Past hour'
    # line_chart.x_labels = map(str, ([x for x in time_list]))
    # line_chart.y_labels = 
    line_chart.x_title='Reading interval - 5 mins'
    line_chart.y_title='mmol/L'
    line_chart.add('BG', past_1h_bg)
    past_24h = line_chart.render_data_uri()

    return past_24h


def past_24h():
    # Fetch current timeframe
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    sql_q = '''SELECT bg FROM glucosedata ORDER BY id DESC LIMIT 288'''
    temp = cursor.execute(sql_q)

    past_24h_bg = []
    for x in temp:
        past_24h_bg.append(x[0])

    past_24h_bg.reverse()

    # Render graph
    line_chart = pygal.Line()
    line_chart.title = 'Past 24 hours'
    # line_chart.x_labels = map(str, ([x for x in time_list]))
    # line_chart.y_labels = 
    line_chart.x_title='Reading interval - 5 mins'
    line_chart.y_title='mmol/L'
    line_chart.add('BG', past_24h_bg)
    past_24h = line_chart.render_data_uri()

    return past_24h


def past_seven_days():
    # Get today's date
    today = dt.date.today()
    # Date in string format
    today_str = today.strftime("%Y-%m-%d")
    # Day in int format
    timescale_days = 24*7

    # Create connection to database
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    sql_q = '''SELECT date, weekday, hour, AVG(bg) FROM glucosedata GROUP BY date, hour ORDER BY date DESC'''

    # Fetch data and put previous 7 days in a list, excluding current day (as probably won't have 100% coverage) 
    data_list = []
    temp = cursor.execute(sql_q)
    for x in temp:
        if x[0] != today_str:
            data_list.append(list(x))
    data_list = data_list[:timescale_days]
        
    # Get weekdays from data list (in descending order) and put in own list
    weekdays = []
    for x in data_list:
        if x[1] not in weekdays:
            weekdays.append(x[1])


    # Organise data for graph
    graph_data = []
    for x in weekdays:
        temp_list = []
        temp_list.append(x)
        for y in data_list:
            y[3] = round(y[3], 1)
            if y[1] == x:
                temp_list.append(y[3])
        graph_data.append(temp_list)


    line_chart = pygal.Line()
    line_chart.title = 'Past 7 days'
    line_chart.x_labels = weekdays
    line_chart.x_labels = range(0, 24)
    line_chart.add(graph_data[0][0], graph_data[0][1:])
    line_chart.add(graph_data[1][0], graph_data[1][1:])
    line_chart.add(graph_data[2][0], graph_data[2][1:])
    line_chart.add(graph_data[3][0], graph_data[3][1:])
    line_chart.add(graph_data[4][0], graph_data[4][1:])
    line_chart.add(graph_data[5][0], graph_data[5][1:])
    line_chart.add(graph_data[6][0], graph_data[6][1:])
    past_seven_days = line_chart.render_data_uri()

    return past_seven_days


def range_stackedbar():
    stats_list = p.stats_processing()

    # Ranges in stacked bar chart
    stats_list = list(stats_list)
    stats_list.pop(-1)

    range_list = []
    for time in stats_list:
        for t in time:
            t.pop(0)
            timeframe = t[0]
            very_high = t[1]['Stats']['Very High']
            high = t[1]['Stats']['High']
            in_range = t[1]['Stats']['In range']
            low = t[1]['Stats']['Low']
            very_low = t[1]['Stats']['Very low']
            value_list = [timeframe, very_high, high, in_range, low, very_low]
            range_list.append(value_list)

    vh, h, r, l, vl = [], [], [], [], []
    timescales = []
    for x in range_list:
        timescales.append(x[0])
        vh.append(x[1])
        h.append(x[2])
        r.append(x[3])
        l.append(x[4])
        vl.append(x[5])
    final_list = [vh, h, r, l, vl]

    # Build chart
    range_stackedbar = pygal.StackedBar(legend_at_bottom=True, legend_at_bottom_columns=5)
    range_stackedbar.title = 'Glucose level range'
    range_stackedbar.x_labels = map(str, ([x for x in timescales]))
    range_stackedbar.y_title='%'
    range_stackedbar.add('<3', final_list[4])
    range_stackedbar.add('<4', final_list[3])
    range_stackedbar.add('4-8', final_list[2])
    range_stackedbar.add('>8', final_list[1])
    range_stackedbar.add('>15', final_list[0])
    range_stackedbar_chart = range_stackedbar.render_data_uri()

    return range_stackedbar_chart


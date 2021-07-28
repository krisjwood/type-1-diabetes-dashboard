from os import stat_result
import sqlite3 as sql
import statistics as stat
import datetime as dt


def stats_processing():
    '''Process data in statistics'''
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    master_object = cursor.execute('SELECT * FROM glucosedata ORDER BY id DESC')

    bg_list = []
    master_list = []

    for record in master_object:
        master_list.append(record)
        bg_list.append(record[3]) # List of only glucose levels for statistical analysis

    # Timescales (readings per timescale)
    hour = 12 # 60 / 5
    day = 24 * hour
    week = 7 * day
    month = 30 * day
    quarter = 3 * month
    year = 365 * day
    all = len(master_list)
    ##best_weekday = 5.5


    stat_titles = ['Total', 'Min', 'Max', 'Mean', 'Median', 'Mode', 'Std Dev', '25th', 'IQR', '75th', 'Very High', 'High', 'In range', 'Low', 'Very low']
    stats_list = [[hour, '1h', {'Stats': {'Total': [], 'Coverage': [], 'Min': [], 'Max': [], 'Mean': [], 'Median': [], 'Mode': [], 'Std Dev': [], '25th percentile': [], 'IQR percentile': [], '75th percentile': [], 'Very High': [], 'High': [], 'In range': [], 'Low': [], 'Very low': []}}], 
        [day, '24h', {'Stats': {'Total': [], 'Coverage': [], 'Min': [], 'Max': [], 'Mean': [], 'Median': [], 'Mode': [], 'Std Dev': [], '25th percentile': [], 'IQR percentile': [], '75th percentile': [], 'Very High': [], 'High': [], 'In range': [], 'Low': [], 'Very low': []}}], 
        [week, '7 days', {'Stats': {'Total': [], 'Coverage': [], 'Min': [], 'Max': [], 'Mean': [], 'Median': [], 'Mode': [], 'Std Dev': [], '25th percentile': [], 'IQR percentile': [], '75th percentile': [], 'Very High': [], 'High': [], 'In range': [], 'Low': [], 'Very low': []}}], 
        [month, '30 days', {'Stats': {'Total': [], 'Coverage': [], 'Min': [], 'Max': [], 'Mean': [], 'Median': [], 'Mode': [], 'Std Dev': [], '25th percentile': [], 'IQR percentile': [], '75th percentile': [], 'Very High': [], 'High': [], 'In range': [], 'Low': [], 'Very low': []}}], 
        [quarter, '3 months', {'Stats': {'Total': [], 'Coverage': [], 'Min': [], 'Max': [], 'Mean': [], 'Median': [], 'Mode': [], 'Std Dev': [], '25th percentile': [], 'IQR percentile': [], '75th percentile': [], 'Very High': [], 'High': [], 'In range': [], 'Low': [], 'Very low': []}}], 
        [year, '12 months', {'Stats': {'Total': [], 'Coverage': [], 'Min': [], 'Max': [], 'Mean': [], 'Median': [], 'Mode': [], 'Std Dev': [], '25th percentile': [], 'IQR percentile': [], '75th percentile': [], 'Very High': [], 'High': [], 'In range': [], 'Low': [], 'Very low': []}}], 
        [all, 'All time', {'Stats': {'Total': [], 'Coverage': [], 'Min': [], 'Max': [], 'Mean': [], 'Median': [], 'Mode': [], 'Std Dev': [], '25th percentile': [], 'IQR percentile': [], '75th percentile': [], 'Very High': [], 'High': [], 'In range': [], 'Low': [], 'Very low': []}}]]

    for x in stats_list:
        ##master_list_timescale = master_list[:x[0]]
        bg_list_timescale = bg_list[:x[0]]

        total_records = len(bg_list_timescale)
        
        coverage = round(total_records / x[0] * 100, 1)
        
        # Stats
        min_bg = min(bg_list_timescale)
        max_bg = max(bg_list_timescale)
        avg_bg = round(stat.mean(bg_list_timescale), 1)
        median_bg = round(stat.median(bg_list_timescale), 1)
        mode_bg = round(stat.mode(bg_list_timescale), 1)
        stddev_bg = round(stat.stdev(bg_list_timescale), 1)
        quart_bg = stat.quantiles(bg_list_timescale, n=4)
        quart25_bg = round(quart_bg[0], 1)
        quartIQR_bg = round(quart_bg[1], 1)
        quart75_bg = round(quart_bg[2], 1)

        # Range percentages
        bg_targets = [3, 4, 8, 15] # 0.Low,  1.in-range,  2.high,  3.very high
        very_high_bgs = round((sum(map(lambda x : x >= bg_targets[3], bg_list_timescale)) / total_records) * 100, 1)
        high_bgs = round((sum(map(lambda x : x >= bg_targets[2] and x < bg_targets[3], bg_list_timescale)) / total_records) * 100, 1)
        in_range_bgs = round((sum(map(lambda x : x >= bg_targets[1] and x < bg_targets[2], bg_list_timescale)) / total_records) * 100, 1)
        low_bgs = round((sum(map(lambda x : x >= bg_targets[0] and x < bg_targets[1], bg_list_timescale)) / total_records) * 100, 1)
        very_low_bgs = round((sum(map(lambda x : x <= bg_targets[0], bg_list_timescale)) / total_records) * 100, 1)


        # Append stats to stats_list dicts
        x[2]['Stats']['Total'] = total_records
        x[2]['Stats']['Coverage'] = coverage
        x[2]['Stats']['Min'] = min_bg
        x[2]['Stats']['Max'] = max_bg
        x[2]['Stats']['Mean'] = avg_bg
        x[2]['Stats']['Median'] = median_bg
        x[2]['Stats']['Mode'] = mode_bg
        x[2]['Stats']['Std Dev'] = stddev_bg
        x[2]['Stats']['25th percentile'] = quart25_bg
        x[2]['Stats']['IQR percentile'] = quartIQR_bg
        x[2]['Stats']['75th percentile'] = quart75_bg
        x[2]['Stats']['Very High'] = very_high_bgs
        x[2]['Stats']['High'] = high_bgs
        x[2]['Stats']['In range'] = in_range_bgs
        x[2]['Stats']['Low'] = low_bgs
        x[2]['Stats']['Very low'] = very_low_bgs

    all_stats = (stats_list, stat_titles)
    return all_stats


def latest_stamp():
    '''Fetch latest record in SQLite database'''
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    object_stamp = cursor.execute('SELECT * FROM glucosedata ORDER BY id DESC LIMIT 1')
    latest_record = [x for x in object_stamp]
    latestdate = latest_record[0][1]
    latesttime = latest_record[0][2]
    latest_stamp = (latestdate, latesttime)
    
    return latest_stamp


def weekday_avg():
    '''Fetch weekday data'''
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    
    # Best and worst weekday
    object = cursor.execute('SELECT AVG(bg), weekday FROM glucosedata GROUP BY weekday ORDER BY weekday')
    weekday_avg = []
    for x in object:
        day = x[1]
        bg =  x[0]
        list_temp = [round(bg, 1), day]
        weekday_avg.append(list_temp)
    # Day order
    weekday_avg[1], weekday_avg[0] = weekday_avg[0], weekday_avg[1]
    weekday_avg[5], weekday_avg[1] = weekday_avg[1], weekday_avg[5]
    weekday_avg[6], weekday_avg[2] = weekday_avg[2], weekday_avg[6]
    weekday_avg[4], weekday_avg[3] = weekday_avg[3], weekday_avg[4]
    weekday_avg[5], weekday_avg[4] = weekday_avg[4], weekday_avg[5]
    weekday_avg[6], weekday_avg[5] = weekday_avg[5], weekday_avg[6]

    weekday_best_worst = sorted(weekday_avg)
    best_weekday = weekday_best_worst[0]
    worst_weekday = weekday_best_worst[-1]

    # Pack Tuple
    weekdays_sorted = (weekday_avg, best_weekday, worst_weekday)

    return weekdays_sorted


def timeOfday_avg():
    '''Fetch time of day data'''
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    
    # Best and worst weekday
    object = cursor.execute('SELECT AVG(bg), timeofday FROM glucosedata GROUP BY timeofday ORDER BY timeofday;')
    timeofday_avg = []

    for x in object:
        time = x[1]
        bg =  x[0]
        list_temp = [round(bg, 1), time]
        timeofday_avg.append(list_temp)
    # Day order
    timeofday_avg[2], timeofday_avg[0] = timeofday_avg[0], timeofday_avg[2]
    timeofday_avg[2], timeofday_avg[1] = timeofday_avg[1], timeofday_avg[2]

    
    timeofday_best_worst = sorted(timeofday_avg)
    best_time = timeofday_best_worst[0]
    worst_time = timeofday_best_worst[-1]

    # Pack Tuple
    weekdays_sorted = (timeofday_avg, best_time, worst_time)

    return weekdays_sorted


def day_avgs(timeframe):
    # Timescales for calculations
    hour = 12 # 60 / 5
    day = 24 * hour

    # Fetch current timeframe
    num_days = int(timeframe / day + 1)
    print("Number of days:", num_days - 1)

    # Connect to database
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    temp = cursor.execute("SELECT date, AVG(bg), weekday FROM glucosedata GROUP BY date ORDER BY date DESC LIMIT ?", (num_days,))

    # Get today's date
    today = dt.date.today()

    # YY/mm/dd
    date_str = today.strftime("%Y-%m-%d")

    # Clean list
    day_avg = []
    for x in temp:
        x = list(x)
        day_avg.append(x)
        

    for x in day_avg:
        x[1] = round(x[1], 1)

    for x in day_avg:
        if x[0] == date_str:
            day_avg.remove(x)
    
    return day_avg
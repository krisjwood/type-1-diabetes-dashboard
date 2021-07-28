import os
from flask import Flask, render_template, request, redirect, url_for, session
from fetch_and_import import sql_import
import sqlite3 as sql
import processing as p
import graph_render as gr
from helper import login_required, apology


# Execute data update
ntz = sql_import()

# Define app
app = Flask(__name__)

# Key for session
app.secret_key = os.urandom(24)


@app.route('/')
@login_required
def index():
    '''Stats'''
    
    # Main table of stats
    all_stats = p.stats_processing()
    (stats_list, stat_titles) = all_stats
    
    # Update stats
    readings_str = '{:,}'.format(stats_list[-1][-1]['Stats']['Total'])
    
    total_data_days = round(stats_list[-1][-1]['Stats']['Total'] / 288, 1)
    total_data_days = '{:,.1f}'.format(total_data_days)

    latest_stamp = p.latest_stamp()
    (latestdate, latesttime) = latest_stamp

    # Weekday table
    weekdays_sorted = p.weekday_avg()
    (weekday_avg, best_weekday, worst_weekday) = weekdays_sorted
    
    # Time of day table
    timeofday_sorted = p.timeOfday_avg()
    (timeofday_avg, best_time, worst_time) = timeofday_sorted

    # Render graphs
    past_1h = gr.past_1h()
    past_24h = gr.past_24h()
    past_seven_days = gr.past_seven_days()
    range_stackedbar_chart = gr.range_stackedbar()


    return render_template('index.html', past_1h=past_1h, range_stackedbar_chart=range_stackedbar_chart, past_24h=past_24h, past_seven_days=past_seven_days, latestdate=latestdate, latesttime=latesttime, stats_list=stats_list, stat_titles=stat_titles, 
    weekday_avg=weekday_avg, timeofday_avg=timeofday_avg, total_data_days=total_data_days, readings_str=readings_str, 
    best_time=best_time, worst_time=worst_time, best_weekday=best_weekday, worst_weekday=worst_weekday)


@app.route('/timeframe', methods=["GET", "POST"])
@login_required
def timeframe():
    '''Choose graph timeframe'''
    # Fetch list of available timeframes
    stats_list = p.stats_processing()
    tf_temp = list(stats_list)
    tf_temp.pop(-1)
    timeframe_list = []

    for x in tf_temp:
        for y in x:
            tf_text = y[1]
            tf_readings = y[0]
            coverage = y[2]['Stats']['Coverage']
            timeframe_list.append([tf_text, tf_readings, coverage])
    
    if request.method == "POST":
        
        # Get user input 
        graph_timeframe = request.form.get("graph_timeframe")
        key = 1

        conn = sql.connect('diabetesdata.db')
        cursor = conn.cursor()
        sql_q = '''UPDATE timeframe SET time = ? WHERE key = ?'''
        cursor.execute(sql_q, (graph_timeframe, key))
        conn.commit()

        return redirect('/graph')

    else:
        return render_template('timeframe.html', timeframe_list=timeframe_list)
    

@app.route('/graph')
@login_required
def graph():
    '''Graphs'''
    global graph_timeframe
    global timeframe_stat

    # Fetch current timeframe
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    sql_q = '''SELECT time FROM timeframe WHERE key = 1'''
    temp = cursor.execute(sql_q)
    for x in temp:
        graph_timeframe = x[0]
    
    # Main table of stats
    all_stats = p.stats_processing()
    (stats_list, stat_titles) = all_stats

    for stat in stats_list:
        if stat[2]['Stats']['Total'] == graph_timeframe:
            timeframe_stat = stat

    # Day averages for timeframe
    day_avgs = p.day_avgs(graph_timeframe)

    # Graphs
    range_stackedbar_chart = gr.range_stackedbar() # graph_timeframe


    return render_template('graphs.html',  day_avgs=day_avgs, timeframe_stat=timeframe_stat, range_stackedbar_chart=range_stackedbar_chart, stats_list=stats_list, stat_titles=stat_titles)

            
@app.route('/diary', methods=["GET", "POST"])
@login_required
def diary():
    '''Patient diary'''
    
    if request.method == "POST":

        if request.form.get("delete"):
            delete = request.form.get("delete")
            conn = sql.connect('diabetesdata.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM diary WHERE id = ?;', delete)
            conn.commit()
            return redirect('diary')
        else:
            edit = request.form.get("edit")
            return render_template('edit.html', edit=edit) 
    else:
        conn = sql.connect('diabetesdata.db')
        cursor = conn.cursor()
        diary_object = cursor.execute('SELECT * FROM diary ORDER BY date DESC')

        diary_log = []
        for entry in diary_object:
            diary_log.append(entry)
        
        return render_template('diary.html', diary_log=diary_log)


@app.route('/add', methods=["GET", "POST"])
@login_required
def add():
    '''Add diary entry''' 
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Get user input 
        date = request.form.get("date")
        info = request.form.get("info")
        
        conn = sql.connect('diabetesdata.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO diary (date, info) VALUES (?, ?)', (date, info))
        conn.commit()

        return redirect('/diary')

    else:
        return render_template('add.html')


@app.route('/edit', methods=["GET", "POST"])
@login_required
def edit():
    '''Edit diary entry''' 

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        edit = request.form.get("edit")

        conn = sql.connect('diabetesdata.db')
        cursor = conn.cursor()
        edit_object = cursor.execute('SELECT * FROM diary WHERE id = ?', (edit,))
        
        # Convert sql object into list
        edit_entry = []
        for x in edit_object:
            edit_entry.append([x[0], x[1], x[2]])
            edit_entry = edit_entry[0] 
        
        return render_template('edit.html', edit_entry=edit_entry)


@app.route('/save_edit', methods=["GET", "POST"])
@login_required
def save_edit():
    '''Save editted diary entry''' 
  
    if request.method == "POST":
        id = request.form.get("id")
        info = request.form.get("info")

        conn = sql.connect('diabetesdata.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE diary SET info = ? WHERE id = ?', (info, id,))
        conn.commit()

        return redirect('/diary')



@app.route('/delete', methods=["GET", "POST"])
@login_required
def delete():
    '''Delete diary entry''' 

    if request.method == "POST":
        
        delete = request.form.get("delete")
        
        conn = sql.connect('diabetesdata.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM diary WHERE id = ?;', (delete,))
        conn.commit()

        return redirect('diary')


@app.route('/log')
@login_required
def log(ntz=ntz):
    '''Data log''' 

    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()
    records_log = cursor.execute('SELECT * FROM glucosedata ORDER BY id DESC')

    return render_template('log.html', records_log=records_log, ntz=ntz)


@app.route('/login', methods=["GET", "POST"])
def login():
    '''Login page'''

    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("user"):
            return apology("No username given", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("No password given", 403)
        
        user = request.form.get("user")
        password = request.form.get("password")

        # Query database for username
        conn = sql.connect('diabetesdata.db')
        cursor = conn.cursor()
        details = list(cursor.execute("SELECT * FROM session WHERE user = ?", (user,)))

        user_list = []
        for x in details:
            user_list.append([x[0], x[1], x[2]])

        # Ensure username exists
        if len(user_list) != 1:
            return apology("No username found", 403)
        
        if password != user_list[0][2]:
            return apology("Incorrect password", 403)

        # Remember which user has logged in
        session["user_id"] = user_list[0]

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("login")

 
if __name__ == "__main__":
    app.run(debug=True)

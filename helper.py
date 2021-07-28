import pytz
import datetime as dt
import calendar as cal
from functools import wraps
from flask import session, redirect, render_template

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def convert (input):
    '''Convert mmol/l from mg/dl'''
    mmol = round(input / 18, 1)
    return mmol


def timezone(current_dt, ctz='GB', ntz='NZ', fmt="%Y-%m-%d %H:%M"):
    current_dt = current_dt[:16]
    current_dt = current_dt.replace('T', ' ')
    
    # Convert to datetime object
    d_naive_obj = dt.datetime.strptime(current_dt, fmt) 
    
    # Make object timezone aware
    timezone = pytz.timezone(ctz) 
    d_aware = timezone.localize(d_naive_obj)

    # Change to new timezone
    new_aware = pytz.timezone(ntz)
    new_aware_obj = d_aware.astimezone(new_aware)

    # Convert object back to string
    new_aware_str = new_aware_obj.strftime(fmt)
    tz_data = (new_aware_str, ntz)
    return tz_data


def findWeekday(date): 
    '''Takes string date and returns weekday'''
    daynum = dt.datetime.strptime(date, '%Y-%m-%d').weekday() 
    return (cal.day_name[daynum]) 


def timeOfday(time):
    '''Takes string time and assign it a time of day (Morning, Afternoon, Evening, Night)'''
    timenum = int(time.replace(':', ''))
    morning = 600
    afternoon = 1200
    evening = 1730
    night = 2100
    if timenum >= morning and timenum < afternoon:
        timeOfday = 'Morning'
    elif timenum >= afternoon and timenum < evening:
        timeOfday = 'Afternoon'
    elif timenum >= evening and timenum < night:
        timeOfday = 'Evening'
    else:
        timeOfday = 'Night'

    return timeOfday


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("login")
        return f(*args, **kwargs)
    return decorated_function

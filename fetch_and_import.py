import sqlite3 as sql
from pymongo import MongoClient
from helper import findWeekday, timeOfday, convert, timezone
from secretsFile import MongoDBaddress # secret keys for MongoDB access


def fetch_mongo_data(sql_count):
    '''Fetch data from Mongodb database'''
    # Client connection
    client = MongoClient(MongoDBaddress)
    
    # Database Name 
    db = client['Cluster0'] 
    # Collection Name 
    col = db['entries'] 

    # Start point for fetch data to avoid duplication/use of memory
    start_point = sql_count

    # Select data and store in list
    mongo_db = list(col.find({},{'_id': 0, 'dateString': 1, 'sgv': 1}))
    mongo_count = len(mongo_db)
    
    print("\n###########################\nMongo records:", mongo_count)
    glucose_data = []
    id = 1
    # if statement to begin fetch at start point?
    for record in mongo_db:
        try:
            record.get('sgv')
            mmol = convert(record['sgv'])
            tz_data = timezone(record['dateString'])
            (db_datetime, ntz) = tz_data # Unpack tuple
            dt_split = db_datetime.split()
            date = dt_split[0]
            time = dt_split[1][:5]
            data_list = [id, date, time, mmol]
            glucose_data.append(data_list)
            id += 1
        except KeyError:
            continue
    glucose_data = glucose_data[start_point:]
    mongo_fetch_data = (ntz, glucose_data)
    
    return mongo_fetch_data


def sql_import():
    '''Update SQL database''' 
    # Connect to database
    conn = sql.connect('diabetesdata.db')
    cursor = conn.cursor()

    # Count existing SQLite and Mongo records
    sql_count = [count[0] for count in cursor.execute('SELECT COUNT (*) FROM glucosedata')]
    sql_count = sql_count[0]

    mongo_fetch_data = fetch_mongo_data(sql_count)
    (ntz, master_list) = mongo_fetch_data

    # Stores data in lists

    # Insert new values
    count = 0
    for record in master_list:
        if record[0] > sql_count:
            record.append(findWeekday(record[1])) # Appends weekday
            record.append(timeOfday(record[2])) # Appends time of day
            date_split = record[1].split('-') # Splits date and appends DD, MM, YY as individual data
            for x in date_split:
                record.append(x)
            time_split = record[2].split(':') # Split time into hh and mm
            for x in time_split:
                record.append(x)
            insert_query = "INSERT INTO glucosedata ('id', 'date', 'time', 'bg', 'weekday', 'timeofday', 'year', 'month', 'day', 'hour', 'minute') VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(insert_query, (record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], record[10]))
            count += 1
    print(f"Updated SQL records: {sql_count+count}")

    # Commit changes and close connection
    conn.commit()
    #conn.close()
    print(f"Upload complete. {count} added\n###########################\n")

    return ntz


from flask import Flask, render_template, g, jsonify
from sqlalchemy import create_engine
# import simplejson as json
#import mysql.connector
# import MySQLdb
#import pymysql
import config
import pandas as pd

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html",
                          title = "Hhome",
                           heading = "Dublin Bikes & Weather App")

    
def connect_to_database():
    # db_str = "mysql+mysqldb://{}:{}@{}:{}/{}"
    db_str = "mysql+mysqlconnector://{}:{}@{}:{}/{}"
    engine = create_engine(db_str.format(config.USER,
                                        config.PASSWORD,
                                        config.URI,
                                        config.PORT,
                                        config.DB),
                           echo=True)
    return engine

def get_db():
    engine = getattr(g, 'engine', None)
    if engine is None:
        engine = g.engine = connect_to_database()
    return engine


@app.route("/dbinfo")
def get_dbinfo():
    # this function shows the tables in your database
    sql = """
    SELECT db.lat, db.lon, db.address, db.last_update
    FROM dbProject db
    INNER JOIN
        (SELECT address, MAX(dbID) AS LastUpdate
        FROM dbProject
        GROUP BY address) groupeddb 
    ON db.address = groupeddb.address 
    AND db.dbID = groupeddb.LastUpdate
    ;
    """.format(config.DB)
    engine = get_db()
    rows = engine.execute(sql).fetchall()
    res = [dict(row.items()) for row in rows]
    # otto_data_JSON = jsonify(res)
    # return render_template("testfile.html", otto_data_JSON=otto_data_JSON)
    # return otto_data_JSON, render_template("testfile.html")
    # test = jsonify(res)
    return jsonify(res)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/stations')
def get_stations():
    engine = get_db()
    sql = 'SELECT number, address, banking FROM dbProject;'
    rows = engine.execute(sql).fetchall()
    print('#found {} stations', len(rows))
    # Line below changes the rows into a list of dicts
    return jsonify(stations=[dict(row.items()) for row in rows])
    stations = jsonify(stations=[dict(row.items()) for row in rows]), render_template("index.html")


@app.route('/station/<int:number>')
def station(number):
    # show the station with the given id, the id is an integer

    # this line would just return a simple string echoing the station_id
    # return 'Retrieving info for Station: {}'.format(station_id)

    # select the station info from the db
    sql = """SELECT * FROM dbProject WHERE number = {}""".format(number)
    engine = get_db() 
    rows = engine.execute(sql).fetchall()  # we use fetchall(), but probably there is only one station
    res = [dict(row.items()) for row in rows]  # use this formula to turn the rows into a list of dicts
    return jsonify(data=res)  # jsonify turns the objects into the correct response


@app.route('/available/<int:number>')
def get_avail_bikes(number):
    engine = get_db()
    data = []
    rows = engine.execute("SELECT address, banking, available_bikes FROM dbProject WHERE (number = {} AND status = 1);".format(number))
    for row in rows:
        data.append(dict(row))
#    return json.dumps(available=data)
    return jsonify(available=data)

@app.route('/occupancyy/<int:number>')
def get_occupied(number):
    engine = get_db()
    data = []
    rows = engine.execute("SELECT address, banking, available_bike_stands FROM dbProject WHERE number = {};".format(number))
    for row in rows:
        data.append(dict(row))
    return jsonify(available=data)
    
#@app.route('/occupancy/<int:number>')
#def get_occupied_bikes(number):
#    engine = get_db()
#    df = pd.read_sql_query('SELECT available_bike_stands FROM dbProject WHERE number = {};', engine, params={'number':number})
##    df['last_update_date'] = pd.to_datetime(df.last_update_date, unit='ms')
##    df.set_index('last_update_date', inplace=True)
#    res = df['available_bike_stands'].resample('1d').mean()
#    print(res)
#    return jsonify(data=json.dumps(list(zip(map(lambda x:x.isoformat(), res.index), res.values))))

#@app.route('/twitter')
#def twitter():
    

if __name__ == "__main__":
    app.run(debug=True)

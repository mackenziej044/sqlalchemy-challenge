# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import re 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# create engine
engine = create_engine("sqlite:///../Resources/hawaii.sqlite",pool_pre_ping=True)

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(engine)

# Save references to each table
station = base.classes.station
measurement = base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# 1. /
@app.route('/')
def homepage():
    return(
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )
# 2. /api/v1.0/precipitation
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    last12 = dt.date(2017,8,23)-dt.timedelta(days=365)
    one_year_ago = dt.date(last12.year, last12.month, last12.day)

    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).order_by(measurement.date.desc()).all()

    p_dict = dict(results)

    print(f'Results for Precipitation - {p_dict}')
    print('Out of Precipitation section.')
    return jsonify(p_dict)

# 3. /api/v1.0/stations
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [station.station, station.name, station.latitude, station.longitude, station.elevation]
    queryresults = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresults:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

# 4. /api/v1.0/tobs
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    queryresults = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date>='2016-08-23').all()

    tob = []
    for date, tobs in queryresults:
         tobs_dict = {}
         tobs_dict["Date"] = date
         tobs_dict["Tobs"] = tobs
         tob.append(tobs_dict)

    return jsonify(tob)

# 5. /api/v1.0/<start> and /api/v1.0/<start>/<end>
@app.route('/api/v1.0/<start>')
def temp_start(start):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, max_temp, avg_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps_dict['Average Temperature'] = avg_temp
        temps.append(temps_dict)
    return jsonify(temps)

@app.route('/api/v1.0/<start>/<end>')
def temps_start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in results:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)

# boilerplate
if __name__ == '__main__':
    app.run(debug=True)
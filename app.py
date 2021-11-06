import numpy as np

import sqlalchemy
import datetime as dt
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify




#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# Save reference to the table
Measurement = Base.classes.measurement

# Save reference to the table
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br>\/ Return JSON list of Date and Precipitation from the dataset \/<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br>\/ Return JSON list of Stations from the dataset \/<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br>\/ Return JSON list of temperature observations (TOBS) for the previous year (most active Station) \/<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br>\/ Return JSON list OF MIN, AVG, AND MAX temperatures >= date provided \/<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"<br>\/ Return JSON list OF MIN, AVG, AND MAX temperatures BETWEEN dates provided (inclusive) \/<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
    )

#################################################
# PRECIPITATION
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all measurement data"""
    # Query all measurements
    #results = session.query(Measurement.id, Measurement.station, Measurement.date, Measurement.prcp, Measurement.tobs).all()
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()

    # Convert list of tuples into normal list
    all_precip = []
    for date, prcp in results:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)


#################################################
# STATIONS
#################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station data"""
    # Query all stations
    results = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = []
    for id, station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["id"] = id
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)

#################################################
# TOBS
#################################################
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()
        
    # ** THIS IS TO KEEP THE QUERY DYNAMIC IF THE DATABASE WERE TO GROW 
    # ** WHILE REPORTING REQUIREMENTS REMAIN THE SAME
    top_station = results[0]

    results = session.query(func.max(Measurement.date)).\
        filter(Measurement.station == top_station).all()

    max_date = results[0][0]

    # Convert max date to datetime, calculate -1 year, convert back into YYYY-MM-DD format for query
    # ** THIS IS TO KEEP THE QUERY DYNAMIC IF THE DATABASE WERE TO GROW 
    # ** WHILE REPORTING REQUIREMENTS REMAIN THE SAME
    max_date_conv = datetime.strptime(max_date,'%Y-%m-%d' )
    query_date = max_date_conv - dt.timedelta(days=365)
    query_date_conv = query_date.strftime('%Y-%m-%d')


    results = session.query(Measurement.tobs).\
        filter(Measurement.station == top_station).\
        filter(Measurement.date >= query_date_conv).all()
    alltemps = list(np.ravel(results))

    session.close()

    return jsonify(alltemps)


#################################################
# START AND/OR END DATES
#################################################
@app.route("/api/v1.0/<start_dt>")
def start(start_dt):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_dt).all()  

    session.close()

    stats = []
    for min, avg, max in results:
        stats_dict = {}
        stats_dict["min"] = min
        stats_dict["avg"] = avg
        stats_dict["max"] = max
        stats.append(stats_dict)
    
    return jsonify(stats)

#################################################

@app.route("/api/v1.0/<start_dt>/<end_dt>")
def startend(start_dt,end_dt):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_dt).\
        filter(Measurement.date <= end_dt).all()  

    session.close()

    stats = []
    for min, avg, max in results:
        stats_dict = {}
        stats_dict["min"] = min
        stats_dict["avg"] = avg
        stats_dict["max"] = max
        stats.append(stats_dict)
    
    return jsonify(stats)

#################################################
if __name__ == "__main__":
    app.run(debug=True)

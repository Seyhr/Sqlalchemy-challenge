# Import the dependencies.

import numpy as np
import datetime as dt

import sqlalchemy
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
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station= Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)
#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end"

    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return Precipitation Data"""
    # Query latest_date
    latest_date = session.query(func.max(Measurement.date)).scalar()
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
       
    session.close()
    # Convert list of tuples into normal list
    prec_data = [{ "date": date, "precipitation": prcp } for date, prcp in results]
    return jsonify(prec_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # List of Stations
    
    #station_list_result=session.query(func.distinct(Measurement.station)).all()
    station_detail= session.query(Station).all()
    session.close()

    # Convert the query result into a list
    station_list= []
    for station in station_detail:
        station_dict={
            "id": station.id, 
            "name": station.name, 
            "latitude": station.latitude,
            "longitude": station.longitude,
            "elevation": station.elevation
        }
        station_list.append(station_dict)
  
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)    
    # Most Active Station
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    Most_active_stat = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= prev_year).filter(Measurement.station == "USC00519281").all()
    session.close()
    # Convert list of tuples into normal list
    Most_active_stat_result = list(np.ravel(Most_active_stat))
    return jsonify(Most_active_stat_result)

@app.route("/api/v1.0/<start>",methods=['Get'])
def get_temperature_start(start):
    try:
        start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

    #Create a Session (Link) from Python to the DB
    session= Session(engine)
    # Query to get min, average and max temp for a specified start or start-end range.
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= start_date).all()
    
    session.close()

    if results:
        tmin, tmax, tavg = results[0]
        return jsonify({
            'TMIN': tmin,
            'TAVG': tavg,
            'TMAX': tmax
        })
    else:
        return jsonify({'error': 'No data available for the specified date range.'}), 404


@app.route("/api/v1.0/<start>/<end>", methods=['GET'])
def get_temperature_range(start, end):
    try:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)] 
    results = session.query(*sel).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()
    
    if results:
        tmin, tmax, tavg = results[0]
        return jsonify({
            'TMIN': tmin,
            'TAVG': tavg,
            'TMAX': tmax
        })
    else:
        return jsonify({'error': 'No data available for the specified date range.'}), 404

if __name__ == '__main__':
    app.run(debug=True)

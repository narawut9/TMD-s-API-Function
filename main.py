import requests
import psycopg2
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# ------------- Load .env to environment variables -------------
load_dotenv()
# PATH url 
station_url = os.getenv("STATION_URL")
weather_url = os.getenv("WEATHER_URL")


# ------------- Connect to database. -------------
DB_CONFIG = {
    'host' : os.getenv("DB_HOST"),
    'dbname' : os.getenv("DB_NAME"),
    'user' : os.getenv("DB_USER"),
    'password' : os.getenv("DB_PASS"),
    'port' : os.getenv("DB_PORT")
}
conn = None
try:
    conn = psycopg2.connect(**DB_CONFIG)
except psycopg2.Error as e:
    print(e)

# ------------- function fetch api station_data & weatherToday -------------
# station
def fetch_stations_data():
    try: 
        response = requests.get(station_url)
        station_data = response.json()
        return station_data
    
    except requests.exceptions.RequestException as e: 
        print(f"Error fetching station data from {station_url}: {e}")
        return None
    except ValueError as e :
        print(f"Error decoding station data JSON from {station_url}: {e}")
        return None
# weather
def fetch_weather_data():
    try: 
        response = requests.get(weather_url)
        weather_data = response.json()
        return weather_data
    
    except(requests.exceptions.RequestException) as e :
        print(f"Error fetching weather data from {weather_url}: {e}")
    except ValueError as e : 
        print(f"Error decoding weather data JSON from {weather_url}: {e}")
        return None

# ------------- check empty station_id -------------
def check_empty_station_id(station_id):

    try:
        sql_query = str('''SELECT * FROM weather."tblWeather_station" where "station_id" = '{}';'''.format(station_id))
        cur = conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        if len(rows) <= 0:
            return True # empty
        else:
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        return str(error) # not empty
    
# ------------- Get PK from tblWeather_station by station_id -------------
def get_weather_station_id_ByStationId(station_id):

    try:
        sql_query = str('''SELECT weather_station_id FROM weather."tblWeather_station" WHERE station_id = '{}'; '''.format(station_id))
        cur = conn.cursor()  
        cur.execute(sql_query) 
        rows = cur.fetchall() 
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error in get_weather_station_id_ByStationId for station_id {station_id}: {error}")
        return str(error)    

# ------------- Get PK(weather_station_id) from tblWeather_station by wmo_code -------------
def get_weather_station_id_ByWmoCode(wmo_code):

    try:
        sql_query = str('''SELECT weather_station_id FROM weather."tblWeather_station" WHERE wmo_code = '{}'; '''.format(wmo_code))
        cur = conn.cursor()  
        cur.execute(sql_query) 
        rows = cur.fetchall() 
        if len(rows) > 0:
            return rows[0][0]
        else:
            return None
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error in get_weather_station_id_ByWmoCode for wmo_code {wmo_code}: {error}")
        return str(error)  

# ------------- Load weather station data (TMD's API) ------------- 
raw_stations = fetch_stations_data()

# Insert data into database. (weather station) 
try:
    stations = raw_stations['Station']

except KeyError  as e: # กรณีคีย์ 'Station' ไม่มี
    stations = []
    print(e)

# Loop insert from stations
for i in range(0, len(stations)):

    try: station_id = str(stations[i]['StationID'])
    except: station_id = None

    try: wmocode = str(stations[i]['WmoCode'])
    except: wmocode = None

    try: station_name_th = str(stations[i]['StationNameThai'])
    except: station_name_th = None

    try: station_name_en = str(stations[i]['StationNameEnglish'])
    except: station_name_en = None

    try: station_type = str(stations[i]['StationType'])
    except: station_type = None

    try: province = str(stations[i]['Province'])
    except: province = None

    try: zipcode = str(stations[i]['ZipCode'])
    except: zipcode = None

    try: latitude = float(stations[i]['Latitude'])
    except: latitude = None

    try: longitude = float(stations[i]['Longitude'])
    except: longitude = None

    try: height_msl = float(stations[i]['HeightAboveMSL'])
    except: height_msl = None

    try: height_wind_wane = float(stations[i]['HeightofWindWane'])
    except: height_wind_wane = None

    try: height_barometer = float(stations[i]['HeightofBarometer'])
    except: height_barometer = None

    try: height_thermometer = float(stations[i]['HeightofThermometer'])
    except: height_thermometer = None

# ------------- Configs Name, Datetime -------------
create_by = 'Narawut.T'
update_by = 'Narawut.T'
create_date = datetime.now()
update_date = datetime.now()

# True station_id is empty 
# INSERT SQl query
if check_empty_station_id(station_id):
        try:
            cur = conn.cursor()
            sql_query = """INSERT INTO weather."tblWeather_station"(
            station_id, wmo_code, station_name_th, station_name_eng, station_type, province, zip_code, latitude, longitude, height_msl, height_wind_wane, 
            height_barometer, height_thermometer, create_by, create_date, update_by, update_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            cur.execute(sql_query, (station_id, wmocode, station_name_th, station_name_en, station_type, province, zipcode, latitude, longitude, height_msl, height_wind_wane, 
            height_barometer, height_thermometer, create_by, create_date, update_by, update_date,))
            conn.commit()
            cur.close()
            print(f"Complete to insert station. ({str(station_id)})")
        except NameError as e:
            print(e)
# False UPDATE     
else:
        weather_station_id = get_weather_station_id_ByStationId(station_id)
        try:
            cur = conn.cursor()
            sql_query = update_sql = '''
                UPDATE weather."tblWeather_station"
                SET 
                    station_name_th      = %s,
                    station_name_eng     = %s,
                    station_type         = %s,
                    province             = %s,
                    zip_code             = %s,
                    latitude             = %s,
                    longitude            = %s,
                    height_msl           = %s,
                    height_wind_wane     = %s,
                    height_barometer     = %s,
                    height_thermometer   = %s,
                    update_by            = %s,
                    update_date          = %s
                WHERE weather_station_id = %s;
                '''
            cur.execute(sql_query, (station_name_th, station_name_en, station_type, province, zipcode, latitude, longitude, height_msl, height_wind_wane, 
            height_barometer, height_thermometer, update_by, update_date, weather_station_id))
            conn.commit()
            cur.close()
            print(f"Complete to update station. ({str(station_id)})")
        except NameError as e:
            print(e)

# -------------Load weather today data (TMD's API) -------------
raw_weather = fetch_weather_data()

# Insert data into database. (weather today)
try:
    weather_daily = raw_weather['Stations']['Station']

except NameError as e:
    weather_daily = []
    print(e)


# Processing(weather today)
for j in range(0, len(weather_daily)):

    try: station_id = str(weather_daily[j]['StationID'])
    except: station_id = None

    try: wmocode = str(weather_daily[j]['WmoStationNumber'])
    except: wmocode = None

    try: obs_datetime = str(weather_daily[j]['Observation']['DateTime'])
    except: obs_datetime = None

    try: pressure_sea_level = float(weather_daily[j]['Observation']['MeanSeaLevelPressure'])
    except: pressure_sea_level = None

    try: temp = float(weather_daily[j]['Observation']['Temperature'])
    except: temp = None

    try: temp_max = float(weather_daily[j]['Observation']['MaxTemperature'])
    except: temp_max = None

    try: temp_min = float(weather_daily[j]['Observation']['MinTemperature'])
    except: temp_min = None

    try: temp_diff_max = str(weather_daily[j]['Observation']['DifferentFromMaxTemperature'])
    except: temp_diff_max = None

    try: humidity = float(weather_daily[j]['Observation']['RelativeHumidity'])
    except: humidity = None

    try: wind_direction = float(weather_daily[j]['Observation']['WindDirection'])
    except: wind_direction = None

    try: wind_speed = float(weather_daily[j]['Observation']['WindSpeed'])
    except: wind_speed = None

    try: rainfall = float(weather_daily[j]['Observation']['Rainfall'])
    except: rainfall = None

# ------------- get weather_station_id  by wmo_code -------------
# Ture = Insert SQL query
weather_station_id = get_weather_station_id_ByWmoCode(wmocode)
if  weather_station_id != None:
    try:
        cur = conn.cursor()
        sql_query = """
        INSERT INTO weather."tblWeather_daily"(
        weather_station_id, obs_datetime, pressure_sea_level, temp, temp_max, temp_min, temp_diff_max, humidity, wind_direction, wind_speed, rainfall,
        create_by, create_date, update_by, update_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cur.execute(sql_query, (
        weather_station_id, obs_datetime, pressure_sea_level, temp, temp_max, temp_min,temp_diff_max, humidity, wind_direction, wind_speed, rainfall, 
        create_by, create_date, update_by, update_date,))
        conn.commit()
        cur.close()
        print(f"Complete to insert weather. (StationID: {weather_station_id}, DateTime: {create_date})")
    except Exception as e:
        print(e)

else:
    print(f"[Warning] Not Found weather_station_id: StationID = {station_id}, WmoCode = {wmocode}")
        
if conn:
    try:
        conn.close()
        print("Database connection closed successfully.")
    except psycopg2.Error as e:
        print(f"Error closing database connection: {e}")
print("Completed to Load all data")
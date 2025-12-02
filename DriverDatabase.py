# This file creates a Database known as 'Driver_Management.db' to 
# store records and information
# Connects with sqlite in order to execute SQL statements

import sqlite3
import os
import pandas as pd

conn = sqlite3.connect('Driver_Management.db')
print("\nOpened database successfully")

#getting the path name in order to connect to the database we are using --> DBVisualizer 

# so the error before was cause because when connecting to db visualizer the correct path was not there hence no tables shown
path = os.path.abspath('Driver_Management.db')
print(path)

conn.execute("DROP TABLE IF EXISTS Driver_Drowsiness_Event;")
conn.execute("DROP TABLE IF EXISTS Driver;")
conn.execute("DROP TABLE IF EXISTS Trip;")
conn.execute("DROP TABLE IF EXISTS Vehicle;")


cur = conn.execute('''

CREATE TABLE IF NOT EXISTS Driver (
    ID INTEGER PRIMARY KEY,
    Name VARCHAR(80) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Phone_Number VARCHAR(10) UNIQUE NOT NULL,
    Age INTEGER,
    Daily_Average_Driving_Hours FLOAT
);


''')

print("\nDriver table created successfully\n")


cur = conn.execute('''

CREATE TABLE IF NOT EXISTS Driver_Drowsiness_Event (
    Event_ID INTEGER PRIMARY KEY,
    Driver_ID INT NOT NULL, 
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    Level_Of_Drowsiness FLOAT, 
    Alert_Sent BOOLEAN DEFAULT 0,
    FOREIGN KEY (Driver_ID) REFERENCES Driver(ID)
);


''')

print("\nDriver_Drowsiness_Event table created successfully\n");


cur = conn.execute('''

CREATE TABLE IF NOT EXISTS Trip (
    Trip_ID INTEGER PRIMARY KEY,
    Driver_ID INT NOT NULL, 
    Vehicle_ID INT,
    Location_Start VARCHAR(80),
    Location_End VARCHAR(80),
    Miles_Traveled FLOAT,
    Time_Started DATETIME,
    Time_Ended DATETIME,
                   
    FOREIGN KEY (Driver_ID) REFERENCES Driver(ID),
    FOREIGN KEY (Vehicle_ID) REFERENCES Vehicle(Vehicle_ID)

);


''')

print("\nTrip table created successfully\n");

cur = conn.execute('''

CREATE TABLE IF NOT EXISTS Vehicle (
    Vehicle_ID INTEGER PRIMARY KEY,
    Driver_ID INT NOT NULL, 
    Model VARCHAR(50),
    Make VARCHAR(50),
    Year INT, 
    License_Plate_Num VARCHAR(8) UNIQUE,
    Vehicle_Type VARCHAR(20),
                   
    FOREIGN KEY (Driver_ID) REFERENCES Driver(ID)
);


''')

print("\nVehicle table created successfully\n");




# putting csv
df_driver = pd.read_csv("Driver.csv")
df_vehicle = pd.read_csv("Vehicle.csv")
df_trip = pd.read_csv("Trip.csv")
df_event = pd.read_csv("Driver_Drowsiness_Event.csv")

df_driver.to_sql("Driver", conn, if_exists="append", index=False)
df_vehicle.to_sql("Vehicle", conn, if_exists="append", index=False)
df_trip.to_sql("Trip", conn, if_exists="append", index=False)
df_event.to_sql("Driver_Drowsiness_Event", conn, if_exists="append", index=False)

conn.commit()

print("All files there success!")
print(" ")
# SQL queries 
print("Get all of the trips with Driver's Name and Vehicle Model:\n")

query = """
SELECT 
    Trip.Trip_ID,
    Driver.Name AS Driver_Name,
    Vehicle.Model AS Vehicle_Model,
    Trip.Location_Start,
    Trip.Location_End,
    Trip.Miles_Traveled
FROM Trip
JOIN Driver ON Trip.Driver_ID = Driver.ID
LEFT JOIN Vehicle ON Trip.Vehicle_ID = Vehicle.Vehicle_ID;

"""

df_result = pd.read_sql_query(query, conn)

print(df_result)
print(" ")

print("Get all vehicle information whose make is Tesla and model type is Truck:\n")
query = """
SELECT 
    v.Vehicle_ID, v.Driver_ID, v.Model, v.Make, v.Year, v.License_Plate_Num, v.Vehicle_Type
FROM Vehicle v WHERE v.Make = 'Tesla' AND v.Vehicle_Type = 'Truck';

"""

df_result = pd.read_sql_query(query, conn)

print(df_result)


print(" ")

print("Left Join: Trips with drivers, even if there is vehicle information that is missing or null: \n")
query = """
SELECT tr.Trip_ID, ve.Model, dr.Name, tr.Miles_Traveled FROM Trip tr 
INNER JOIN Driver dr ON tr.Driver_ID = dr.ID LEFT JOIN Vehicle ve ON tr.Vehicle_ID = ve.Vehicle_ID;
"""

df_result = pd.read_sql_query(query, conn)

print(df_result)

print(" ")

print("Trips longer than 350 miles: \n")
query = """
SELECT Driver_ID, Miles_Traveled, Trip_ID from Trip WHERE Miles_Traveled > 350
ORDER BY Miles_Traveled ASC;
"""

df_result = pd.read_sql_query(query, conn)

print(df_result)

print(" ")

print("Count the number of duplicate driver's names in ascending order: \n")
query = """
SELECT Name, COUNT(*) AS name_counter FROM Driver GROUP BY Name
HAVING COUNT(*) > 1 ORDER BY name_counter ASC;
"""

df_result = pd.read_sql_query(query, conn)

print(df_result)


print(" ")
print("Count of trips per vehicle: \n")
query = """
SELECT v.Model, COUNT(t.Trip_ID) AS Trip_Count
FROM Trip t
INNER JOIN Vehicle v ON t.Vehicle_ID = v.Vehicle_ID GROUP BY v.Model
ORDER BY Trip_Count ASC;

"""
df_result = pd.read_sql_query(query, conn)

print(df_result)




print(" ")
print("Average drowsiness level per driver, no duplicates: \n")
query = """
SELECT d.Name, AVG(e.Level_Of_Drowsiness) AS Avg_Drowsiness
FROM Driver_Drowsiness_Event e
INNER JOIN Driver d ON e.Driver_ID = d.ID
GROUP BY d.Name
ORDER BY Avg_Drowsiness ASC;

"""
df_result = pd.read_sql_query(query, conn)

print(df_result)

print(" ")

# TO DO: 
#plots and create a prediction model (training/testing data)

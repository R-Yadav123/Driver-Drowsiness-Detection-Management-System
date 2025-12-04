# This file creates a Database known as 'Driver_Management.db' to 
# store records and information
# Connects with sqlite in order to execute SQL statements

import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

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

# Plots

df_trip['Time_Started'] = pd.to_datetime(df_trip['Time_Started'])
df_trip['Time_Ended'] = pd.to_datetime(df_trip['Time_Ended'])


# Finding the trip duration hours
df_trip['Duration_Hours'] = (df_trip['Time_Ended'] - df_trip['Time_Started']).dt.total_seconds() / 3600

# merging the trips and driver's information 
merged = df_trip.merge(df_driver, left_on='Driver_ID', right_on='ID')

# Scatter Plot: Miles Traveled vs. Trip Duration
plt.figure(figsize=(10,6))
plt.scatter(merged['Duration_Hours'], merged['Miles_Traveled'], alpha=0.8)
plt.xlabel('Trip Duration in Hours')
plt.ylabel('Miles Traveled')
plt.title('Miles Traveled Vs. Trip Duration')
plt.grid(True)
plt.show()

# Bar Plot: Count of vehicles by model 
model_counts = df_vehicle['Model'].value_counts()

plt.figure(figsize=(10,6))
model_counts.plot(kind='bar', color='orange', edgecolor='black')
plt.xlabel('Vehicle Model')
plt.ylabel('Number of Vehicles')
plt.title('Number of Vehicles per Model')
plt.xticks(rotation=45)
plt.show()

# Bar Plot: Count of vehicles by vehicle type
model_counts = df_vehicle['Vehicle_Type'].value_counts()

plt.figure(figsize=(10,6))
model_counts.plot(kind='bar', color='lightblue', edgecolor='black')
plt.xlabel('Vehicle Type')
plt.ylabel('Number of Vehicles')
plt.title('Number of Vehicles per Vehicle Type')
plt.xticks(rotation=45)
plt.show()


# Scatter Plot: Age vs. Daily Avg Driving Hours
plt.scatter(df_driver['Age'], df_driver['Daily_Average_Driving_Hours'], color='purple', alpha=0.7)
plt.xlabel('Driver Age')
plt.ylabel('Daily Average Driving Hours')
plt.title('Driver Age vs Daily Average Driving Hours')
plt.show()

# Boxplot: Age vs. Model 
merged_df = pd.merge(df_driver, df_vehicle, left_on='ID', right_on = 'Driver_ID', how = 'inner')

# Get unique models
models = merged_df['Model'].unique()

# Create a list of age arrays, one for each model
data_to_plot = [merged_df['Age'][merged_df['Model'] == model] for model in models]

plt.figure(figsize=(10, 7))
plt.boxplot(data_to_plot, tick_labels=models) # Pass the list of data and labels for x-axis

plt.title('Age Distribution by Vehicle Model')
plt.xlabel('Vehicle Model')
plt.ylabel('Age')
plt.xticks(rotation=45, ha='right') # Rotate labels if they overlap
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout() # Adjust layout to prevent labels from being cut off
plt.show()

#creating more plots in order to really perform the analysis/goal which is driver drowsiness

plt.figure(figsize=(15,5))  

plt.hist(df_event['Level_Of_Drowsiness'], bins = 6, color = 'pink', edgecolor = 'brown')
plt.ylabel('Occurrences')
plt.xlabel('Drowsiness Level')

plt.title("The Distribution of Drowsiness Levels")
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.show()

# Creation of a prediction model
# Training Data: Driver_Drowsiness_Event.csv
# Testing Data: Driver_Drowsiness_Event_Testing_Dataset.csv

# The testing data has removed the column "Alert_Sent" as that it what is going to be predicted (boolean values).
# Alert Sent = 1 (true)
# Alert Not Sent = 0 (false)

df_event['Timestamp'] = pd.to_datetime(df_event['Timestamp'])

# time-based features
df_event['Hour'] = df_event['Timestamp'].dt.hour
df_event['Day_of_Week'] = df_event['Timestamp'].dt.dayofweek
df_event['Month'] = df_event['Timestamp'].dt.month
print("Data Subset Head (5 rows): \n")
print(df_event.head())

features = ['Level_Of_Drowsiness', 'Hour', 'Day_of_Week', 'Month']
x_train = df_event[features]
y_train = df_event['Alert_Sent']

# Fitting a model with linear regression
model = LinearRegression()
model.fit(x_train, y_train)

# Testing data
test_data = pd.read_csv("Driver_Drowsiness_Event_Testing_Dataset.csv")
test_data['Timestamp'] = pd.to_datetime(test_data['Timestamp'])
test_data['Hour'] = test_data['Timestamp'].dt.hour
test_data['Day_of_Week'] = test_data['Timestamp'].dt.dayofweek
test_data['Month'] = test_data['Timestamp'].dt.month

x_test = test_data[features]

y_test_prediction = model.predict(x_test)

# Converting the predictions to 0/1 using a 0.5 threshold
y_prediction = (y_test_prediction >= 0.5).astype(int)
test_data['Predicted_Alert'] = y_prediction
print(" ")
print("Predictions: \n")
print(test_data[['Event_ID', 'Driver_ID', 'Level_Of_Drowsiness', 'Predicted_Alert']])

print(" ")

accuracy = (y_prediction == y_train).mean() * 100
print(f"Model Accuracy: {accuracy:.2f}%")
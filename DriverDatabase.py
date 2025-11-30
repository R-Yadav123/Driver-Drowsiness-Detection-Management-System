# This file creates a Database known as 'Driver_Management.db' to 
# store records and information
# Connects with sqlite in order to execute SQL statements


import sqlite3

conn = sqlite3.connect('Driver_Management.db')
print("\nOpened database successfully")

# Creating tables

cur = conn.execute('''

DROP TABLE IF EXISTS Driver_Drowsiness_Event;

''')

cur = conn.execute('''

DROP TABLE IF EXISTS Driver;

''')

cur = conn.execute('''

DROP TABLE IF EXISTS Trip;

''')

cur = conn.execute('''

DROP TABLE IF EXISTS Vehicle;

''')

cur = conn.execute('''

CREATE TABLE IF NOT EXISTS Driver (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name VARCHAR(80) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Phone_Number VARCHAR(10) UNIQUE NOT NULL,
    Age INTEGER,
    Daily_Average_Driving_Hours FLOAT
);


''')

print("\nDriver table created successfully\n")


cur = conn.execute('PRAGMA table_info(Driver);')

rows = cur.fetchall()  

for row in rows:
    print(row)


cur = conn.execute('''

CREATE TABLE IF NOT EXISTS Driver_Drowsiness_Event (
    Event_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Driver_ID INT NOT NULL, 
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    Level_Of_Drowsiness FLOAT, 
    Alert_Sent BOOLEAN DEFAULT 0,
    FOREIGN KEY (Driver_ID) REFERENCES Driver(ID)
);


''')

print("\nDriver_Drowsiness_Event table created successfully\n");


cur = conn.execute('PRAGMA table_info(Driver_Drowsiness_Event);')

rows = cur.fetchall()  

for row in rows:
    print(row)


cur = conn.execute('''

CREATE TABLE IF NOT EXISTS Trip (
    Trip_ID INTEGER PRIMARY KEY AUTOINCREMENT,
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

cur = conn.execute('PRAGMA table_info(Trip);')

rows = cur.fetchall()  

for row in rows:
    print(row)

cur = conn.execute('''

CREATE TABLE IF NOT EXISTS Vehicle (
    Vehicle_ID INTEGER PRIMARY KEY AUTOINCREMENT,
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

cur = conn.execute('PRAGMA table_info(Vehicle);')

rows = cur.fetchall()  

for row in rows:
    print(row)

cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = cur.fetchall()

print("\n\033[1mTables in the database:\033[0m\n")

for table in tables:
    print(table[0])

#  Inserting into the tables/adding sample records
# IDs autoincrement, so not needed to include
conn.execute('''
INSERT INTO Driver (Name, Email, Phone_Number, Age, Daily_Average_Driving_Hours)
VALUES
('Mary Smith', 'msmith@gmail.com', '1232012689', 25, 2.5),
('John Doe', 'jdoe@gmail.com', '9876543210', 30, 3.0),
('Alice Johnson', 'alicej@gmail.com', '5551234567', 28, 4.2),
('Bob Williams', 'bobw@gmail.com', '4445556666', 35, 1.8),
('Carol Brown', 'carolb@gmail.com', '3334445555', 26, 2.7),
('David Lee', 'davidl@gmail.com', '2223334444', 32, 3.5),
('Eve Miller', 'evem@gmail.com', '1112223333', 29, 4.0),
('Frank Harris', 'frankh@gmail.com', '9998887777', 31, 2.9),
('Grace Clark', 'gracec@gmail.com', '8887776666', 27, 3.8),
('Henry Adams', 'henrya@gmail.com', '7776665555', 33, 2.3);
''')
print("\n Records in Driver Table: \n")
cur = conn.execute('SELECT * FROM Driver;')
rows = cur.fetchall()

for row in rows:
    print(row)

conn.execute('''
INSERT INTO Vehicle (Driver_ID, Model, Make, Year, License_Plate_Num, Vehicle_Type)
VALUES
(1, 'Model S', 'Tesla', 2022, 'TES1234', 'Sedan'),
(2, 'F-150', 'Ford', 2020, 'FORD567', 'Truck'),
(3, 'Civic', 'Honda', 2019, 'HND8901', 'Sedan'),
(4, 'Corolla', 'Toyota', 2021, 'TYT2345', 'Sedan'),
(5, 'Accord', 'Honda', 2018, 'ACD3322', 'Sedan'),
(6, 'Silverado', 'Chevrolet', 2022, 'CHV9911', 'Truck'),
(7, 'Camry', 'Toyota', 2020, 'CAM2020', 'Sedan'),
(8, 'Mustang', 'Ford', 2019, 'MST4455', 'Sports'),
(9, 'RAV4', 'Toyota', 2021, 'RAV5566', 'SUV'),
(10,'Explorer', 'Ford', 2023, 'EXP7777', 'SUV');
''')

print("\n Records in Vehicle Table: \n")
cur = conn.execute('SELECT * FROM Vehicle;')
rows = cur.fetchall()

for row in rows:
    print(row)

conn.execute('''
INSERT INTO Trip (Driver_ID, Vehicle_ID, Location_Start, Location_End, Miles_Traveled, Time_Started, Time_Ended)
VALUES
(1, 1, 'New York', 'Boston', 215, '2025-11-23 08:00:00', '2025-11-23 12:00:00'),
(2, 2, 'Chicago', 'Detroit', 280, '2025-11-22 09:00:00', '2025-11-22 13:30:00'),
(3, 3, 'Los Angeles', 'San Diego', 120, '2025-11-21 07:30:00', '2025-11-21 10:00:00'),
(4, 4, 'Houston', 'Dallas', 240, '2025-11-20 06:00:00', '2025-11-20 10:30:00'),
(5, 5, 'Phoenix', 'Tucson', 113, '2025-11-22 10:00:00', '2025-11-22 12:00:00'),
(6, 6, 'Miami', 'Orlando', 235, '2025-11-23 07:00:00', '2025-11-23 11:00:00'),
(7, 7, 'Seattle', 'Portland', 174, '2025-11-19 08:45:00', '2025-11-19 11:30:00'),
(8, 8, 'San Francisco', 'Sacramento', 87, '2025-11-18 09:00:00', '2025-11-18 10:45:00'),
(9, 9, 'Atlanta', 'Savannah', 250, '2025-11-17 06:30:00', '2025-11-17 10:00:00'),
(10,10,'Denver', 'Boulder', 30, '2025-11-16 08:00:00', '2025-11-16 08:40:00');
''')

print("\n Records in Trip Table: \n")
cur = conn.execute('SELECT * FROM Trip;')
rows = cur.fetchall()

for row in rows:
    print(row)

conn.execute('''
INSERT INTO Driver_Drowsiness_Event (Driver_ID, Level_Of_Drowsiness, Alert_Sent)
VALUES
(1, 0.7, 1),
(2, 0.5, 0),
(3, 0.9, 1),
(4, 0.4, 0),
(5, 0.3, 0),
(6, 0.85, 1),
(7, 0.6, 0),
(8, 0.92, 1),
(9, 0.25, 0),
(10,0.78, 1);
''')

print("\n Records in Driver_Drowsiness_Event Table: \n")
cur = conn.execute('SELECT * FROM Driver_Drowsiness_Event;')
rows = cur.fetchall()

for row in rows:
    print(row)


print(" ")



# already inserted records
# now clear all the tables and use a dataset for soe of the values 
# SQL Joins, filtering, cleaning, etc. , use a dataset
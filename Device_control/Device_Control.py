# imports
from gpiozero import LED, MCP3008
import sys
import time
from time import sleep
from datetime import datetime
import csv
import os
import mariadb


class Sensor:
    id: int
    pin: int
    max_val: int
    min_val: int
    isWorking: bool
    
    def __init__(self, id, pin, min, max, isWorking):
        self.id = id
        self.pin = pin
        self.min = min
        self.max = max
        self.isWorking = isWorking
        
    def __str__(self):
        return 'sens' + str(self.id)
    

class Solenoid:
    id: int
    pin: int
    debit: int
    
    def __init__(self, id, pin, debit):
        self.id = id
        self.pin = pin
        self.debit = debit
        
    def __str__(self):
        return 'sol' + str(self.id)   
    
class Plant:
    id: int
    name: str
    category: int
    
    def __init__(self, id, name, category):
        self.id = id
        self.name = name
        self.category = category
        
    def __str__(self):
        return 'plant ' + self.name
    

class Pot:
    id: int
    sensor: Sensor
    sol: Solenoid
    plant: Plant
    mode: str
    isIrrigated: bool
    
    def __init__(self, id: int, sens: Sensor, sol: Solenoid, pl: Plant, mode: str, isIrrigated: bool):
        self.id = id
        self.sensor = sens
        self.sol = sol
        self.plant = pl
        self.mode = mode
        self.isIrrigated = isIrrigated
        
    def __str__(self):
        return 'pot' + str(self.id)


# Logging to file
def errorLogging(file_name: str, log_level: str, log_str: str):
    
    with open(file_name, mode='a') as file:        
        current_time = datetime.now()
        time_stamp = current_time.timestamp()            
        date_time = datetime.fromtimestamp(time_stamp)
        
        str_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S") 
        
        file.write(str_date_time + ' ' + log_level + ' ' + log_str + '\n')
        file.close()

def databaseConn():
    try:
        conn = mariadb.connect(
            #replace file!
            user="admin",
            password="admin",
            host="localhost",
            database="arrosage"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    return conn
    
def fillSensor(cur):
    cur.execute("SELECT * FROM Sensor")
    for (id_sensor,	pin_sensor,	max_humidity, min_humidity) in cur:
        print(Sensor(id_sensor, pin_sensor, min_humidity, max_humidity, True))

def fillSolenoid(cur):
    cur.execute("SELECT * FROM Solenoide")
    for (id_solenoid, pin_solenoid, capacity) in cur:
        print(Solenoid(id_solenoid, pin_solenoid, capacity))

def fillPlant(cur):
    cur.execute("SELECT * FROM Plant")
    for (id_plant, name, id_category) in cur:
        print(Plant(id_plant, name, id_category))

def fillPot(cur):
    cur.execute("SELECT * FROM Flowerpot")
    for (id_flowerpot, id_plant, id_sensor, id_solenoid, mode, is_irrigated ) in cur:
        print(Pot(id_flowerpot, id_sensor, id_solenoid, id_plant, mode, is_irrigated))
    
if __name__ == '__main__':
    
    auto_mode = -1
    max_iter  = -1
    log_file  = ''
    
    #1) read parameters from config    
    with open('config.txt', mode='r') as config:
        for line in config:
            p = line.strip().split('=')
            if (p[0] == 'mode'):
                if(p[1] == 'auto'):
                    auto_mode = 1
                else:
                    auto_mode = 0
            if (p[0] == 'maxIterations'):
                max_iter = int(p[1])
            if (p[0] == 'logFile'):
                path_dir = os.path.abspath(os.path.join('..'))
                log_file = os.path.join(path_dir, p[1])

                
    if (auto_mode < 0 or max_iter < 0):
        errorLogging(log_file, 'fatal', 'Problem with config')

    #2) connect to DB
    cur = databaseConn().cursor()
    
    #3) data from DB -> fill classes
    fillSensor(cur)
    fillSolenoid(cur)
    fillPlant(cur)
    fillPot(cur)
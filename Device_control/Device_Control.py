# imports
from gpiozero import LED, MCP3008
import sys
import time
from threading import Thread
from time import sleep
import random
from datetime import datetime
import csv
import os
import mariadb

PIN_PUMP = 24


class Sensor:
    id: int
    pin: int
    max_val: int
    min_val: int
    isWorking: bool
    
    def __init__(self, id, pin, min, max, isWorking):
        self.id = id
        self.pin = pin
        self.min_val = min
        self.max_val = max
        self.isWorking = isWorking
        
    def __str__(self):
        return 'sens' + str(self.id) + '/pin' + str(self.pin)
    

class Solenoid:
    id: int
    pin: int
    debit: int
    
    def __init__(self, id, pin, debit):
        self.id = id
        self.pin = pin
        self.debit = debit
        
    def __str__(self):
        return 'sol' + str(self.id) + '/pin' + str(self.pin)   


class Category:
    id: int
    lower_limit: int
    upper_limit: int
    
    def __init__(self, id, low, up):
        self.id = id
        self.lower_limit = low
        self.upper_limit = up
        
    def __str__(self):
        return 'cat ' + self.id + '/low' + str(self.lower_limit) + '/up' + str(self.upper_limit) 

class Plant:
    id: int
    name: str
    category: Category
    
    def __init__(self, id, name, category):
        self.id = id
        self.name = name
        self.category = category
        
    def __str__(self):
        return 'plant ' + self.name + '/cat' + str(self.category.id) 
    

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
        return 'pot' + str(self.id) + ' ' + str(self.sensor) + ' ' + str(self.sol) + ' ' + str(self.plant)
    


# Logging to file
def logging(file_name: str, log_level: str, log_str: str):    
    with open(file_name, mode='a') as file:        
        current_time = datetime.now()
        time_stamp = current_time.timestamp()            
        date_time = datetime.fromtimestamp(time_stamp)        
        str_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")        
        file.write(str_date_time + ' ' + log_level + ' ' + log_str + '\n')
        file.close()


def databaseConnection(log_file):
    try:
        conn = mariadb.connect(
            #replace file!
            user="admin",
            password="admin",
            host="localhost",
            database="arrosage"
        )
    except mariadb.Error as e:
        logging(log_file, 'error', 'Error connecting to MariaDB Platform')        
    return conn


def desactivateSensor(pin, cur, connection):
    cur.execute("UPDATE Sensor SET is_working = False WHERE id_sensor = %s", (pin, )) 
    connection.commit()    
    
    
def desactivateAutoMode(idPot, cur, connection):
    cur.execute("UPDATE Flowerpot SET mode = 'model' WHERE id_flowerpot = %s", (idPot, ))
    connection.commit()
    
    
        
def fillCurrentObjects(cur):
    list_pots = []
    cur.execute("SELECT * FROM Flowerpot")
    pots = cur.fetchall()
    
    for pot in pots:
        # plant
        cur.execute("SELECT * FROM Plant WHERE id_plant = %s;", (pot[1], ))
        rez = cur.fetchone()
        cur.execute("SELECT * FROM Categories WHERE id_category = %s;", (rez[2], ))
        rez1 = cur.fetchone()
        newPlant = Plant(rez[0], rez[1], Category(rez1[0], rez1[1], rez1[2]))
        
        # sensor        
        cur.execute("SELECT * FROM Sensor WHERE id_sensor = %s;", (pot[2], ))
        rez = cur.fetchone()
        newSensor = Sensor(rez[0], rez[1], rez[2], rez[3], True)       #TODO  make field in DB isWorking        
        
        #solenoid
        cur.execute("SELECT * FROM Solenoide WHERE id_solenoid = %s;", (pot[3], ))
        rez = cur.fetchone()
        newSol = Solenoid(rez[0], rez[1], rez[2])
        
        list_pots.append( Pot(pot[0], newSensor, newSol, newPlant, pot[4], pot[5]) )
        
    return list_pots


    

# Take data from MCP pin specified
def takeDataFromSensor(pin: int, log_file: str) -> int:
    try:
        return MCP3008(pin).raw_value
    except Exception as error:
        logging(log_file, 'debug', error)
    return -1

# Watering one pot.
# WARNING: it is not an error that the "on" function is first called to stop the current supply (in case it is supplied)
#        - this is not a mistake!
# The wiring diagram of the relay in our system is such that "on" works like "off" and vice versa
def wateringOne(led, duration): 
    led.off()
    time.sleep(duration)
    led.on()

def wateringAll(list_pins: [(int, int)], log_file: str) -> ():   
    sol_list = []
    dur_list = []
    durPump = 0
    pump = LED(PIN_PUMP)
    
    # find duration pump and compose list of LEDs
    for el in list_pins:        
        sol_list.append(LED(el[0]))
        if ( durPump < el[1]):
            durPump = el[1]        
        dur_list.append(el[1])
    
    # off all
    pump.on()
    for led in sol_list:
        led.on()    

    threads = []
    p = Thread(target=wateringOne, args=(pump, durPump,))
    threads.append(p)
    p.start()
        
    for i in range(len(dur_list)):
        t = Thread(target=wateringOne, args=(sol_list[i], dur_list[i],))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()



def makeReport(log_file, modeGlob, sens, sol, modeLoc, attempt, hum, cat, dur):
    s = 'A, sens' if (modeGlob == 1) else 'M, sens'
    s += str(sens)+', sol'+str(sol)+', mode '+modeLoc+', attempt '+str(attempt)+', humidity '+str(hum)+'%, category '+str(cat)+', duration '+str(dur)+'s.'
    print(s)
    logging(log_file, 'info', s)


def autoMode():
    auto_mode = -1
    max_iter  = -1
    log_file  = ''
    absorption_duration = 3*60
    between_take_data = 5
    repeat_if_error = 1*60
    
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
                log_file = p[1]
        config.close()
        
                
    if (auto_mode < 0 or max_iter < 0):
        logging(log_file, 'fatal', 'Problem with config')

    #2) connect to DB
    connection = databaseConnection(log_file)
    cur = connection.cursor()
    
    #3) data from DB -> fill classes    
    list_pots = fillCurrentObjects(cur)
    for el in list_pots:
        print(el)
    
    needWater = []
    passToModel = []
    attempt = 1
    durPump = 0
    
    #4) main loop
    while (True):
        # collect info who needs water and how much        
        for pot in list_pots:
            if pot.sensor.isWorking:
                
                humValue = takeDataFromSensor(pot.sensor.pin, log_file)
                
                if ( humValue == 1023 ):
                    logging(log_file, 'debug', 'Connection to sensor ' + str(pot.sensor.pin) + ' is broken.')
                    
                    #desactivateSensor(pot.sensor.pin)             # TODO incomment when is_working will be added to Sensor in DB
                    desactivateAutoMode(pot.id, cur, connection)
                    
                    # TODO take data from model to arrosage
                 
                else:                        
                    persHum = int(100*(humValue - pot.sensor.min_val)/(pot.sensor.max_val - pot.sensor.min_val))
                    persHum = 0 if (persHum < 0) else persHum
                   
                    if ( persHum < (pot.plant.category.upper_limit - pot.plant.category.lower_limit)/2 ):
                        needWater.append((pot, attempt, persHum, humValue))   # (pot, attempt, persHum, humValue)
                        
            else:
                print("TODO")
                # take info from model - how much water he needs - and put it to needWater

        # check if somebody still needs water
        nbWorkingSol = len(needWater)
        print(nbWorkingSol)
        
        if (nbWorkingSol == 0):   # all plants watered, dont need working next 24h
            cur.close()
            connection.close()
            return
        
        # arrosage
        else:
            list_pins = []
            for item in needWater:
                pot      = item[0]
                attempt  = item[1]
                persHum  = item[2]
                humValue = item[3]
                
                debit = pot.sol.debit               
                duration = random.randint(3, 7)     #diff/debit                       TODO  calculate correctly according volume of water/soil                

                list_pins.append([pot.sol.pin, duration])

                makeReport(log_file, auto_mode, pot.sensor.id, pot.sol.id, pot.mode, attempt, persHum, pot.plant.category.id, duration)
                
            wateringAll(list_pins, log_file)

        # create session, wait to verify
        # TODO create session
        attempt += 1
        needWater.clear()
        time.sleep(absorption_duration)
        
        
    
if __name__ == '__main__':
    autoMode()
    
    
    
    
    
    
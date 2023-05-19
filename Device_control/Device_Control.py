# imports
from gpiozero import LED, MCP3008
import sys
import os
import time
from time import sleep
from datetime import datetime
from datetime import timedelta
from datetime import date
from threading import Thread
import csv
import json
import requests
import mariadb
import math


PIN_PUMP = 24


class Sensor:
    id: int
    pin: int
    max_val: int
    min_val: int
    isTrusted: bool
    
    def __init__(self, id, pin, max, min, isTrusted):
        self.id = id
        self.pin = pin
        self.min_val = min
        self.max_val = max
        self.isTrusted = isTrusted
        
    def __str__(self):
        return 'sens' + str(self.id) + '/pin' + str(self.pin)

    
    def desactivateSensor(self, cur, connection):
        self.isTrusted = False
        cur.execute("UPDATE Sensor SET isTrusted = False WHERE id_sensor = %s", (self.pin, )) 
        connection.commit()
        
    def activateSensor(self, cur, connection):
        self.isTrusted = True
        cur.execute("UPDATE Sensor SET isTrusted = True WHERE id_sensor = %s", (self.pin, )) 
        connection.commit()

    ''' Take data from MCP pin specified '''
    def takeDataFromSensor(self):
        return MCP3008(self.pin).raw_value

    

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
    volume: int
    square: float
    mass_soil: float
    mass_water_max: float
    rest_moisture: int    
    
    def __init__(self, id: int, sens: Sensor, sol: Solenoid, pl: Plant, mode: str, isIrrigated: bool, vol: int, sq: float, density: float, koeff: float, rest: int):
     
        self.id = id
        self.sensor = sens
        self.sol = sol
        self.plant = pl
        self.mode = mode
        self.isIrrigated = isIrrigated
        self.volume = vol
        self.square = sq
        self.mass_soil = self.volume * density    
        self.mass_water_max = self.mass_soil * koeff    
        self.rest_moisture = rest
        
    def __str__(self):
        return 'pot' + str(self.id) + ' ' + str(self.sensor) + ' ' + str(self.sol) + ' ' + str(self.plant)    

            
    def activateModelMode(self, cur, connection):
        self.mode = 'model'
        cur.execute("UPDATE Flowerpot SET mode = 'model' WHERE id_flowerpot = %s", (self.id, ))
        connection.commit()
        
    def activateSensorMode(self, cur, connection):
        self.mode = 'real'
        cur.execute("UPDATE Flowerpot SET mode = 'real' WHERE id_flowerpot = %s", (self.id, ))
        connection.commit()

    def takeNeedWaterByModel(self, temp, hum, rain, cur, connection):
        refers = [10, 20, 30, 40, 50]
        limits = [None, None]

        for x in refers:
            if (int(temp/x) == 1):
                limits[0] = x
            if (int(temp/x) + 1 == 1):
                limits[1] = x
                break
        
        cat = self.plant.category.id
  
        cur.execute("SELECT water FROM TemperatureData WHERE (id_category = %s AND temperature = %s);", (cat, limits[0]))
        prev = cur.fetchone()[0]
        cur.execute("SELECT water FROM TemperatureData WHERE (id_category = %s AND temperature = %s);", (cat, limits[1]))
        post = cur.fetchone()[0]

        needForTemp = (post - prev)*(temp - limits[0])/(limits[1]-limits[0]) + prev
        kPot = 0
        if (self.volume > 10000):
            kPot = self.volume/20000
        elif (self.volume > 1500):
            kPot = (self.volume/2000)
        else:
            kPot = 1
        
        print('need for this temperature = ' + str(needForTemp) + '  pot koeff = ' + str(kPot))
        
        # calculate volume of precipitations added yesterday
        volumeRain = self.square * rain * 10    # API send rain in mm -> convert to cm
        
        need = 0
        if (volumeRain + self.rest_moisture >= needForTemp * kPot):       # if precipitations were > needForTemp  ->  save in BD all which wasn't consumed
                        
            rest = volumeRain + self.rest_moisture - needForTemp * kPot
            
            # save the rest in DB
            cur.execute("UPDATE Flowerpot SET rest_moisture = %s WHERE id_flowerpot = %s;", (rest, self.id, ))
            connection.commit()
            
            return need
        
        else:
            need = needForTemp * kPot - volumeRain - self.rest_moisture           
            return int(need)


    def takeNeedWaterBySensors(self, persents):        
        # comfort watering level = mid ( upper_limit, lower_limit )
        needWaterMass = int(self.mass_water_max * (self.plant.category.upper_limit + self.plant.category.lower_limit)/200) # g

        print("mass of water for 100% humidity " + str(self.mass_water_max))
        actualWaterMass = int(self.mass_water_max * persents/100)
        
        print("needWaterMass / actualWaterMass = " + str(needWaterMass) + ' / ' + str(actualWaterMass))

        return needWaterMass - actualWaterMass


class DeviceControl:
    auto_mode: int
    max_iter: int
    log_file: str
    density_soil: float
    water_koeff: float
    absorption_duration: int
    outdoor: int
    nbWatered: int

    def __init__(self):
        self.auto_mode    = ''
        self.max_iter     = -1
        self.log_file     = ''
        self.density_soil = -1
        self.water_koeff  = -1
        self.absorption_duration = -1
        self.list_pots = []
        self.nbWatered = 0
        # read parameters from config
        try:
            with open('config.txt', mode='r') as config:
                for line in config:
                    p = line.strip().split('=')
                    if (p[0] == 'mode'):
                        self.auto_mode = p[1]
                    if (p[0] == 'maxIterations'):
                        self.max_iter = int(p[1])
                    if (p[0] == 'logFile'):                
                        self.log_file = p[1]
                    if (p[0] == 'density'):                
                        self.density_soil = float(p[1])
                    if (p[0] == 'waterKoeff'):                
                        self.water_koeff = float(p[1])
                    if (p[0] == 'absorbDur'):                
                        self.absorption_duration = int(p[1])
                    if (p[0] == 'outdoor'):                
                        self.outdoor = int(p[1])
                config.close()
        except IOError:
            self.logging('fatal', 'Initialisation: open config failure')
                    
        if (self.auto_mode == '' or self.max_iter < 0):
            self.logging('fatal', 'Problem with config')


    ''' Write logs to file'''
    def logging(self, log_level, log_str):        
        try:
            with open(self.log_file, mode='a') as file:        
                current_time = datetime.now()
                time_stamp = current_time.timestamp()            
                date_time = datetime.fromtimestamp(time_stamp)        
                str_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")        
                file.write(str_date_time + ' ' + log_level + ' ' + log_str + '\n')
                file.close()
        except Exception as e:
            print('Cannot open config file by path ' + self.log_file)
    
    ''' Compose report to log'''
    def makeReport(self, sens, sol, modeLoc, attempt, hum, cat, dur):
        s = 'A, sens' if (self.auto_mode == 'auto') else 'M, sens'
        s += str(sens)+', sol'+str(sol)+', mode '+modeLoc+', attempt '+str(attempt)+', humidity '+str(hum)+'%, category '+str(cat)+', duration '+str(dur)+'s.'
        print(s)
        self.logging('info', s)
        
    
    ''' Create connection'''
    def databaseConnection(self):
        try:
            conn = mariadb.connect(
                #replace file!
                user="admin",
                password="admin",
                host="localhost",
                database="arrosage"
            )
            return conn
        except mariadb.Error as e:
            self.logging('error', 'Error connecting to MariaDB Platform: ' + str(e))        
                
        
    ''' Create all classes with data from DB'''   
    def fillCurrentObjects(self, cur):        
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
            newSensor = Sensor(rez[0], rez[1], rez[2], rez[3], rez[4])    
            
            #solenoid
            cur.execute("SELECT * FROM Solenoide WHERE id_solenoid = %s;", (pot[3], ))
            rez = cur.fetchone()        
            newSol = Solenoid(rez[0], rez[1], rez[2])
            
            self.list_pots.append( Pot(pot[0], newSensor, newSol, newPlant, pot[4], pot[5], pot[6], pot[7], self.density_soil, self.water_koeff, pot[8]))
            
    
    
    '''Watering one pot '''
    ''' WARNING: it is not an error that the "on" function is first called to stop the current supply (in case it is supplied)
            - this is not a mistake!'''
    ''' The wiring diagram of the relay in our system is such that "on" works like "off" and vice versa'''
    def wateringOne(self, led, duration): 
        led.off()
        time.sleep(duration)
        led.on()
    
    ''' Watering all pots '''
    def wateringAll(self, list_pins: [(int, int)]) -> ():   
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
        p = Thread(target = self.wateringOne, args = (pump, durPump, ))
        threads.append(p)
        p.start()
            
        for i in range(len(dur_list)):
            t = Thread(target = self.wateringOne, args = (sol_list[i], dur_list[i], ))
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
    
        
   # def isInList(self, liste, el):
   #     try:
    #        liste.index(el)
    #    except Exception as e:
    #        return False        
    #    return True
    
    ''' Ask sensors 2 times per minute during 30 mimutes, and calculate dispersion'''
    def sensorsVerification(self, cur, connection):
        dataLists = list()
        pots = list()
        avgList = list()
        dispList = list()
        
        for pot in self.list_pots:            
            if (pot.isIrrigated):
                pots.append(pot)
                newList = list()
                dataLists.append(newList)
                self.nbWatered += 1
        
        # collect row data
        counter = 5
        #counter = 60             TODO change
        while(counter):
            print('iter : ' + str(counter))
            
            for i in range(self.nbWatered):
                dataLists[i].append(pots[i].sensor.takeDataFromSensor())
            counter -= 1            
            time.sleep(10)
           # time.sleep(30)       TODO change
           
        
        # calculate dispertion
        for i in range(self.nbWatered):
            avg = sum(dataLists[i]) / len(dataLists[i])
            
            if (1023 == avg):
                self.logging('debug', 'Connection to sensor ' + str(pots[i].sensor.pin) + ' is broken. Sensor is desactivated.')
                pots[i].sensor.desactivateSensor(cur, connection)
                pots[i].activateModelMode(cur, connection)
                
            summ = 0
            for val in dataLists[i]:
                summ += math.pow((val - avg), 2)
                
            dispList.append( math.sqrt(summ / len(dataLists[i])) )
            avgList.append(avg)
            
        # analyse results
        for i in range(self.nbWatered):
            # normal deviation is less than 5% of the sensor's range
            #  and values doesn't out of sensor's range more then 10%
            onePercentEq = (pots[i].sensor.max_val - pots[i].sensor.min_val)/100
            if (dispList[i] > (5 * onePercentEq)) or (min(dataLists[i]) < (pots[i].sensor.min_val - 10 * onePercentEq)) or (max(dataLists[i]) > (pots[i].sensor.max_val + 10 * onePercentEq)) :                
                self.logging('debug', 'Sensor' + str(pots[i].sensor.pin) + ' is unstable and will be desactivated.')
                pots[i].sensor.desactivateSensor(cur, connection)
                pots[i].activateModelMode(cur, connection)
        
        return avgList


    def takeWheatherStatistics(self):
        count = 5      # 5 attempts to obtain weather forecast 
        today = date.today()
        yesterday = today - timedelta(days = 1)
        req = 'https://api.open-meteo.com/v1/forecast?latitude=48.85&longitude=2.35&hourly=temperature_2m,relativehumidity_2m,precipitation&start_date=' + str(yesterday) + '&end_date=' + str(yesterday)
        while (count):
            try:            
                response = requests.get(req).text
                response_info = json.loads(response)
                hourly = response_info['hourly']
            
                temperatures = hourly['temperature_2m']
                print('temperatures : ' + str(temperatures))
                humidities = hourly['relativehumidity_2m']
                print('humidities : ' + str(humidities))
                precipitations = hourly['precipitation']
                print('precipitations : ' + str(precipitations))

                def weighted_average(list):
                    n_measurements = len(list)
                    durations = [1] * n_measurements
    
                    # calculate the total duration for the day
                    total_duration = sum(durations)
    
                    # calculate the sum of the products of temperatures and durations
                    weighted_sum = sum([temp * duration for temp, duration in zip(list, durations)])
    
                    # calculate the weighted average temperature
                    weighted_average = weighted_sum / total_duration
    
                    return weighted_average 

                average_temp = weighted_average(temperatures)
                print('average_temp          = ' + str(average_temp))
                average_humidity = weighted_average(humidities)
                print('average_humidity      = ' + str(average_humidity))
                sum_precipitation = sum(precipitations)
                print('sum_precipitation     = ' + str(sum_precipitation))

                return (average_temp, average_humidity, sum_precipitation)
            
            except Exception as e:
                count -= 1
                time.sleep(30)
                self.logging('error', 'Weather forecast error : ' + str(e))  
        self.logging('error', 'Weather forecast error : ' + str(e)) 
        return None
    
    
    def saveModelAndReal(self, data):
        path_dir = os.path.abspath(os.path.join('..'))
        path_dir = os.path.join(path_dir, 'Data_To_Teach')
        if (not os.path.exists(path_dir)):
            os.mkdir(path_dir)
        path = os.path.join(path_dir, 'data.txt')
    
        with open(path, mode='a') as csvfile:            
            writer = csv.writer(csvfile, delimiter = ",", lineterminator="\r")
                       
            for k,v in data.items():               
                writer.writerow([k.sensor.id, v[0], v[1]])
                
            writer.writerow([])
            csvfile.close()
    

    def autoMode(self):    
   
        #1) connect to DB
        connection = self.databaseConnection()
        cur = connection.cursor()
        
        #2) data from DB -> fill classes    
        self.fillCurrentObjects(cur)
        
        #3) Check sensors      
        self.sensorsVerification(cur, connection)

        #4) take YESTERDAY weather forecast if outdoor
        temp = 20
        hum  = 40
        rain = 0
        
        if self.outdoor:            
            res = self.takeWheatherStatistics()
            if ( res != None):
                temp = res[0]
                hum = res[1]
                rain = res[2]
            else:
                print('TODO user email alert + arrosage by old data')

        #5) Calculate model for all pots + watering those that work according to the model
        listPins = []
        data = dict()
        attempt = 1  
        
        for pot in self.list_pots:
                if (pot.isIrrigated):
                
                    waterNeedModel = pot.takeNeedWaterByModel(temp, hum, rain, cur, connection)
                    data[pot] = [waterNeedModel]
                    
                    if (not pot.sensor.isTrusted):
                        duration = int(waterNeedModel/pot.sol.debit)
                        listPins.append([pot.sol.pin, duration])    
                        self.makeReport(pot.sensor.id, pot.sol.id, pot.mode, attempt, None, pot.plant.category.id, duration)                    
        
        self.wateringAll(listPins)
        listPins.clear()        
        
        modelWatered = []    
        realWatered = []        
       
        
        #6) Watering by sensors
        while (True):                   
            for pot in self.list_pots:
                if (pot.isIrrigated):
                    if (pot.sensor.isTrusted):
                        value = pot.sensor.takeDataFromSensor()                        
                        print('value from sensor : ' + str(value))
                    
                        if ( 1023 == value ):
                            self.logging('debug', 'Connection to sensor ' + str(pot.sensor.pin) + ' is broken.')
                        
                            pot.sensor.desactivateSensor(cur, connection)                        
                            pot.activateModelMode(cur, connection)
                            
                            waterNeedModel = pot.takeNeedWaterByModel(temp, hum, rain, cur, connection)
                            data[pot][0] = waterNeedModel
                            duration = int( waterNeedModel/pot.sol.debit )
                            
                            modelWatered.append((pot, attempt, None, duration))
                     
                        else:

                            
                            persents = 100 - 100*(value - pot.sensor.min_val)/(pot.sensor.max_val - pot.sensor.min_val)
                            persents = 0 if (persents <= 0) else int(persents)
                            print(str(persents) + '%')                           
                            
                            waterNeedSensors = pot.takeNeedWaterBySensors(persents)
                            print('water need by real  = ' + str(waterNeedSensors))                            
                            print('water need by model = ' + str(data[pot][0]))
                            if (1 == attempt):
                                data[pot].append(waterNeedSensors)

                            duration = int( 0 if (waterNeedSensors <= 0) else waterNeedSensors/pot.sol.debit )

                            realWatered.append((pot, attempt, int(persents), duration))
                            
                            print('==================================')   

            # check if somebody still needs water            
            nbReal = len(realWatered)
            nbModel = len(modelWatered)
            print('nb Watering Real Pots :' + str(nbReal))
            print('nb new Broken Sensors :' + str(nbModel))
            
            if (nbReal == 0) and (nbModel == 0):   # all plants watered, dont need working next 24h
                self.logging('info', 'Watering completed by ' + str(attempt - 1) + ' attempt(s), no errors')
                cur.close()
                connection.close()
                return
            
            # arrosage
            else:
                if (attempt > self.max_iter):
                    self.logging('error', 'The number of attempts has been exceeded, but the data on the need for watering continues to be received')
                    cur.close()
                    connection.close()
                    return
                    
                listPins = []
                for item in realWatered:
                    p        = item[0]
                    attempt  = item[1]
                    persHum  = item[2]  # for report
                    duration = item[3]  # duration

                    listPins.append([p.sol.pin, duration])
                    
                    self.makeReport(p.sensor.id, p.sol.id, p.mode, attempt, persHum, p.plant.category.id, duration)
                
                for item in modelWatered:
                    p        = item[0]
                    attempt  = item[1]
                    persHum  = item[2]  # for report
                    duration = item[3]  # duration
                    
                    listPins.append([p.sol.pin, duration])
    
                    self.makeReport(p.sensor.id, p.sol.id, p.mode, attempt, persHum, p.plant.category.id, duration)
                    
                self.wateringAll(listPins)
    
                        
            if (1 == attempt):
                self.saveModelAndReal(data)
                
            attempt += 1
            realWatered.clear()
            modelWatered.clear()
            listPins.clear()
            
            
            #time.sleep(self.absorption_duration)       TODO change
            time.sleep(10)
       
        

def main():
    dc = DeviceControl()  
    if (dc.auto_mode == 'auto'):
        dc.autoMode()
    


    
if __name__ == '__main__':
    main()
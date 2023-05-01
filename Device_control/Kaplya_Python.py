
# imports
from gpiozero import LED, MCP3008
import sys
import time
from time import sleep
from datetime import datetime
import csv
import os


# constants
MCP_pins_count = 4
PIN_PUMP = 24
PIN_SOL0 = 17
PIN_SOL1 = 27
PIN_SOL2 = 22
PIN_SOL3 = 14

LOG_FILE = 'log.txt'

MODE = "Relais test"    # comment   it to test sensor's data reception
                        # uncomment it to manipulate by relais

      
# Errors logging to file
def errorLogging(file_name: str, log_level: str, log_str: str):
    path_dir = os.path.abspath(os.path.join('..'))
    path_dir = os.path.join(path_dir, 'Server Nginx', 'arrosage')
    if (not os.path.exists(path_dir)):
        os.mkdir(path_dir)
    path = os.path.join(path_dir, file_name)
    
    with open(path, mode='a') as file:
        
        current_time = datetime.now()
        time_stamp = current_time.timestamp()            
        date_time = datetime.fromtimestamp(time_stamp)
        
        str_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S") 
        
        file.write(str_date_time + ' ' + log_level + ' ' + log_str + '\n')
        file.close()
    

# Tests sensors or solenoids + pump
def firstTests():
    
    if 'MODE' in globals():    # manipulate by relais  
        
        list_pins = [PIN_SOL0, PIN_SOL1, PIN_SOL2, PIN_SOL3, PIN_PUMP]
        sol_list = []

        for i in list_pins:
            sol_list.append(LED(i))
            
        for el in sol_list:        
            el.on() 
        
        while True:
            for el in sol_list:        
                el.off()
            time.sleep(1)
            
            for el in sol_list:        
                el.on()
            time.sleep(7)

    
    else:        # take data from MCP3008
        print(" 1   2   3   4 ")
        print("================================")
        while True:     
            # cycle: check the data from each of MCP's pins 
            for i in range(0, MCP_pins_count):        
                pot = MCP3008(i)                
                print(str(pot.raw_value), end = " ")            
            print("")
            time.sleep(PERIOD_1)

# Watering one pot.
# WARNING: it is not an error that the "on" function is first called to stop the current supply (in case it is supplied)
#        - this is not a mistake!
# The wiring diagram of the relay in our system is such that "on" works like "off" and vice versa
def wateringOne(relay_pin: int, duration: int) -> ():
    led = LED(relay_pin)
    pump = LED(PIN_PUMP)
    pump.on()    
    led.on()
    pump.off()
    led.off()
    time.sleep(duration)
    pump.on()
    led.on()

# Watering all pots.
# WARNING: it is not an error that the "on" function is first called to stop the current supply (in case it is supplied)
#        - this is not a mistake!
# The wiring diagram of the relay in our system is such that "on" works like "off" and vice versa
def wateringAll(list_pins: [int], duration: int) -> ():
    try:
        sol_list = []

        for i in list_pins:
            sol_list.append(LED(i))        

        for el in sol_list:        
            el.on()

        for el in sol_list:        
            el.off()
        
        time.sleep(duration)

        for el in sol_list:        
            el.on()
    except Exception as error:
        errorLogging(LOG_FILE, 'debug', error)
        
    
# Take data from each of MCP's pins specified
def takeDataFromAllSensors(buffer, pots) -> [int]:
    try:
        for i in range(0, MCP_pins_count):
            buffer.append(pots[i].raw_value)
        return buffer
    except Exception as error:
        errorLogging(LOG_FILE, 'debug', error)

# Take data from MCP pin specified
def takeDataFromSensor(pin: int) -> int:
    try:
        return MCP3008(pin).raw_value
    except Exception as error:
        errorLogging(LOG_FILE, 'debug', error)
    return -1


# Writes raw data from sensors to the .csv file (file_name) 'nb_iterations' times with a pause of 'period' seconds
def testAllSensors(nb_iterations: int, period: int, file_name) -> ():
    path_dir = os.path.abspath(os.path.join('..'))
    path_dir = os.path.join(path_dir, 'Tests')
    if (not os.path.exists(path_dir)):
        os.mkdir(path_dir)
    path = os.path.join(path_dir, file_name) 
 
    with open(path, mode='a') as csvfile:
            
        writer = csv.writer(csvfile, delimiter = ",", lineterminator="\r")
            
        current_time = datetime.now()
        time_stamp = current_time.timestamp()            
        date_time = datetime.fromtimestamp(time_stamp)
        str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")
        writer.writerow([str_date_time])
        
        buffer = []
        count = nb_iterations
        pots = list()
        for i in range(0, MCP_pins_count):    
            pots.append(MCP3008(i))
            
        while (count > 0):
            
            takeDataFromAllSensors(buffer, pots)                    
            print(buffer)                  
            writer.writerow(buffer)
            buffer.clear()
            count -= 1
            time.sleep(period)
            
        writer.writerow(buffer)
        csvfile.close()


    
# Writes raw data from sensors to the .csv file ('name_file')
# - sprinkling: execute sprinkling program according 'list_sprinkl_durations'
# - reading tha row data: reads row data 'repeat' times from sensors
# - save file in folder 'Tests' on root project
def calibration(list_pins: [int], list_sprinkl_durations: [float], repeat: int, name_file: str) -> ():
    
    absorption_duration = 5*60
    between_take_data = 5
    repeat_if_error = 1*60
    
    path_dir = os.path.abspath(os.path.join('..'))
    path_dir = os.path.join(path_dir, 'Tests')
    if (not os.path.exists(path_dir)):
        os.mkdir(path_dir)
    path = os.path.join(path_dir, name_file)
    
    with open(path, mode='a') as csvfile:
            
        writer = csv.writer(csvfile, delimiter = ",", lineterminator="\r")
        buffer = []
        
        # 0% : take initial data
        count = repeat
        while (count > 0):
            try:
                takeDataFromAllSensors(buffer)
                writer.writerow(buffer)
                print(buffer)
                buffer.clear()
                
                time.sleep(between_take_data)
                count-=1
            except Exception as error:
                errorLogging(LOG_FILE, 'debug', error)
                time.sleep(repeat_if_error)
        writer.writerow(buffer)         # insert space
                
        print("0% made")            
        # apply the plan of sprinkling and taking the row data
        for duration in list_sprinkl_durations:
            
            # sprinkling
            quantum = duration/int(duration)       # sprinkling will be made by quantum of 1,.. seconds
            
            times = int(duration)
            
            while (times > 0):
                try:
                    wateringAll(list_pins, quantum)
                    time.sleep(duration)
                    times-=1
                except Exception as error:
                    errorLogging(LOG_FILE, 'debug', 'solenoids failure: ' + error)
                    time.sleep(repeat_if_error)
                
            # wait to absorption accomplished            
            time.sleep(absorption_duration)
            
            # take data from sensors
            count = repeat
            while (count > 0):
                try:
                    takeDataFromAllSensors(buffer)
                    writer.writerow(buffer)
                    print(buffer)
                    buffer.clear()                    
                    time.sleep(between_take_data)
                    count-=1
                except Exception as error:
                    errorLogging(LOG_FILE, 'debug', 'sensors failure: ' + error)
                    time.sleep(repeat_if_error)
                    
            writer.writerow(buffer)         # insert space        
            print(str(duration) + " made")
            
        csvfile.close()
        

if __name__ == '__main__':  
    
    list_pins = [PIN_SOL0, PIN_SOL1, PIN_SOL2, PIN_SOL3, PIN_PUMP]

   # calibration(list_pins, [3.4, 2,3], 5, "test_file.csv")
   # buf = list()
   # print (takeDataFromAllSensors(buf))
   # testAllSensors(10, 5, "sensors_test_moist_soil.csv")

     

    
   # wateringOne(PIN_SOL0, 7)
    time.sleep(4)
   # wateringAll(list_pins, 7)
   
    wateringOne(PIN_SOL3, 2)



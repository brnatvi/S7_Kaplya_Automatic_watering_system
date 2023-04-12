
# imports
from gpiozero import LED, MCP3008
import sys
import time
from time import sleep
from datetime import datetime
import csv
import os


# constants
PERIOD_1 = 10
PERIOD_2 = 20
MCP_pins_count = 4
PIN_PUMP = 24
PIN_SOL0 = 17
PIN_SOL1 = 27
PIN_SOL2 = 22
PIN_SOL3 = 14

MODE = "Relais test"    # comment   it to test sensor's data reception
                        # uncomment it to manipulate by relais

# Tests sensors or solenoids + pump
def firstTests():
    
    if 'MODE' in globals():    # manipulate by relais  
        
        list_pins = [PIN_SOL0, PIN_SOL1, PIN_SOL2, PIN_SOL3, PIN_PUMP]
        sol_list = []

        for i in list_pins:
            sol_list.append(LED(i))
        
        while True:
            for el in sol_list:        
                el.on()

            for el in sol_list:        
                el.off()
            time.sleep(PERIOD_1)

            for el in sol_list:        
                el.on()
            time.sleep(PERIOD_1)

    
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



# Writes raw data from sensors to the .csv file 10 times with a pause of PERIOD_1 seconds
def testSensors():
    path_dir = os.path.abspath(os.path.join('..'))
    path_dir = os.path.join(path_dir, 'Tests')
    if (not os.path.exists(path_dir)):
        os.mkdir(path_dir)
    path = os.path.join(path_dir, 'sensors_calibration.csv') 
 
    with open(path, mode='a') as csvfile:
            
        writer = csv.writer(csvfile, delimiter = ",", lineterminator="\r")
            
        current_time = datetime.now()
        time_stamp = current_time.timestamp()            
        date_time = datetime.fromtimestamp(time_stamp)
        str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")

        writer.writerow([str_date_time])
        buffer = []
        count = 10
        while (count > 0):
            for i in range(0, MCP_pins_count):        
                pot = MCP3008(i)                    
                buffer.append(pot.raw_value)
                    
            print(buffer)                  
            writer.writerow(buffer)
            buffer.clear()
            count -= 1
            time.sleep(PERIOD_1)
            
        writer.writerow(buffer)
        csvfile.close()
        
def sprinkling(list_pins, duration):
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
        
    
# Check the data from each of MCP's pins 
def takeDataFromSensors(buffer):
    for i in range(0, MCP_pins_count):    
        pot = MCP3008(i)                
        buffer.append(pot.raw_value)           
    return buffer

    
# Writes raw data from sensors to the .csv file accordin the plan from 'calculation.xlsx' file 'calibration'
def calibration(list_pins):
    path_dir = os.path.abspath(os.path.join('..'))
    path_dir = os.path.join(path_dir, 'Tests')
    if (not os.path.exists(path_dir)):
        os.mkdir(path_dir)
    path = os.path.join(path_dir, 'persentage_calibration.csv')
    

 
    with open(path, mode='a') as csvfile:
            
        writer = csv.writer(csvfile, delimiter = ",", lineterminator="\r")

        writer.writerow(["==== PERSENTAGE CALIBRATION ======"])
        
        current_time = datetime.now()
        time_stamp = current_time.timestamp()            
        date_time = datetime.fromtimestamp(time_stamp)
        str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S") 

        writer.writerow([str_date_time])        
        
        buffer = []
        
        # 0% : take data
    #    for i in range(10):
   #         takeDataFromSensors(buffer)
    #        print(buffer)                  
    #        writer.writerow(buffer)
    #        buffer.clear()
    #        time.sleep(5)
        
        # 10% :   3,5s + 10min wait + take data
     #   qwant = 3.5/3
     #   for i in range(3):
     #       sprinkling(list_pins, qwant)
     #       time.sleep(60)
            
     #   time.sleep(10*60)
        
     #   for i in range(10):
     #       takeDataFromSensors(buffer)
     #       print(buffer)                  
     #       writer.writerow(buffer)
     #       buffer.clear()
     #       time.sleep(5)
            
        # 30% :   6,9s + 10min wait + take data
     #   qwant = 6.9/6
     #   for i in range(6):
     #       sprinkling(list_pins, qwant)
     #       time.sleep(60)
            
     #   time.sleep(10*60)
        
     #   for i in range(10):
      #      takeDataFromSensors(buffer)
     #       print(buffer)                  
     #       writer.writerow(buffer)
     #       buffer.clear()
     #       time.sleep(5)
     #   print(" 50%")
        
        # 50% :   6,9s + 10min wait + take data
     #   qwant = 6.9/6
     #   count = 6
     #   while(count > 0):
     #       try:
     #           sprinkling(list_pins, qwant)
     #           time.sleep(60)
     #           count-=1
     #       except SPISoftwareFallback, GPIOPinInUse:
     #           print("exception")
     #           time.sleep(60)
            
     #   time.sleep(5*60)
        
     #   count = 10
     #   while(count > 0):
     #       try:
     #           takeDataFromSensors(buffer)
     #           print(buffer)                  
      #          writer.writerow(buffer)
      #          buffer.clear()
      #          time.sleep(5)
     #           count-=1
     #       except SPISoftwareFallback, GPIOPinInUse:
     #           print("exception")
     #           time.sleep(60)
     #   print(" ")
        
        # 70% :   6,9s + 10min wait + take data
     #   qwant = 6.9/6
     #   count = 6
     #   while(count > 0):
     #       try:
     #           sprinkling(list_pins, qwant)
     #           time.sleep(60)
     #           count-=1
     #       except SPISoftwareFallback, GPIOPinInUse:
     #           print("exception")
     #           time.sleep(60)
            
     #   time.sleep(5*60)
        
        count = 4
        while(count > 0):
            try:
                takeDataFromSensors(buffer)
                print(buffer)                  
                writer.writerow(buffer)
                buffer.clear()
                time.sleep(5)
                count-=1
            except (SPISoftwareFallback, GPIOPinInUse) as error:
                print(error)
                time.sleep(60)
        print(" ")
        
        # 100% : 10,4s + 10min wait + take data
        qwant = 10.4/10
        count = 10
        while(count > 0):
            try:
                sprinkling(list_pins, qwant)
                time.sleep(60)
                count-=1
            except (SPISoftwareFallback, GPIOPinInUse) as error:
                print(error)
                time.sleep(60)                
            
        time.sleep(5*60)
        
        count = 10
        while(count > 0):
            try:
                takeDataFromSensors(buffer)
                print(buffer)                  
                writer.writerow(buffer)
                buffer.clear()
                time.sleep(5)
                count-=1
            except (SPISoftwareFallback, GPIOPinInUse) as error:
                print(error)
                time.sleep(60)
                
        csvfile.close()
        

if __name__ == '__main__':  
    
    #list_pins = [PIN_SOL0, PIN_SOL1, PIN_SOL2, PIN_SOL3, PIN_PUMP]
    
   # calibration(list_pins)
   firstTests()






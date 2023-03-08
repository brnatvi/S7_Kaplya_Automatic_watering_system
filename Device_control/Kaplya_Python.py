
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
        
        list_pins = [PIN_SOL0, PIN_SOL2, PIN_SOL2, PIN_SOL3, PIN_PUMP]
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
    path = os.path.join(path_dir, 'sensors_test_moist_nonisolated.csv') 
 
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
    


if __name__ == '__main__':
    testSensors()

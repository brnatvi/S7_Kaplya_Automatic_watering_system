
# imports
from gpiozero import LED, MCP3008
import sys
import time
from time import sleep
import datetime 


# constants
PERIOD = 5
MCP_pins_count = 8

MODE = "Relais test"    # comment   it to test sensor's data reception
                        # uncomment it to manipulate by relais


def firstTests():
    
    if 'MODE' in globals():    # manipulate by relais  
        
        list_pins = [14, 15, 17, 18, 22, 23, 24, 27]
        sol_list = []

        for i in list_pins:
            sol_list.append(LED(i))
        
        while True:
            for el in sol_list:        
                el.off()
            time.sleep(PERIOD)
            for el in sol_list:        
                el.on()
            time.sleep(PERIOD)
    
    else:        # take data from MCP3008   
        while True:     
            # cycle: check the data from each of MCP's pins 
            for i in range(0, MCP_pins_count):        
                pot = MCP3008(i)
                print("pin " + str(i) + " row value = " + str(pot.raw_value))                
            print("================================")
            time.sleep(PERIOD)



if __name__ == '__main__':
    firstTests()

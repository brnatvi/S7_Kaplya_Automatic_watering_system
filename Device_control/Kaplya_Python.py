
# imports
from gpiozero import LED, MCP3008
import sys
import time
from time import sleep
import datetime 


# constant
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


def firstTests():
    
    if 'MODE' in globals():    # manipulate by relais  
        
        list_pins = [PIN_SOL0, PIN_SOL2, PIN_SOL2, PIN_SOL3, PIN_PUMP]
        sol_list = []

        for i in list_pins:
            sol_list.append(LED(i))
        
        #while True:
            #for el in sol_list:        
            #    el.off()
            #time.sleep(PERIOD)
            #for el in sol_list:        
            #    el.on()
            #time.sleep(PERIOD)
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
            time.sleep(PERIOD)



if __name__ == '__main__':
    firstTests()

#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2019 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26
# @version $Id$

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import csv
import numpy as np

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 57600  # number of time steps
    # demand per second from different directions
    pWE = 1. / 10
    pEW = 1. / 10
    pNS = 1. / 30
    pSN = 1. / 30

    with open("data/osm.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="Bus" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="bus"/>

        <route id="right" edges="14342450 315218164#1 315218164#2 315218164#3 315218164#4 315218164#5 315218164#6 315218164#7 315218164#8 315218164#9 315218164#10 315218164#11" />

        <route id="left" edges="319655874#0 319655874#1 319655874#2 319655874#3 319655874#4 319655874#5 319655874#6 319655874#8 319655874#9 24252817#1" />

        <route id="up" edges="67701598#0 67701598#1 319655871#2 319655871#3 338413096" />

        <route id="down" edges="315557586#0 315557586#1 337605612 337605613 330154010#0 33783509#0 33783509#1 33783509#2" />""", file=routes)

        vehNr = 0
        for i in range(N):
            if random.uniform(0, 1) < pWE:
                print('    <vehicle id="right_%i" type="Bus" route="right" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1

            if random.uniform(0, 1) < pEW:
                print('    <vehicle id="left_%i" type="Bus" route="left" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1

            if random.uniform(0, 1) < pNS:
                print('    <vehicle id="down_%i" type="Bus" route="down" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1

            if random.uniform(0, 1) < pSN:
                print('    <vehicle id="up_%i" type="Bus" route="up" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
            
        print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#        <phase duration="30" state="GrGr"/>
#        <phase duration="5"  state="yryr"/>
#        <phase duration="30" state="rGrG"/>
#        <phase duration="5"  state="ryry"/>
#    </tlLogic>

def run():
    """execute the TraCI control loop"""
    step = 0
    
    NewCycleTime = 90
    TimePhase2 = 42
    TimePhase4 = 42
    K = 2
    Tw = 6
    n = 0			# n
    TotalHalt = 0	# TotalHalt
    TotalWTime = 0	# TotalWTime
  

    #Definir: Arreglo de n y Halt COMPLETE
  
    number=np.array([0,0,0,0,0,0,0,0,0,0])
    
    halt_acum=np.array([0,0,0,0,0,0,0,0,0,0])
    halt_average=np.array([0.0,0,0,0,0,0,0,0,0,0])
    halt_180=[0.0]
    
    cycle_acum=np.array([0,0,0,0,0,0,0,0,0,0])
    cycle_average=np.array([0.0,0,0,0,0,0,0,0,0,0])
    cycle_180=[0.0]
    
    waiting_acum=np.array([0,0,0,0,0,0,0,0,0,0])
    waiting_average=np.array([0.0,0,0,0,0,0,0,0,0,0])
    waiting_180=[0.0]    
    
    timing_Halt=180

    
    #Nombres COMPLETE

    Lanes = np.array([["-23804816#1_0","23804816#0_0","33783846#2_0","459468698#1_0"],["33783846#5_0","459468698#1_0","24252105#1_0","459468698#1_0"],["24252809#0_0","330172468#0_0","-330172468#1_0","459468698#1_0"],["319655871#3_0","315557586#1_0","33783846#6_0","459468698#1_0"],["14342450_0","319655874#9_0","330154010#0_0","67701598#1_0"],["315218164#1_0","319655874#8_0","33783824#1_0","459468698#1_0"],["315218164#2_0","319655874#6_0","33783335#3_0","459468698#1_0"],["337605613_0","319655871#2_0","330172469_0","459468698#1_0"],["330154009#7_0","459468698#1_0","23843773#1_0","459468698#1_0"],["315218164#10_0","319655874#0_0","23843773#5_0","459468698#1_0"]])

    Lights = np.array(["138851476","138851481","262577709","cluster_138851483_138852223","cluster_138852135_138852136_262577852_262577856_4318920281_4318920282","cluster_138852138_262577857_4318920283","cluster_138852139_2022135050_262577858_4318920284","cluster_138854732_138854733","cluster_138854740_4042381253_4042381255_4042381257_4042381260","cluster_258374867_262577862_4335777522"])

    #Arreglo de Tiempos y Fases COMPLETE
    T = np.array([[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90]])
    Phase = np.array([[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42]])
    
    #Inicializar todos los semaforos COMPLETE
    for i in range(len(Lights)):
        traci.trafficlight.setPhase(Lights[i], 0)

    while timing_Halt <= 3600:

        #Busca el tiempo siguiente
        timing = T.min()
        
        if timing_Halt < timing:
            traci.simulationStep(timing_Halt)
            for i in range(len(number)):
                halt_average[i]=halt_acum[i]/number[i]
                cycle_average[i]=cycle_acum[i]/number[i]
                waiting_average[i]=waiting_acum[i]/number[i]
                
                number[i]=0
                halt_acum[i]=0
                cycle_acum[i]=0
                waiting_acum[i]=0
                
            halt_180.append(sum(halt_average))
            cycle_180.append(sum(cycle_average))
            waiting_180.append(sum(waiting_average))

            timing_Halt +=180

        
        traci.simulationStep(timing)

        for i in range(len(T)):
                for j in range(len(T[i])):
                    if (T[i][j]) == timing:
                        if j == 2:
                            Number_E = traci.lane.getLastStepVehicleNumber(Lanes[i][0])
                            Number_W = traci.lane.getLastStepVehicleNumber(Lanes[i][1])
                            Number_N = traci.lane.getLastStepVehicleNumber(Lanes[i][2])
                            Number_S = traci.lane.getLastStepVehicleNumber(Lanes[i][3])
                            TotalNumber = Number_N + Number_S + Number_E + Number_W

                            NewCycleTime = round(((TotalNumber/K)+1)*Tw)
                            TimePhase2 = round(((Number_E + Number_W)/(K+TotalNumber))*NewCycleTime) -1 + 5
                            NewCycleTime = NewCycleTime + 10
                            TimePhase4 = NewCycleTime - TimePhase2 - Tw -2                

                            T[i][0] = timing + 1
                            T[i][1] = timing + TimePhase2 + (Tw/2) + 1 + 1
                            T[i][2] = timing + NewCycleTime
                            Phase[i][0] = TimePhase2
                            Phase[i][1] = TimePhase4

                            Times = [NewCycleTime, TimePhase2+1, Tw/2,TimePhase4+1, Tw/2]
                            #print("Inter:",i," ",Times)

                            Halt_N = traci.lane.getLastStepHaltingNumber(Lanes[i][0])
                            Halt_S = traci.lane.getLastStepHaltingNumber(Lanes[i][1])
                            Halt_E = traci.lane.getLastStepHaltingNumber(Lanes[i][2])
                            Halt_W = traci.lane.getLastStepHaltingNumber(Lanes[i][3])
                            TotalHalt = Halt_N+Halt_S+Halt_E+Halt_W
                            
                            Wait_N = traci.lane.getWaitingTime(Lanes[i][0])
                            Wait_S = traci.lane.getWaitingTime(Lanes[i][1])
                            Wait_E = traci.lane.getWaitingTime(Lanes[i][2])
                            Wait_W = traci.lane.getWaitingTime(Lanes[i][3])
                            TotalWait = Wait_N+Wait_S+Wait_E+Wait_W
                            
                            
                            halt_acum[i] = halt_acum[i] + TotalHalt
                            cycle_acum[i] = cycle_acum[i] + NewCycleTime
                            waiting_acum[i] = waiting_acum[i] + TotalWait
                            
                            number[i] = number[i]+1
                            
                        else:
                            traci.trafficlight.setPhaseDuration(Lights[i], Phase[i][j])
                            T[i][j] = 99999
                            
    
    halt_180 = np.multiply(halt_180,2)
    waiting_180 = np.multiply(waiting_180,2) 
    
    print(halt_180)
    print(cycle_180)
    print(waiting_180)
    
    # Guarda en Excel
    
    with open('Average Halting Vehicles.csv', mode='w') as csv_file:
        fieldnames = ['Total Halting vehicles', 'Total Cycle Time','Total Waiting Time']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for i in range(len(halt_180)):
            writer.writerow({'Total Halting vehicles': halt_180[i], 'Total Cycle Time':cycle_180[i], 'Total Waiting Time': waiting_180[i]})
    # Fin

    traci.close()
    sys.stdout.flush()
    


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/osm.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()

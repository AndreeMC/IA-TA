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
import genetic_algorithm as ga

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


def generate_routefile():
    #random.seed(42)  # make tests reproducible
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

def run():
    """execute the TraCI control loop"""

    #step = 0
    #TimePhase2 = 42
    #TimePhase4 = 42
    K = 2                       # Parametro de tuneo de funcion fitness
    Tw = 6                      # Duracion de fases en ambar ( 2 fases de ambar de 3 segundos)
    RefreshTime = 180           # Cada cuanto tiempo se actualizaran los tiempos en los semaforos
    
    number=np.array([0,0,0,0,0,0,0,0,0,0])                  # Arreglo de cantidad de ciclos que pasaron cada "RefreshTime" segundos

    CycleTime=np.array([90,90,90,90,90,90,90,90,90,90])  	# Arreglo de duracion de cada Ciclo en las 10 intersecciones

    totalVeh_acum = np.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]])
    totalVeh_average = np.array([[0.0,0.0,0.0,0.0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]])

    halt_acum=np.array([0,0,0,0,0,0,0,0,0,0])               # Suma de Cantidad de vehiculos detenidos al inicio de cada ciclo en "RefreshTime" segundos
    halt_average=np.array([0.0,0,0,0,0,0,0,0,0,0])          # Cantidad promedio de vehiculos detenidos al inicio del ciclo en "RefreshTime" segundos
    halt_180=[0.0]                                          # Arreglo que registrara cada "RefreshTime" segundos la Cantidad promedio de vehiculos
                                                            # detenidos al inicio del ciclo en toda la configuracion
    
    cycle_acum=np.array([0,0,0,0,0,0,0,0,0,0])              # Suma de Duracion de ciclo en "RefreshTime" segundos
    cycle_average=np.array([0.0,0,0,0,0,0,0,0,0,0])         # Duracion de ciclo promedio en "RefreshTime" segundos
    cycle_180=[0.0]                                         # Arreglo que registrara cada "RefreshTime" segundos la Duracion de ciclo promedio en
                                                            # toda la configuracion
    
    waiting_acum=np.array([0,0,0,0,0,0,0,0,0,0])            # Suma de Tiempo de espera al inicio de cada ciclo en "RefreshTime" segundos
    waiting_average=np.array([0.0,0,0,0,0,0,0,0,0,0])       # Tiempo de espera promedio al inicio del ciclo en "RefreshTime" segundos
    waiting_180=[0.0]                                       # Arreglo que registrara cada "RefreshTime" segundos el Tiempo de espera promedio
                                                            # al inicio del ciclo en toda la configuracion
    
    RefreshingTime=RefreshTime                              # Inicializo el tiempo de actualizacion

    #Arreglo de Tiempos y Fases COMPLETE
    T = np.array([[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90],[99999,99999,90]])
    
    Phase = np.array([[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42]])
    NewPhase = np.array([[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42],[42,42]])
    
    #Nombres COMPLETE

    Lanes = np.array([["-23804816#1_0","23804816#0_0","33783846#2_0","459468698#1_0"],["33783846#5_0","459468698#1_0","24252105#1_0","459468698#1_0"],["24252809#0_0","330172468#0_0","-330172468#1_0","459468698#1_0"],["319655871#3_0","315557586#1_0","33783846#6_0","459468698#1_0"],["14342450_0","319655874#9_0","330154010#0_0","67701598#1_0"],["315218164#1_0","319655874#8_0","33783824#1_0","459468698#1_0"],["315218164#2_0","319655874#6_0","33783335#3_0","459468698#1_0"],["337605613_0","319655871#2_0","330172469_0","459468698#1_0"],["330154009#7_0","459468698#1_0","23843773#1_0","459468698#1_0"],["315218164#10_0","319655874#0_0","23843773#5_0","459468698#1_0"]])

    Lights = np.array(["138851476","138851481","262577709","cluster_138851483_138852223","cluster_138852135_138852136_262577852_262577856_4318920281_4318920282","cluster_138852138_262577857_4318920283","cluster_138852139_2022135050_262577858_4318920284","cluster_138854732_138854733","cluster_138854740_4042381253_4042381255_4042381257_4042381260","cluster_258374867_262577862_4335777522"])


   
    #Inicializar todos los semaforos en Fase 1
    for i in range(len(Lights)):
        traci.trafficlight.setPhase(Lights[i], 0)


    # Simulación de 1 hora
    while RefreshingTime <= 3600:
        
        timing = T.min()                                    # Busca el tiempo siguiente de la matriz T (el mas proximo)
        
        if RefreshingTime < timing:                         # Si el tiempo de actualizacion esta mas proximo que todos los tiempos de la matriz T
            traci.simulationStep(RefreshingTime)            # Espera a que la simulacion llegue al tiempo de actualizacion
            for i in range(len(totalVeh_acum)):
                for j in range(len(totalVeh_acum[i])):
                    totalVeh_average[i][j]=totalVeh_acum[i][j]/number[i]
                    totalVeh_acum[i][j]=0

                halt_average[i]=halt_acum[i]/number[i]
                cycle_average[i]=cycle_acum[i]/number[i]
                waiting_average[i]=waiting_acum[i]/number[i]
                
                number[i]=0
                halt_acum[i]=0
                cycle_acum[i]=0
                waiting_acum[i]=0
                
            halt_180.append(sum(halt_average))
            cycle_180.append(sum(cycle_average))            # Agrego el valor de duracion de ciclo promedio de la configuracion al arreglo
            waiting_180.append(sum(waiting_average))        # Agrego el valor de tiempo de espera promedio de la configuracion al arreglo
            RefreshingTime += RefreshTime                   # Actualizo el tiempo de actualizacion

            # LLAMAR A GENETICOS
            
            # build the pool of alleles with the suitable random numbers
            target_example = [[10,20], [10,20], [10,20], [10,20], [10,20], [10,20], [10,20], [10,20], [10,20], [10,20]]
            #queued_vehicles = [[10,20,10,20], [10,20,10,20], [10,20,10,20], [10,20,10,20],[10,20,10,20], [10,20,10,20],[10,20,10,20], [10,20,10,20],[10,20,10,20], [10,20,10,20]]
            allele_pool = []
            allele_pool.extend( [x for x in range(5, 60)]) # posibles valores para los semaforos en verde

            #initialize a initial population randomnly
            num_individuals = 100
            population = ga.init_population(num_individuals, len(target_example)*2, allele_pool)

            #call genetic algorithm
            best_ind, best_fitness = ga.genetic_algorithm(population, ga.gpa_maximization, totalVeh_average, 300, 0.0, "uniform", "position")

            for i in range(len(Phase)):
                CycleTime[i] = Tw
                for j in range(len(Phase[i])):
                    NewPhase[i][j] = best_ind.chromosome[i][j]-1
                    CycleTime[i] = CycleTime[i] + NewPhase[i][j] + 1
            #plt.plot(bestfitness)
            #plt.show()

            # FIN DE GENETICOS
        
        traci.simulationStep(timing)                        # Espera a que la simulacion llegue al tiempo mas proximo de la matriz T

        for i in range(len(T)):
                for j in range(len(T[i])):
                    if (T[i][j]) == timing:
                        if j == 2:
                            Number_E = traci.lane.getLastStepVehicleNumber(Lanes[i][0])
                            Number_W = traci.lane.getLastStepVehicleNumber(Lanes[i][1])
                            Number_N = traci.lane.getLastStepVehicleNumber(Lanes[i][2])
                            Number_S = traci.lane.getLastStepVehicleNumber(Lanes[i][3])

                            totalVeh_acum[i][0] = totalVeh_acum[i][0] + Number_E
                            totalVeh_acum[i][1] = totalVeh_acum[i][1] + Number_W
                            totalVeh_acum[i][2] = totalVeh_acum[i][2] + Number_N
                            totalVeh_acum[i][3] = totalVeh_acum[i][3] + Number_S

                            #TotalNumber = Number_N + Number_S + Number_E + Number_W

                            #NewCycleTime = round(((TotalNumber/K)+1)*Tw)
                            #TimePhase2 = round(((Number_E + Number_W)/(K+TotalNumber))*NewCycleTime) -1 + 5
                            #NewCycleTime = NewCycleTime + 10
                            #TimePhase4 = NewCycleTime - TimePhase2 - Tw -2 
                            Phase[i] = NewPhase[i]

                            T[i][0] = timing + 1
                            T[i][1] = timing + Phase[i][0] + (Tw/2) + 1 + 1
                            T[i][2] = timing + CycleTime[i]

                            Times = [CycleTime[i], Phase[i][0]+1, Tw/2,Phase[i][1]+1, Tw/2]
                            print("Inter:",i," ",Times)

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
                            cycle_acum[i] = cycle_acum[i] + CycleTime[i]
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
    #generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/osm.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()

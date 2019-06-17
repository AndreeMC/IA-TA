#!/usr/bin/env python
# Algorithm that implements a discrete PSO algorithm
# for the traffic lights problem. It exposes a public
# interface with two methods:
# init_population and pso_algorithm.

# @file    pso.py
# @author  Alejandro Román
# @date    2019-06-16
# @version 0.1.0

from random import randrange

def init_population(num_particles, num_traffic_lights, max_time):
	"""
	Initializes population for pso algorithm for a 2-axes based traffic light.
    num_particles:  Number of particles in population
    num_traffic_lights: Number of traffics lights in one solution
	max_time: Max cicle time in seconds
	"""
	minPos = 1
	maxPos = max_time - 1
	population = []
	for i in range(num_particles):
		# Set the time for each axes.
		firstAxisPos = randrange(minPos, maxPos)
		secondAxisPos = max_time - firstAxisPos
		position = [firstAxisPos, secondAxisPos]

		# Set a random velocity. The new velocity must not have an axis that is below minPos or is greater than maxPos
		maxDelta = max(maxPos - firstAxisPos, maxPos - secondAxisPos, firstAxisPos - minPos, secondAxisPos - minPos)
		firstAxisVel = randrange(-maxDelta, maxDelta)
		if firstAxisPos + firstAxisVel < 1 or firstAxisPos + firstAxisVel > 89:
			firstAxisVel = -firstAxisVel

		# Remember that x + y must always be max_time, so if x increases by n, y must decrease by n.
		secondAxisVel = -firstAxisVel
		velocity = [firstAxisVel, secondAxisVel]

		# Store the new position-velocity pair
		population.append((position, velocity))
	return population

def pso_algorithm():
	print('pso_algorithm')

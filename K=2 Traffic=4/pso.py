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

class _Particle(object):
	"""
	Class that stores the information for a particle (a solution)
	:param pos: A list of pairs. Each pair represents a traffic light's times
	:param vel: A list of pairs. Each pair represents the velocity for the n-th traffic light in self.pos
	"""

	def __init__(self, trafficLightsTimes, max_time):
		self.pos = trafficLightsTimes
		self.vel = self.generateRandomVelocities(trafficLightsTimes, max_time)

	def generateRandomVelocities(self, trafficLightsTimes, max_time):
		"""
		Returns a list of random velocities pair for each pair of times in trafficLightsTimes.
		The velocities will comply the rule that states: (xTime + yTime = max_time).
		"""
		velocities = []
		minPos = 1
		maxPos = max_time - 1
		for tl in trafficLightsTimes:
			xPos = tl[0]
			yPos = tl[1]

			# Set a random velocity. The new velocity must not have an axis that is below minPos or is greater than maxPos
			maxDelta = max(maxPos - xPos, maxPos - yPos, xPos - minPos, yPos - minPos)
			xVel = randrange(-maxDelta, maxDelta)
			if xPos + xVel < minPos or xPos + xVel > maxPos:
				xVel = -xVel

			# Remember that (x + y) must always sum max_time, so if x increases by n, y must decrease by n.
			yVel = -xVel
			velocities.append((xVel, yVel))
		return velocities

def init_population(num_particles, num_traffic_lights, max_time):
	"""
	Return an initialized population for the pso algorithm for a 2-axes based traffic light problem.
    num_particles:  Number of particles in population
    num_traffic_lights: Number of traffics lights in one solution
	max_time: Max cicle time in seconds
	"""
	minPos = 1
	maxPos = max_time - 1
	population = []
	for particle in range(num_particles):
		trafficLights = []
		for tl in range(num_traffic_lights):
			# Set the time for each axis. Remember that xPos + yPos must sum max_time
			xPos = randrange(minPos, maxPos)
			yPos = max_time - xPos

			trafficLights.append((xPos, yPos))

		# Will the list of pairs of times for each traffic light, create a new particle
		p = _Particle(trafficLights, max_time)
		population.append(p)
	return population

def pso_algorithm(population, fitness_fn, w, phi1, phi2, max_iter):
	"""
	Return the best population and the best fitness obtained for the traffic light optimization problem.
    population:  The initial population
    fitness_fn: The fitness function that will the maximized
	w: Inertial factor
	phi1: Individual factor
	phi2: Social factor
	max_iter: Maximum number of iterations that the search will have
	"""
	bestPopulation = []
	bestFitness = -1

	#for iteration in range(max_iter):


	return bestPopulation, bestFitness

def _printPopulation(population):
	""" Debug function that prints a population """
	for particle in population:
		print("\nParticle")
		print(particle.pos)
		print(particle.vel)
#_printPopulation(init_population(6,10,90))

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

	def __init__(self, trafficLightsTimes, min_time, max_time):
		self.pos = trafficLightsTimes
		self.vel = self.generateRandomVelocities(trafficLightsTimes, min_time, max_time)

	def generateRandomVelocities(self, trafficLightsTimes, min_time, max_time):
		"""
		Returns a list of random velocities pair for each pair of times in trafficLightsTimes.
		"""
		velocities = []
		for tl in trafficLightsTimes:
			# Get the current position
			xPos = tl[0]
			yPos = tl[1]

			# Get a random new velocity that complies that (xPos + xVel) is in the range [min_time, max_time]
			xVel = randrange(min_time, max_time + 1) - xPos
			yVel = randrange(min_time, max_time + 1) - yPos

			velocities.append((xVel, yVel))
		return velocities

def init_population(num_particles, num_traffic_lights, min_time, max_time):
	"""
	Return an initialized population for the pso algorithm for a 2-axes based traffic light problem.
    num_particles:  Number of particles in population
    num_traffic_lights: Number of traffics lights in one solution
	max_time: Max green time for a traffic light
	min_time: Min green time for a traffic light
	"""
	population = []
	for particle in range(num_particles):
		trafficLights = []
		for tl in range(num_traffic_lights):
			# Set the time for each axis
			xPos = randrange(min_time, max_time + 1)
			yPos = randrange(min_time, max_time + 1)

			trafficLights.append((xPos, yPos))

		# Will the list of pairs of times for each traffic light, create a new particle
		p = _Particle(trafficLights, min_time, max_time)
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

	for iteration in range(max_iter):
		# Evaluate individual and global fitness
		for particle in population:
			# Update bestPopulation and bestFitness
			pass

		# Move each particle
		for particle in population:
			pass


	return bestPopulation, bestFitness

def _printPopulation(population):
	""" Debug function that prints a population """
	for particle in population:
		print("Particle")
		print("Pos: {}".format(particle.pos))
		print("Vel: {}\n".format(particle.vel))
_printPopulation(init_population(6,10,5,60))

#!/usr/bin/env python
# Algorithm that implements a discrete PSO algorithm
# for the traffic lights problem. It exposes a public
# interface with two methods:
# init_population and pso_algorithm.

# @file    pso.py
# @author  Alejandro Román
# @date    2019-06-16
# @version 0.1.0

from random import randrange, uniform
from genetic_algorithm import gpa_one_intersection

class _Particle(object):
	"""
	Class that stores the information for a particle (a solution)
	:param pos: A list of pairs. Each pair represents a traffic light's times
	:param vel: A list of pairs. Each pair represents the velocity for the n-th traffic light in self.pos
	:param previousBestPos: A pair of numbers that representes the previous best position for this particle.
	:param min_time: The minimun time allowed for a traffic light
	:param max_time: The maximum time allowed for a traffic light
	"""

	def __init__(self, trafficLightsTimes, min_time, max_time):
		self.pos = trafficLightsTimes
		self.vel = self.generateRandomVelocities(trafficLightsTimes, min_time, max_time)
		self.previousBestPos = self.pos # Initialized with the initial position
		self.min_time = min_time
		self.max_time = max_time

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

	def updatePosition(self, w, phi1, phi2, globalBestParticlePos):
		# Set the new velocity
		self.updateVelocity(w,phi1,phi2, globalBestParticlePos)

		# Add each velocity to their corresponding position
		for i in range(len(self.pos)):
			newX = self.pos[i][0] + self.vel[i][0]
			newY = self.pos[i][1] + self.vel[i][1]

			# Handle the valid range
			if newX < self.min_time:
				newX = self.min_time
			elif newX > self.max_time:
				newX = self.max_time

			if newY < self.min_time:
				newY = self.min_time
			elif newY > self.max_time:
				newY = self.max_time
			self.pos[i] = (newX, newY)

	def updateVelocity(self, w, phi1, phi2, globalBestParticlePos):
		for i in range(len(self.vel)):
			newX = self.updateVelSingleDimension(self.pos[i][0], self.vel[i][0], w, phi1, phi2, self.previousBestPos[i][0], globalBestParticlePos[i][0])
			newY = self.updateVelSingleDimension(self.pos[i][1], self.vel[i][1], w, phi1, phi2, self.previousBestPos[i][1], globalBestParticlePos[i][1])
			self.vel[i] = (newX, newY)

	def updateVelSingleDimension(self, pos, vel, w, phi1, phi2, previousBestPos, globalBestPos ):
		""" Updates the velocity in a single dimension (not with 2-dimension values) """
		return w * vel + phi1 * uniform(0,1) * (previousBestPos - pos) + phi2 * uniform(0,1) * (globalBestPos - pos)

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

def pso_algorithm(population, fitness_fn, queued_vehicles, w=0.8, phi1=2, phi2=2, max_iter=100):
	"""
	Return the best population and the best fitness obtained for the traffic light optimization problem.
    population:  The initial population
    fitness_fn: The fitness function that will the maximized
	queued_vehicles: A list of 4-dimension tuples that hold the queued vehicles for each lane.
	w: Inertial factor
	phi1: Individual factor
	phi2: Social factor
	max_iter: Maximum number of iterations that the search will have
	"""
	globalBestParticlePos = population[0].pos # Initialized with the first particle

	for iteration in range(max_iter):
		# Update individual and global fitness
		for particle in population:
			fitness = fitness_fn(particle.pos, queued_vehicles)
			if fitness > fitness_fn(particle.previousBestPos, queued_vehicles):
				particle.previousBestPos = particle.pos

			if fitness_fn(particle.previousBestPos, queued_vehicles) > fitness_fn(globalBestParticlePos, queued_vehicles):
				globalBestParticlePos = particle.pos

		# Move each particle
		for particle in population:
			particle.updatePosition(w, phi1, phi2, globalBestParticlePos)

	return _roundPosition(globalBestParticlePos), fitness_fn(globalBestParticlePos, queued_vehicles)

def pso_maximization(particlePosition, queued_vehicles):
	""" Returns the fitness for the particle's position and the current queued_vehicles distribution """
	fitness = 0
	for traffic_light in particlePosition:
		fitness += gpa_one_intersection(traffic_light, queued_vehicles)
	return fitness

def _roundPosition(positions):
	""" Returns the populations with it's positions rounded to the nearest integer """
	newPos = []
	for i in range(len(positions)):
		newX = round(positions[i][0])
		newY = round(positions[i][1])
		newPos.append((newX, newY))
	return newPos


#population = init_population(20,10,5,60)
#bestTimes, bestFitness = pso_algorithm(population, pso_maximization, [5,6,7,8], 0.8, 0.1, 0.1, 10)

#print('Best times: {}\nBest Fitness:{}'.format(bestTimes, bestFitness))

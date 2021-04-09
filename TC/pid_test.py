import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.interpolate import make_interp_spline as spl

class PID():

	def __init__(self,
	             kp = 1.0,
	             ki = 0.1,
	             kd = 0.0):
		'''
			Define the 'PID' object
		'''
		# PID parameters
		self.kp = kp
		self.ki = ki
		self.kd = kd

		# PID terms
		self.pTerm = 0
		self.iTerm = 0
		self.dTerm = 0

		# Default value of set point
		self.set_point = 0

		# Sampling time
		self.sample_time = 0.02

		# Timing
		self.current_time = time.time()
		self.old_time = self.current_time

		# Last returned output value
		self.outValue = 0

		# Last error
		self.last_error = 0

		# Last measured value of variable y
		self.last_y = 0

	def __repr__(self):
		r = '''
		(kp,
		 ki,
		 kd,
		 set_point,
		 sample_time)
		 ''' %(self.kp,
		       self.ki,
		       self.kd,
		       self.set_point,
		       self.sample_time)
		return r

	def output(self, y_measured):
		'''
			Calculate PID output value via:
			outValue(t) =   kd * f(t)
						  + ki * cumulative_sum(f(t) * dt)
						  + kd * df(t)/dt
		'''
		# Calculate current error
		error = self.set_point - y_measured

		# Get elapsed time
		self.current_time = time.time()
		dt = self.current_time - self.old_time

		# Calculate output
		if dt >= self.sample_time:
			# P term
			self.pTerm  = self.kp * error
			# I term
			self.iTerm += self.ki * error * dt
			# D term
			self.dTerm  = self.kd * (self.last_y - y_measured)/dt

			# Update variables
			self.last_error = error
			self.last_y     = y_measured
			self.old_time   = self.current_time

			# Output value to be returned
			self.outValue = self.pTerm + self.iTerm + self.dTerm

			return self.outValue
		else:
			return 0



def Run_PID(dutycycle,setpoint,t1,kp,ki,kd):
	pid = PID(kp, ki, kd)
	dutycycle+=pid.output(t1)
	pid.set_point=setpoint
	return(dutycycle)

################################################################################
#								 End PID test
################################################################################

'''Vowel evolution program.
Run with Convention, Prototype, Game_fns, im_game, Agent
See Game_fns.py
Last update March 2016 HJMS'''

import random #used for generating formants 

class Vowel:
	'''Vowel class -- 
	Represented by tuple: Vowel(f1_hz, f2_hz, length, weight)
	Arguments taken and stored in ERB, Hz conversions are determined on initialization
	Call self.f1_erb and self.f2_erb for ERB values

	f1_hz is open to closed, type int
	f2_hz is front to back, type int
	Length is duration in milliseconds

	Hertz values are for interface / user interaction,
	ERB values are for calculations.

	Weight is functional load where zero is weakest.
	Weight is determined by the number of words "using" a vowel for an Agent.
	If no weight is set, it will default to zero.
	'''

	def __init__(self, e1, e2, length, name, weight = 0):
		self.e1 = e1	#ERB first formant (lip rounding e.g. high/low)
		self.e2 = e2	#ERB second formant (tongue position e.g. front/back)
		self.length = length	#duration (constant--no trajectory--in milliseconds) e.g. [100..300]
		self.name = name		#IPA symbol name (see Convention class)
		self.weight = weight	#Heavy vowels resist change, see Agent class
		

		#FEATURES
		#NOTE TO LINGUISTS...
		#Please don't misconstrue this as an implementation of binary features
		self.nasal = False
		self.rounded = False
		self.retracted = False
		
		self.neighbors = []	 #neighbors are Agent's other Vowels within some margin (see Agent.py)
		


	def erb_tuple(self):
		'''returns a tuple of (e1, e2) i.e. (float, float)''' 
		return (self.e1, self.e2)

	
				
	def euclid_dist(self, v, w):
		'''
		Distance in ERB between two Vowels
		v, w are both Vowel objects
		returns a float
		'''
		e1_dif = (v.e1 - w.e1)
		e2_dif = (v.e2 - w.e2)
		return ((e1_dif * e1_dif) + (e2_dif * e2_dif))**.5

	

	def cc(self):
		V = Vowel
		nv = V(self.e1, self.e2, self.length, self.name)
		nv.weight = self.weight
		return nv

	
	
	def euc(self, v):
		'''
		Distance in ERB between self and another Vowel
		v is a Vowel object
		returns a float
		'''
		e1_dif = (self.e1 - v.e1)
		e2_dif = (self.e2 - v.e2)
		return ((e1_dif * e1_dif) + (e2_dif * e2_dif))**.5

	

	def set_weight(self, weight):
		'''overwrite vowel weight'''
		self.weight = weight

		

	def __repr__(self):
		'''shown as 'f1_hz, f2_hz, rounded, length' '''
		e1 = self.e1
		e2 = self.e2
		repr_s = ", ".join( [ str(e1), str(e2), str(self.length)] )
		return '('+repr_s+')'

	
	
	def __str__(self):
		'''
		shown as 'f1, f2, length, weight, features'
		features <- [rounded, retracted, nasal] where true

		str() and repr() use HZ as INTs for first formant, second formant,
		where everything else is in ERB units, which are FLOATs

		The e1, e2 values are converted at every print call
		because hz_to_erb and erb_to_hz functions are not invertible.
		'''
		f1, f2 = to_hz_praat(self.e1, self.e2)
		str_l = [str(int(f1)), str(int(f2)), str(self.length), ("%.4f" %self.weight)]
		
		if self.rounded:
			str_l.append("rnd")
		if self.nasal:
			str_l.append("nsl")
		if self.retracted:
			str_l.append("rtr")
			
		str_s = ", ".join(str_l)
		
		return '('+str_s+')'

	

	def __hash__(self):
		'''use e1 (float), e2 (float) and length (int)'''
		return hash((self.e1, self.e2, self.length))

	

	def __eq__(self, other):
		'''True if formant values match exactly (not weight).
		NOT suitable as a matching function for RECOGNIZING vowels,
		see Agent match functions
		This will only compare objects to see if they are identical i.e. "is" function '''
		vwl = (self.e1, self.e2, self.length) == (other.e1, other.e2, other.length)
	

#########################
#	Utility Functions	#
#########################

def to_erb(f1, f2):
	'''
	direct implementation of traunmuller formula to convert from hertz to ERB
	just converts a tuple (f1, f2) in hz to erb
	benefit is that it doesn't have to be a Vowel, just the values
		i.e. calling >>to_erb(2400, 800) in IDLE will output (22.44472228978699, 13.58504853003826)
	NOT invertible with to_hz function -- some data / precision lost in conversions
	'''

	from math import log
	
	def conv(f):
		b_n = f/1000 + .312
		b_d = f/1000 + 14.680
		b_r = b_n/b_d
		prod =(11.17 * (log(b_r)))
		s = prod + 43
		return s

	e1 = conv(f1)
	e2 = conv(f2) 
	return (e1, e2)

#gives an approximate answer. There seems to be some data loss, but it's pretty close
#I don't know if this is due to insufficient bit size (float may not be precise enough)
#or if it's the formula
#voicebox method:
def to_hz_vb(e1, e2 = 0):
	'''
	Formula used in Voicebox software
	Origin undetermined
	'''
	from math import log, exp, e
	f1 = ( 676170.4 * ( 47.06538 - exp( 0.08950404*abs(e1) ) ) ** (-1) - 14678.5 )
	f2 = 0
	if e2:
		f2 = ( 676170.4 * ( 47.06538 - exp( 0.08950404*abs(e2) ) ) ** (-1) - 14678.5 )
	return(f1, f2) 
	
#praat method
def to_hz_praat(e1, e2):
	'''
	Traunmuller's formula used in Praat software
	not invertible with to_erb (some loss during conversions)
	'''
	from math import exp
	d1 = exp ((e1 - 43.0) / 11.17)
	f1 = (14680.0*d1 - 312.0) / (1 - d1)

	d2 = exp ((e2 - 43.0) / 11.17)
	f2 = (14680.0*d2 - 312.0) / (1 - d2)
	return (f1, f2)


'''
Vowel Evolution program Phonology class.
Run in PYTHON 3(!)
with Vowel, Game_fns, Prototype, Word, Agent, Convention, graphics files in same directory

import time, random, re from Python library
Last update November 2017 HJMS


SYLLABLES		
Using a grammary organization to represent syllables
Dynamic vowels may be overreaching for this project,
so we've ditched those for now.
We've also made consonant features more fluid.

	Syllable => onset + nucleus + coda
	Onset => (consonant | null)
	Nucleus => vowel
	Coda => (consonant | null)
	consonant =>  (coronal | labial | dorsal | laryngeal) + (voiced | voiceless)
	vowel => (high | mid | low) + (front | central | back) + (long | short)

	We are forbidding vowels in onsets or codas.
	
	* In future we hope to have 
		Nucleus => (vowel + vowel) | (vowel + null) | (null + vowel)
	  To accommodate diphthongs
	

COARTICULATION/FEATURE EFFECTS
If you're wondering how we got these precise values for the formant effects,
the official answer is "we stayed at a Holiday Inn Express last night,
more succinctly FIIK;WMTU."

'''

import Agent, Convention, Vowel
from time import ctime
from graphics import *
import re
from random import sample, choice, uniform, randint

max_e1 = Agent.e1_max()
min_e1 = Agent.e1_min()
max_e2 = Agent.e2_max()
min_e2 = Agent.e2_min()
extra = 1.0




def edge_adj(edge, f):
	bound_buff = abs(edge - f) #decrease effect close to boundary
	mult = min([1, bound_buff]) #goes to 0 if peripheral, up to 1
	return mult





class Phonology:

	def __init__(self, features = None):
		self.set_features(features)

		
		
		

	def set_features(self, fl=None):
		'''

		Based on Flynn 2012.
		Each key needs to be mapped to a function.
		Functions can be reused, but keys can't.
		
		'''
		
												
		self.articulations = {"null": self.null,
							  "stop": self.stop,
							  "nasal": self.nasal,
							  "rhotic": self.rhotic,
							  "labial": self.labial,
							  "rounded": self.rounded,	#round is a reserved word in Python
							  "coronal": self.coronal,
							  "lateral": self.lateral,
							  "strident": self.strident,
							  "laryngeal": self.laryngeal,
							  "fricative": self.fricative,
							  "posterior": self.posterior,
							  "laminal": self.laminal, 
							  "dorsal": self.dorsal,
							  "voiced": self.voiced,
							  "voiceless": self.voiceless,
							  "retracted": self.retracted,
							  "spread": self.spread_glottis,	#spread==aspirated
							  "constricted": self.constricted_glottis,
							  "palatal": self.palatal, #unlisted in Flynn 12 (not phonological),
							  #VOWELS
							  "high": self.high,
							  "mid": self.mid,
							  "low": self.low,
							  "front": self.front,
							  "central": self.central,
							  "back": self.back
							}
		arts = self.articulations
		self.features = fl
		
		
		
		

################################################################################
# FEATURES 
################################################################################
	
	def laryngeal(self, syll, pos, assim):
		'''
		Does nothing
		--increase-e1,-decrease-e2--
		'''
		#unpack the syllable
		o, n, c = syll #o <- onset, n <- nucleus, c <- coda
		
		#if assim:
		#	 n = self.lower_v(n)
		#	 n = self.back_v(n)
		#else:
		#	 n = self.raise_v(n)
		#	 n = self.front_v(n)
		return n






	def labial(self, syll, pos, assim):
		'''
		decrease e1, decrease e2
		'''
		o, n, c = syll
		mi = .25
		ma = 1.0
		if assim:
			
			n = self.raise_v(n, mi, ma)
			n = self.back_v(n, mi, ma)
			
		else:
			
			n = self.lower_v(n, mi, ma)
			n = self.front_v(n, mi, ma)
			
		return n




	
	
	def coronal(self, syll, pos, assim):
		'''
		increase e1 of preceding vowels
		'''

		o, n, c = syll
		mi = .1
		ma = .5
		
		if pos is 2: #coda
			if assim:
				n = self.raise_v(n, mi, ma)
				n = self.front_v(n, mi, ma)
			else:
				n = self.lower_v(n, mi, ma)
				n = self.back_v(n, mi, ma)
			
		return n





	def posterior(self, syll, pos, assim):
		o, n, c = syll
		return n




	
	def laminal(self, syll, pos, assim):
		o, n, c = syll
				
		return n




	
	def dorsal(self, syll, pos, assim):
		'''
		decrease e2
		'''
		o, n, c = syll
		mi = .1
		ma = .75
		if assim:
			n = self.front_v(n, mi, ma)
		else:
			n = self.back_v(n, mi, ma)
		return n



	
	
	def front(self, syll, pos, assim):
		o, n, c = syll
#
		amount = uniform(.5, 1.0)
		if pos == 1: 
			if assim:
				self.front_v(n, mi, ma)
			else:
				self.back_v(n, mi, ma)
			
		return n




	
	def high(self, syll, pos, assim):
		o, n, c = syll
		amount = uniform(.75, 1.25)
		if pos == 1:
			if assim:
				self.lower_v(n, mi, ma)
			else:
				self.raise_v(n, mi, ma)
			
		return n

	
	
	
	
	def low(self, syll, pos, assim):
		o, n, c = syll

		mi = 1.25
		ma = 2.25
		if pos == 1:
			if assim:
				self.lower_v(n, mi, ma)
			else:
				self.raise_v(n, mi, ma)
		
		return n
		
		
		
		
		
	def mid(self, syll, pos, assim):
		o, n, c = syll
		mi = .75
		ma = 2.25
		
		if pos == 1:
			e1 = n.e1
			e1_0 = e1 - ma
			e1_1 = e1 + ma
			ne1 = uniform(e1_0, e1_1)
			if ne1 > max_e1:
				ne1 = max_e1
			if ne1 < min_e1:
				ne1 = min_e1
			n.e1 = ne1
				
		return n




		
	def central(self, syll, pos, assim):
		o, n, c = syll
		ma = .5
		
		if pos == 1:
			e2 = n.e2
			e2_0 = e2 - ma
			e2_1 = e2 + ma
			ne2 = uniform(e2_0, e2_1)
			if ne2 > max_e2:
				ne2 = max_e2
			if ne2 < min_e2:
				ne2 = min_e2
			n.e2 = ne2
			
		return n
		
		
		
		
		
	def back(self, syll, pos, assim):
		o, n, c = syll
		mi = .25
		ma = .5
		
		if pos == 1:
			if assim:
				self.back_v(n, mi, ma)
			else:
				self.front_v(n, mi, ma)
		return n
		
		
		
		

	
	def retracted(self, syll, pos, assim):
		o, n, c = syll
		
		return n
		
	
	
	

	
	def voiced(self, syll, pos, assim):
		o, n, c = syll
		#lengthen preceding vowels
		
		if pos is 2:
			amount = randint(50, 75)
			if assim:
				if (n.length + amount) < 300:
					n.length += amount
			else:
				if (n.length - amount) > 75:
					n.length -= amount
		
		return n





	def voiceless(self, syll, pos, assim):
		o, n, c = syll
		if pos is 2: #coda
			amount = randint(50, 75)
			if (assim and ( (n.length - amount) >= 75)):
				n.length -= amount
			elif (n.length + amount <= 300):
				n.length += amount
		return n




	
	def spread_glottis(self, syll, pos, assim):
		'''
		decrease length 
		'''
		
		o, n, c = syll
		
		l_amount = randint(0, 50) #up to 50 ms
		
		if assim:
			if (n.length - l_amount) > 75: #aspirated onset
				n.length -= l_amount #reduce length)
		else:
			if (n.length + l_amount) < 300:
				n.length += l_amount
				
		return n




	
	def constricted_glottis(self, syll, pos, assim):
		'''
		increase e1, decrease e2 of adjacent vowels
		'''
		o, n, c = syll
		
						 
		if assim:
			n = self.lower_v(n)
			n = self.back_v(n)
		else:
			n = self.raise_v(n)
			n = self.front_v(n)
		return n


		

	def null(self, syll, pos, assim):
		o, n, c = syll
		
		return n





	def rounded(self, syll, pos, assim):
		o, n, c = syll
		e1_mi = .25
		e1_ma = 1.0
		if assim:
			n = self.raise_v(n, e1_mi, e1_ma)
		else:
			n = self.lower_v(n, e1_mi, e1_ma)
		
		e2_mi = .5
		e2_ma = 1.0
		if assim:
			n = self.back_v(n, e2_mi, e2_ma)
		else:
			n = self.front_v(n, e2_mi, e2_ma)
		
		return n
		
	
	
	

	def palatal(self, syll, pos, assim):
		#not a phonological feature, but has a phonetic effect
		o, n, c = syll
		mi = .1
		ma = .75
		if assim:
			n = self.front_v(n, mi, ma)
		else:
			n = self.back_v(n, mi, ma)
		return n
	
	
	
				  
	def lateral(self, syll, pos, assim):
		o, n, c = syll
		mi = .5
		ma = 1.5
		
		if pos == 2:
			mi += .25
			ma += .25
		
		if assim:
			n = self.back_v(n, mi, ma)
		else:
			n = self.front_v(n, mi, ma)
			
		return n



	

	def rhotic(self, syll, pos, assim):
		#hahaha yeah, right. 
		o, n, c = syll
		
		return n



	
	
	def fricative(self, syll, pos, assim):
		o, n, c = syll
		
		return n



	

	def stop(self, syll, pos, assim):
		'''
		shorten a preceding vowel's duration 
		'''
		#similar to rounding?
		# different if it's guttural?
		o, n, c = syll
		
		amount = randint(0, 50) #up to 50 ms
		
		if pos is 2: #stop is in the coda
			if (assim and ( (n.length - amount) > 50) ):
				n.length -= amount #reduce length
			elif ( (n.length + amount) < 300):
				n.length += amount
		return n

	
	
	

	def strident(self, syll, pos, assim):
		o, n, c = syll
		
		return n





	def nasal(self, syll, pos, assim):
		'''
		decrease e1
		effect increased if nasal is in the coda
		'''
		o, n, c = syll

		mi = .1
		ma = .5
		if pos is 2:

			if assim:
				n = self.lower_v(n, mi, ma)
			else:
				n = self.raise_v(n, mi, ma)	
				 
		return n





################################################################################
#TRANSFORMATION METHODS#########################################################

	def raise_v(self, v, mi = .025, ma = .75):
		'''
		decrease v.e1 by [mi, ma]
		if ma is greater than 0, it will be random from [mi, ma]
		if no ma amount is specified, it will use mi
		'''
		e1_adj = edge_adj(min_e1, v.e1)
		if ma:
			amount = uniform(mi, ma) * e1_adj * extra #goes to 0 at edges
		else:
			amount = mi * e1_adj * extra
		ne1 = v.e1 - amount
		if ne1 > min_e1:
			v.e1 = ne1

		return v




		
	def lower_v(self, v, mi = .025, ma = .75):
		'''
		increase v.e1 by [mi, ma]
		if ma is greater than 0, it will be random from [mi, ma]
		if no ma amount is specified, it will use mi
	
		'''
		e1_adj = edge_adj(max_e1, v.e1)
		if ma:
			amount = uniform(mi, ma) * e1_adj * extra
		else:
			amount = mi * e1_adj * extra
			
		ne1 = v.e1 + amount
		if (ne1 < max_e1 and ne1 < v.e2):
			v.e1 = ne1

		return v





	def front_v(self, v, mi = .025, ma = .75):
		'''
		increase v.e2 by [mi, ma]
		if ma is greater than 0, adjustment will be random from [mi, ma]
		if no ma amount is specified, it will use mi
		'''
		e2_adj = edge_adj(max_e2, v.e2)
		if ma:
			amount = uniform(mi, ma) * e2_adj * extra
		else:
			amount = mi * e2_adj * extra
			
		ne2 = v.e2 + amount
		if ne2 < max_e2:
			v.e2 = ne2
		return v
	




	def back_v(self, v, mi = .1, ma = .75):
		'''
		decrease v.e2 by [mi, ma]
		if ma is greater than 0, adjustment will be random from [mi, ma]
		if no ma amount is specified, it will use mi
		'''
		e2_adj = edge_adj(min_e2, v.e2)
		if ma:
			amount = uniform(mi, ma) * e2_adj * extra
		else:
			amount = mi * e2_adj * extra
		ne2 = v.e2 - amount
		if (ne2 > min_e2 and ne2 > v.e1):
			v.e2 = ne2

		return v








def perceive(agent, convention):
	for word in convention:
		res = agent.call_matchers(word) #use a different matching function which calls assimilate and de-assimilate
	return





def articulations():
	p = Phonology()
	arts = [print(a) for a in p.articulations.keys()]



	

def get_feature_dict(language = "english"):
	lang = language.lower()
	
	languages = {"english": english}
	
	if lang not in languages:
		print(language, "undefined in Phonology.")
		return
	

	return languages[lang]()





def english():
	'''
	Refer to Phonology.articulations for full list
	articulations() will print the list

	TIPS FOR CHANGING CONSONANTS
	1. No duplicate keys, but common substrings are OK
	2. Duplicate values are allowed
	3. All articulations in the value lists have to be defined in
	   Phonology.articulations()
	   AND have to have a method (even if it's just an identity function)
	4. There are no limits on how many articulatory methods can be in a value list
	5. There are no constraints to ensure coherency of the methods in a value list
	   e.g. you can have any combination
	6. You can change the names of the features,
	   *but you have to make sure everything gets updated appropriately*

	'''
	
	##########################################################
	#				 CHANGE CONSONANTS HERE					 #
	##########################################################
	
	matrix = {"t": ["coronal", "voiceless", "stop", "spread"],	 
			  "p": ["labial", "voiceless", "stop", "spread"], 
			  "g": ["dorsal", "voiced", "stop"],
			  "h": ["laryngeal", "voiceless", "fricative"],
			  "s": ["coronal", "voiceless", "fricative", "strident"],
			  "d": ["coronal", "voiced", "stop"],  #
			  "b": ["labial", "voiced", "stop"],
			  "k": ["dorsal", "voiceless", "spread", "stop"],
			  "m": ["nasal", "labial"],
			  "n": ["nasal", "voiced", "coronal"],
			  "eng": ["dorsal", "nasal"],
			  "f": ["labial", "fricative", "voiceless"],
			  "v": ["labial", "fricative", "voiced"],
			  "theta": ["coronal", "voiceless", "fricative"],
			  "eth": ["coronal", "voiced", "fricative"],
			  "z": ["coronal", "voiceless", "fricative", "strident"],
			  "esh": ["voiceless", "fricative", "strident", "palatal"],
			  "ezh": ["voiced", "fricative", "strident", "palatal"],
			  "l": ["coronal", "voiced", "lateral"],
			  "r": ["coronal", "rhotic", "voiced"], #^identical to l?
			  "w": ["rounded", "voiced"],
			  "-": ["null"]
			  }

	return matrix



	

def dum_v():
	from Vowel import Vowel
	e1 = uniform(min_e1, max_e1)
	e2 = uniform(min_e2, max_e2)
	length = randint(100, 300)
	v = Vowel(e1, e2, length, "")
	name = []
	if is_high(v):
		name.append("high")
	elif is_low(v):
		name.append("low")
	else:
		name.append("mid")
	if is_back(v):
		name.append("back")
	elif is_front(v):
		name.append("front")
	else:
		name.append("central")
	if length > 200:
		name.append("long")
	else:
		name.append("short")

	v.name = "-".join(name)
	
	return v





def test_symbol(symbol_name, assimilate = True, vowel = None):
	'''
	Apply the features of the symbol to the vowel.
	Assimilate indicates whether the changes are applied (coarticulated)
	or 'undone' / deassimilated
	If no vowel is provided, a random one will be created. 
	'''
	
	if not vowel:
		vowel = dum_v()
		
	fm = get_feature_dict()
	if symbol_name not in fm:
		print(symbol_name, "undefined in Phonology.Articulations")
		return
	symbol = Segment.Segment(symbol_name, fm[symbol_name])
	#w = Word.Word(symbol, vowel, "-", vowel) 
	w = None
	child = make_child()
	child.chosen = True
	print("Original vowel:", vowel, "in syllable", w)
	
	if assimilate:
		pv = w.get_vowel()
		print("Applying features", fm[symbol])
		print("Assimilated vowel:", pv)
	else:
		pv = child.get_vowel(w)
		print("Correcting features", fm[symbol])
		print("De-assimilated vowel", pv)

	
	
	

def get_consonant_symbols():
	'''print the consonant keys'''
	return [c for c in get_feature_set(None).keys()]





def view_coarts(v):
	lex = get_rand_lex(v)





def get_rand_lex(v):
	#draw the articulation and dearticulation perimeters
	#center is v
	#borders are defined by coart functions + phone/vowel noise
	
	
	#from Word import Word
	conv = make_convention(v)
	c_words = conv.lexicon.values()
	cbpd = conv.base_proto_dict
	#for cw in c_words:
		
	
	conv.draw_def_margin()
	



def is_high(v):
	'''True when v occupies the vertical top third of the space'''
	min_high = max_e1 - ((max_e1 - min_e1)/3) #above the 2/3 portion
	if v.e1 >= min_high:
		return True
	return False





def is_low(v):
	'''True when v occupies the vertical bottom third of the space'''
	max_low = min_e1 + ((max_e1 - min_e1)/3) #below the 2/3 portion
	if v.e1 <= max_low:
		return True
	return False





def is_front(v):
	'''True when v is in the left-most third of the space'''
	min_front = max_e2 - ((max_e2 - min_e2)/3) #front of the space (left)
	if v.e2 >= min_front:
		return True
	else:
		return False

	
	
	

def is_back(v):
	'''True when v is in the right-most third of the space'''
	max_back = min_e2 + ((max_e2 - min_e2)/3) #back of the space (right)
	if v.e2 <= max_back:
		return True
	else:
		return False
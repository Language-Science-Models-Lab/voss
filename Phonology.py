'''
Vowel Evolution program Phonology class.
Run in PYTHON 3(!)
with Vowel, Game_fns, Prototype, Word, Agent, Convention, graphics files in same directory

import time, random, re from Python library
Last update December 2016 HJMS


This module can also be used as an alternate driver to Game_fns,
intended for use in experimenting with articulatory constraints,
and other phonetics-phonology interface mechanics.
It does not run a population simulation;
instead, it provides a set of methods which call the same modules.

SYLLABLES		
Using a grammary organization to represent syllables
Dynamic vowels may be overreaching for this project,
so we've ditched those for now.
We've also made consonant features more fluid.

	Syllable => onset + nucleus + coda
	Onset => (consonant | null)
	XXXX Nucleus => (vowel + vowel) | (vowel + null) | (null + vowel)
	Nucleus => vowel
	Coda => (consonant | null)
	consonant =>  (coronal | labial | dorsal | laryngeal) + (voiced | voiceless)
	vowel => (high | mid | low) + (front | central | back) + (long | short)

	XXXX A "long" vowel is vowel+vowel where both vowels have same formants.
	XXXX A "diphthong" is a vowel+vowel where the vowels have different formants.
	We are forbidding vowels in onsets or codas.
	
	

COARTICULATION/FEATURE EFFECTS
If you're wondering how we got these precise values for the formant effects,
the answer is "we stayed at a Holiday Inn Express last night, more succinctly
FIIKWMTU."

'''

import Agent, Convention, Segment
from time import ctime
from graphics import *
import re
from random import sample, choice, uniform, randint

max_e1 = Agent.e1_max()
min_e1 = Agent.e1_min()
max_e2 = Agent.e2_max()
min_e2 = Agent.e2_min()



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
							  #"mid": self.mid,
							  #"low": self.low,
							  "front": self.front,
							  #"central": self.central,
							  #"back": self.back,
							  #"rounded": self.labial
							}
		arts = self.articulations
		self.features = fl

		

	def null(self, syll, pos, assim):
		o, n, c = syll
		
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


#TRANSFORMATION METHODS

	def raise_v(self, v, mi = .025, ma = .75):
		'''
		decrease v.e1 by [mi, ma]
		if ma is greater than 0, it will be random from [mi, ma]
		if no ma amount is specified, it will use mi
		'''
		e1_adj = edge_adj(min_e1, v.e1)
		if ma:
			amount = uniform(mi, ma) * e1_adj #goes to 0 at edges
		else:
			amount = mi * e1_adj
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
			amount = uniform(mi, ma) * e1_adj
		else:
			amount = mi * e1_adj
			
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
			amount = uniform(mi, ma) * e2_adj
		else:
			amount = mi * e2_adj
			
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
			amount = uniform(mi, ma) * e2_adj
		else:
			amount = mi * e2_adj
		ne2 = v.e2 - amount
		if (ne2 > min_e2 and ne2 > v.e1):
			v.e2 = ne2

		return v

		
	
	def laryngeal(self, syll, pos, assim):
		'''
		increase e1, decrease e2
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



	def rounded(self, syll, pos, assim):
		o, n, c = syll
		#decrease e1, decrease e2
		mi = .5
		ma = 1.0

		if assim:
			#n = self.raise_v(n)
			n = self.back_v(n, mi,ma)
			
		else:
			#n = self.lower_v(n)
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
			n = self.back_v(n, mi, ma)
		else:
			n = self.front_v(n, mi, ma)
		return n

	
	
	def front(self, syll, pos, assim):
		o, n, c = syll
#
		amount = uniform(.025, .75)

		if assim:
			ne2 = n.e2 + amount
			if ne2 < max_e2:
				n.e2 = ne2
		else:
			ne2 = n.e2 - amount
			if (ne2 > min_e2 and ne2 > n.e1):
				n.e2 = ne2
			
		return n


	
	def high(self, syll, pos, assim):
		o, n, c = syll
		amount = uniform(.01, .75)

		if assim:
			ne1 = n.e1 - amount
			if ne1 > min_e1:
				n.e1 = ne1
		else:
			ne1 = n.e1 + amount
			if (ne1 < max_e1 and ne1 < n.e2):
				n.e1 = ne1
		
		return n

	
	
	def low(self, syll, pos, assim):
		o, n, c = syll

		amount = uniform(.01, .75)

		if assim:
			ne1 = n.e1 + amount
			if (ne1 < max_e1 and ne1 < n.e2):
				n.e1 = ne1
		else:
			ne1 = n.e1 - amount
			if ne1 > min_e1:
				n.e1 = ne1
		
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



##################
#Testing Methods #
##################

def make_child():
	
	#####################################################
	#			CHANGE THE AGENT PARAMS HERE			#	
	#####################################################
	
	perc = 1.5	  #perception margin (matching radius distance)
	prox = -5.0	   #proximity margin (conflict trigger radius distance)
	prod = .25	  #phone_radius (imitation / internal representation radius distance)
	noise = 0	#utterance noise -- radius to limit randomly generated spoken voel
	lf = True	#length flag (distinguish length, or not)
	adapt = 0	#feedback adjustment to margins
	prest = 0	#social prestige
	age_adult = 2 #age at which children stop learning
	
	####################################################
	A = Agent.Agent
	child = A(0, 0, perc, prox, prod, noise, lf, adapt, prest)
	child.age = 1
		
	return child



def make_convention(lang = None):
	
	###########################
	# CHANGE THE VOWELS HERE  #
	###########################
	if not lang:
		lang = "i:, I, o_slash, Y, y, e:, epsilon, ae, u:, horseshoe, o:, open_o:, wedge, script_a"
	#need to add consonant inventory
	#create lexicon of combinations
	cur_dict = get_feature_dict()
	
	num_words = len(lang.split(","))+10
	c = Convention.Convention(True, True, num_words)
	c.str_to_protos(lang)
	c.strap_protos()
	
	return c



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
	
	matrix = {"t": ["coronal", "voiceless", "spread"],	 
			  "p": ["labial", "voiceless", "stop", "spread"], 
			  "g": ["dorsal", "voiced"],
			  "h": ["laryngeal", "voiceless", "fricative"],
			  "s": ["coronal", "voiceless", "fricative", "strident"],
			  "d": ["coronal", "voiced", "stop"],  #
			  "b": ["labial", "voiceless", "stop"],
			  "k": ["dorsal", "voiceless", "spread"],
			  "m": ["nasal", "labial"],
			  "eng": ["dorsal", "nasal"],
			  "f": ["labial", "fricative", "voiceless"],
			  "v": ["labial", "fricative", "voiced"],
			  "theta": ["coronal", "voiceless", "fricative"],
			  "eth": ["coronal", "voiced", "fricative"],
			  "z": ["coronal", "voiceless", "fricative", "strident"],
			  "esh": ["voiceless", "fricative", "strident", "palatal"],
			  "ezh": ["voiced", "fricative", "strident", "palatal"],
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
	from Word import Word
	if not vowel:
		vowel = dum_v()

	fm = get_feature_dict()
	if symbol_name not in fm:
		print(symbol_name, "undefined in Phonology.Articulations")
		return
	symbol = Segment.Segment(symbol_name, fm[symbol_name])
	word = Word(symbol, vowel, "-", vowel) 
	child = make_child()
	child.chosen = True
	print("Original vowel:", vowel, "in syllable", word)
	
	if assimilate:
		pv = word.get_vowel()
		print("Applying features", fm[symbol])
		print("Assimilated vowel:", pv)
	else:
		pv = child.get_vowel(word)
		print("Correcting features", fm[symbol])
		print("De-assimilated vowel", pv)

	

def get_consonant_symbols():
	'''print the consonant keys'''
	return [c for c in get_feature_set(None).keys()]



def test_perception(iterations = 1):
	'''observe a child 'correcting' vowels in words'''
	child = make_child()
	child.chosen = True
	conv = make_convention()
	c_words = conv.lexicon.values()
	print("LEXICON")
	pc = [print(c) for c in c_words]
	conv.draw_color_map()
	sampling = []
	for i in range(iterations):
		perceive(child, c_words)
		sampling_i = [w.get_vowel() for w in child.idio.values()]
		sampling.extend(sampling_i)
		m = str(iterations-i)
		conv.plot_sets(sampling_i, 1, m)
		
	print("\n\nVOCABULARY")
	child.print_vocab()
	conv.plot_sets(sampling, 0, "all perceived vowels")
	#conv.plot(0, 0, "")
	conv.close_win()



def view_coarts(v):
	lex = get_rand_lex(v)



def get_rand_lex(v):
	#draw the articulation and dearticulation perimeters
	#center is v
	#borders are defined by coart functions + phone/vowel noise
	
	
	from Word import Word
	conv = make_convention(v)
	c_words = conv.lexicon.values()
	cbpd = conv.base_proto_dict
	#for cw in c_words:
		
	
	conv.draw_def_margin()
	


def test_vowel_class(v):
	'''
	observe how a phone might be affected by environments when spoken
	'''
	from Word import Word
	conv = make_convention(v)
	c_words = conv.lexicon.values()
	cbpd = conv.base_proto_dict
	
	fm = get_feature_dict()
	
	A = Agent.Agent #(g, a, perc, prox, phoneradius, noise, lf, adapt, prestige)
	perception = 1.0
	prox_addon = -5.0
	phone_prod_noise = .5 #irrelevant
	vowel_prod_noise = .25 #supplementary to assimilation; set to 0 for coarticulation only
	child = A(0, 0, perception, prox_addon, phone_prod_noise, vowel_prod_noise, 1, 0, 0)
	child.chosen = True
	child.age = 1


	for cw in c_words:
		child.call_matchers(conv.lexicon[cw.id])

	#conv.draw_color_map()
	conv.draw_proto_margins(child.perception, child.prox_margin, 0)
	child.repertoire = [w.get_vowel() for w in child.idio.values()]
	sampling = []
	#sampling_i = []
	print("Child's vowel radius:", child.phone_radius_noise)
	print("Child's phone formants:", child.repertoire[0])
	for w in child.idio.values():
		m = w #str(iterations-i)
		
		vo = w.get_vowel()
		sampling.append(vo)
		conv.plot_sets([vo], 0, m.id)
		
		print(w, "with vowel", vo)

	#conv.plot(0, 0, "")
	conv.plot_sets(sampling, 0, "all words with "+v)
	conv.close_win()



def test_phone_radius(iterations=1):
	'''observe a child saying the words'''
	child = make_child()
	child.chosen = True
	child.age = 1

	conv = make_convention()
	c_words = conv.lexicon.values()
	print("LEXICON")
	pc = [print(c, '\t', c.get_vowel()) for c in c_words]
	conv.draw_color_map()

	for cw in c_words:
		child.idio[cw.id] = conv.lexicon[cw.id]

	child.repertoire = [w.get_vowel() for w in child.idio.values()]
	sampling = []
	for i in range(iterations):
		sampling_i = []
		for w in child.idio.values():
			pv = child.get_vowel(w)
			sampling_i.append(pv)
			print(w, "with vowel formants", w.get_vowel())
			print("child's phone:", pv)
		m = str(iterations-i)
		conv.plot_sets(sampling_i, 1, m)
		sampling.extend(sampling_i)
	
	#conv.plot(0, 0, "")
	conv.plot_sets(sampling, 0, "all phones")
	conv.close_win()



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


	

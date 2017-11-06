'''Vowel evolution program.
Run with Convention, Prototype, Game_fns, im_game, Agent, Phonology
Last update February 2017 HJMS'''
import Agent, Phonology, Vowel, Segment
max_e1 = Agent.e1_max()
min_e1 = Agent.e1_min()
max_e2 = Agent.e2_max()
min_e2 = Agent.e2_min()
phon_fd = Phonology.get_feature_dict() #consonant compensation methods (feature matrix)
		
class Word():
	'''
	Word class
	Words exist in Agents' vocabularies.
	The "orthography" of Words never changes,
	 no matter what happens to the pronunciations.

	   
	'''
	
	def __init__(self, onset, nucleus, coda, percept = None, pn = 0):
		'''
		tag is the word ID i.e. String
		In phase 2, ID is set by the elder group's pronunciation
		e.g. "o:-00" is a word in lexicon which is pronounced with [o:]
		'''
		
		tag = "'[{0}][{1}][{2}]'".format(onset, nucleus, coda)
		self.id = tag
		self.count = 0
		
		self.noise = pn

		self.onset = onset
		self.nucleus = nucleus
		self.coda = coda
		
		self.morphs = True	#morphological alternations

		if percept:
			self.fixed = True #adults' words are fixed
			self.vowel_hist = [(percept, 1)]
			self.percept = percept
			self.vowel = percept
		else:
			self.fixed = False
			self.vowel_hist = []
			self.percept = None
			self.vowel = None
			
			
			
					
		
	def __str__(self):
		name = ("{0:15}".format(self.id))
		return name
		
		
		
		

	def __repr__(self):
		return self.id
		
		
		
		

	def set_percept(self, percept):
		self.percept = percept
		
		
		
		

	def set_vowel(self, vowel):
		self.vowel = vowel	 
		
		
		
		

	def get_vowel(self):
		'''
		applies random noise
		then assimilation
		
		'''
		from random import uniform, randint
		fm = phon_fd
		P = Phonology.Phonology
		onset = self.onset.name
		nuc = self.percept
		coda = self.coda.name

		#apply random noise first
		radius = self.noise
		if radius > 0:
			circle_range = self.circle_range

			#radius = perception margin in ERB units
			#imitation will be a randomly selected point inside this circle
			
			e1 = nuc.e1
			e2 = nuc.e2
			l = int(nuc.length)

			#find the domain of circle fn to get x-coord (f2 value)
			left = e2 + radius
			right = e2 - radius
			rand_x = uniform(right, left)		 #generate x
			
			#find the range for y-coord (f1 value at x = rand_x)
			floor, c = circle_range(rand_x, e2, e1, radius)
			ceiling = min(rand_x, c)					#constraint: f1 <= f2
			rand_y = uniform(floor, ceiling)	 #generate y

			#constraint: length of imitation needs to be in range [100..300]
			#random number in that range and within original length+-50
			length_min = max([100, (l - 50)])
			length_max = min([length_min+50, 300])

			new_e1, new_e2 = rand_y, rand_x 
			new_length = randint(length_min, length_max)
			name = nuc.name							 #match the name for the incoming signal

			#keep the imitations in a range
			if new_e1 > max_e1:
				new_e1 = max_e1
			if new_e2 > max_e2:
				new_e2 = max_e2
			if new_e1 < min_e1:
				new_e1 = min_e1
			if new_e2 < min_e2:
				new_e2 = min_e2

			n_nuc = Vowel.Vowel(new_e1, new_e2, new_length, name)
  
		else:
			n_nuc = nuc.cc()
		
		#APPLY COARTICULATION TRANSFORMS
		
		c1 = P(fm[onset])
		c2 = P(fm[coda])
		nfl = n_nuc.features
		ofl = c1.features
		cfl = c2.features
		
		#simulated morphological alternations
		#chance of a feature being "left off" due to context/use (inflectional/derivational)
		#morphable_features = ["stop", "voiced", "fricative", "spread"] 
		morph_chance = 50
		
		#onset transformations (coart)
		for of in ofl:
			ofns = c1.articulations
			of_nuc = ofns[of]((onset, n_nuc, coda), 0, True)
			n_nuc = of_nuc
		
		#nucleus production noise (art)
		for nf in nfl:
			nf_nuc = ofns[nf]((onset, n_nuc, coda), 1, True)
			n_nuc = nf_nuc
		
		#coda transformations (coart)
		for cf in cfl:
			cfns = c2.articulations
			cf_nuc = cfns[cf]( (onset, n_nuc, coda), 2, True)
			n_nuc = cf_nuc
			
		return n_nuc
		
		
		
		
		
	def get_form(self):
		from random import randint
		#simulated morphological alternations
		#chance of a feature being "left off" due to context/use (inflectional/derivational)
		#morphable_features = ["stop", "voiced", "fricative", "spread"] 
		onset = self.onset
		nuc = self.nucleus
		coda = self.coda
		
		morph_chance = 75 # 75% chance for each feature to be included

		ofl = [f for f in onset.features if ((randint(0, 99) < morph_chance) or f is "null")]
		cfl = [f for f in coda.features if ((randint(0, 99) < morph_chance)  or f is "null")]		
		onset_cc = Segment.Segment(onset.name, ofl, onset.symbol)
		coda_cc = Segment.Segment(coda.name, cfl, coda.symbol)
		
		form = Word(onset_cc, nuc, coda_cc, self.percept, self.noise)
		
		return form





	def assimilate(self):
		'''
		nuc is the Phonology unit (vowel) to be modified.
		onset is the preceding syllable unit.
		coda is the following syllable unit.

		This adjusts the formant values of the vowel
		according to ***articulatory constraints***
		which we suppose occur as a result of the gestures
		involved in transitioning between syllable constituents.
		Adjustments are linear functions; 
		the onset features are applied first. 

		returns the modified vowel
		'''
		P = Phonology.Phonology
		fm = Phonology.get_feature_dict() #consonant compensation methods (feature matrix)
		
		onset = self.onset
		nucleus = self.percept
		coda = self.coda
		
		nuc = nucleus.cc()
		c1 = P(fm[onset])
		c2 = P(fm[coda])
		ofl = c1.features
		cfl = c2.features

		for of in ofl:
			ofns = c1.articulations
			nucleus = ofns[of]((onset, nuc, coda), 0, True)
		for cf in cfl:
			cfns = c2.articulations
			nucleus = cfns[cf]( (onset, nuc, coda), 2, True)
			
		return nucleus
		
		
		
		
	
	def get_vowel_random(self):
		'''
		The vowel is the agent's phonetic representation of a vowel
		i.e. their pronunciation of their vowel percept.

		generative -> vowel is identical to percept
		mod generative -> vowel is noisy production of percept
		exemplar -> vowel is average of history (percept is a memory bank)
		'''
		from random import uniform, randint
		
		p = self.percept
		radius = self.noise

		
		if ((not radius) or (not p)):
			return p
		
		circle_range = self.circle_range

		#radius = perception margin in ERB units
		#imitation will be a randomly selected point inside this circle
		
		e1 = p.e1
		e2 = p.e2
		l = int(p.length)

		#find the domain of circle fn to get x-coord (f2 value)
		left = e2 + radius
		right = e2 - radius
		rand_x = uniform(right, left)		 #generate x
		
		#find the range for y-coord (f1 value at x = rand_x)
		floor, c = circle_range(rand_x, e2, e1, radius)
		ceiling = min(rand_x, c)					#constraint: f1 <= f2
		rand_y = uniform(floor, ceiling)	 #generate y

		#constraint: length of imitation needs to be in range [100..300]
		#random number in that range and within original length+-50
		length_min = max([100, (l - 25)])
		length_max = length_min+50

		new_e1, new_e2 = rand_y, rand_x 
		new_length = randint(length_min, length_max)
		name = p.name						   #match the name for the incoming signal

		#keep the imitations in a range
		if new_e1 > max_e1:
			new_e1 = max_e1
		if new_e2 > max_e2:
			new_e2 = max_e2
		if new_e1 < min_e1:
			new_e1 = min_e1
		if new_e2 < min_e2:
			new_e2 = min_e2
			
		new_v = Vowel.Vowel(new_e1, new_e2, new_length, name)
		self.set_vowel(new_v)
		return new_v
		
		
		
		

	def circle_range(self, x, h, k, r):
		a = (x-h)**2
		c = r**2.0
		ceiling = (c - a)**(.5) + k
		floor =	 2.0*k - ceiling
		return (ceiling, floor)
		
		
		
		

	def add_hist(self, v):
		'''
		   v is the Vowel the agent matched (not the one it heard).
		   Agent just matched v with this word.
		   Increase the count for v.
		   If v is the new lead in frequency, move it to the front;
		   otherwise, add it to the end of history list.
		'''

		v_ind = self.vowel_record_i(v)
		if (v_ind is None):
			self.vowel_hist.append( (v, 1) )
			if not self.percept:
				self.set_percept(v)
		else:
			p, c = self.vowel_hist.pop(v_ind)
			counts = c+1
			
			if (not self.vowel_hist):
				self.vowel_hist.append( (v, counts) )
				self.set_percept(v)
			elif (counts > self.vowel_hist[0][1] ):
				self.vowel_hist.insert(0, (v, counts) )
				self.set_percept(v)
			else:
				self.vowel_hist.append( (v, counts) )





	def has_record(self, v):
		'''
		v is a Vowel
		returns Bool
		True if the agent has matched this vowel to word (self) before
		False if vowel has no entry in history
		'''
		
		for (p, c) in self.vowel_hist:
			if p is v:
				return True
		return False





	
	def vowel_record_i(self, v):
		for i in range(len(self.vowel_hist)):
			p, c = self.vowel_hist[i]
			if v is p:
				return i
		return None
	
	
	
	
	
   
	def merge_absorb(self, wv, sv):
		'''
		wv is the "weaker vowel" (lower weight)
		sv is the "stronger vowel" (higher weight)
		one vowel has absorbed the other in agent rep.
		Move the words to the stronger vowel.
		'''
		sv_vci = self.vowel_record_i(sv)

		if (sv_vci is not None):
			sv_copy, sv_counts = self.vowel_hist.pop(sv_vci)
		else:
			sv_copy, sv_counts = sv, 0
			
		wv_vci = self.vowel_record_i(wv)
		if (wv_vci is not None):
			wv_copy, wv_counts = self.vowel_hist.pop(wv_vci)
			
			new_sv_counts = sv_counts + wv_counts
			if ( len(self.vowel_hist) is 0 or
				 new_sv_counts > self.vowel_hist[0][1]):
				self.vowel_hist.insert(0, (sv_copy, new_sv_counts))
				self.set_percept(sv_copy)
			else:
				self.vowel_hist.append((sv_copy, new_sv_counts))

		else:	#something has gone wrong
			print("error report:", wv, "not in history:")
			for v, c in self.vowel_hist:
				print(v, c)
				
				
				
				

	def merge_absorb_rb(self, wv, sv):
		'''
		one vowel has absorbed the other in agent rep.
		Move the words to the stronger vowel.
		'''

		counts = 0
		if ( (wv in self.vowel_hist) and
			 (sv in self.vowel_hist) and
			 (wv is not sv)):
			counts = self.vowel_hist[wv]
			self.vowel_hist[sv] += counts
			self.vowel_hist[wv] = 0





	def merge_midpoint(self, v1, v2, mv):
		'''
		v1, v2, mv are Vowels
		v1 and v2 have merged into mv
		find v1 and v2 in the history,
		change them both to mv,
		and update mv's weight to ( v1's weight + v2's weight )
		'''

		v1_vci = self.vowel_record_i(v1)	#get v1 frequency count (0 if no entry)
		if (v1_vci is not None):
			v1_copy, v1_counts = self.vowel_hist.pop(v1_vci)
		else:
			v1_copy, v1_counts = v1, 0

		v2_vci = self.vowel_record_i(v2)	#get v2 frequency count (0 if no entry)
		if (v2_vci is not None):
			v2_copy, v2_counts = self.vowel_hist.pop(v2_vci)
		else:
			v2_copy, v2_counts = v2, 0
			
		counts = v1_counts + v2_counts
		
		if ( (not self.vowel_hist) or
			 counts > self.vowel_hist[0][1]):
			self.vowel_hist.insert(0, (mv, counts))
			self.set_percept(mv)
		else:
			self.vowel_hist.append( (mv, counts) )

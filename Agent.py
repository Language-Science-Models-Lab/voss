'''Vowel evolution program.
Run with Convention, Prototype, Game_fns, Vowel
Last update November 2017 HJMS'''


#For now, these are just arbitrary numbers, but that may change
def e1_max():
	return 14.5 #first formant maximum in ERB

def e1_min():
	return 6.8 #first formant minimum in ERB

def e2_max():
	return 23.25 #second formant max

def e2_min():
	return 12.5 #second formant minimum

max_e1 = e1_max()
min_e1 = e1_min()
max_e2 = e2_max()
min_e2 = e2_min()

import Vowel, Word, datetime
from random import uniform, randint

class Agent:
	"""Agents have
	#a vowel repertoire (initially empty list of Vowels),
	#a vocabulary (initially empty dictionary of Prototype->Word),
	#an age (initially zero),
	#a binary discern/ignore length flag,
	#perception in ERB units"""
	
	def __init__(self, g, a, perc, prox, phone_radius, noise, lf, adapt, prestige):
		'''Arguments: generation number gen and agent index a.
		repertoire is initially empty'''
		self.group = g #agents are appended to the population in groups
		self.ind = a   #agent's index within its group
		self.repertoire = [] #list of Vowels an agent "knows"
		self.idio = dict()	   #of the form {"word.id": word}
		self.length_flag = lf #True means the agent recognizes long vs short
		self.age = 0 #agents are removed when they reach an age limit
		self.perception = perc #margin within which vowels are matched (neighbor search distance)
		self.phone_radius = phone_radius #guess_by_margin radius; internal representation accuracy
		self.phone_radius_noise = noise #phonetic representation (noise added to copy of word.proto)
		self.prox_margin = prox #margin within which vowels conflict
		self.name = (str(self.group)+str(self.ind)) #String id
		self.chosen = False #micro view highlights a single agent
		self.family = [] #list of agent ids in this agent's "nuclear family"

		self.wall_bias = True
		self.adaptive = adapt #defunct
		self.prestige = prestige #defunct
		self.pot_spreadables = ["nasal", "labial", "rounded"]


	def set_phone_radius(self, prod):
		self.phone_radius = prod

		

	def set_noise(self, noise):
		self.phone_radius_noise = noise

		

	def print_vocab(self):
		words = self.idio.values()
		if (not words):
			print("(Baby--no vocabulary yet)")
		else:
			print("\n{0:25}\t{1:14}\t{2:15}".format("Word", "Agent's Vowel", "Formant Values"))
			for w in sorted(words, key=lambda w: w.id):
#
				#use get_vowel() for the utterance instead of internal representation
				p = w.percept
				original_nuc = w.id.split("][")[1]

				if p.name != original_nuc:	#detect whether vowel has changed
					print("{0:25}>\t{1:14}\t{2:15}".format(w.id, p.name, str(p))) 

				else:
					print("{0:25}\t{1:14}\t{2:15}".format(w.id, p.name, str(p)))



	def get_vocab_str(self):
		si = []
		if self.age <= 1:
			return("baby")
		else:
			si.append("{0:25}{1:14}{2:15}".format("Word", "Agent's Vowel", "Formant Values"))
			for w in sorted(self.idio.values(), key=lambda w: w.id.split("][")[1]):
				p = w.percept
				original_nuc = w.id.split("][")[1]

				if p.name != original_nuc:	#detect whether vowel has changed
					si.append("{0:25}>\t{1:14}{2:15}".format(w.id, p.name, str(p)))
				else:
					si.append("{0:25}\t{1:14}{2:15}".format(w.id, p.name, str(p)))
		si_str = "\n".join(si)
		return si_str
		


	def print_rep(self):
		for v in self.repertoire:
			print(v.name+": ", v)

			

	def get_rep_set(self, match_vowel):
		'''returns a list which is the agent's rep as a set
		the vowels in the list are mean centers of vowels
		grouped by convention prototype counterpart
		Renames vowels which have merged/shifted'''
		V = Vowel.Vowel

		rep_set_dict = dict()
		rep_set = list()
		for v in self.repertoire:
			real_name = match_vowel(v).name
			v.name = real_name
			if v.name in rep_set_dict:
				rep_set_dict[v.name].append(v)
			else:
				rep_set_dict[v.name] = [v]
		for (v_name, v_list) in rep_set_dict.items():
			n = len(v_list)
			e1 = (sum([v.e1 for v in v_list]) / n)
			e2 = (sum([v.e2 for v in v_list]) / n)
			l = (sum([v.length for v in v_list]) / n) 
			proto_vowel = V(e1, e2, l, v_name)
			rep_set.append(proto_vowel)
		return rep_set

	

	def guess_by_margin(self, unknown_v):

		#radius = perception margin in ERB units
		#imitation will be a randomly selected point inside this circle
		radius = self.phone_radius
		if not radius:
			return self.copy_vowel(unknown_v)

		e1 = unknown_v.e1
		e2 = unknown_v.e2
		l = int(unknown_v.length)

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
		length_max = min([length_min+50, 300])

		new_e1, new_e2 = rand_y, rand_x 
		new_length = randint(length_min, length_max)
		w = unknown_v.name							#match the name for the incoming signal
		
		if new_e1 > max_e1:
			new_e1 = max_e1
		if new_e2 > max_e2:
			new_e2 = max_e2
		if new_e1 < min_e1:
			new_e1 = min_e1
		if new_e2 < min_e2:
			new_e2 = min_e2
			
		new_v = Vowel.Vowel(new_e1, new_e2, new_length, w)
		new_v.set_features(max_e1, max_e2, min_e1, min_e2)
		return new_v


		
	def inc_age(self):
		'''Increments the agent's age'''
		self.age += 1



	def purge_vwls(self):
		#self.weigh_vowels()
		vocab = self.idio.values()
		dist_vwls = set([w.percept for w in vocab])
		#rep = [v for v in self.repertoire if v.weight > 0]
		self.repertoire = list(dist_vwls)
		for w in self.idio.values():
			w.fixed = True


		
	def euc(self, v, w):
		e1_dif = (v.e1 - w.e1)
		e2_dif = (v.e2 - w.e2)
		return ((e1_dif * e1_dif) + (e2_dif * e2_dif))**.5



#MATCHING
		######## CASES ##############################################
		#children													#
		#	( New vowel + new word )   | ( New vowel + known word ) #
		#	( Known vowel + new word ) | ( Known vowel + known word)#
		#															#
		#babies														#
		#	New vowel | Known vowel									#
		#############################################################

	def call_matchers_nh(self, w):
		'''
		Match the vowel, then the word if age > 0
		use assimilation/deassimilation
		resist homophone creation
		'''
		w_form = w.get_form() #may be an alternation
		inc_vwl = w_form.get_vowel()
		corr_vwl = self.dissimilate( (w.onset, inc_vwl, w.coda) )
		v = self.vowel_match_nh(corr_vwl, w)
		
		if self.chosen:
			print("\nAgent", self.name, "hears", w.id, inc_vwl, "corrects to", corr_vwl, end=", ")

		if v is None:	#new vowel or possibly homophone avoidance
			v = self.vowel_match_rb(corr_vwl)
		if v is None: #definitely a new vowel
			#? should babies use corr_vwl or inc_vwl?
			v = self.guess_by_margin(corr_vwl)	 #generate an imitation within margin
			self.add_vowel(v)					#add vowel to rep
			if self.chosen:
				print("adds", v, "to repertoire", end=" ")
				
		else: #known vowel
			v.weight += .001 #crude priming
			if self.chosen: #micro view printing 
				print("matches vowel to", v, end=" ")
			
		if self.age > 0:				#baby--agents under 1 only hear the vowel
			self.word_match(v, w)		#child--add word to vocabulary

		#micro view printing and micro change detection
		if self.chosen: 
			ivn = inc_vwl.name
			vn = v.name
			if ivn != vn:
				print("\n", ivn, ">", vn)

			if self.adaptive:
				print( "\nPerception = {0:.4f}".format(self.perception), end=" ")
		return v



	def call_matchers(self, w):
		'''
		Match the vowel, then the word if age > 0
		This is the method used if 'armchair mode' is on
		'''
		#speaker uses the word 
		formed_word = w.get_form() #word object; may be an alternation
		inc_vwl = formed_word.get_vowel() #vowel object; assimilation 
		
		#listener processes the word
		corr_vwl = self.dissimilate( (w.onset, inc_vwl, w.coda) )
		v = self.vowel_match(corr_vwl, w)
		if self.chosen:
			print("\nAgent", self.name, "hears", w.id, inc_vwl, "corrects to", corr_vwl, end=", ")		  #Cases:
		
		#if no match was found, babies will expand their repertoire
		if v is None: 
			
			if self.age < 1:	#new vowel
				#? should babies use corr_vwl or inc_vwl?
				#^This is why we need intelligent agents in a MAS...
				v = self.guess_by_margin(corr_vwl)	 #generate an imitation within margin
				self.add_vowel(v)					 #add vowel to rep
				if self.chosen:
					print("adds", v, "to repertoire", end=" ")
					
			else: #Agent couldn't find a match, but isn't a baby (not good)
				whole_rep = [phone for phone in self.repertoire]
				#print("*Something's not right in 'Agent.call_matchers()'")
				print("*Agent couldn't find a match for", corr_vwl)
				v = self.rec_vowel_match(corr_vwl, whole_rep)[0] #nothing matched the length
				print("*Found possible match", v, ". Check phonology coarticulation functions.")
				
		else: #known vowel
			
			if self.chosen: #micro view printing 
				print("matches vowel to", v, end=" ")
				
#BABIES WEIGHING VOWELS
			if self.age < 1:
				v.weight += .001
				if self.prox_margin:
					#t0 = datetime.datetime.now()
					self.settle_conflicts()
					#t1 = datetime.datetime.now()
					#dif = t1 - t0
					#print(dif)
			
		if self.age > 0:				#baby--agents under 1 only hear the vowel
			self.word_match(v, w)		#child--add word to vocabulary

		#micro view printing and micro change detection
		if self.chosen: 
			ivn = inc_vwl.name
			vn = v.name
			if ivn != vn:
				print("\n", ivn, ">", vn)

			if self.adaptive:
				print( "\nPerception = {0:.4f}".format(self.perception), end=" ")
		return v





	def call_matchers_no_coart(self, w):
		'''
		DEFUNCT
		Match the vowel, then the word if age > 0
		'''
		inc_vwl = w.get_vowel()
		v = self.vowel_match_rb(inc_vwl)
		if self.chosen:
			print("\nAgent", self.name, "hears", w.id, inc_vwl, end=", ")

		
		if v is None:						   
			v = self.guess_by_margin(inc_vwl)	#generate an imitation within margin
			self.add_vowel(v)					#add vowel to rep
			if self.chosen:
				print("adds", v, "to repertoire", end=" ")
		else:
			if self.chosen:
				print("matches vowel to", v, end=" ")
			
		if self.age > 0:					#agents under 1 only hear the vowel
			self.word_match(v, w)		   #add word to vocabulary

		if (self.chosen and self.adaptive):
			print( "\nPerception = {0:.4f}".format(self.perception), end=" ")
		return v



	

	def add_vowel(self, v):
		#work-around just appends vowel directly without filtering
		self.append_vowel(v)





#Here's where you can toggle agent functions
	def vowel_match(self, v, w):
		#with homophone avoidance
		#children use perceptual margin
		#self.vowel_match_nh(v, w)
		
		#with no lexical preservation
		#children use perceptual margin
		#self.vowel_match_rb(v)

		#with homophone tolerance
		#children do not use perceptual margin (babies do)
		if self.age < 1:
			return self.vowel_match_rb(v)
		else:
			return self.vowel_match_armchair(v)





	def vowel_match_nh(self, v, w):
		'''
		with homophone resistance
		v is the vowel being heard
		w is the context of the vowel (v is w's nucleus)
		'''
		vl = v.length <= 200
		vpd = self.euc
		closest = 999
		heaviest = 0
		best_phone = None
		isa_baby = self.age < 1
		perc = self.perception
		nh = self.no_homo
		
		def lm(vi, p):
			#ld = ( (p.length > 200) == (v.length > 200) ) #old method
			diff = abs(p.length - vi.length)
			ld = diff <= (p.length * .5) #signal length is within 50% difference of phone length
			return ld
		
		lf = self.length_flag
		if lf:
			rep = ((p, vpd(v, p)) for p in self.repertoire if (lm(v, p) and (vpd(v, p) <= perc)) )
		else:
			rep = self.repertoire

		for (phone, d) in rep: 
			if isa_baby: #pick the closest
				if d < closest:
					best_phone = phone
					closest = d
			else: #pick the heaviest that doesn't create homophone
				if ( ( (phone.weight > heaviest) or ( (not heaviest) and (d < closest) )) and
					nh(phone, w) ):
					best_phone = phone
					heaviest = phone.weight
					closest = d
						
		return best_phone

				



	def no_homo(self, phone, w):
		'''
		True when adding the word with phone as nucleus would NOT create a homophone
		where a homophone is multiple meanings (word IDs) mapped to a single phonetic sequence

		example: speaker says "bed" with nucleus [epsilon],
				 listener applies deassimilation and finds a nearby phone [I]
						  which is mapped to "bid" already.
				 This would create a homophone where [b][I][d] is mapped to both
					  "[b][I][d]" and "[b][epsilon][d]".
				 The listener would not allow the micro-change,
					 so would either choose another nearby phone or add a new one,
					 i.e. not recognize the match

		Will always return True if the agent has 
		'''
		
		w_ons = w.onset
		w_cod = w.coda
		w_nuc = w.nucleus
		phone_n = phone.name
		pot_w = Word.Word(w_ons, w_nuc, w_cod)
		if (phone_n != w_nuc and pot_w.id in self.idio):
			return False
		
		return True





	def length_matcher(self, incom_v, intern_p):
		diff = abs(incom_v.length - intern_p.length)
		ld = diff <= (intern_p.length * .5) #signal length is within 50% difference of phone length
		return ld
			
			
			
			
			
	def vowel_match_armchair(self, v):
		'''
		no perception margin
		uses length matching
		no homophone consideration
		'''
		lm = self.length_matcher
		rep = [phone for phone in self.repertoire if lm(v, phone)]
		match = None
		if len(rep):
			match = self.rec_vowel_match(v, rep)[0]
		if not match: 
			print("Something's wrong with the armchair matching")
		return match
			
		
		
		
	def vowel_match_rb(self, p):
		'''look for a vowel in repertoire within perceptual margin radius'''
		
		# vvvv RB code
		'''lf = self.length_flag
		euc = self.euc
		nearest_dist = 999
		margin = max([0, self.perception])
		nearest = None
		dist = 999
		perception = self.perception
		for e in self.repertoire:
			if ( (not lf) or
				( lf and
				 ( (e.length < 200) is (p.length < 200) ) ) ):
				dist = euc(e, p)
				if (dist < nearest_dist and dist <= margin):
					nearest = e
					nearest_dist = dist
		return nearest'''
		
		#p is the incoming signal
		
		def lm(v):
			#ld = ( (p.length > 200) == (v.length > 200) ) #old method
			diff = abs(p.length - v.length)
			ld = diff <= (v.length * .5) #signal length is within 50% difference of phone length
			return ld
		
		lf = self.length_flag
		if lf:
			rep = [v for v in self.repertoire if lm(v)]
		else:
			rep = self.repertoire

		#find the closest acoustic match
		def rec_vowel_match(vwls):
			if len(vwls) < 2:
				d0 = self.euc(p, vwls[0])
				return (vwls[0], d0)
			else:
				l = len(vwls)
				m = int(l/2)
				l_c, l_d = rec_vowel_match(vwls[:m])
				r_c, r_d = rec_vowel_match(vwls[m:])
				if l_d < r_d:
					return(l_c, l_d)
				return(r_c, r_d)

		#find the heaviest match
		#if no potentials have weight, find the closest
			
		perc = self.perception
		
		def heaviest_match(vwls):
			neighbors = [v1 for v1 in vwls if ( (p.euc(v1) <= perc) )] # (v1.weight > 0) and
			if (not neighbors and len(vwls)):
				return rec_vowel_match(vwls)
			if (len(neighbors) > 1 and self.adaptive):
				self.perception = max([0, (self.perception-self.adaptive)]) #recognize a crowded system
				self.phone_radius = max([0, (self.phone_radius-self.adaptive)]) #imitate signals more closely
			
			heaviest = neighbors[0]
			for neighbor in neighbors:
				if neighbor.weight > heaviest.weight:
					heaviest = neighbor
			distance = p.euc(heaviest)
			return (heaviest, distance)
			
		if rep:
			c_v, c_d = heaviest_match(rep)
			if c_d <= self.perception:
				return c_v
			elif self.adaptive:	  #the closest vowel is not within perception margin
				self.perception += (self.adaptive/2) #adjust agent's perception
			
		return None
		
		
	
	def rec_vowel_match(self, p, vwls):
		'''
		find the closest acoustic match
		'''
		if len(vwls) < 2:
			d0 = self.euc(p, vwls[0])
			return (vwls[0], d0)
		else:
			l = len(vwls)
			m = int(l/2)
			l_c, l_d = self.rec_vowel_match(p, vwls[:m])
			r_c, r_d = self.rec_vowel_match(p, vwls[m:])
			if l_d < r_d:
				return(l_c, l_d)
			return(r_c, r_d)

	
	
	def word_match(self, v, w):
		'''match known word or add new word.
		If the word is 'fixed' i.e. not in probationary period,
		then the agent doesn't respond.
		Otherwise, it adds to the word's history and re-weighs its vowels'''
		wi = w.id
		if wi in self.idio:
			word = self.idio[wi]
			word.add_hist(v)
			if self.chosen:
				print(", updates", w.id, end="")
		else:
			pn = self.phone_radius_noise
			new_word = Word.Word(w.onset, w.nucleus, w.coda, None, pn)
			new_word.add_hist(v)
			self.idio[wi] = new_word
			if self.chosen:
				print(", adds", w.id, "to vocabulary", end="")
				
		#update weights
		#self.weigh_vowels()
		
#uncomment both of these to reinstate conflict resolution
		#self.settle_conflicts()
		#self.weigh_vowels()



	def weigh_vowels(self):
		'''Vowels are weighed according to the number of words using them'''
		if self.age > 0:
			vocab = self.idio.values()
			vocab_size = len(vocab)
			rep = [v for v in self.repertoire]
			
			for i in range(len(rep)):
				v = rep[i]
				count = 0
				#words = [w.vowel for w in vocab if w.vowel is v]
				#count = len(words)
				for w in vocab:
					if w.percept is v:
						count += 1
####WEIGHT WEIGHT
				if (count and vocab_size):
					v.weight = min([(count/vocab_size)* 10, 5])
					#v.weight = (count/vocab_size)
				else:
					v.weight = 0


			
	def settle_conflicts(self):
		'''settle proximity confrontations between neighboring vowels
		   only iterate through original repertoire once
		   i.e. don't settle conflicts from results of resolutions
		   otherwise it may never terminate'''
		rep = [v for v in self.repertoire]
		perc = self.perception

		ld = self.length_matcher
			
		for i in range(len(rep)):
			v = rep[i]
			if v.weight:
				prox = v.weight + self.prox_margin
				prox = max( 0, prox )
				v.neighbors = [v1 for v1 in rep[i+1:] if ( v1.weight and (v.euc(v1) <= prox) and ld(v, v1))]
				while v.neighbors:
					n = v.neighbors.pop()
					if v in n.neighbors:
						n.neighbors.remove(v)
					
					self.settle(v, n) 
				

					
	def copy_vowel(self, v):
		V = Vowel.Vowel
		nv = V(v.e1, v.e2, v.length, v.name)
		nv.weight = v.weight
		return nv

	
			
	def get_midpt(self, v1, v2):
		nv_e1 = int( (v1.e1 + v2.e1) / 2 )
		nv_e2 = int( (v1.e2 + v2.e2) / 2 )
		if nv_e1 > nv_e2:
			nv_e1 = nv_e2
		nv_l = int( (v1.length + v2.length) / 2 )

		###########################################################
		#Not sure what to do here...
		#If the names don't match then new vowel should be compared
		#to the convention prototypes, except we can't access those
		#Maybe if the names match they should merge to one vowel
		#but if the names differ they should join to form a diphthong?
		##############################################################
		name = v1.name
		
		nv = Vowel.Vowel(nv_e1, nv_e2, nv_l, name)
		for w in self.idio.values():
			w.merge_midpoint(v1, v2, nv)

		return nv

	
	
	def settle(self, v1, v2):
		'''Determine whether a vowel needs to shift/merge'''
		
		#Chance to avoid (shift_away) or merge (merge_abs) 
		merge_chance = 50
		
		if (v1 in self.repertoire and
			v2 in self.repertoire):
			#cases:
			#	v has higher functional load:
			#		n avoids v or is absorbed
			#	n has higher functional load:
			#		v avoids n or is absorbed
			#	n and v have equal functional load:
			#		v and n merge to midpoint
			
			if (v1.weight == v2.weight):
				if (not v1.weight):
					return
				else:
					self.merge_mid(v1, v2)
					return
			elif v1.weight < v2.weight:
				weaker = v1
				stronger = v2
			else:
				weaker = v2
				stronger = v1
		
			roll = randint(1, 100)

			if self.prox_margin <= 0:
				return
			
			if (roll > merge_chance or
				weaker.weight is 0):  #adding rule: weightless vowels get automatically absorbed
				self.merge_abs(weaker, stronger)
			else:
				if self.wall_bias:
					self.shift_wall_bias(weaker, stronger)
				else:
					self.shift_away(weaker, stronger)

					
				
	def merge_mid(self, v1, v2):
		'''two vowels of equal fnl load merge to their midpoint'''

		nv_e1 = ( (v1.e1 + v2.e1) / 2 )
		nv_e2 = ( (v1.e2 + v2.e2) / 2 )
		if nv_e1 > nv_e2:
			nv_e1 = nv_e2
		nv_l = int( (v1.length + v2.length) / 2 )

		###########################################################
		#Not sure what to do here...
		#If the names don't match then new vowel should be compared
		#to the convention prototypes, except we can't access those
		#UPDATE: Convention fixes this in get_rep_set method
		# ^Not a great fix
		#Maybe if the names match they should merge to one vowel
		#but if the names differ they should join to form a diphthong?
		##############################################################
		#name = ""
		name = v1.name
		nv = Vowel.Vowel(nv_e1, nv_e2, nv_l, name)
		nv.weight = v1.weight + v2.weight
#
		if self.chosen:
			print("\nCONFLICT:", v1, "and", v2, "merging to midpoint at", nv)
			v1n = v1.name
			v2n = v2.name
			nvn = nv.name
			if v1n != nvn:
				print(v1n, ">", nvn)
			if v2n != nvn:
				print(v2n, ">", nvn)
				
		for w in self.idio.values():
			w.merge_midpoint(v1, v2, nv)
		rep = self.repertoire
		rep.remove(v1)
		rep.remove(v2)
		rep.append(nv)

		

	def merge_abs(self, weaker_vwl, stronger_vwl):
		'''stronger vowel absorbs the other'''
		if self.chosen:
			print("\nCONFLICT:", weaker_vwl, "absorbed by", stronger_vwl)
			wvn = weaker_vwl.name
			svn = stronger_vwl.name
			if wvn != svn:
				print(wvn, ">", svn)

		if (weaker_vwl in self.repertoire and stronger_vwl in self.repertoire):# and weaker_vwl is not stronger_vwl):
			sv = stronger_vwl
			words = [w for w in self.idio.values() if w.has_record(weaker_vwl)]
			for w in words:
				w.merge_absorb(weaker_vwl, sv)
#

			self.repertoire.remove(weaker_vwl)

			

	def shift_wall_bias(self, wv, sv):
		'''
		shift the weaker vowel away with biasing
		weaker vowel tries to escape boundaries and stronger vowel
		weaker vowel calculates sum distance from nearby walls + stronger vowel
		and picks the direction (up/down/left/right) with max sum distance
		'''
		wv_c = self.copy_vowel(wv)
		words = [w for w in self.idio.values() if w.has_record(wv_c)]
		ne2, ne1 = self.get_dest(wv, sv)
		wv.e1 = ne1
		wv.e2 = ne2

		if sv.length > wv.length:
			if wv.length - 10 > 100:
				wv.length -= 10
		elif wv.length + 10 < 300:
			wv.length += 10
		
		for word in words:
			ind = word.vowel_record_i(wv_c)
			v, counts = word.vowel_hist.pop(ind)
			if counts > word.vowel_hist[0][1]:
				word.vowel_hist.insert(0, (wv, counts))
			else:
				word.vowel_hist.append((wv, counts))
#
		if self.chosen:
			print("\nCONFLICT:", wv_c, "shifting away from", sv, "to new position", wv)
			wvcn = wv_c.name
			wvn = wv.name
			if wvcn != wvn:
				print(wvcn, ">", wvn)

				
		
	def get_dest(self, weaker_vwl, stronger_vwl):
		
		wv = weaker_vwl
		sv = stronger_vwl

		wve1 = wv.e1
		wve2 = wv.e2

		dist = self.coord_dist
		
		perc = self.perception
		margin = (perc*2) #use diameter instead of radius
		
		#figure out if there are any walls to avoid
		w_above = ( (wve1 - margin) <= min_e1 )	 #there is a wall above within margin distance
		w_below = ( (wve1 + margin) >= max_e1 )
		w_left = ( (wve2 + margin) >= max_e2 )
		w_right = ( (wve2 - margin) <= min_e2 )

		#make a list of positions we want to avoid
		avoid_li = [(sv.e2, sv.e1)] #the stronger vowel
		ala = avoid_li.append
		pos_li = []
		pla = pos_li.append
		#if the wall is in range, add the coordinates
		#to the list of positions to prioritize distance from
		#and cut off the direction at the limit
		#otherwise, add the coordinates
		#to the list of potential new positions
		
		#note: di_perc has a margin of error of approx ( 4 / (10^15) )
		di_perc = ( (perc*perc)/2.0) ** (.5) #convert diagonal distance to formant adjustment amount
		ur = ( (wve2-di_perc), (wve1-di_perc) ) #position if it shifts diagonally up-right
		dr = ( (wve2-di_perc), (wve1+di_perc) ) #position if it shifts diagonally down and right
		ul = ( (wve2+di_perc), (wve1-di_perc) ) #position if it shifts up-left
		dl = ( (wve2+di_perc), (wve1+di_perc) ) #position if it shifts down-left
		
		if w_above: #there's a wall above--avoid it
			up = (wve2, min_e1) #intercept coord of the wall above
			ala(up)
		else: #there's no nearby wall above, include upward three directions
			up = (wve2, (wve1-perc)) #position if it shifts straight upward
			pla(up)
			if not w_right:
				pla(ur)
			if not w_left:
				pla(ul)
			   
		if w_below: #there's a wall below--avoid it
			down = (wve2, max_e1) #intercept coord of the wall below
			ala(down)
		else:
			down = (wve2, (wve1+perc)) #position if it shifts downward
			pla(down)
			if not w_right:
				pla(dr)
			if not w_left:
				pla(dl)
			
		if w_left: #there's a wall to the left
			left = (max_e2, wve1) #intercept coordinates to the left
			ala(left)
		else:
			left = ((wve2+perc), wve1) #position if it shifts left
			pla(left)
			if not w_above:
				pla(ul)
			if not w_below:
				pla(dl)
		
		if w_right: #there's a wall to the right
			right = (min_e2, wve1) #intercept coord to the right
			ala(right)
		else:
			right = ((wve2-perc), wve1) #position if it shifts right
			pla(right)
			if not w_above:
				pla(ur)
			if not w_below:
				pla(dr)

		#mind the e1 < e2 constraint
		if (wve1 + margin) >= wve2:
			ala( (wve2, (wve1+margin)) )
		if (wve2 - margin) < wve1:
			ala( ((wve2-margin), wve1) )

		best_pos = (wve2, wve1)
		best_dist = wv.euc(sv)
		for position in pos_li: #for each potential new location
			total_dist = sum([dist(p, position) for p in avoid_li]) #sum distance from all points to avoid
			if total_dist > best_dist:
				best_dist = total_dist
				best_pos = position

		return best_pos



	def coord_dist(self, p1, p2):
		'''yet another euc method, but for coordinates'''
		p1x, p1y = p1
		p2x, p2y = p2
		return (((p1y - p2y)**2) + ((p1x - p2x)**2))**.5

	

	def shift_away(self, weaker_vwl, stronger_vwl):
		'''weaker vowel moves away from stronger one
		distance is currently 1% of perception'''
		#move dist = 10% of perceptual margin away from stronger vowel
		dist = self.perception #* .1
		
		wv = weaker_vwl
		wv_c = self.copy_vowel(wv)
		sv = stronger_vwl
		words = [w for w in self.idio.values() if w.has_record(wv_c)]
		
		if sv.e1 > wv.e1:
			wv.e1 -= dist
			if wv.e1 <= min_e1:
				wv.e1 += dist
		else:
			wv.e1 += dist
			e1_constraint = wv.e2 - wv.e1
			if	(e1_constraint < 0 or wv.e1 >= max_e1):
				wv.e1 -= dist
				
		if sv.e2 > wv.e2:
			wv.e2 -= dist
			e1_constraint = wv.e2 - wv.e1
			if (e1_constraint < 0 or wv.e2 <= min_e2):
				wv.e2 += dist
		else:
			wv.e2 += dist
			if wv.e2 >= self.max_e2:
				wv.e2 -= dist

		if ((sv.length > wv.length) and (wv.length - 10 > 100)):
			wv.length -= 10
		elif (wv.length + 10 < 300):
			wv.length += 10

		for word in words:
			ind = word.vowel_record_i(wv_c)
			v, counts = word.vowel_hist.pop(ind)
			if counts > word.vowel_hist[0][1]:
				word.vowel_hist.insert(0, (wv, counts))
			else:
				word.vowel_hist.append((wv, counts))
#
		if self.chosen:
			print("\nCONFLICT:", wv_c, "shifting away from", sv, "to new position", wv)





	def get_vowel(self, word):
		'''
		dissimilated vowel in the context of word
		'''
		onset = word.onset
		nucleus = word.get_vowel()
		coda = word.coda

		return self.dissimilate( (onset, nucleus, coda) )
		


	def assimilate(self, syllable):
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
		import Phonology
		P = Phonology.Phonology
		fm = Phonology.get_feature_dict() #consonant compensation methods (feature matrix)
		
		onset, nucleus, coda = syllable
		nuc = nucleus.cc()
		c1 = P(fm[onset])
		c2 = P(fm[coda])
		ofl = c1.features
		cfl = c2.features
		for of in ofl:
			ofns = c1.articulations
			nuc = ofns[of]((onset, nuc, coda), 0, True)
		for cf in cfl:
			cfns = c2.articulations
			nuc = cfns[cf]( (onset, nuc, coda), 2, True)
			
		return nuc



	def dissimilate(self, syllable):
		'''
		nuc is the unit being un-modified.
		onset is the preceding syllable unit.
		coda is the succeeding syllable unit.

		This 'undoes' the supposed adjustment forced on a unit via assimilate()

		*As of 3.9, this also includes feature spreading
		
		Returns the modified vowel
		'''
		import Phonology
		import random
		P = Phonology.Phonology
		fm = Phonology.get_feature_dict() #consonant compensation methods (feature matrix)
		ps = self.pot_spreadables
		onset, nucleus, coda = syllable
		nuc = nucleus.cc()
		c1 = P(fm[onset.name])
		c2 = P(fm[coda.name])
		
		spread_chance = random.randint(0, 99)
	
		ofl = [f for f in onset.features]

		nfl = [f for f in nuc.features]
		
		onset_spreadables = [feat for feat in ofl if feat in ps and spread_chance < 25]
		if onset_spreadables:
			spreader = random.choice(onset_spreadables)
			if spreader not in nfl:
				ofl.remove(spreader)
				nfl.append(spreader)
				#print(spreader, "spread from onset to nucleus")
				
		cfl = [f for f in coda.features]
		coda_spreadables = [feat for feat in cfl if feat in ps and spread_chance > 75]
		if coda_spreadables:
			spreader = random.choice(coda_spreadables)
			if spreader not in nfl:
				cfl.remove(spreader)
				nfl.append(spreader)
				#print(spreader, "spread from coda to nucleus")
		
		for of in ofl:
			ofns = c1.articulations
			nuc = ofns[of]( (onset, nuc, coda), 0, False)
					
		for nf in nfl:
			ofns = c1.articulations
			nf_nuc = ofns[nf]((onset, nuc, coda), 1, False)
			nuc = nf_nuc
			
		for cf in cfl:
			cfns = c2.articulations
			nuc = cfns[cf]( (onset, nuc, coda), 2, False)

		return nuc




	def append_vowel(self, new_v, show = False):
		'''Directly append a vowel without filtering.'''
		if show:
			print("Agent added: ", new_v.name, new_v)
		#Check to see if the new vowel will threaten the space of another
		self.repertoire.append(new_v)

	
		
	def get_rep(self):
		'''returns repertoire (list type) unless rep is empty'''
		if self.repertoire:
			return self.repertoire
		else:
			print("Empty rep.")

			

	def rep_size(self):
		'''returns number of vowels in rep. duplicates may exist'''
		return len(self.repertoire)

	
	 
	def print_rep(self):
		'''Prints the caller's entire repertoire or reports Empty.
		Does not return string'''
		print("Agent", self.name, "current rep: ", end="")
		if not self.repertoire:
			print("Empty.")
		else:
			print("{")
			for i in self.repertoire:
				print(i)
			print("}")

			
			
	def set_rep(self, rep):
		'''Directly replaces agent's rep. Be careful! The old one will be GONE'''
		self.repertoire = rep

		

	def __str__(self):
		'''String form: group number-agent number '''
		s = "-".join( str(self.group), str(self.ind) )
		return s



		
#this method not currently in use by Game etc.
#use for faster testing--time is improved because it short-circuit evaluates
#might be useful if most-recently-heard sorting is ever used
	def first_match(self, sound):
		'''returns the first match it finds'''
		if self.repertoire:
			rep = self.repertoire.values()
			return next((v for v in rep if sound.perc_match(v)), None)
		return None




def to_hz_praat(e1, e2):
	'''An implementation of the converter used in Praat software
	which is based on Traunmuller's formula. '''
	from math import exp
	d1 = exp ((e1 - 43.0) / 11.17)
	f1 = (14680.0*d1 - 312) / (1.0 - d1)

	d2 = exp ((e2 - 43.0) / 11.17)
	f2 = (14680.0*d2 - 312.0) / (1.0 - d2)
	return (f1, f2)



#gives an approximate answer. There seems to be some data loss, but it's pretty close
#I don't know if this is due to insufficient bit size (float may not be precise enough)
#or if it's the formula
#voicebox method:
def to_hz_vb(e1, e2 = 0):
	from math import log, exp, e
	f1 = ( 676170.4 * ( 47.06538 - exp( 0.08950404*abs(e1) ) ) ** (-1) - 14678.5 )
	f2 = 0
	if e2:
		f2 = ( 676170.4 * ( 47.06538 - exp( 0.08950404*abs(e2) ) ) ** (-1) - 14678.5 )
	return(f1, f2)



def to_erb(f1, f2):
	'''direct implementation of traunmuller formula to convert from hertz to ERB
	just converts a tuple (f1, f2) in hz to erb
	benefit is that it doesn't have to be a Vowel, just the values
		i.e. calling >>to_erb(2400, 800) in IDLE will output (22.44472228978699, 13.58504853003826)'''

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


				
def circle_range(x, h, k, r):
			a = (x-h)**2
			c = r**2.0
			ceiling = (c - a)**(.5) + k
			floor =	 2.0*k - ceiling
			return (ceiling, floor)



def margin_tester(margin = 1):
	import Convention
	
	v = Vowel.Vowel(10.5, 18.5, 250, 0)
	
	a = Agent(1, 1, margin, 1)
	v_str = str(v)
	m_str = str(margin)
	pts = [v]
	print("original:", v)
	c = Convention.Convention()
	for i in range(1000):
		im = a.guess_by_margin(v)
		dist = v.euc(im)
		#print("im: ", im, " dist: ", dist)
		pts.append(im)
		#v = im

	c.win = c.formant_space()
	
	c.plot_sets([pts], 0, v_str+" | "+m_str)

	

def converter_demo(tests = 100):
	#converts ERB values to hz and back again test times
	#prints the original ERB values, does the conversion test times
	#then 
	e1 = 0
	e2 = 0.4
	for i in range(tests):
		x = i/10 + .034
		e1+=x
		e2+=x
		print("original:\t\t", e1, e2)
		for i in range(tests):
			f1 = to_hz_praat(e1, e2)[0]
			f2 = to_hz_praat(e1, e2)[1]
			e1 = to_erb(f1, f2)[0]
			e2 = to_erb(f2, f2)[1]
		print("converted", tests, "times:\t", e1, e2)



#converter_demo(100)

#use the following to test the guess_by_margin function:
#margin_tester()

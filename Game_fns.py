'''
Vowel evolution program driver.
Run in PYTHON 3 (!)
with Vowel, Prototype, Word, Agent, Convention, graphics files in same directory

import time, random, re from Python library
Last update February 2017 HJMS

HOW TO RUN
Use 'run' (f5) from IDLE, or
execute this file while the others^ are in same directory, or use
$python3 Game_fns.py
in Linux (Python3 and TKinter must be installed)

The menu will print defaults and the commands you can enter at the prompt.
Use 'demo' if it's your first time and you want to be walked through setup of a game.
Use 'run' if you just want to see what happens with default parameters.
'''

import Vowel, Convention, Agent, Prototype, profile, Word
from time import ctime
from graphics import *
import re
from random import sample, choice

class Game_fns:
	'''Game Class
	Population starts as empty list for groups, which are lists of Agents of same age/stage.
	Game runs through number of 'cycles' one 'step' at a time.
	Each step exposes agents to Prototypes, appends a new group to the population, updates Prototypes.
	One cycle is the number of steps required for the incoming group to complete its lifespan'''
	
	def __init__(self):
		'''Sets default parameters'''
		self.languages= self.set_languages()
		self.total_interactions = 0
		self.num_cycles = 1						#cycle = follow a group from introduction to removal i.e. birth to death
		self.cycle_lim = self.num_cycles
		self.population_max = 300				#population control
		self.age_limit = 30						#Age at which agents are removed.
		al = self.age_limit						
		self.max_groups = al					#max length of self.population	
		pm = self.population_max				#population won't grow beyond this size
		self.anc_group_size = int((pm/al)*10)	#ancestor group (first group with matching repertoires) is 10x larger
		self.g_size = max([2, int( (pm-self.anc_group_size)/al )]) #num. of agents in each age group. If you want to use large numbers, turn off show
		self.show = False						 #True -> more information is displayed. Turning this off makes runtime shorter
		self.color_on = True					#True -> prototypes and vowels are color-coded in graphic reports
		self.length_flag = True					#True -> all agents discriminate long vs short vowels
		self.pause_time = 1						#number of seconds to show step reports (0 to wait for click)
		self.perception = .75					  #margin within which agents recognize matches (uniform and static for all agents)				
		self.phone_radius = .5					   #margin within which agents form internal representation
		self.phone_radius_noise = .5			   #margin within which agents produce their internal representation when speaking
		self.prox = -5						   #controls the sensitivity of vowels in agent's reps
		#PROX NOTE: prox is in ERB units and is added to vowel.weight
		
		self.adapt_perc = 0						#amount agents modify perception from feedback (0 will disable)
		self.social = 0							#social prestige ranking levels (0 will diable)
		
		self.lang_fn = "english"
		self.base = self.languages[self.lang_fn]   #base convention, which can be overwritten in the menu interface

		self.lex_size = 75					   #override the Convention default
		self.convention = Convention.Convention(self.show, self.color_on, self.lex_size)  #Convention tracks the prototypes
		self.convention.str_to_protos(self.base)#Convention reads in a string and splits into keys
		self.use_ipa_symbols = True
		if self.use_ipa_symbols:
			self.convention.plot = self.convention.plot_symbols
		else:
			self.convention.plot = self.convention.plot_spots
		
		self.min_carrier_p = .25				#population size * min_carrier_p = minimum carriers

		self.age_adult = int(self.age_limit/10) + 1		#at 10% lifespan, agents purge their vowels and stop listening
		
		self.contact_agents = 5	   #limit on number of "non-family" agents a listener hears at each step
		self.contact_words = 15		#limit on how many words a listener heard from each "non-family" contact at each step
		self.fam_size = 15
		self.micro = False
		self.micro_agent = None
		

		self.sample_report = self.percept_sampling
		self.find_prototypes = self.percept_protos
		self.avg_adults_only = True
		self.margin_watcher = False
		self.curr_cycle = 0
		self.str_buf = []
		
		
		'''
		SOME NOTES ON THE MARGIN MECHANICS
		ex. perception = .75
			When checking their rep. for a match to incoming signal, agents check the distance between their vowels and the signal
			If the distance is less than .75, they will recognize it as a match
			If no matches are found, agent will produce a randomized imitation within phone_radius ERB of the original.
			Two vowels will conflict if they are within (vowel.weight + prox) ERB of each other
			e.g. with a five vowel system {i, e, o, u, retracted_a} and prox add-on set to .75 :
				 vowel weight will be ~.2
				 average proximity for each vowel will be
				 .2 + .75 = .95 ERB
				 Which means any two Agent's Vowels within .95 ERB will "crowd" each other.
			See Agent.py class.

		A negative prox will effectively disable conflict micromanagement.
		
		'''



	def set_languages(self):
		'''
		Sets up a dictionary of vowel systems.
		Entries are intended to be used as presets
		which correspond to natural languages.
		consonants are defined separately
		'''
		languages = dict()
	
		languages["english"] = "i:, I, e:, epsilon, ae, u:, horseshoe, o:, open_o:, wedge, script_a:"
		languages["spanish"] = "i, e, retracted_a, u, o"
		
		#DEVELOPER NOTE ABOUT LANGUAGE PRESETS
		#the following "languages" are all unreviewed approximations,
		# sources:	wikipedia,
				#	UCPI ( http://zimmer.csufresno.edu/~sfulop/UCPI/UCPI%20index.html ),
				#	and this site ( http://gesc19764.pwp.blueyonder.co.uk/vowels/vowel_systems.html )
		# So far, the most interesting ones to watch are Dutch, Danish, and Swedish.
		# You can adjust these yourself by altering the lines below and then running the program as normal.
		# You can also add as many languages as you want.
		# Note that prototype names which include ':' are long (250 ms)
		# The complete "master set" can be viewed in Convention.py
		
		# TIP: You can use command "languages" from the menu
		# And it will iterate through these languages so you can review them

		languages["russian"] = "i, epsilon, u, o, retracted_a, barred_i, retracted_a, e"
		languages["italian"] = "i, e, epsilon, retracted_a, o, open_o, u"
		languages["german"] = "i:, y, I, Y, e, o_slash, epsilon:, u, o, horseshoe, oe, retracted_a:, script_a, open_o"
		languages["netherlandicdutch"] = "i, i:, e:, I, y, y:, Y, epsilon, epsilon:, oe:, retracted_a:, script_a, Y, u, u:, o:, open_o, open_o:"
		languages["ancientgreek"] = "i, i:, y, y:, e, e:, retracted_a, retracted_a:, epsilon:, u, u:, o, o:"	
		languages["albanian"] = "i, y, e, retracted_a, u, o, schwa" 
		languages["swedish"] = "i:, y:, I, Y, e, e:, epsilon, epsilon:, o_slash, barred_o, rev_eps, oe, retracted_a, script_a, o:, u, u:, barred_u, barred_u:, open_o"
		languages["japanese"] = "i, epsilon, turned_m, u, retracted_a, o, open_o"
		languages["bengali"] = "i, epsilon, e, ae, retracted_a, script_a, horseshoe, o, open_o, u"
		languages["arabic"] = "i, retracted_a, u"
		languages["bulgarian"] = "i, e, rev_e, retracted_a, o, u"
		languages["cantonese"] = "i, y, epsilon, oe, turned_a, retracted_a:, u, open_o"
		languages["catalan"] = "i, e, epsilon, retracted_a, schwa, o, u, open_o"
		languages["chichewa"] = "i, epsilon, retracted_a, o, u"
		languages["chipewyan"] = "i, y, I, e, o_slash, oe, epsilon, ae, retracted_a, schwa, wedge, o, script_a, u" 
		languages["czech"] = "i, i:, I, e:, e, epsilon, epsilon:, schwa, retracted_a, retracted_a:, script_a, script_a:, open_o:, o, u"
		languages["danish"] = "i, i:, y, y:, I, I:, epsilon, epsilon:, o_slash:, o_slash, e, e:, oe:, oe, ae:, ae, schwa, schwa:, horseshoe:, horseshoe, u, u:, o, o:, open_o, open_o:, script_a, script_a:"
		languages["lyonnaisfrench"] = "i, epsilon, oe, o_slash, e, oe, ae, schwa, retracted_a, script_a, rev_script_a, o, u, open_o"
		languages["hakka"] = "i, e, epsilon, ae, schwa, retracted_a, u, horseshoe, o, open_o, script_a"
		languages["icelandic"] = "i, e, epsilon, o_slash, oe, u, o, script_a"
		languages["idoma"] = "i, e, epsilon, retracted_a, u, o, open_o"
		languages["korean"] = "i, I, e, epsilon, schwa, retracted_a, o, u"
		languages["latvian"] = "i, I, e, e:, epsilon:, epsilon, wedge, retracted_a:, retracted_a, u, u:, horseshoe, horseshoe:, open_o, script_a, script_a:"
		languages["malay"] = "i, I, e, epsilon, retracted_a, wedge, schwa, u, o, turned_m, open_o"
		languages["norwegian"] = "i, y, I, e, o_slash, epsilon, ae, schwa, retracted_a, u, o, turned_m, o, open_o, script_a"
		languages["zulu"] = "i, e, epsilon, schwa, retracted_a, u, horseshoe, o, open_o"
		languages["slovak"] = "i, i:, epsilon:, epsilon, retracted_a, retracted_a:, u, u:, open_o, open_o:"
		languages["tibetan"] = "i, y, I, e, o_slash, epsilon, retracted_a, wedge, u, horseshoe, o, open_o"
		languages["tigrinya"] = "i, e, epsilon, retracted_a, schwa, u, o, open_o"
		languages["turkish"] = "i, y, epsilon, oe, retracted_a, turned_m, u, open_o"
		languages["ukranian"] = "i, I, epsilon, a, u, o"
		languages["vietnamese"] = "i, e, epsilon, wedge, a, a:, turned_m, u, Y, o, open_o"
		languages["xumi"] = "i:, e:, epsilon, barred_o, u, o:, script_a, retracted_a, wedge"
		languages["oldenglish"] = "i, i:, y, y:, e, e:, ae, ae:, o_slash, o_slash:, script_a, script_a:, u, u:, o:, o" 
		languages["welsh"] = "i:, I, e:, epsilon, retracted_a, script_a:, barred_i, barred_i:, schwa, schwa:, open_o, horseshoe, u:, o:" 
		languages["arrernte"] = "retracted_a, schwa"
		languages["finnish"] = "i, i:, y, y:, u, u:, e, e:, o_slash, o_slash:, epsilon, epsilon:, a, a:, u, u:, o, o:"
		languages["karaja"] = "i, I, e, epsilon, wedge, barred_i, retracted_a, open_o, o, horseshoe, u"
		#languages["yourlanguage"] = ""
		

		#######		ADD LANGUAGES ABOVE THIS LINE	 ########
		#the names should be all lowercase alpha-num characters and there CANNOT (!) be any duplicates* 
		# *as in, no keyword (e.g. "spanish") can be used twice, but different languages may use the same set of vowels 
		
		#The following are for testing the values in the Convention IPA set;
		# they aren't meant to be used as languages,

		languages["high"] = "i, y, barred_i, barred_u, u, horseshoe, turned_m"
		languages["mid"] = "I, Y, e, o_slash, barred_o, schwa, rams_horn, o, open_o, wedge, lil_bum, rev_e"
		languages["low"] = "OE, epsilon, oe, ae, rev_eps, a, rev_script_a, turned_a, retracted_a, script_a"
		languages["front"] = "i, y, I, e, o_slash, epsilon, ae, OE"
		languages["central"] = "barred_i, barred_u, barred_o, rev_eps, lil_bum, rev_e, schwa, turned_a, retracted_a"
		languages["back"] = "u, wedge, horseshoe, turned_m, rams_horn, o, open_o, script_a, rev_script_a"
		high = languages["high"]
		mid = languages["mid"]
		low = languages["low"]
		languages["short"] = ", ".join([high, mid, low])
		languages["long"] = languages["short"].replace(",", ":,")+":"
		languages["ipa"] = ", ".join([languages["short"], languages["long"]])

		return languages
	


#############################
#		STEP METHODS		#
#############################

	def step(self):
		'''
		Passage of time in steps.
		Number of steps controlled by lifespan (age_limit) and cycles (num_cycles)
		i.e. each agent takes age_limit steps from birth to death
		'''
		if self.show:
			print("Stepping...")
			
		self.reproduce()		#append list of new agents to population	
		self.diffuse()			#signal vowels in convention to all agents
		self.increment()		#advances every current agents' development. Insert argument for number of years
		self.charon()			#removes agents who have completed all cycles and increments cycle count  



	def get_prestige(self):
		if self.social:
			levels = range(self.social)
			return choice(levels)
		else:
			return 0



	def reproduce(self):
		'''
		Adds a new group of Agents with age = 0 to population--
		babies eager to learn their parents' vowels and grow up to speak words.
		Population size controlled by max_groups.
		'''
		popul = self.population
		pot_fam = [k for k in self.get_sampling().keys()]
		fam_size = min([self.fam_size, len(pot_fam)])
		
		
		pm = self.population_max
		ta = self.total_agents
		al = self.age_limit
		#gs = self.g_size
		gs = max([1, int( (pm-ta) / (al - len(popul)) )] )
		self.g_size = gs
		if (ta+gs) <= pm:  #population growth control. Peak population size = g_size * max_groups
			a = Agent.Agent
			gc = self.g_count+1
			lf = self.length_flag
			bp = self.perception
			pm = self.prox
			prod = self.phone_radius
			pn = self.phone_radius_noise
			ap = self.adapt_perc
			gp = self.get_prestige
			babies = [a(gc, i, bp, pm, prod, pn, lf, ap, gp()) for i in range(gs)]
			popul.append(babies)
			self.total_agents += gs
			self.g_count = gc
			#assign constant "nuclear family" to baby
			for baby in babies:
				baby.fam = sample(pot_fam, fam_size)


				
	def diffuse(self):	  
		'''
		Transmits lexicon to Agents,
		which will lead to the words being replicated in Agents' vocabularies.
		'''
		gs = self.g_size
		c = self.convention
		s = self.get_sampling()

		proto_list = c.proto_dict.keys()
		adult_age = int(self.age_limit/10)+1
		children = [g for g in self.population if g[0].age < adult_age]
		ta = self.total_agents

		#"micro" mode: pick a random agent to monitor closely
		if (self.micro and not self.micro_agent):
			babies = self.population[-1]
			self.micro_agent = choice(babies)
			self.micro_agent.chosen = True

		if not s:
			#something has gone wrong; probably crazy parameters used
			print("The language has died--agents were unable to pass on the lexicon.")
			print("If you could please save and send your shell session or parameter values to")
			print(" hannahjmscott@gmail.com , the developer will be super grateful and reply with a funny picture or something.")
			self.curr_cycle = self.num_cycles+1
			return	

		ca = self.contact_agents
		cw = self.contact_words
		
		s_keys = [s for s in s.keys()]
		sample_size = int(min([self.lex_size, (len(s_keys)/4), ca ]))
		
		t = self.transmit
		#iterate through population
		for g in children:
			for a in g:
				#get sample_size random words from population
				random_speakers = sample(s_keys, sample_size)
#
				#random_words = [sample(s[rsp], min([len(s[rsp]), cw]) ) for rsp in random_speakers if len(s[rsp])]
				#cw is the limit on how many words to get (0 for the whole vocab)
				random_words = ( self.sample_agent_words(s[rsp], cw) for rsp in random_speakers if len(s[rsp]))
				for rws in random_words:
					for rw in rws:
						t(a, rw) #show the random words to the learner
					
				#get "family" input
				family = [f for f in a.family if f in s]
				#replace the dead family members (after a brief moment of respectful silence)
				if len(family) < self.fam_size:
					dead = self.fam_size - len(family)
					new_fam = sample( [sk for sk in s_keys if sk != a.name and sk not in family and len(s[sk])], dead)
					family.extend(new_fam)
				
				fam_words = (self.sample_agent_words(s[member]) for member in family)
				for ws in fam_words:
					for w in ws:
						t(a, w)
					 
		if self.show:
			self.sample_report() #draw population repertoires
			self.proto_report()	 #draw current Prototypes



	def sample_agent_words(self, vocab, lim = 0):
		vg = [w for w in vocab.values()]
		if len(vg):
			if lim:
				return sample(vg, lim)
			return vg
		return None

	

	def get_sampling(self):
		'''
		Returns a dictionary of utterances for this step
		i.e. {"agent name": [Word]}
		'''
		sampling = dict()
		l = len(self.population)
		if l < 3:
			p = [self.population[0]]
		else:
			p = self.population
		for g in p:
			for a in g:
				#sampling[a.name] = [w for w in a.idio.values()]
				sampling[a.name] = a.idio
		return sampling

	

	def transmit(self, agent, n):
		'''signals a word n to agent'''
		self.total_interactions += 1
		im = agent.call_matchers(n)
		return

	

	def increment(self):
		'''increase age of every live agent'''
		popul = self.population
		adult_age = self.age_adult
		for g in popul:
			for a in g:
				a.inc_age()
				if a.age is adult_age:
					a.purge_vwls()
		chosen = self.micro_agent
		if (chosen and chosen.age > adult_age):
			print("\nAgent", chosen.name, "is all grown up!")
			#chosen.print_rep()
			#chosen.print_vocab()
			#self.convention.draw_agent_margins(chosen)
			self.draw_proto_margins()
			chosen.chosen = False
			self.micro_agent = None

			

	def charon(self):
		'''Removes the group of agents who have completed all stages.
		Increments cycle counter for game'''
		popul = self.population
		oldest = popul[0]
		
		if not oldest:	#something has gone wrong
			self.curr_cycle = self.num_cycles+1
			print("Error in charon: the babies have been abandoned!")
			return
		
		a = oldest[0].age
		age_lim = self.age_limit
		d = []

		#if the oldest group has reached the lifespan limit, remove them
		#and inc the cycle counter if the new oldest group is 1 year under lifespan limit		 
		if a >= age_lim:
			d = popul.pop(0)
			self.total_agents -= len(d)	   
			if(popul[0][0].age >= (age_lim - 1)):  
				self.curr_cycle += 1
				if self.show:
					print("Cycle ", self.curr_cycle, "completed.")
					
		if self.avg_adults_only:
			min_age_avg = self.age_adult
			
		else:
			min_age_avg = 0
			
		self.find_prototypes(min_age_avg, self.age_limit)



	def percept_protos(self, min_age = 0, max_age = 100):
		'''
		Gets the average internal representation for each word in lexicon.
		Shifting of vowels is enabled by updating the mean center for each word.
		For each word, the Agents' vocabularies are scanned and
		the Vowels used by Agents for that word are collected and averaged.

		This updates the Convention's proto_dict.
		'''
		c = self.convention
		adult = self.age_adult
		adults = [g for g in self.population if g[0].age > 1]
		pd = c.proto_dict
		adult_vowels = []
		lex = c.lexicon.items()
		for (w_id, word) in lex:
			nuc = word.nucleus
			word_vowels = [a.idio[w_id].percept for g in adults for a in g if (w_id in a.idio and a.age > min_age and a.age <= max_age)]

			if word_vowels:
				word_proto = c.get_word_prototype(word_vowels, w_id) #, word
				adult_vowels.append(word_proto)
			else:
				print("RIP", word)
				
		
		r = self.perception + self.prox
		c.group_word_protos(r, adult_vowels)
		return 1

	def vowel_protos(self, min_age = 0, max_age = 100):
		'''
		Gets the average pronunciation for each word in lexicon.
		Shifting of vowels is enabled by updating the mean center for each word.
		For each word, the Agents' vocabularies are scanned and
		the Vowels used by Agents for that word are collected and averaged.

		This updates the Convention's proto_dict.

		Accesses the agent's word's vowel, which may be dynamically generated
		'''
		c = self.convention
		adult = self.age_adult
		adults = [g for g in self.population if g[0].age > 1]
		#pd = c.proto_dict
		adult_vowels = []
		lex = c.lexicon.items()
		for (w_id, word) in lex:
			nuc = word.nucleus
			word_vowels = [(a.idio[w_id]).get_vowel() for g in adults for a in g if (w_id in a.idio and a.age > min_age and a.age <= max_age)]
			if word_vowels:
				word_proto = c.get_word_prototype(word_vowels, w_id) 
				adult_vowels.append(word_proto)
			else:
				print("RIP", word)
		r = self.perception + self.prox
		c.group_word_protos(r, adult_vowels)
		return 1
			
#################################
#		REPORTING METHODS		#
#################################

######## GRAPHICAL				 

	def proto_report(self):
		'''
		Plots the current convention in vowel space.

		The convention is shown as a number of spots in the vowel space,
		where each spot is the averaged pronunciation of the vowel in a word.

		This method also prints an update on the game state in the shell,
		which lists the number of live Agents (adults, children, babies),
		the current mean centers for each word prototype,
		and the cycle counter.
		'''
		c = self.convention
		sl = []
		sol = sl.append

		protos = sorted(c.proto_dict.values(), key = lambda proto: (proto.name.split("]["))[1])
		ta = self.total_agents
		num_adults = sum([len(g) for g in self.population if g[0].age >= self.age_adult])
		num_babies = len(self.population[-1])
		num_children = ta - (num_adults + num_babies)
		s0 = "STEP COMPLETED. "
		#print number of adults, children, babies, and cycles
		s = ("\n{0} live agents ({1} babies, {2} children, {3} adults)\n".format(ta, num_babies, num_children, num_adults))
		sol(s0+s)
		print(s)
		message = "Mean centers of adult agents' vowels (Cycle "+str(self.curr_cycle)+")"
		mcp = self.min_carrier_p
		min_carriers = (ta * mcp)

		if (self.micro and self.micro_agent):
			self.micro_agent.print_rep()
			self.micro_agent.print_vocab()
			

		else: #macro mode: show averages
			s_header = "{0:25}{1}".format("WORD", "AVERAGE VOWEL")
			sol(s_header)
			for p in protos:
				si = "{0:25} {1}".format(p.name, str(p))
				sol(si)
				print(si)
			

		#draw the graphic
		c.plot(self.pause_time, min_carriers, message)
		if self.margin_watcher:
			#c.draw_avg_margins(protos, self.perception, self.prox)
			c.draw_base_margins(protos, self.perception, self.prox)
		self.str_buf.append("\n".join(sl))
		return 1

	
	
	def vowel_sampling(self):
		'''
		Plots the protos of every agent (overlaid) in the vowel space.

		This 'sampling' shows the population's Vowels,
		where each Vowel is represented by a dot in the output window.

		This also updates the centered label in the window,
		which shows the number of live Agents,
		the Agents' perception,
		and the user-set prox supplement.
		'''
		lf = self.length_flag
		p = self.population
		c = self.convention
		adult = self.age_adult

		#get all Agents' Vowels that are being used in Words
		all_reps = set() #will be a set of Vowels
		for g in p:
			for a in g:
				for w in a.idio.values():
					#retrieve protos i.e. vowels as they are spoken (dynamically generated)
					all_reps.add(w.get_vowel())

		#Update the center label and plot the vowels
		if all_reps:
			s = "Live agents = {0}, Perception = {1}, Prox add-on = {2}, Phone radius = {3}, Vowel noise = {4}".format(self.total_agents, self.perception, self.prox, self.phone_radius, self.phone_radius_noise)
			if len(all_reps) < 2:
				c.plot_sets([all_reps], self.pause_time, s)
			c.plot_sets(all_reps, self.pause_time, s)
			if (self.micro and self.micro_agent):
				c.plot_micro(self.micro_agent)
		return 1

	

	def percept_sampling(self):
		'''
		Plots the percepts of all agents (overlaid) in the vowel space.

		This 'sampling' shows the population's Vowels,
		where each Vowel is represented by a dot in the output window.

		This also updates the centered label in the window,
		which shows the number of live Agents,
		the Agents' perception,
		and the user-set prox supplement.
		'''
		lf = self.length_flag
		p = self.population
		c = self.convention
		adult = self.age_adult

		#get all Agents' Vowels that are being used in Words
		all_reps = set() #will be a set of Vowels
		for g in p:
			for a in g:
				for w in a.idio.values():
					#retrieve percepts i.e. internal representation of vowels in agents' minds
					all_reps.add(w.percept)
					

		#Update the center label and plot the vowels
		if all_reps:
			s = "Live agents = {0}, Perception = {1}, Prox add-on = {2}, Phone radius = {3}, Vowel noise = {4}".format(self.total_agents, self.perception, self.prox, self.phone_radius, self.phone_radius_noise)
			if len(all_reps) < 2:
				c.plot_sets([all_reps], self.pause_time, s)
			c.plot_sets(all_reps, self.pause_time, s)
			if (self.micro and self.micro_agent):
				c.plot_micro(self.micro_agent)
		return 1
		


		
	def init_report(self, pause = 0):
		'''
		Plots base convention in vowel space at the beginning of a simulation.
		pause is the number of seconds window stays open.
		 Enter 0 to wait for mouse before continuing. (default)
		'''

		#set up the graphical output window
		c = self.convention
		s = str(len(self.base.split(", ")))
		label = (s+" vowels; "+("%.4f" %self.perception))
		c.draw_win(label)
		
		#wait for user to be ready before starting
		c.plot(pause, 1, "Starting Prototypes. (Click in window to continue)")
		return 1


	
	def final_report(self):
		'''
		Shows the final sampling and mean center results.
		Closes the Convention window when user clicks in it. 
		'''
		c = self.convention
		ta = self.total_agents
		min_carriers = (ta * .1) + 1

		lf = self.length_flag
		fs = self.fam_size
		ca = self.contact_agents
		cw = self.contact_words
		nc = self.curr_cycle
		cps = "Family = {0}, Contacts = {1}, Words = {2}, Cycles = {3}".format(fs, ca, cw, nc)
		c.set_param_str(cps)
		self.sample_report()
		if c.proto_dict.values():
			c.plot(0, min_carriers, "End results. (Click in window to continue.)")

		if (self.micro and self.micro_agent):
			c.plot_micro(self.micro_agent)
			if not self.show:
				c.close_win()
				
		self.count_near_splits() #counts the number of agents with lexical splits
		return 1

	

	def displacement_report(self, save = None):
		'''
		Calls the current Convention's show_displacement method
		which plots the original and current averages of prototypes
		'''
		conv = self.convention
		p = str(self.perception)
		b = self.base
		mcp = self.min_carrier_p
		mc = (self.total_agents * mcp)
		protos = [p for p in conv.proto_dict.values() if p.carriers > mc]

		lf = self.length_flag
		fs = self.fam_size
		ca = self.contact_agents
		cw = self.contact_words
		nc = self.curr_cycle
		l1 = "Live agents = {0}, Perception = {1}, Prox add-on = {2}, Phone radius = {3}, Vowel noise = {4}".format(self.total_agents, self.perception, self.prox, self.phone_radius, self.phone_radius_noise)	 
		cps = "Family = {0}, Contacts = {1}, Words = {2}, Cycles = {3}".format(fs, ca, cw, nc)
		conv.set_param_str(cps)
		
		if save:
			fn = self.file_name(save)+"_shift"
			conv.show_displacement(l1, protos, 1)
			conv.save_win(fn)
			conv.close_win()
		elif self.margin_watcher:
			#conv.draw_avg_margins(protos, self.perception, self.prox, True)
			conv.draw_base_margins(protos, self.perception, self.prox, True)
		else:
			conv.show_displacement(l1, protos, 0)


		return 1

	

	def draw_proto_margins(self, save = None):
		'''Calls the current Convention's draw_proto_margins metretracted_a
		   which draws the convention prototypes,
					   the perceptual margin as a radius around the prototype, and
					   the average proximity margin as a radius around the prototype'''
		if (self.micro and self.micro_agent):
			return self.draw_agent_margins(self.micro_agent)
		else:
			c = self.convention
			if (not c.lexicon.keys()):
				c.strap_protos()
			perc = self.perception
			prox = self.prox
			if prox < 0:
				prox = 0
			c.draw_proto_margins(perc, prox, False)
			if save:
				fn = self.file_name(save)+"_margins"
				c.save_win(fn)
			else:
				cfn = None
				c.win.getMouse()
			c.close_win()
			return 1
		
	def file_name(self, pref=""):
			perc_s = str(self.perception).replace(".", "")
			prox_s = str(self.prox).replace(".", "")
			phone_s = str(self.phone_radius).replace(".", "")
			v_s = str(self.phone_radius_noise).replace(".", "")
			fam_s = str(self.fam_size)
			friend_s = str(self.contact_agents)
			cc = "{0:03d}".format(self.curr_cycle)
			cfn = ("_".join([pref+fam_s+friend_s, perc_s, prox_s, phone_s, v_s, cc]))
			return cfn


		
	def draw_agent_margins(self, agent):
		c = self.convention
		c.draw_agent_margins(agent)
		if not self.show:
			c.close_win()
		return 1


	
	def redraw_last(self, save = None):
		'''
		Plots the most recent sampling of the live agents' vowels.
		Show == True is not required for this to be called.
		If user closes the window, they can use this
		to re-open and get last sampling.
		Closes the window on mouse click.

		If called by write_image(),
		it will save the window as a gif
		then close the window
		
		'''
		
		c = self.convention
		self.sample_report()
		ta = self.total_agents
		message = "Mean centers of adult agents' vowels (Cycle "+str(self.curr_cycle)+")"
		mcp = self.min_carrier_p
		min_carriers = 1 #(ta * mcp)

		#Draw the results and
		#either save, then close the window, or
		#show and wait for mouse before closing it.
		if save:
			if self.use_ipa_symbols:
				c.plot = c.plot_spots
			self.proto_report()
			fn = self.file_name(save)
			c.save_win(fn)
			c.plot = c.plot_symbols
		else:
			c.plot(0, min_carriers, message)
		c.close_win()
		return 1



######## TEXT-ONLY		  
	def shifting_report(self):
		'''
		Prints a table listing the convention's Prototypes.
		Shows the IPA formant values,
			  the current mean center,
			  the current weight, and
			  the displacement (from ipa i.e. self.base, not last run)
		 for each word in the lexicon.
		'''
		s_out_li = [] #save output to write to file later
		sol = s_out_li.append
		
		ta = self.total_agents - self.g_size #don't count the babies
		cv = self.convention.proto_dict.values()
		pl = sorted(cv, key=lambda proto: (proto.name.split("]["))[1])	#sorts the Prototypes by f1
		bpd = self.convention.base_proto_dict
		bvd = self.convention.base_vowel_dict
		s1 = "Resulting Prototypes with {0} agent perception, {1} proximity margin".format(self.perception, self.prox)
		sol("\n\n"+s1)
		print(s1)

		s2 = "{0:25}{1:18}{2:18}{3:16}".format("Name", "Original", "Current", "Displacement")
		sol(s2)
		print(s2)
		base = self.base.split(", ")
		for p in pl:
			p_class = (p.name.split("][")[1])
			#p_class = "".join(re.findall("[a-zA-Z_:]+", p.name))
			if p_class in base:
				original = bvd[p_class]
				shift = "{0:.4f}".format(p.euc(original))
				o = original		
			else:
				shift = "{:12}".format(" --")
				o = "{:18}".format(" --")
			#r = "{0:.0f}%".format((p.carriers/ta)*100)		  #retention
			name = p.name
			si = "{0:25}{1:18}{2:18}{3:16}".format(name, str(o), str(p), str(shift))
			sol(si)
			print(si)

		s_out = "\n".join(s_out_li)
		self.str_buf.append(s_out)
		return 1
		
	def margin_report(self, g):
		'''
		Prints the current tolerance margins for an age group.
		g is the group e.g. population[0].

		Deprecated in phase 2 because Agents' margins don't change. 
		'''
		percs = [a.perception for a in g]
		avg_perc = sum(p for p in percs)/self.g_size
		print("\nAVERAGE MARGINS FOR OLDEST GROUP (age {0})".format(g[0].age))
		print("Perception: ", ("%.4f" % avg_perc))
		return 1
	
	def lexicon_report(self):
		'''
		Called by the 'report' command.
		Prints each word in lexicon,
			   a list of the vowels being used,and
			   the number of live agents using each one.
		'''
		c = self.count_word_vowels(True)
		#s_h = "Checking for sound changes."
		#self.str_buf.append(s_h)
		#print(s_h)
		#self.find_sound_changes()
		return 1

	def find_sound_changes(self):
		'''
		Called by lexicon_report() which is the 'report' menu command.
		Returns a list of vowels and the number of agents
		 for each word in the lexicon.
		'''
		c = self.convention
		lex = c.lexicon
		lex = sorted(lex.values(), key=lambda Word: Word.id)
		s_out_li = []
		sol = s_out_li.append
		changes = []
		
		for w in lex: #every word in lexicon
			#find original (ancestors') proto
			anc_proto = "".join(re.findall("[a-zA-Z_:]+", w.id))

			#group agents by vowel consensus
			w_p_cntr = dict()
			for g in self.population:
				for a in g:
					if w.id in a.idio: #should always be True, but check anyway
						
						#figure out what vowel the agent thinks it is
						vowel = a.idio[w.id].percept
						w_v = vowel.name
						
						#figure out what IPA prototype it matches
						proto = c.match_proto(vowel, True)
						w_p = proto.name
						
						#add the prototype to word vowel counter
						if w_p in w_p_cntr:
							w_p_cntr[w_p].append(proto)
						else:
							w_p_cntr[w_p] = [proto]
							
			
			counts = [(p, len(c)) for (p, c) in w_p_cntr.items() if c]
			counts_sorted = sorted(counts, key=lambda p: p[1], reverse=True)
			highest = counts_sorted[0][0]
			if (highest != anc_proto):
				#print(highest, "!=", anc_proto)
				changes.append(counts_sorted)
				cntr = ", ".join([" ["+p+"] = " + str(c) for (p, c) in counts_sorted])
				si = ("{0:16}{1}".format( w.id, cntr ))
				sol(si)

		#save for file
		
		if len(changes) > 1:
			s_out = "\n".join(s_out_li)
		elif changes:
			s_out = s_out_li[0]
		else:
			s_out = "No significant sound changes detected."
		self.str_buf.append(s_out)
		print(s_out)

	
	def count_word_vowels(self, show_out = False):
		'''
		Uses the Agents' percepts (stable), NOT vowels (dynamically generated)
		Called by lexicon_report() which is the 'report' menu command.
		Returns a list of vowels and the number of agents
		 for each word in the lexicon.
		'''
		c = self.convention
		lex = c.lexicon
		lex = sorted(lex.values(), key=lambda Word: Word.id.split("][")[1])
		s_out_li = []
		sol = s_out_li.append
		
		for w in lex:
			s_label = "\n{0:30}{1:14}{2:10}".format(w.id, "vowel", "num. agents")
			sol(s_label)
			if show_out:
				print(s_label)
			w_p_cntr = dict()
			for g in self.population:
				for a in g:
					if w.id in a.idio:
						vowel = a.idio[w.id].percept
						w_p = vowel.name
						if w_p in w_p_cntr:
							w_p_cntr[w_p].append(vowel)
						else:
							w_p_cntr[w_p] = [vowel]
			cntr = w_p_cntr.items()
			
			for (v, c) in cntr:
				si = ("{0:30}{1:14}{2:10}".format( "", str(v), str( len(c) ) ) )
				sol(si)
				if show_out:
					print(si)

		#save for file
		s_out = "\n".join(s_out_li)
		self.str_buf.append(s_out)

		return(cntr)

		
	def count_near_splits(self):
		'''
		Counts the number of agents who have at least one 'duplicated' vowel.
		Duplicated means that the ancestor group had one vowel, but this agent has two.
		 AKA a "near split"
		Near splits may lead to lexical splits in the convention,
		 i.e. phonological change in the language.
		'''
		agent_total = 0
		pl = self.convention.ipa_dict.values()
		for g in self.population:
			agent_count = 0
			if g[0].age > 0:
				for a in g:
					split_count = 0
					for p in pl:
						splits = [v for v in a.repertoire if (v.name is p.name and v.weight > 0)]
						if splits:	  #agent has duplicates of p in rep
							split_count += 1	
					if split_count:
						agent_count += 1
				agent_total += agent_count
		si = str(agent_total)+" agents have near splits."
		print(si)
		self.str_buf.append(si)
		return 1
			
	def agent_report(self):
		'''prints margin report and number of agents with apparent splits'''
		for g in self.population:
			self.margin_report(g)
		self.count_near_splits()
		return 1
		
	def print_all_reps(self):
		'''
		Prints every agent's rep, sorted by age group.
		Called by the "details" menu command. 
		'''
		sl = [] 
		sol = sl.append #for file if saved
		sol("\nALL AGENT REPERTOIRES")
		
		for g in self.population:
			for a in g:
				s0 = "\nAgent #"+a.name+" Age: "+str(a.age)
				sol(s0)
				print(s0)
				s1 = "VOWELS"
				sol("\n"+s1)
				print(s1)
				si = []
				for v in a.repertoire:
					si.append("{0:25}{1}".format(v.name, str(v)))
				si_str = "\n".join(si)
				sol(si_str)
				print(si_str)
				s3 = "VOCABULARY"
				sol("\n"+s3)
				print(s3)
				s4 = a.get_vocab_str()
				sol(s4)
				print(s4)
		sl_str = "\n".join(sl)
		self.str_buf.append(sl_str)
		return 1

	def print_param(self):
		'''prints a table with the current settings'''
		c = self.convention
		sl = [] 
		sol = sl.append
		
		print("CURRENT GAME PARAMETERS")		
		nc = str(self.num_cycles)
		pl = str(self.population_max)
		al = str(self.age_limit)
		ss = str(self.show)
		pm = str(self.perception)
		lf = str(self.length_flag)
		ls = str(self.lex_size)
		gbm = str(self.prox)
		ca = self.contact_agents
		cw = self.contact_words
		prox = str((c.lex_size/len(self.base.split(" ")))/(c.lex_size) + self.prox )
		fs	= self.fam_size
		prn = str(self.phone_radius_noise)
		pr = str(self.phone_radius)

		s1 = "| {0:^9} | {1:^9} | {2:^8} | {3:^8} | {4:^6} | {5:^5} | {6:^5} |".format("SHOW", "POPUL MAX", "LIFESPAN", "LEX SIZE", "CYCLES", "PHONE", "NOISE")
		print(s1)

		s2 = " {0:^11} {1:^11} {2:^10} {3:^10} {4:^8} {5:^7} {6:^7} ".format(ss, pl, al, ls, nc, pr, prn)
		print(s2)

		s3 = "| {0:^10} | {1:^8} | {2:^7} | {3:^12} | {4:^9} | {5:^8} |".format("PERCEPTION", "FAM SIZE", "FRIENDS", "WORDS/FRIEND", "PROX SUPP", "AVG PROX")
		print(s3)

		s4 = " {0:^12} {1:^10} {2:^9} {3:^14}\t{4:^.6}\t {5:^.6}   ".format(pm, fs, ca, cw, gbm, prox)		  
		print(s4)

		s5 = "BASE CONVENTION\n"+self.base+"\n"

		print(s5)

	
	def summarize_param(self):
		'''Prints a summary of the game's parameters'''
		c = self.convention
		nc = self.num_cycles
		pm = self.population_max
		al = self.age_limit
		#b_perc = self.perception
		
		s6 = "LEXICON\n"+("\n ".join([w.id for w in sorted(c.lexicon.values(), key = lambda word: word.nucleus)])) 
		print(s6)

		#print("Running {0} cycles, max population {1}, {2}-step lifespan.".format(nc, pm, al))
		#print("Convention:", (", ".join([k for k in c.proto_dict.keys()])))
		if (not self.length_flag):
			print("Agents ignore length")
			
		
#################################
# PARAMETER-SETTING METHODS		#
#################################
	
	def strap_game(self, reset):
		'''
		Boot-strapping method.
		Sets up a population of Agents at midpoint of their lifespan.
		Here's where we drop off a group of adult same-language speakers on an island.
		'''
		lf = self.length_flag
		al = self.age_limit
		gs = self.anc_group_size
		pm = self.perception
		prox = self.prox
		prod = self.phone_radius
		noise = self.phone_radius_noise
		a = Agent.Agent
		c = self.convention
		
		pop_max = self.population_max
		gp = self.get_prestige
		
		if pop_max <= al:
			self.population_max = al+1
			self.g_size = max([2, int( (self.population_max-gs)/al )])
		if reset:
			self.curr_cycle = 0
			c.reset(self.base)
			self.population = list()
			ap = self.adapt_perc
			ancestors = [a(0, j, pm, prox, prod, noise, lf, ap, gp()) for j in range(gs)]
			self.total_agents = gs		  
			self.population.append(ancestors)
			self.g_count = 0		#number of groups who have been born
			c.strap_protos()	  #sets the number of carriers manually because everyone is the same 
			self.strap_ancestors()	
			c.lf = self.length_flag
			self.total_interactions = 0
			self.str_buf = []

		fs = self.fam_size
		ca = self.contact_agents
		cw = self.contact_words
		#s1 = "Current number of agents = {0}. Perception = {1}. Prox add-on set to {2}.".format(self.total_agents, self.perception, self.prox)
		cps = "Family = {0}, Contacts = {1}, Words = {2}".format(fs, ca, cw) 
		c.set_param_str(cps)


			
	def strap_ancestors(self):
		'''
		Bootstrapping method used to set up the simulation.
		These Agents aren't counted in final reports,
		and they don't change their rep's or vocabularies.
		They just talk at their babies every step
		until they die at the age of self.age_limit.
		'''

		P = Prototype.Prototype
		
		'''ancestor agents all have approximately the same rep i.e. the base convention'''
		if not self.population:
			print("error in strap_ancestors")
			return
		age = int(self.age_limit/2)
		vocab = self.convention.lexicon
		ancestors = self.population[0]
		prod = self.phone_radius
		
		#set up ancestors with repertoires of vowels
		# that are slightly noisy imitations of base convention prototypes.
		for a in ancestors:
			
			####noise control / sloppiness handling / ancestor consensus
			#no multiple will use the phone_radius variable directly
			#change multiplier to something larger for "sloppier" imitations
			#or to something smaller for more precise imitations
			a.phone_radius = prod	
			
			gbm = a.guess_by_margin
			a.age = age
			for (word, w) in vocab.items():
				p = w.percept.cc()
				#ap = gbm(p)
				ap = w.get_vowel() #assimilated vowel
				dap = a.dissimilate( (w.onset, ap, w.coda) ) #deassimilated assimilated vowel
				pn = a.phone_radius_noise
				a.idio[word] = Word.Word(w.onset, w.nucleus, w.coda, dap, pn)
				a.repertoire.append(dap)
				
		
		self.find_prototypes()
			


	def set_cycles(self, more = False, get = None):
		'''Overwrite default number of cycles between reports.'''
		if more:
			print("A cycle is completed every time a group of agents completes a lifespan.")
			print("The first cycle always takes the longest because the ancestor group is not counted.")
			print("After all cycles finish, the vowel space will appear with the original base convention and current averages.")			 
			print("You can get a 'report' of those results and 'extend' the game for another set of cycles after the first set.")
		if not get:
			nc = input("Number of cycles:")
			if not nc:
				print("Canceled.")
				return 1
		else:
			nc = eval(get)
		nc = int(nc)
		while nc < 1:
			nc = int(input("Try a number greater than 0: "))
		self.num_cycles = nc
		return 1
							  


	def set_size(self, more = False, get = None):
		'''Overwrite default population size.'''
		if more:
			print("The population will continue to grow by adding new agents at every step until a limit is reached.")
			print("At that point, the game will stop adding agents until a group is removed.")
			print("The population maximum has to be greater than the age limit.")
		if not get:
			pm = input("Population size limit: ")
			if not pm:
				print("Canceled.")
				return 1
		else:
			pm = eval(get)
		pm = int(pm)
		al = self.age_limit
		if pm <= al:
			pm = al+1
			print("Population size must be >", al, ". Setting to", al+1, ".")
		self.max_groups = al		
		self.population_max = pm
		self.g_size = max([1, int(pm/al)])
		self.fam_size = min(self.fam_size, self.g_size)
		self.anc_group_size = self.g_size * 10
		return 1



	def set_lifespan(self, more = False, get = None):
		'''Overwrite Agent age limit.'''
		if more:
			print("The lifespan is the number of steps agents take before being removed and replaced by new agents.")
			print("The ancestor group will start at the midpoint of their lifespan. The age of maturity will be 10% of the lifespan.")
			print("The lifespan limit can be any int from 20 to 100.")
		if not get:
			al = input("Lifespan: ")
			if not al:
				print("Canceled.")
				return 1
		else:
			al = eval(get)
		al = int(al)
		while (al < 20 or al > 100):
			al = int(input("Try a number between 20 and 100: "))
		self.age_limit = al
		self.max_groups = al
		self.population_max = max( [(al+1), self.population_max] )
		pm = self.population_max
		self.g_size = max([1, int(pm/al)])
		return 1



	def switch_show(self, more = False):
		if more:
			print("The 'show' command can be used to watch the game played out step-by-step.")
			print("When 'show' is on, the agents repertoires will be printed at each step.")
			print("The shell will also print the current mean centers i.e. convention prototypes at each step.")
			self.show = int(input("Enter '1' to turn show on or '0' to turn it off."))
		else:
			self.show = not self.show
			print("show each step:", self.show)
		return 1
			


	def set_protos(self, more = False, get = None):
		'''Overwrite base convention with a list of IPA prototypical vowels. '''
		c = self.convention
		if more:
			print("The ancestor group starts off the game with a set of similar vowel 'prototypes.'")
			print("These vowels are used in words to communicate with children in the population.")
			print("The available prototypes have key names. Here's the full list:")
			p = [print("\t", k) for k in c.ipa_dict.keys()]
		self.base = c.enter_protos()
		#self.base = ", ".join(c.base_proto_dict.keys())
		c.strap_protos(self.g_size)
		return 1



	def set_margin(self, more = False, get = None):
		'''Overwrite default perception margin for Agents'''
		if more:
			print("Agents use a perceptual margin to find matches to incoming signals in their repertoires.")
			print("The perceptual margin is measured in Equivalent Rectangular Bandwidth units (ERB) and represents a euclidian distance in the vowel space.")
			print("The margin can be a float between 0 and 11.0")
			print("When the margin is lower (below 1.5), agents learn more nearly perfectly.")
		if not get:
			perc = input("Agent starting perception tolerance: ")
			if not perc:
				print("Canceled.")
				return 1
		else:
			perc = eval(get)
		perc = float(perc)
		#Not sure whether this should have an upper limit or not...
		#for now, set to 11 ERB
		while (perc < 0 or perc > 11):
			perc = float(input("Try a number between 0 and 11: "))
		#print("Previewing average perception/proximity margins. Click in the window to close it.")
		self.perception = perc
		prox = self.prox
		if prox < 0:
			prox = 0
		#self.convention.draw_proto_margins(perc, prox)
		return 1



	def switch_length_flag(self, more = False, get = None):
		'''Change whether Agents view length as contrastive.'''
		if more:
			print("The agent's 'length flag' determines whether the agent discriminates between short and long vowels.")
			print("If the flag is set to 'True', agents will not match long vowels with short ones and vice versa.")
			print("Enter '1' to set the length flag to True or '0' to set it to False.")
			self.length_flag = int(input("Length flag: "))
		if not get:
			self.length_flag = not self.length_flag
			print("Length flag: ", self.length_flag)
		else:
			self.length_flag = eval(get)
		return 1
	


	def activate_protos(self):
		''' used by trigger command
			Introduces a new vowel to the population
			Description: a 'phantom agent' passes through the community,
			dropping a foreign word wherever it goes (i.e. everyone hears it).
			The agent disappears but the new word remains and may cause new conflicts. 
		'''
		A = Agent.Agent
		c = self.convention
		pd = self.convention.base_proto_dict
		actives = pd.keys()
		print(actives)
		inactives = [p for p in c.ipa_dict.keys() if p not in actives]
		print(inactives)
		p_list = input("Prototypes to add to convention: ")
		c.activate(p_list, 1)
		P = Prototype.Prototype
		
		if not self.population:
			print("error strapping adults in activate_protos")
			return
		age = int(self.age_limit)
		
		protos = pd.values()
		prox = self.prox
		perc = self.perception*.1
		prod = self.phone_radius
		noise = self.noise
		lf = self.length_flag
		ap = self.adapt_perc
		gp = self.get_prestige
		phantom_agents = [A(0, 0, perc, prox, prod, noise, lf, ap, gp())]
		self.population.insert(0, phantom_agents)
		vocab = c.lexicon
		a = phantom_agents[0]
		gbm = a.guess_by_margin
		a.age = age
		for (word, w) in vocab.items():
			p = w.percept
			ap = gbm(p)
			a.repertoire.append(ap)
			a.idio[word] = Word.Word(w.onset, w.nucles, w.coda, ap)
		print("Exposing population to new word . . .")
		self.diffuse()
		self.population.pop(0)
		self.find_prototypes()
		self.final_report()
		c.close_win()
		print("Make any other changes and then use 'extend' to continue simulation.")
		return 1



	def set_prox(self, more = False, get = None):
		'''Overwrite default proximity add-on.'''
		avg_prox = ((self.lex_size/len(self.base.split(" ")))/self.lex_size)
		if more:
			print("When agent's vowels move within a proximity margin of each other, a conflict ensues.")
			print("With the current parameters, the average proximity margin will be", avg_prox, "ERB.")
			print("You can enter a float which will supplement this margin,")
			print("e.g. using '1.0' will result in an average proximity margin of", avg_prox + 1.0)
			print("Using '0' will leave it at", avg_prox)
		if not get:
			prox = input("proximity margin supplement: ")
			if not prox:
				print("canceled.")
				return 1
		else:
			prox = eval(get)
		self.prox = float(prox)
		avg_prox += self.prox
		if avg_prox < 0:
			avg_prox = 0
		print("Avg proximity margin will be", avg_prox)
		return 1
		


	def demo_mode(self):
		'''
		Prompt user to set up the simulation
		one parameter at a time.
		'''
		more = True
		print("This simulation has several adjustable parameters. Let's walk through them.")
		print("There will be a short description for each parameter, and then a prompt where you can enter a value.")
		
		print("\nMARGIN")
		self.set_margin(more)
		print("\nPROXIMITY MARGIN")
		self.set_prox(more)
		print("\nPHONE RADIUS")
		self.set_phone_radius(more)
		print("\nVOWEL NOISE")
		self.set_prod_noise(more)
		print("\nBASE PROTOTYPES")
		self.use_lang(more)
		print("\nLIFESPAN")
		self.set_lifespan(more)
		print("\nPOPULATION LIMIT")
		self.set_size(more)
		print("\nCYCLES")
		self.set_cycles(more)
		print("\nCOLOR MODE")
		self.color_sampling(more)
		print("\nSAMPLING METHOD")
		self.set_sampling_method(more)
		print("\nAll done! A window will (eventually) appear with the results.")
		self.game_driver()
		print("\nWasn't that fun. You can now start the prompt process all over with 'demo'")
		print("or restart the current game with 'run' \nor let this one continue for another set of cycles with 'extend'.")
		return 2



	def set_lex_size(self, more = False, get = None):
		if not get:
			ls = int(input("Lexicon size (e.g. 50):"))
		else:
			ls = eval(get)
		self.lex_size = ls
		self.convention = Convention.Convention(self.show, self.color_on, self.lex_size)  #Convention tracks the prototypes
		self.convention.str_to_protos(self.base)#Convention reads in a string and splits into keys
		return 1
	


	def set_prod_noise(self, more = False, get = None):
		if not get:
			pn = float(input("phone_radius noise margin in ERB (e.g. .25):"))
		else:
			pn = eval(get)
		self.phone_radius_noise = pn
		return 1



	def set_phone_radius(self, more = False, get = None):
		if not get:
			p = float(input("Imitation margin in ERB (e.g. .25):"))
		else:
			p = eval(get)
		self.phone_radius = p
		return 1
		

	
	def set_adapt(self, more = False, get = None):
		'''
		Adjust the amount by which agents alter perception
		according to self-administered feedback.
		'''
		if not get:
			ad = float(input("Perception adjustment amount (e.g. .1):"))
		else:
			ad = eval(get)
		self.adapt_perc = ad
		return 1
	


	def use_lang(self, more = False, get = None):
		'''
		Overwrite base convention with one of the presets listed in this file. 
		'''
		if not get:
			print("Pre-set languages:")
			for n in self.languages.keys():
			   print(" "+n)
			lang_name = input("Enter the name of the language set you want to use: ").lower()
		else:
			lang_name = get
		lang_name.replace(" ", "")
		while lang_name not in self.languages:
				lang = lang_name
				del lang_name
				lang_name = input(lang+" not reconized. Use one of these: "+"\n ".join([l for l in self.languages.keys()]).lower()+"\nlanguage: ")
		c = self.convention
		self.lang_fn = lang_name
		language = self.languages[lang_name]
		self.base = language
		c.str_to_protos(language)
		c.strap_protos()
		avg_prox = ((self.lex_size/len(self.base.split(" ")))/self.lex_size)
		avg_prox += self.prox
		if avg_prox < 0:
			avg_prox = 0
		print(lang_name, "prototypes are ["+language+"]")
		print("Previewing language preset '"+lang_name+"' with average perception/proximity margins.")
		print("Click in the window to close it.")

		if self.use_ipa_symbols:
			self.convention.plot_symbols()
		else:
			self.convention.draw_proto_margins(self.perception, self.prox, True)	
		self.convention.close_win()

		return 1



	def switch_ipa_symbols(self, more = False):
		'''
		Switch IPA symbol display on/off.
		If IPA symbols are off, protos will be displayed with spots
		and the names will use the strings defined in the Convention class
		'''
		
		if more:
			print("Protos can be drawn in color-coded spots, gray spots, or colored IPA symbols.")
		self.use_ipa_symbols = not self.use_ipa_symbols
		
		if self.use_ipa_symbols:
			print("IPA symbols turned on.")
			self.convention.plot = self.convention.plot_symbols
		else:
			print("IPA symbols turned off.")
			self.convention.plot = self.convention.plot_spots
		self.convention.plot()
		self.convention.close_win()
		return 1



	def color_sampling(self, more = False):
		'''Switch color-coded graphics on/off'''
		if more:
			print("The vowels shown at each step can be color-coded so that they are distinguishable.")
			self.color_on = int(input("Enter 1 to turn on color-coding or 0 to turn it off:"))
		else:
			self.color_on = not self.color_on
		return 1



	def set_contact_agents(self, more = False, get = None):
		if more:
			print("At every step, all babies and children listen to the complete vocabularies of a number of family member agents")
			print("and partial vocabularies of randomly selected agents.")
		if not get:
			ca = int(input("Enter an upper limit on how many random agents a child hears at each step:"))
		else:
			ca = eval(get)
		self.contact_agents = ca
		return 1



	def set_contact_words(self, more = False, get = None):
		if more:
			print("At every step, listeners hear partial vocabularies from randomly selected agents.")
		if not get:
			cw = int(input("Enter an upper limit on the number of words children hear from random agents (per step):"))
		else:
			cw = eval(get)
		self.contact_words = cw
		return 1



	def get_language_charts(self):
		'''
		Calls up each language and displays it
		with default margins drawn.
		Click each window to advance.
		'''
		ls = [l for l in self.languages.keys()]
		for l in ls:
			self.use_lang(False, l)
		return self.use_lang()

	

	def set_fam_size(self, more = False, get = None):
		if more:
			print("Agents are assigned a number of permanent family member agents at birth.")
			print("At every step, listeners hear the complete vocabularies of each family member.")
		if not get:
			fs = int(input("Enter a number of family members to be assigned each agent at birth (max {0}):".format(self.anc_group_size)))
		else:
			fs = eval(get)
		self.fam_size = min([fs, (self.anc_group_size)])
		return 1



	def set_sampling_method(self, more = False, get = None):
		'''
		
		'''
	
		sample_methods = {'phones': self.percept_sampling,
						  'vowels': self.vowel_sampling}
		proto_methods = {'phones': self.percept_protos,
						 'vowels': self.vowel_protos}
		
		if more:
			print("Agents have internal percepts and temporary vowels.")
			print("You can change the sampling method to choose which of these is used to represent the convention.")
			co = [option for option in sample_methods.keys()]
			print("Current options:", co)
		if not get:
			sm = input("Enter the method you want to use:")
		else:
			sm = get

		while sm not in sample_methods:
			del sm
			print("Sorry, the word has to match one of these:", sample_methods.keys())
			sm = input("Try again:")
					   
		self.sample_report = sample_methods[sm]
		self.find_prototypes = proto_methods[sm]
		if self.curr_cycle:
			self.find_prototypes()
		return 1

	

	def switch_micro(self, more = False):
		'''
		Track the activity of a single agent in the shell and graphic window
		'''
		if more:
			print("Viewing in 'micro' mode will highlight a single agent's vowels on the chart.")
			print("A single (random) agent's vowels will be outlined in black until it reaches adulthood.")
			print("When that agent matures, a new (random) agent will be selected.")
			print("The agent's activities will also be printed in place of the community step reports.")
		self.micro = not self.micro
		print("Micro mode", self.micro)
		return 1

#################################
#								#
# PHONOLOGY THEORY-SWAPPING		#
#								#
#################################

	def golston_presets(self):
		'''
		Modified generative phonology.
		Babies have perfect internal representations:
		word vowel percepts are identical to what they hear,
		and update according to conflict resolution.
		Adults have imperfect phonological representations:
		word vowel protos are "noisy" every time they are uttered.
		Children have very good recognition:
		they become as precise as necessary to learn their language.
		'''
		
		self.perception = .6 #recognition precision
		self.phone_radius = 0 #internal representation noise
		self.phone_radius_noise = .3 #phonetic representation noise
		self.prox = 1.2	  #vowel sensitivity
		self.adapt_perc = .01	 #adjustment to perception from feedback
		self.fam_size = 2
		self.summ_presets()
		return 1



	def labov_presets(self):
		'''
		Socially mediated implementation of sound change
		
		Agents rate each other with levels of 'prestige'
		
		'''
		self.perception = 1.0 #recognition precision
		self.phone_radius = 1.0 #internal representation noise
		self.phone_radius_noise = .75 #phonetic representation noise
		self.prox = -1	 #vowel sensitivity
		self.adapt_perc = 0	   #adjustment to perception from feedback
		self.fam_size = 0
		self.social = 4		#number of prestige ranking levels
		
		self.summ_presets()
		return 1

	

	def exemplar_presets(self):
		'''
		Agents store a memory bank of perceived tokens;
		percepts are the most current average of all stored exemplars.
		Agents don't have repertoires and don't match vowels.
		They just store everything and produce the average when speaking.
		'''
		
		return 1

	

	def wedel_presets(self):
		'''
		Functional load determined by minimal pairs.
		Words are combinations of onset+nucleus+coda,
		instead of vowels with word ID tags
		'''
		
		return 1

	

	def sapir_presets(self):
		'''
		Morphophonemic Approach.
		Contrastive to 'Chomsky' presets.
		Nullify the percept level
		'''
		self.perception = 0	  #recognition precision
		self.phone_radius = 0	#internal representation noise
		self.phone_radius_noise = 0 #phonetic representation noise
		self.prox = 0	   #vowel sensitivity
		self.adapt_perc = 0	   #adjustment to perception from feedback
		self.fam_size = 0
		self.social = 0		#number of prestige ranking levels
		
		self.summ_presets()
		return 1

	

	def chomsky_presets(self):
		'''
		Pure generative phonology;
		Contrasting approach to 'Sapir' mode.
		'''
		self.perception = 1.0	#recognition precision
		self.phone_radius = 1.0	  #internal representation noise
		self.phone_radius_noise = 0 #phonetic representation noise
		self.prox = -1	 #vowel sensitivity
		self.adapt_perc = 0	   #adjustment to perception from feedback
		self.fam_size = 4
		self.social = 0		#number of prestige ranking levels
		
		self.summ_presets()
		return 1

#######################
# DIY PRESET TEMPLATE #
#######################

	def my_presets(self):
		'''
		Go nuts!
		
		'''
		self.perception = 0	  #recognition precision
		self.phone_radius = 0	#internal representation noise
		self.phone_radius_noise = 0 #phonetic representation noise
		self.prox = 0	#vowel sensitivity
		self.adapt_perc = 0	   #adjustment to perception from feedback
		self.fam_size = 0
		self.social = 0		#number of prestige ranking levels

		self.summ_presets()
		print("If all of these are zero, change the values in the my_presets method")

		return 1

	

	def set_paradigm(self, more = False, get = None):
		'''
		Use a set of parameters designed to model a specific position.
		None of these have been approved by anyone; the names are temporary
		and solely for the convenience of the developer,
		who is still trying to get her facts straight. 
		'''
		paradigms = {
			'golston': self.golston_presets,
			#'labov': self.labov_presets,
			#'wedel': self.wedel_presets,
			'custom': self.my_presets,
			'sapir': self.sapir_presets,
			'chomsky': self.chomsky_presets
			}
		
		if not get:
			print(paradigms.keys())
			para = input("Paradigm:")
		else:
			para = get
			
		while para not in paradigms:
			para_corr = para
			del para
			para = input("Paradigm:")
		print("Using preset:", para)
		return paradigms[para]()

	

	def summ_presets(self):
		bp = self.perception
		prod = self.phone_radius
		pn = self.phone_radius_noise
		prox = self.prox
		ap = self.adapt_perc
		fs = self.fam_size
		print( "Base Perception\t= {0}\tphone_radius\t= {1}".format(bp, prod) )
		print( "Prod. Noise\t= {0}\tProx Addon\t= {1}".format(pn, prox) )
		print( "Perception Adj.\t= {0}\tFam. Size\t= {1}".format(ap, fs) )
		return 1
		
		
#############################
#		CONTROL METHODS		#
#############################

	def game_driver(self, reset = True):
		'''runs the simulation by calling the menu. '''
		print(ctime())
		
		self.strap_game(reset)
		self.summarize_param()
		cc = self.curr_cycle
		nc = self.num_cycles
		pm = self.population_max
		al = self.age_limit
		if reset:
			self.cycle_lim = self.num_cycles
		else:
			self.cycle_lim += self.num_cycles
			
		if self.show:
			self.init_report()
		while (self.curr_cycle < self.cycle_lim and pm > al): #note: cycle is incremented by charon fn
			self.step()
		if self.show:
			self.final_report()
		conv = self.convention

		print(ctime())
		print(self.total_interactions, "interactions performed.")
		mcp = self.min_carrier_p
		mc = (self.total_agents * mcp)
		p_list = [k.name for k in conv.proto_dict.values() if k.carriers > mc]
		#print("Resulting convention:", (", ".join(p_list)))

		self.displacement_report()
		self.shifting_report()
#		 self.count_near_splits()
		if reset:
			self.micro_agent = None
		return 2

	

	def game_extender(self):
		'''game continues on for self.num_cycles'''
		return self.game_driver(False)

	

	def stop(self):
		'''Just exits the program. Not really needed.'''
		return 0



	def save_sim(self, cf = None):
		'''
		saves the final displacement report as an eps,
			  the most recent sampling as an eps,
			  and a text report as a txt
		if no prefix is entered, it will name the file
		 using the language preset used. 
		'''
#
		if not cf:
			cf = self.lang_fn
		self.displacement_report(cf)
		self.redraw_last(cf)
		self.write_report(cf)
		return 1


	def write_images(self, cust_fn = None):
		self.displacement_report(cust_fn)
		self.redraw_last(cust_fn)

		

	def write_report(self, lang = None):
		'''prints a table with the current settings'''
		c = self.convention
		sl = []
		sol = sl.append
		
		s0 = "CURRENT GAME PARAMETERS"
		sol(s0)
		
		nc = str(self.num_cycles)
		pl = str(self.population_max)
		al = str(self.age_limit)
		ss = str(self.show)
		pm = str(self.perception)
		lf = str(self.length_flag)
		ls = str(self.lex_size)
		prox = str(self.prox)
		ca = self.contact_agents
		cw = self.contact_words
		vn = str(self.phone_radius_noise)
		phn = str(self.phone_radius)
		fs	= self.fam_size

		s1 = "| {0:^7} | {1:^12} | {2:^10} | {3:^16} | {4:10} | ".format("SHOW", "CYCLES", "POPUL. MAX", "LIFESPAN", "LEX. SIZE")
		sol(s1)
		
		s2 = "{0:^14} {1:^11} {2:^15} {3:^16} {4:^13}".format(ss, nc, pl, al, ls)
		sol(s2)

		s3 = "| {0:^3} | {1:^6} | {2:^11} | {3:^4} | {4:^11} | {5:^5} | {6:5} |".format("FAM", "FRIENDS", "WORDS/FRIEND", "PERC", "PROX SUPP", "PHONE", "VOWEL")
		sol(s3)

		s4 = "{0:^8}{1:^9}{2:^15}{3:^7} \t {4:^.6} \t\t {5:^.4} \t {6:^.4}".format(fs, ca, cw, pm, prox, vn, phn)			 
		sol(s4)

		s5 = "BASE CONVENTION\n"+self.base+"\n"
		sol(s5)

		if lang:
			fn = self.file_name(lang)+".txt"
		else:
			fn = ctime().replace(" ", "_")+".txt"
			fn = fn.replace(":", "")
		print("Saving to file", fn)
		f = open(fn, "w")
		s_label = "\n".join(sl)
		self.str_buf.insert(0, s_label)
		out = "\n".join(self.str_buf)
		f.write(out)
		f.close()
		return 1



#########################
#	GLOBAL METHODS		#
#########################

def start_game(show = True):
		'''initialize a new game with default values'''
		default_game = Game_fns()
		default_game.show = show
		default_game.game_driver()

		

def settings_dict(game):
	cmds = {'run': game.game_driver,		 #new game
			'stop': game.stop,				 #exits simulation
			'cycles': game.set_cycles,		 #max cycles
			'size': game.set_size,			 #population limit
			'lifespan': game.set_lifespan,	 #number of steps in each agent's lifespan
			'show': game.switch_show,		 #shows outcomes for each step
			'protos': game.set_protos,		 #change base convention
			'margin': game.set_margin,		 #base perception (for babies)
			'?': menu_help,					 #explains what the commands do
			'length': game.switch_length_flag, #Agents see length as contrastive
			'demo': game.demo_mode,			 #prompt for each parameter
			'prox': game.set_prox,			 #adjust prox supplement
			'color': game.color_sampling,	 #vowels plotted in color
			'colour': game.color_sampling,
			'language': game.use_lang,		 #use a preset for base convention
			'draw margins': game.draw_proto_margins, #draw the average perception/prox margins 
			'profile': show_profile,
			'lex': game.set_lex_size,
			'languages': game.get_language_charts,
			'contacts': game.set_contact_agents,
			'words': game.set_contact_words,
			'family': game.set_fam_size,
			'micro': game.switch_micro,
			'paradigm': game.set_paradigm,
			'adapt': game.set_adapt,
			'noise': game.set_prod_noise,
			'sampling': game.set_sampling_method,
			'phone': game.set_phone_radius,
			'archive': build_archive,
			'parchive': param_archive,
			'symbols': game.switch_ipa_symbols
			}
	return cmds



def menu():
	'''User interface.'''
	game = Game_fns()
	game.print_param()
	adj_li = ['cycles', 'size', 'show', 'margin', 'language', 'prox', 'lifespan', 'phone', 'noise', 'protos', 'sampling']
	ctrl_li = ['run', 'stop', 'extend', 'details', 'report', 'save', 'draw margins', 'symbols']
	help_li = ['?', 'demo']
	
	options = settings_dict(game)
	
	run = 1

	while run:
		print("ADJUSTMENTS")
		print_opts(adj_li)
		print("MAIN")
		print_opts([c for c in ctrl_li if c in options])
		print("HELP")
		print_opts(help_li)
		cl = input("command: ").lower() #might be a list
		command, arg = get_cmd(options.keys(), cl)
		if arg:
			run = options[command](False, arg)
		else:
			run = options[command]()
		if run is 2:				#add options if there is an ongoing game
			options["extend"] = game.game_extender		
			options["trigger"] = game.activate_protos	
			options["details"] = game.print_all_reps
			options["report"] = game.lexicon_report
			options["draw"] = game.displacement_report
			options["draw last"] = game.redraw_last
			options["save"] = game.save_sim

			
			
def ret_0(): return 0



def print_opts(li):
	'''menu display formatting'''
	cols = 7
	rows = int(len(li)/cols)
	i = 0
	while i < len(li):
		c = 0
		print(" ", end = "")
		while (c < cols and i < len(li)):
			print("-{0:10}".format(li[i]), end="")
			c += 1
			i += 1
		print("")

		
	
def get_cmd(opts, c):
	'''simple error-handler'''
	cond_li = c.split("=")
	if len(cond_li) > 1:
		cmnd = cond_li[0].replace(" ", "")
		arg = cond_li[1].replace(" ", "")
	else:
		cmnd = c
		arg = None
	while cmnd not in opts:
		cmnd = input("invalid command. Try again: ")
	return (cmnd, arg)



def menu_help():
	'''command descriptions'''
	print("run: starts a new game with current settings.")
	print("cycles: set the number of agent groups tracked over lifespan.")
	print("size: set the population peak limit.")
	print("lifespan: set the age at which agents are removed from population.")
	print("show: shows results of each step (agent's reps, Prototype positions.")
	print("protos: specify the Prototypes in the base convention.")
	print("margin: set the base perception tolerance margin for agents.")
	print("extend: continue running the current game for another set of cycles.")
	#print("trigger: introduce a non-native vowel to the convention.")
	print("stop: end game")
	print("report: prints a table with current stats from the game.")
	print("prox: reduce or increase the proximity margin to trigger vowel conflicts.")
	print("demo: set up a new game with prompting")
	print("draw: draws the shifted prototypes")
	print("color: vowels are color-coded in chart")
	print("language: use one of the language presets")
	print("draw margins: show the base convention with perception and proximity margins.")
	print("draw last: open a window showing the most recent sampling of population vowels.")
	print("save: save a summary of the output to a text file.")
	print("contacts: set the limit on how many random agents a listener hears from per step.")
	print("words: set a limit on how many words listeners hear from each random agent per step.")
	print("lex: set the size of the lexicon (number of words divided by number of vowels.")
	print("charts: view the configured language presets.")
	print("family: set the number of family members assigned to each agent")
	print("sampling: use either 'phones' or 'vowels' for representing the speech community")
	return 1
	


def show_profile():
		'''runs profile() on a game with default parameters.
		For testing purposes (complexity, identifying bottlenecks)
		Increases total runtime significantly; suggest using fewer agents'''
		profile.run('start_game(False)')
		return 0



def build_archive(l = None):
	'''
	Use to test different parameters on the same language
	Saves eps and txt files documenting semi-automated simulations.
	
	Call from the menu by command "archive"
	'''
	if not l:
		lang = input("Enter Language: ")
	cycle_inc = 1	#CYCLE INCREMENT: NUMBER OF CYCLES BETWEEN IMAGE CAPTURES
	total_cc = 100 #TOTAL NUMBER OF CYCLES (will be divided by num_cycles for loop)
	if cycle_inc > total_cc:
		print("cycle increment > total cycles!")

	g = Game_fns()
	perc0 = g.perception #default
	#perc_i = .75 #increment
	prox0 = g.prox #default
	#prox_i = .3 #inc
	phone0 = g.phone_radius #default
	#phone_i = .5 #inc
	v0 = g.phone_radius_noise #default
	#v_i = .5 #inc
	fam0 = g.fam_size #default
	#fam_i = 1 #inc
	friends0 = g.contact_agents #default
	#friends_i = 15 #inc

	pop_lim = 300
	
	# ("margin", perc_i), ("prox", prox_i), ("phone", phone_i), ("noise", v_i), ("family", fam_i), ("contacts", friends_i)
	params = [("margin", perc0)] #, ("prox", prox_i), ("phone", phone_i), ("noise", v_i), ("family", fam_i), ("contacts", friends_i)] 
	
	print(ctime(), "-- Archiving results.")

		
	for i in range(len(params)):
		cmd, adj = params[i]
		if cmd == "margin":
			r = range(1, 2)
		else:
			r = range(3)
		for j in r:
			g.show = False
			conv = g.convention
			g.set_size(False, str(pop_lim))
			g.base = g.languages[lang]

			g.perception = perc0
			g.prox = prox0
			g.phone_radius = phone0
			g.phone_radius_noise = v0
			g.fam_size = fam0
			g.contact_agents = friends0
			
			options = settings_dict(g)
			options[cmd](False, str(adj*j) ) #set the game parameter to j * adjustment
			fs = str(g.fam_size)
			cs = str(g.contact_agents)
			conv.str_to_protos(g.base)
			conv.strap_protos()
		
			g.strap_game(True)
			g.summarize_param()
			
			pm = g.population_max
			al = g.age_limit
			g.draw_proto_margins(lang)
		
			print(ctime(), " -- Running", total_cc, "cycles total in", cycle_inc, "cycle increments using preset convention", lang)
			while g.curr_cycle < total_cc:
				inc_counter = g.curr_cycle + cycle_inc
				gcc = g.curr_cycle
				while gcc < inc_counter: 
					g.step()
					gcc = g.curr_cycle
				g.set_sampling_method(0, "phones")
				g.shifting_report()
				g.write_images(lang+"P")
				g.set_sampling_method(0, "vowels")
				g.write_images(lang+"v")
			
			print("Finished", total_cc, "on", params, "at", ctime())
			print(g.total_interactions, "interactions performed.")
			g.count_word_vowels(0)
			
			g.write_report(lang)
	print("Finished all combinations --", ctime())
	return 2
	


def param_archive():
	'''
	Use to test the same parameters on multiple languages
	Saves eps and txt files documenting semi-automated simulations.
	Uses the default parameters in game_fns for perception, prox, etc.
	
	Call from the menu by command "parchive"
	'''
	#Done with 1.0, .5, .25, .25, 300, 4-50-100: english, spanish, russian
	# .5, 1.0, .25, .25, 300, 4-50-100: italian, german, dutch
	# .75, .75, .5, .5 4-50-100: ancientgreek
	# .75, .5, .25, .25, 4-50-100: albanian, (japanese)
	# .5, .5, .1, .1, 4-50-100: swedish
	
	lang_li = ["swedish"] #LANGUAGE PRESETS TO SIMULATE, IN ORDER
	
	print(ctime(), "-- Archiving results for", lang_li)
	for lang in lang_li:
		g = Game_fns()
		g.show = False
		conv = g.convention

		g.base = g.languages[lang]
		conv.str_to_protos(g.base)
		conv.strap_protos()
		
		g.strap_game(True)
		g.summarize_param()
		
		cycle_inc = 5	#CYCLE INCREMENT: NUMBER OF CYCLES BETWEEN IMAGE CAPTURES
		total_cc = 100 #TOTAL NUMBER OF CYCLES (will be divided by num_cycles for loop)
		if cycle_inc > total_cc:
			print("cycle increment > total cycles!")
		
		pm = g.population_max
		al = g.age_limit
		g.draw_proto_margins(lang)
	
		print(ctime(), " -- Running", total_cc, "cycles total in", cycle_inc, "cycle increments using preset convention", lang)
		while g.curr_cycle < total_cc:
			inc_counter = g.curr_cycle + cycle_inc
			gcc = g.curr_cycle
			while gcc < inc_counter: 
				g.step()
				gcc = g.curr_cycle
			g.shifting_report()
			g.write_images(lang)
		
		print("Finished", total_cc, "on", lang, "at", ctime())
		print(g.total_interactions, "interactions performed.")
		g.count_word_vowels(0)
		
		g.write_report(lang)
	print("Finished all languages --", ctime())
	return 2
		
menu()

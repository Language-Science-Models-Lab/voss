'''
Vowel Evolution program Phonology class.
Run in PYTHON 3(!)
with Vowel, Game_fns, Prototype, Word, Agent, Convention, graphics files in same directory

import time, random, re from Python library
Last update July 2016 HJMS


This module can also be used as an alternate driver to Game_fns,
intended for use in experimenting with articulatory constraints,
and other phonetics-phonology interface mechanics.
It does not run a population simulation;
instead, it provides a set of methods which call the same modules.

SYLLABLES       
    Using a grammary organization to represent syllables
    Syllable => onset + nucleus + coda
    Onset => (consonant | null)
    Nucleus => (vowel + vowel) | (vowel + null) | (null + vowel)
    Coda => (consonant | null)
    consonant =>  (coronal | labial | dorsal | laryngeal) + (voiced | voiceless)
    vowel => (high | mid | low) + (front | central | back) + (round | unround)Variables = {

    A "long" vowel is vowel+vowel where both vowels have same formants.
    A "diphthong" is a vowel+vowel where the vowels have different formants.
    We are forbidding vowels in onsets or codas. 
'''

import Agent, Convention
from time import ctime
from graphics import *
import re
from random import sample, choice, uniform, randint

max_e1 = Agent.e1_max()
min_e1 = Agent.e1_min()
max_e2 = Agent.e2_max()
min_e2 = Agent.e2_min()

class Phonology:

    def __init__(self, features = None):
        self.set_features(features)

    def set_features(self, fl=None):
                                                
        self.articulations = {"null": self.null,
                              "stop": self.stop,
                              "nasal": self.nasal,
                              "rhotic": self.rhotic,
                              "labial": self.labial,
                              "rounded": self.rounded,  #round is a reserved word in Python
                              "coronal": self.coronal,
                              "lateral": self.lateral,
                              "strident": self.strident,
                              "laryngeal": self.laryngeal,
                              "fricative": self.fricative,
                              "posterior": self.posterior,
                              "laminal": self.laminal,
                              "dorsal": self.dorsal,
                              "front": self.front,
                              "high": self.high,
                              "low": self.low,
                              "voiced": self.voiced,
                              "voiceless": self.voiceless,
                              "retracted": self.retracted,
                              "spread": self.spread_glottis,
                              "constricted": self.constricted_glottis,
                              
                              }
        
        arts = self.articulations
        self.features = fl

    def null(self, syll, pos, assim):
        o, n, c = syll
        
        return n
                  
    def lateral(self, syll, pos, assim):
        o, n, c = syll
        
        return n

    def rhotic(self, syll, pos,  assim):
        o, n, c = syll
        
        return n
    
    def fricative(self, syll, pos, assim):
        o, n, c = syll
        
        return n

    def stop(self, syll, pos, assim):
        o, n, c = syll
        
        amount = randint(0, 50) #up to 50 ms
        
        if pos is 2: #stop is in the coda
            if assim:
                n.length -= amount #reduce length
            else:
                n.length += amount
        return n

    def strident(self, syll, pos, assim):
        o, n, c = syll
        
        return n

    def nasal(self, syll, pos, assim):
        o, n, c = syll
        
        return n

    def laryngeal(self, syll, pos, assim):
        o, n, c = syll
        
        return n

    def labial(self, syll, pos, assim):
        o, n, c = syll

        amount = uniform(1.0, 1.5)
                         
        if assim:
            ne1 = n.e1 - amount
            ne2 = n.e2 - amount
            
            if ne1 > min_e1:
                n.e1 = ne1
            if (ne2 > min_e2 and ne2 > n.e1):
                n.e2 = ne2
        else:
            ne1 = n.e1 + amount
            ne2 = n.e2 + amount

            if (ne1 < max_e1 and ne1 < n.e2):
                n.e1 = ne1
            if ne2 < max_e2:
                n.e2 = ne2
                
        return n

    def rounded(self, syll, pos, assim):
        o, n, c = syll
        amount = uniform(.75, 1.25) #effective range [200, 400] hz
        
        if assim:
            ne2 = n.e2 - amount
            if (ne2 > min_e2 and ne2 > n.e1):
                n.e2 = ne2
        else:
            ne2 = n.e2 + amount
            if ne2 < max_e2:
                n.e2 = ne2
                
        return n
    
    def coronal(self, syll, pos, assim):
        o, n, c = syll
        
        return n

    def posterior(self, syll, pos, assim):
        o, n, c = syll
        return n
    
    def laminal(self, syll, pos, assim):
        o, n, c = syll
        
        return n
    
    def dorsal(self, syll, pos, assim):
        o, n, c = syll
        amount = uniform(.1, .75)
        
        if assim:
            ne1 = n.e1 - amount
            if ne1 > min_e1:
                n.e1 = ne1
        else:
            ne1 = n.e1 + amount
            if (ne1 < max_e1 and ne1 < n.e2):
                n.e1 = ne1
        return n
    
    def front(self, syll, pos, assim):
        o, n, c = syll

        amount = uniform(.25, 1.0)

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
        amount = uniform(.1, .5)

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

        amount = uniform(.1, .5)

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
        
        return n

    def voiceless(self, syll, pos, assim):
        o, n, c = syll
        return n
    
    def spread_glottis(self, syll, pos, assim):
        o, n, c = syll
        
        return n
    
    def constricted_glottis(self, syll, pos, assim):
        o, n, c = syll
        
        return n

##################
#Testing Methods #
##################

def make_child():
    #####################################################
    #           CHANGE THE AGENT PARAMS HERE            #   
    #####################################################
    perc = .25    #perception margin (matching radius distance)
    prox = 1.5    #proximity margin (conflict trigger radius distance)
    prod = .5    #production (imitation / internal representation radius distance)
    noise = 0   #utterance noise -- radius to limit randomly generated spoken voel
    lf = True   #length flag (distinguish length, or not)
    adapt = 0   #feedback adjustment to margins
    prest = 0   #social prestige
    age_adult = 2 #age at which children stop learning
    
    ####################################################
    A = Agent.Agent
    child = A(0, 0, perc, prox, prod, noise, lf, adapt, prest)
    child.age = 1
        
    return child


def make_convention():
    ###########################
    # CHANGE THE VOWELS HERE  #
    ###########################
    lang = "i:, I, e:, epsilon, ae, u:, horseshoe, o:, open_o:, wedge, script_a"
    #need to add consonant inventory
    #create lexicon of combinations
    cur_dict = get_feature_dict()
    
    num_words = len(lang.split(","))+1
    c = Convention.Convention(True, True, num_words)
    c.str_to_protos(lang)
    c.strap_protos(0)
    
    return c

def perceive(agent, convention):
    for word in convention:
        res = agent.call_matchers(word) #use a different matching function which calls assimilate and dissimilate
    return


def articulations():
    p = Phonology()
    arts = [print(a) for a in p.articulations.keys()]

def get_feature_dict(language = "English"):
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
    name = language.lower()
    languages = {"english": english}

    return english()

def english():
    ##########################################################
    #                CHANGE CONSONANTS HERE                  #
    ##########################################################
    #Below is an example set. 
    matrix = {"t": ["coronal", "voiced"],   
              "p": ["labial", "voiced", "stop", "spread"],
              "g": ["dorsal", "voiced"],
              "h": ["laryngeal", "voiced", "fricative"],
              "s": ["coronal", "voiced", "fricative", "strident"],
              "d": ["coronal", "voiceless"],   
              "b": ["labial", "voiceless", "stop"],
              "k": ["dorsal", "voiceless"],
              "m": ["nasal", "labial"],
              "agma": ["laryngeal", "nasal"],
              "f": ["labial", "fricative", "voiced"],
              "v": ["labial", "fricative", "voiceless"],
              "theta": ["coronal", "voiceless", "fricative"],
              "eth": ["coronal", "voiced", "fricative"],
              "z": ["coronal", "voiceless", "fricative", "strident"],
              "esh": ["coronal", "voiceless", "fricative", "strident"],
              "ezh": ["coronal", "voiced", "fricative", "strident"],
              "-": ["null"]
              }
    if symbol in matrix:
        print(matrix[symbol])

    return matrix

def dum_v():
    from Vowel import Vowel
    e1 = uniform(min_e1, max_e1)
    e2 = uniform(min_e2, max_e2)
    length = randint(100, 300)
    name = "dummy"
    v = Vowel(e1, e2, length, name)
    return v

def test_symbol(symbol, assimilate = True, vowel = None):
    '''
    Apply the features of the symbol to the vowel.
    Assimilate indicates whether the changes are applied (coarticulated)
    or 'undone' / dissimilated
    If no vowel is provided, a random one will be created. 
    '''
    from Word import Word
    if not vowel:
        vowel = dum_v()

    fm = get_feature_dict()
    word = Word(symbol, vowel.name, "-", vowel) 
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
        print("Dissimilated vowel", pv)
    

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
    
    for i in range(iterations):
        perceive(child, c_words)
        sampling = [w.get_vowel() for w in child.idio.values()]
        conv.plot_sets(sampling, 1, "")

    conv.plot_sets(sampling, 0, "")
    child.print_vocab()
    #conv.plot(0, 0, "")
    conv.close_win()

def test_production(iterations=1):
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
    
    for i in range(iterations):
        sampling = []
        for w in child.idio.values():
            pv = child.get_vowel(w)
            sampling.append(pv)
            print(w, "with vowel formants", w.get_vowel())
            print("child's production:", pv)
        conv.plot_sets(sampling, 1, "")

    #conv.plot(0, 0, "")
    conv.close_win()

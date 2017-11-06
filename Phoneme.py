'''
Vowel evolution program consonant class.
Run in PYTHON 3(!)
with Vowel, Game_fns, Prototype, Word, Agent, Convention, graphics files in same directory

import time, random, re from Python library
Last update June 2016 HJMS

'''

def Phoneme:

    def __init__(self, features):
        self.set_features()
        for feat in self.features:
            feat = False
        
        fm = self.feature_matrix
        
        for f in features:
            if f in fm:
                fm[f] = True
            

    def set_features(self):
        self.features= [self.lateral,
                        self.rhotic,
                        self.fricative,
                        self.stop,
                        self.strident,
                        self.nasal,
                        self.labial,
                        self.round,
                        self.coronal,
                        self.posterior,
                        self.laminal,
                        self.dorsal,
                        self.front,
                        self.high,
                        self.low,
                        self.retracted,
                        self.voice,
                        self.spread_glottis,
                        self.constricted_glottis,
                        ]
                                                
        self.matrix = {"lateral": self.lateral,
                       "rhoict": self.rhotic,
                       "fricative": self.fricative,
                       "stop": self.stop,
                       "strident": self.strident,
                       "nasal": self.nasal,
                       "labial": self.labial,
                       "round": self.round,
                       "coronal": self.coronal,
                       "posterior": self.posterior,
                       "laminal": self.laminal,
                       "dorsal": self.dorsal,
                       "front": self.front,
                       "high": self.high,
                       "low": self.low,
                       "retracted": self.retracted,
                       "voice": self.voice,
                       "spread": self.spread_glottis,
                       "constricted": self.constricted_glottis
                       }
                  

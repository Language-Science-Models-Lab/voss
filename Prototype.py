'''Vowel evolution program.
Run with Vowel, Convention, Game_fns, Agent, Word
Import Vowel
Last update March 2016 HJMS'''

import Vowel

class Prototype(Vowel.Vowel):
    '''Prototype class *Vowel subclass*
    A Prototype indicates the average f1/f2 position, length of a vowel
    and the number of carriers (Agents)
    i.e. the conventional representation of a vowel for some population.
    Prototypes are formed by collecting Vowels from agents. '''
    
    def __init__(self, e1, e2, length, name):
        super(Prototype, self).__init__(e1, e2, length, name)
        self.carriers = 1     #some assumed agent not in population (so it's never 0)
        
    def __str__(self):
        '''shown as '(f1, f2, length, carriers)'
        NOTE: STR and REPR use HZ as INTS for first formant, second formant,
        where everything else is in ERB units as FLOATS'''
        f1, f2 = self.to_hz_praat(self.e1, self.e2)
        f1 = int(f1)
        f2 = "{:>4}".format(int(f2))
        l = int(self.length)
        s = "({0}, {1}, {2})".format(f1, f2, l)
        return s
    
    def __repr__(self):
        '''shown as 'f1_hz, f2_hz, length' '''
        e1 = self.e1
        e2 = self.e2
        repr_s = ", ".join( [ str(e1), str(e2), str(self.length)] )
        return '('+repr_s+')'
    
    def to_hz_praat(self, e1, e2):
        '''Traunmuller formula used in Praat software'''
        from math import exp
        d1 = exp ((e1 - 43.0) / 11.17)
        f1 = (14680*d1 - 312.0) / (1 - d1)

        d2 = exp ((e2 - 43.0) / 11.17)
        f2 = (14680*d2 - 312.0) / (1 - d2)
        return (f1, f2)

    def __eq__(self, other):
        matches = (self.e1 == other.e1 and
                   self.e2 == other.e2 and
                   self.length == other.length)
        return matches
    
    def update(self, ne1, ne2, nl, c):
        '''
        overwrite formant values (e.g. to update mean centers)
        '''
        self.e1 = ne1
        self.e2 = ne2
        self.length = nl
        self.carriers = c

    def __hash__(self):
        '''use e1 (float), e2 (float) and length (int)'''
        return hash((self.e1, self.e2, self.length))

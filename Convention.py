'''Vowel evolution program.
Run with Vowel, Prototype, Game_fns, Agent, Word
Also import time, random and graphics modules
Last update July 2017 HJMS'''

import Vowel, Prototype, time, random, Word, re, Agent, Segment
from graphics import *

class Convention:
    '''
    A convention is a set of prototypical vowels
    representing the collective repertoires of a population of speakers.
    The convention is like a model speaker, which may not exist.
    A convention is what linguists use to make a language tangible. 
    
    Prototypes are updated by averaging the Agents' vowels/phones for each word.
    This Convention class handles the representation (output) of the system,
    e.g. the vowel chart, mean centers, color-coding,
    and the IPA "master set" used to 'strap' the ancestor group. 
    '''
    
    def __init__(self, show = False, color_on = True, ls = 50):
        '''
        Can be initialized with no arguments.d
        show == True means more output e.g. step reports.
        color_on == True means vowels are color-coded,
         where the colors are static according to master set (IPA symbol names).
        ls is the minimum lexicon size,
         where the actual size is determined by the size of the convention
         (the number of prototypes active in the base set).
        '''
        self.show = show
        self.lf = True              #length flag (whether length is contrastive)
        self.win = False            #No window drawn yet (use to prevent multiples)
        self.color_on = color_on    
        self.color_list = []

        self.circles = []
        self.set_formant_limits()   #sets up the f1, f2 ranges
        self.base_vowel_dict = dict()   #vowels in base convention
        self.base_proto_dict = dict()   #doesn't change
        self.proto_dict = dict()        #live prototypes
        self.base_weights = dict()
        self.lexicon = dict()           #words
        self.lex_size = ls              #number of words in lexicon
        self.curr_proto_pts = []        #live graphic prototype points
        self.curr_sampling = []         #live graphic agent vowel points 
        self.updating_label = None      #center graphic label if no color chart
        self.proto_label = None         #live prototype graphic label
        self.color_key = False          #side key of proto-color map
        self.param_str = ""             #center label
        self.set_vowels()               #creates ipa_dict "master set"
        self.plot = self.plot_spots     #plot_symbols will use symbols instead
        self.func_load_max = 5


    def __str__(self):
        pl = self.proto_dict.values()
        if pl:
            ps = [str(p) for p in pl]
            s = ",".join(ps)
        else:
            s = "Empty Convention"
        return s
    


    def set_param_str(self, s):
        '''
        the current parameters e.g. perception
        '''
        self.param_str = s


        
    def reset(self, base):
        '''
        reset the prototypes to the IPA originals
        '''
        self.str_to_protos(base)    #for new games (not extensions)


        

    def enter_protos(self):         #user input of list prototypes
        '''
        prompt user for input
        initialize convention using a custom list of protos (i.e. not a preset)
        '''
        base = input("Base convention (e.g. i:, retracted_a, o, u): ") 
        self.str_to_protos(base)
        return base


    
    def str_to_protos(self, vs):    #instantiate base convention from String list
        '''Uses list of vowel names to create convention dictionary and Prototype list'''

        if not vs: #user enters nothing -- assume they don't want to change anything
            print("Convention overwrite canceled.")
            return
        
        P = Prototype.Prototype
        v_strlist = vs.split(", ")
        self.proto_dict = dict()
        self.base_proto_dict = dict()
        #base = self.base_proto_dict
        
        self.base_vowel_dict = dict()
        ipa = self.ipa_dict
        for v in v_strlist:
            #use regular expressions to get symbol name for grouping
            p_class = "".join(re.findall("[a-zA-Z_:]+", v)) 

            #error handling: all prototypes must be in the master set
            while p_class not in ipa:
                pc = p_class.copy()
                del p_class
                p_class = input((pc+" is not a recognized vowel. Please re-enter: "))
                
            ip = ipa[p_class] #lookup the IPA prototype
            self.base_vowel_dict[p_class] = P(ip.e1, ip.e2, ip.length, ip.name)


     
    def strap_protos(self):
        '''
        you can switch between un/balanced distr. lexicon
        by commenting the one you don't want to use. 
        '''
        #self.lexicon = self.uni_lexicon()
        #self.lexicon = self.cust_lexicon() #manually set each proto weight
        self.lexicon = self.rand_lexicon()


                
    def match_proto(self, im, ipa = False):
        '''
        Matches a signal imitation against ACTIVE IPA Prototypes.
        If the imitation is in fact closer to some other ACTIVE IPA proto, it will return that proto.
        If the imitation is closest to the signal it will return the signal.'''
        P = Prototype.Prototype
        def lm(p):
            if not self.lf:
                return True
            else:
                return( (p.length > 200) is (im.length > 200) )

        #use this version to match against all in master set
        #(enables splitting / phonological change):
        if ipa:
            p_list = [p for p in self.ipa_dict.values() if lm(p)]
            
        #use this one to match against all active prototypes (present in base convention)        
        else:
            p_list = [p for p in self.proto_dict.values() if lm(p)]
        

        def rec_match_proto(protos):
            if len(protos) < 2:
                d0 = euc(im, protos[0])
                if not lm(protos[0]):
                    d0 = 999
                return (protos[0], d0)
            else:
                l = len(protos)
                mid = int(l/2)
                left_closest, dl = rec_match_proto(protos[:mid])
                right_closest, dr = rec_match_proto(protos[mid:])
                if dl < dr:
                    return (left_closest, dl)
                return (right_closest, dr)
                
        real_proto = (rec_match_proto(p_list)[0])
        rpn = real_proto.name
        if rpn not in self.proto_dict:  #something has gone wrong, fix it
            self.proto_dict[rpn] = P(im.e1, im.e2, im.length, rpn)
            
        #activate if it hasn't been already
        #if real_proto.name not in self.proto_dict:
        #    self.proto_dict[real_proto.name] = real_proto

        return real_proto

    

    def activate(self, str_list, c):
        '''
        Used by trigger function (unlisted command)
        Add a new word to the lexicon
        '''
        if c < 1:
            c = 1
        P = Prototype.Prototype
        W = Word.Word
        
        for p in (str_list.split(", ")):
            if (p in self.ipa_dict and p not in self.proto_dict):
                ip = self.ipa_dict[p]
                #self.proto_dict[p] = P(ip.e1, ip.e2, ip.length, ip.name)
                np = P(ip.e1, ip.e2, ip.length, ip.name) # self.proto_dict[p]
                self.base_proto_dict[p] = np
            else:
                p_correction = input("{0} is invalid. Retry:".format(p))
                if p_correction:
                    ip = self.ipa_dict[p]
                    np = P(ip.e1, ip.e2, ip.length, ip.name)
                    self.base_proto_dict[p] = np
            np.carriers = c
            #name = "{0}{1}{2:02d}".format(np.name, "-", 0)
            null_seg = Segment.Segment("-", [])
            new_word = W(null_seg, np.name, null_seg, np)
            self.lexicon[name] = (new_word)
            
        self.proto_label = False #label needs to be redrawn to include new prototype
        self.color_key = False  #color map needs to be redrawn to include new prototype
        


    def f1f2_to_e1e2(self, f1, f2 = None):
        '''
        direct implementation of traunmuller formula to convert from hertz to ERB
        just converts a tuple (f1, f2) in hz to erb
        benefit is that it doesn't have to be a Vowel, just the values
        >>>f1f2_to_e1e2(2400, 800) = (22.44472228978699, 13.58504853003826) 
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
        if f2:
            e2 = conv(f2)
        else:
            e2 = 0
        return (e1, e2)



    def p_hz(self, f1, f2, l, n):
        '''creates a prototype from hertz values
           f1 = first formant, f2 = second formant,
           l = length in ms, n is name (string) '''
        P = Prototype.Prototype
        e1, e2 = self.f1f2_to_e1e2(f1, f2)
        return P(e1, e2, l, n)

    


 ############################################################
 #              MASTER SET (IPA VOWELS)                     #
 ############################################################
 
    def set_vowels(self):
        '''
        To add a new Prototype, copy and paste this line:

        new_pro( p_hz(f1, f2, length, name) )
        
        anywhere within this function above the ######### line
        and replace f1, f2, length, name with values.
        You can also adjust the formant values here. 
        Name must be unique, may contain {[A..Z], [a..z], :, _}
        For the translation dictionary, see global IPA_trans dict
         ^used for IPA symbol representation (unicode)
        '''
        
        p_hz = self.p_hz
        ipa_list = list()
        new_pro = ipa_list.append

        ######## ADD NEW PROTOS BELOW THIS LINE ############
        
        #FRONT
        new_pro( p_hz(331, 2368, 150, "i") )    #unrounded [i]
        new_pro( p_hz(331, 2368, 250, "i:") )    #unrounded [i:]
        new_pro( p_hz(331, 1968, 150, "y") )       #rounded [y]
        new_pro( p_hz(331, 1968, 250, "y:") )       #rounded [y:]
        
        new_pro( p_hz(395, 2034, 150, "I") )  #singleton [I]
        new_pro( p_hz(395, 2034, 250, "I:") )  #singleton [I:]
        new_pro( p_hz(395, 1750, 150, "Y") ) #singleton [Y]
        new_pro( p_hz(395, 1750, 250, "Y:") ) #singleton [Y:]
        
        new_pro( p_hz(462, 2309, 150, "e") )       #unrounded[e]
        new_pro( p_hz(462, 2309, 250, "e:") )       #unrounded[e:]
        new_pro( p_hz(462, 1950, 150, "o_slash") ) #rounded [o_slash] 
        new_pro( p_hz(462, 1950, 250, "o_slash:") ) #rounded [o_slash:]
        
        new_pro( p_hz(622, 2077, 150, "epsilon") )  #unrounded [epsilon]
        new_pro( p_hz(622, 2077, 250, "epsilon:") )  #unrounded [epsilon:]
        new_pro( p_hz(622, 1700, 150, "oe") )   #rounded [oe]
        new_pro( p_hz(622, 1700, 250, "oe:") )   #rounded [oe:]
        
        new_pro( p_hz(775, 1952, 150, "ae") )      #singleton [ae]
        new_pro( p_hz(775, 1952, 250, "ae:") )      #singleton [ae:]
        
        new_pro( p_hz(900, 1670, 150, "a") )       #unrounded [a]
        new_pro( p_hz(900, 1670, 250, "a:") )       #unrounded [a:]
        new_pro( p_hz(900, 1470, 150, "OE") ) #[OE]
        new_pro( p_hz(900, 1470, 250, "OE:") ) #[OE:] 


        #CENTRAL
        new_pro( p_hz(331, 1600, 150, "barred_i") ) #unrounded [barred_i]
        new_pro( p_hz(331, 1600, 250, "barred_i:") ) #unrounded [barred_i:]
        new_pro( p_hz(331, 1370, 150, "barred_u") )#rounded [barred_u]
        new_pro( p_hz(331, 1370, 250, "barred_u:") )#rounded [barred_u:]
        
        new_pro( p_hz(460, 1550, 150, "rev_e") )   #unrounded [schwa]
        new_pro( p_hz(460, 1550, 250, "rev_e:") )   #unrounded [schwa:]
        new_pro( p_hz(459, 1300, 150, "barred_o") )    #rounded [barred_o]
        new_pro( p_hz(459, 1300, 250, "barred_o:") )    #rounded [barred_o:]
        
        new_pro( p_hz(530, 1400, 150, "schwa") ) #singleton [turned_schwa]
        new_pro( p_hz(530, 1400, 250, "schwa:") ) #singleton [turned_schwa:]
        
        new_pro( p_hz(605, 1500, 150, "rev_eps") ) #unrounded [rev_eps]
        new_pro( p_hz(605, 1500, 250, "rev_eps:") ) #unrounded [rev_eps:]
        new_pro( p_hz(605, 1250, 150, "lil_bum") ) #rounded [closed_rev_eps] <Needs a new name
        new_pro( p_hz(605, 1250, 250, "lil_bum:") ) #rounded [closed_rev_eps:] <Needs a new name

        new_pro( p_hz(700, 1450, 150, "turned_a") )     #singleton [turned_a]
        new_pro( p_hz(700, 1450, 250, "turned_a:") )    #singleton [turned_a:]

        new_pro( p_hz(824, 1400, 150, "retracted_a") )  #singleton [hod]
        new_pro( p_hz(824, 1400, 250, "retracted_a:") ) #singleton [hod:]


        #BACK
        new_pro( p_hz(331, 999, 150, "turned_m") ) #unrounded [turned_m]
        new_pro( p_hz(331, 999, 250, "turned_m:") ) #unrounded [turned_m:]
        new_pro( p_hz(331, 850, 150, "u") )          #rounded [u]
        new_pro( p_hz(331, 850, 250, "u:") )        #rounded [u:]

        new_pro( p_hz(405, 1150, 150, "horseshoe") ) #singleton [omega]
        new_pro( p_hz(405, 1150, 250, "horseshoe:") ) #singleton [omega:]

        new_pro( p_hz(465, 1000, 150, "rams_horn") ) #unrounded [rams_horn]
        new_pro( p_hz(465, 1000, 250, "rams_horn:") ) #unrounded [rams_horn:]
        new_pro( p_hz(465, 850, 150, "o") )     # rounded [o]
        new_pro( p_hz(465, 850, 250, "o:") )     # rounded [o:]

        new_pro( p_hz(600, 1000, 150, "wedge") ) #unrounded [wedge] aka ^
        new_pro( p_hz(600, 1000, 250, "wedge:") ) #unrounded [wedge:] aka ^
        new_pro( p_hz(600, 850, 150, "open_o") )    #rounded [open_o]
        new_pro( p_hz(600, 850, 250, "open_o:") )    #rounded [open_o:] 

        new_pro( p_hz(734, 1020, 150, "script_a") )  #unrounded [script_a]
        new_pro( p_hz(734, 1020, 250, "script_a:") )  #unrounded [script_a:]
        new_pro( p_hz(734, 850, 150, "rev_script_a") )  #rounded [rev_script_a]
        new_pro( p_hz(734, 850, 250, "rev_script_a:") )  #rounded [rev_script_a:]
        
           
        ############Add new prototypes above this line##############
        self.ipa_dict = dict((p.name, p) for p in ipa_list)
        self.assign_colors(ipa_list)

    

    def get_size(self):
        '''returns the number of currently active Prototypes'''
        return len(self.proto_dict.values())

    

    def get_load_avg(self):
        '''average functional load of vowels in convention'''
        s = self.get_size()
        v_list = self.proto_dict.values()
        if s:
            total = sum(v.weight for v in v_list)
            avg = total/s
            return avg
        else:
            print("Not enough vowels to get an average.")

            

    def print_list(self):
        for p in self.proto_dict.values():
            print(p)

            

    def sorted_protos(self):
        #using modified insertion sort
        #because the list will always be shortish (n < 56)
        protos = [p for p in self.proto_dict.values()]
        for i in range(len(protos)):
            curr = protos[i]
            j = i
            while j >= 0 and protos[j-1].e1 < curr.e1:
                protos[j] = protos[j-1]
                j = j-1
            protos[j] = protos
        return protos

    

    def rand_lexicon(self):
        '''
        Returns a dictionary.
        Uses the base vowel convention to generate a lexicon.
        The minimum lex size is set in Game_fns.
        The prototypical vowels are given a random number of environments (words).
        The dictionary keys are the word IDs i.e. String.
        the dictionary values are the Word objects.
        The elder group will use a close imitation of the prototypical vowel
        to pronounce the word for the child Agents. 
        
        e.g. a five-vowel system "Spanish" {i, e, o, retracted_a, u}
        with a min lex size of fifty will produce a lexicon
        where each vowel has [10, 40] words.
        Each word is a unique combination of CVC
        where each C (consonant) is a segment
		(a list of articulatory features)
        and V is one of the base protos.
        See Phonology class for articulations.
        '''
        
        r = random
        W = Word.Word
        p_list = self.base_vowel_dict.values()
        lex_size = self.lex_size
        pl_len = len(p_list)

        min_words_vowel = int(lex_size/pl_len)+1
         
        lexicon = dict()
        
        #CONSONANTS
        from Phonology import get_feature_dict
        self.consonant_dict = get_feature_dict() #default is English (sorry)
        cd = self.consonant_dict
        consonants = [c for c in cd.keys()]
        
        
        #proto balance (functional load)
        #should probably seed instead of generating inside the loop.
        #ex. ratio_lim = 5 means any proto can have up to 5x as many words as another proto
        ratio_lim = self.func_load_max # (min_words_vowel) <= number of words in class <= (min_words_vowel * ratio lim)

        for nucleus in p_list:
            num_words_vowel = r.randint(min_words_vowel, min_words_vowel*ratio_lim)
            for i in range(num_words_vowel):
                onset_name = r.choice(consonants)
                onset = Segment.Segment(onset_name, cd[onset_name])
                coda_name = r.choice(consonants)
                coda = Segment.Segment(coda_name, cd[coda_name])
                #name = "{0}+{1}+{2}".format(onset, nucleus.name, coda)
                #new_word = W(name, nucleus, None)
                new_word = W(onset, nucleus.name, coda, nucleus)
                lexicon[new_word.id] = new_word
            self.base_weights[nucleus.name] = num_words_vowel

        lex_size = len(lexicon.keys())
        for n in p_list:
            num_words = self.base_weights[n.name]
            weight = (num_words/lex_size) * 10
            self.base_weights[n.name] = weight

        return lexicon

    

    def cust_lexicon(self):
        '''
        Returns a dictionary.
        Uses the base vowel convention to generate a lexicon.
        The minimum lex size is set in Game_fns.
        The prototypical vowels are given a random number of environments (words).
        The dictionary keys are the word IDs i.e. String.
        the dictionary values are the Word objects.
        The elder group will use a close imitation of the prototypical vowel
        to pronounce the word for the child Agents. 
        
        '''

        r = random
        W = Word.Word
        p_list = self.base_vowel_dict.values()
        lex_size = self.lex_size
        pl_len = len(p_list)
        min_words_vowel = int(lex_size/pl_len)+1
         
        lexicon = dict()
        
        #CONSONANTS
        from Phonology import get_feature_dict
        self.consonant_dict = get_feature_dict()
        
        consonants = [c for c in self.consonant_dict.keys()]
        for nucleus in p_list:
            num_words_vowel = int(input("Number of words for ["+nucleus.name+"] :"))
            for i in range(num_words_vowel):
                onset = r.choice(consonants)
                coda = r.choice(consonants)
                #name = "{0}+{1}+{2}".format(onset, nucleus.name, coda)
                #new_word = W(name, nucleus, None)
                new_word = W(onset, nucleus.name, coda, nucleus)
                lexicon[new_word.id] = new_word
            self.base_weights[nucleus.name] = num_words_vowel

        lex_size = len(lexicon.keys())
        for n in p_list:
            num_words = self.base_weights[n.name]
            weight = (num_words/lex_size) * 10
            self.base_weights[n.name] = weight

        return lexicon  



    def uni_lexicon(self):
        '''
        Returns a dictionary.
        Uses the base vowel convention to generate a lexicon.
        The prototypical vowels are represented equally among words.
        The dictionary keys are the word IDs i.e. String.
        the dictionary values are the Word objects.
        The elder group will use a close imitation of the prototypical vowel
        to pronounce the word for the child Agents. 
        
        e.g. a five-vowel system "Spanish" {i, e, o, retracted_a, u}
        with a lex size of fifty will produce a lexicon
        where each vowel has eleven words.
        Each word is a unique combination of CVS
        where each C (consonant) is a set of articulatory gestures.
        See Phonology class for articulations.
        
        '''
        r = random
        W = Word.Word
        p_list = self.base_vowel_dict.values()
        lex_size = self.lex_size
        pl_len = len(p_list)
        num_words_vowel = int(lex_size/pl_len)+1
        lexicon = dict()
        
        #CONSONANTS
        from Phonology import get_feature_dict
        self.consonant_dict = get_feature_dict()
        
        consonants = [c for c in self.consonant_dict.keys()]
        
        for nucleus in p_list:
            for i in range(num_words_vowel):
                onset = r.choice(consonants)
                coda = r.choice(consonants)
                #name = "{0}+{1}+{2}".format(onset, nucleus.name, coda)
                #new_word = W(name, nucleus, None)
                new_word = W(onset, nucleus.name, coda, nucleus)
                lexicon[new_word.id] = new_word
            self.base_weights[nucleus.name] = (num_words_vowel/(num_words_vowel*pl_len))
        return lexicon  



    def get_word_prototype(self, vl, p_name):
        '''
        Find the prototype of a word by averaging its pronunciation
        among all agents.
        vl is a list of Vowels (tokens)
        w_id is the ID tag of the Word we are updating
        '''
        P = Prototype.Prototype
        c = len(vl)
        if c:
            e1_avg = (sum( [v.e1 for v in vl] ) / c)
            e2_avg = (sum( [v.e2 for v in vl] ) / c)
            l_avg = (sum( [v.length for v in vl] ) / c)
            proto = P(e1_avg, e2_avg, l_avg, p_name)
            proto.carriers = c
            return proto
        else:
            print("error in get_word_prototype:", vl, w_id)
    


    def group_word_protos(self, radius, pl):
        '''
        Update the prototype dictionary with current averages.
        radius is for clustering (not currently in use--maybe in future phase).
        pl is the list of Prototypes.
        '''
        for p in pl:
            self.proto_dict[p.name] = p
        


    
#############################
#   Graphical functions     #
#############################
        
    def assign_colors(self, ipa_vl):
        '''
        Set up color mapping for chart
        Sampling shows each vowel as a different color in reports
        ipa_vl is the list of vowels to be mapped to colors. 
        color_map is a dict {"proto_name": color(r, g, b)} for each proto.
        This is a sortof fragile method;
        it will break if there are too many IPA prototypes (in master set).

        Creates a collection of contrastive colors,
        so that each prototype can be assigned one statically.
        Several base colors are used, then several shades of each base color.

        Recall that long/short vowels are stacked and that vowels move and spread.

        If you want to edit this . . . good luck. :/ :D...

        '''

        self.color_map = dict()
        color_map = self.color_map

        vl = [v.name for v in ipa_vl]

        scm = self.build_color_lists
        cl = self.color_list
        shade_list = []
        sla = shade_list.append #list of shades of base colors
        
        teal = [5, 109, 79] #"base" color
        sla(scm([], teal, (27, 29, 39))) #list of shades of base color
        red = [90, 0, 0] #"base" color
        sla(scm([], red, (39, 10, 9)))
        green = [0, 55, 0]
        sla(scm([], green, (11, 37, 14)))
        purple = [255, 0, 255]
        sla(scm([], purple, (-47, 8, -47)))
        orange = [255, 130, 30]
        sla(scm([], orange, (-21, -18, -9)))
        blue = [0, 0, 65]
        sla(scm([], blue, (20, 20, 40)))
        brown = [100, 49, 0]
        sla(scm([], brown, (41, 45, 40)))
        yellowgreen = [50, 100, 10]
        sla(scm([], yellowgreen, (50, 50, -2)))
        gray = [49, 59, 69]
        sla(scm([], gray, (39, 29, 19)))
        violet = [75, 0, 26]
        sla(scm([], violet, (43, 33, 48)))
        yellow = [105, 105, 49]
        sla(scm([], yellow, (35, 35, -11)))
        indigo = [37, 0, 79]
        sla(scm([], indigo, (30, 23, 38)))

        i = 0
        while shade_list:
            base = shade_list[i] #list of shades
            if base: #base list is not empty
                shade = base.pop()
                cl.append(shade)
            else: #out of shades for that base color
                shade_list.pop(i)
            i += 1
            if i >= len(shade_list):
                i = 0
                    
        
        self.assign_contrast_colors(cl, ipa_vl)

        

    def build_color_lists(self, bcl, base, sups):
        '''cl is a list of values to use as the "base color"
        vl is a list of vowel names which should match the keys in color map
        sups is a tuple of ints used to increment (r, g, b)'''
        #recall color(0, 0, 0) = black, color(255, 255, 255) = white
        a, b, c = sups
        c1, c2, c3 = base[0], base[1], base[2]
        while (c1 <= 255 and c1 >= 0 and
               c2 <= 255 and c2 >= 0 and
               c3 <= 255 and c3 >= 0):
            new_color = (c1, c2, c3)
            bcl.append(new_color)
            c1 += a
            c2 += b
            c3 += c
        return bcl



    def assign_contrast_colors(self, cl, vwl_li):
        '''
        Assign the colors to prototypes in Convention.
        Uses a dictionary where key is prototype name, value is color.
        '''
        pl = [v.name for v in vwl_li]
        i = 0
        color = color_rgb
        if not self.color_on:
            for p in vwl_li:
                self.color_map[p] = color(150, 150, 150)
            return
        while (pl and cl):
            r, g, b = cl.pop()
            p = pl.pop()
            self.color_map[p] = color(r, g, b)
            #print(p, ":", r, g, b) #see what shade is assigned to which proto
    


    def plot_spots(self, pause = 0, mc = 1, s = None):
        '''
        Plots the list of active Prototypes.
        pause is the number of seconds window will stay open.
         pause = 0 will wait for mouse click to close
        mc is minimum carriers (a number of agents)
        s is the text which will appear below the vowel chart.

        Used in step reports if Game_fns.show is on.
        '''

        #redraw window if necessary, but don't make a duplicate
        if (not self.win or self.win.isClosed()):
            self.win = self.formant_space(s)
        win = self.win

        #set heights for labels
        h_side = self.win_margin - 20
        h = self.chart_h + 130 #int(win.getHeight()*.92)

        #set up text
        h2 = h + 30 #next line
        cp = self.proto_dict.values()
        if not cp:
            cp = self.ipa_dict.values() #used in plot_protos()--show all
        protos = []
        for p in cp:
            #if p.carriers >= mc:
            p_class = "".join(re.findall("[a-zA-Z_:]+", p.name))
            if p_class not in protos:
                protos.append(p_class)
                
            #reset list so we know last step has been cleared
            curr_proto_pts = list() 
            
        coord = self.proto_to_xy #converts Prototype to x, y coordinates

        #update the printout of prototypes 
        if self.color_on:
            w = self.chart_w+(self.win_margin*2)+145
            message1 = self.side_label("Convention Vowels", w, h_side)
            message2 = self.label(self.param_str, h)
                
        else:
            message3 = self.label("Currently Active Prototypes:", h)
            #if there are a lot of prototypes, break into lines
            if len(protos) > 11:
                vl1 = "["+("], [".join([v for v in protos[:11]]))+"],"
                vl2 = "\n ["+("], [".join([v for v in protos[11:]]))+"]"
                proto_names = vl1+vl2
            else:
                proto_names = "["+("], [".join([v for v in protos]))+"]"
            #if there are a shit ton of prototypes, decrease the font size
            if len(protos) > 24:
                message2 = self.label(proto_names, h2, 8)
            #otherwise, leave it alone
            else:
                message2 = self.label(proto_names, h2)

            if not self.proto_label:
                message3.draw(win)

        if (not self.updating_label and message1):
            message1.draw(win)
            #message2.draw(win)
            self.updating_label = message2

        #draw the side chart with the colored spots and proto names
        self.draw_color_map()

        #draw all prototypes with enough carriers
        #these are the spots outlined in black (i.e. the mean centers)
        pts = cp
        if pts:
            for pt in pts:
                x, y = coord(pt)
                circle = Circle(Point(x, y), 6)
                if "[" in pt.name:
                    p_class = ((pt.name).split("[")[2])[:-1] #"".join(re.findall("[a-zA-Z_:]+", pt.name))
                else:
                    p_class = "".join(re.findall("[a-zA-Z_:]+", pt.name))
                if self.color_on:
                    color = self.color_map[p_class]
                else:
                    color = 'black'
                circle.setFill(color) #mean center fill color
                circle.setOutline('black') #mean center outline color
                circle.setWidth(1) #width (thickness) of outline
                circle.draw(win)
                curr_proto_pts.append(circle) #store so we can undraw later

        #undraw the previous step sampling if it is still showing
        if self.curr_proto_pts:
            for p in self.curr_proto_pts:
                p.undraw()

        self.curr_proto_pts = curr_proto_pts

        #if pause is 0, wait for user to click before moving on       
        if pause is 0:
            print("(Click on the chart to continue.)")
            win.getMouse()



    def plot_symbols(self, pause = 0, mc = 1, s = None):
        '''
        plot symbols using ipa_trans table instead of spots

        Plots the list of active Prototypes.
        pause is the number of seconds window will stay open.
         pause = 0 will wait for mouse click to close
        mc is minimum carriers (a number of agents)
        s is the text which will appear below the vowel chart.

        Used in step reports if Game_fns.show is on.
        '''

        #redraw window if necessary, but don't make a duplicate
        if (not self.win or self.win.isClosed()):
            self.win = self.formant_space(s)
        win = self.win

        #set heights for labels
        h_side = self.win_margin - 20
        h = self.chart_h + 130 #int(win.getHeight()*.92)

        #set up text
        h2 = h + 30 #next line
        cp = self.proto_dict.values()
        if not cp:
            cp = self.base_vowel_dict.values() #used in plot_protos()--show all
        protos = []
        for p in cp:
            #if p.carriers >= mc:
            p_class = "".join(re.findall("[a-zA-Z_:]+", p.name))
            if p_class not in protos:
                protos.append(p_class)
                
        #reset list so we know last step has been cleared
        curr_proto_pts = list() 
            
        coord = self.proto_to_xy #converts Prototype to x, y coordinates

        #update the printout of prototypes 
        if self.color_on:
            w = self.chart_w+(self.win_margin*2)+145
            message1 = self.side_label("Convention Vowels", w, h_side)
            message2 = self.label(self.param_str, h)
                
        else:
            message3 = self.label("Currently Active Prototypes:", h)
            #if there are a lot of prototypes, break into lines
            if len(protos) > 11:
                vl1 = "["+("], [".join([v for v in protos[:11]]))+"],"
                vl2 = "\n ["+("], [".join([v for v in protos[11:]]))+"]"
                proto_names = vl1+vl2
            else:
                proto_names = "["+("], [".join([v for v in protos]))+"]"
            #if there are a shit ton of prototypes, decrease the font size
            if len(protos) > 24:
                message2 = self.label(proto_names, h2, 8)
            #otherwise, leave it alone
            else:
                message2 = self.label(proto_names, h2)

            if not self.proto_label:
                message3.draw(win)

        if not self.updating_label:
            message1.draw(win)
            #message2.draw(win)
            self.updating_label = message2

        #draw the side chart with the colored spots and proto names
        self.draw_color_map(True)

        #draw all prototypes with enough carriers
        #these are the spots outlined in black (i.e. the mean centers)
        pts = cp
        if pts:
            for pt in pts:
                x, y = coord(pt)
                circle = Circle(Point(x, y), 6)

                #find out the vowel's 'true identity' 
                if "[" in pt.name:
                    p_class = ((pt.name).split("[")[2])[:-1] #"".join(re.findall("[a-zA-Z_:]+", pt.name))
                else:
                    p_class = "".join(re.findall("[a-zA-Z_:]+", pt.name))

                #use color-coding for symbol to match dots
                if self.color_on:
                    color = self.color_map[p_class]
                else:
                    color = 'black'

                tp = Point(x, y) #proto's location in the chart
                symb = ipa_trans[p_class] #proto's name (may be unicode)

                #black outlines of the symbols
                proto_symb_stroke = self.get_symbol_obj(symb, tp, 30, 'gray4', 'bold')
                proto_symb_stroke.draw(win)
                curr_proto_pts.append(proto_symb_stroke) #store so we can undraw later

                if self.color_on:
                    proto_symb = self.get_symbol_obj(symb, tp, 30, color)
                    proto_symb.draw(win)
                    curr_proto_pts.append(proto_symb)

        #undraw the previous step sampling if it is still showing
        if self.curr_proto_pts:
            for p in self.curr_proto_pts:
                p.undraw()

        self.curr_proto_pts = curr_proto_pts

        #if pause is 0, wait for user to click before moving on       
        if pause is 0:
            print("(Click on the chart to continue.)")
            win.getMouse()



    def get_symbol_obj(self, symb, loc, size, color, style = ""):
        '''
        returns the Text object, ready to be drawn in a window.
        '''
        proto_symb = Text(loc, symb)
        proto_symb.setFace('arial')
        proto_symb.setSize(size)
        proto_symb.setTextColor(color)
        if style:
            proto_symb.setStyle(style)
        return proto_symb
        


    def label(self, m, height, size = 10, color = 'black'):
        '''
        returns a centered text label, which can be drawn
        m is the text to be printed i.e. String
        height is height in window (the y coord) i.e. int
        size is the font size for the text i.e. int (default 10)
        color is the color of the text (default 'black) i.e. String
        '''
        
        if not self.win:
            return
        win = self.win
        tp = Point(win.getWidth()*.4, height)
        message = Text(tp, m)
        message.setTextColor(color)
        message.setSize(size)
        return message

    
        
    def side_label(self, m, w, height, color = 'black'):
        '''
        returns a left-side Label, which can then be drawn
        m is the text to be printed i.e. String
        height is height in window (the y coord) i.e. int
        size is the font size for the text i.e. int (default 10)
        color is the color of the text (default 'black) i.e. String
        '''
        if not self.win:
            return
        win = self.win
        if self.color_on:
            tp = Point(w, height)
        else:
            tp = Point(win.getWidth()/2, height)
        message = Text(tp, m)
        message.setSize(11)
        message.setTextColor(color)
        
        return message


    
    def plot_sets(self, pt_list, pause = 0, s = ""):
        '''
        Plots a given list of vowels
        pt_list is a list of Vowel or Prototype objects
        pause is the number of seconds window stays open i.e. int
        where pause = 0 will wait for mouse click to close
        s is an optional line of text to be printed under the chart i.e. String
        '''
        in_color = self.color_on
        
        coord = self.proto_to_xy
        
        if (not self.win or self.win.isClosed()):
            self.win = self.formant_space()
        win = self.win

        #remove the old label if its already been drawn
        if self.updating_label:
            self.updating_label.undraw()

        #draw the centered text beneath the chart
        h = self.chart_h + self.win_margin + 67 #int(win.getHeight()*.8)
        if not s:
            if in_color:
                line1 = "Live agents' vowels in color with mean centers outlined."
            else:
                line1 = "Live agents' vowels in gray with mean centers outlined"
            lines = line1+"\n"+param_str
        else:
            lines = s+"\n"+self.param_str

        if pause is 0:
            lines = lines+"\nClick to close."
        message1 = self.label(lines, h)
        message1.draw(win)
        self.updating_label = message1

        #draw the current dots i.e. Agents' Vowels
        curr_sampling = self.draw_colored_pts(pt_list)

        #remove the old dots
        all_pts = self.curr_sampling 
        if all_pts:
            for p in all_pts:
                p.undraw()
        del all_pts
        
        #update list of current drawn dots
        self.curr_sampling = curr_sampling

        #if pause > 0:
            #time.sleep(pause)
        if pause is 0:
            win.getMouse()

            
            
    def plot_micro(self, chosen, wait=False):
        if chosen.age:
            rep = (v for v in chosen.repertoire if v.weight)
        else:
            rep = chosen.repertoire
            
        #draw the window if it's been closed or not opened yet
        if (not self.win or self.win.isClosed()):
            self.win = self.formant_space()
        win = self.win
        
        in_color = self.color_on
        coord = self.proto_to_xy #convert Prototypes to (x, y)
        #create the Circle objects
        #color-coded or gray
        for pt in rep:
            if "[" in pt.name:
                pn = ((pt.name).split("[")[2])[:-1] #"".join(re.findall("[a-zA-Z_:]+", pt.name))
            else:
                pn = "".join(re.findall("[a-zA-Z_:]+", pt.name))
            x, y = coord(pt)
            p_xy = Circle(Point(x, y), 3)
            color = self.color_map[pn]
            p_xy.setFill(color)
#
            p_xy.setOutline('gray2')
            p_xy.setWidth(3)
            p_xy.draw(win)
            self.curr_sampling.append(p_xy)
            
        if wait: #wait for user to click before moving on       
            print("(Click on the chart to continue.)")
            self.win.getMouse()

            

    def draw_colored_pts(self, pt_list, size = 1):
        '''
        Draws the dots in the window.
        Returns list to set self.current_pts to current sampling
        '''

        #draw the window if it's been closed or not opened yet
        if (not self.win or self.win.isClosed()):
            self.win = self.formant_space()
        win = self.win
        
        in_color = self.color_on
        coord = self.proto_to_xy #convert Prototypes to (x, y)
        all_pts = []
        #create the Circle objects
        #color-coded or gray
        for pt in pt_list:
            if "[" in pt.name:
                pn = ((pt.name).split("[")[2])[:-1]
            else:
                pn = "".join(re.findall("[a-zA-Z_:]+", pt.name))
            x, y = coord(pt)
            p_xy = Circle(Point(x, y), size)
            color = self.color_map[pn]
            p_xy.setFill(color)
#
            p_xy.setOutline(color)
            p_xy.draw(win)
            all_pts.append(p_xy)
            '''
            c_circle = Circle(p_xy, size)
            if in_color:
                color = self.color_map[pn]
            else:
                color = 'grey'
            c_circle.setOutline(color)
            c_circle.setFill(color)
            if c_circle not in all_pts:
                c_circle.draw(win)  
                all_pts.append(c_circle)
            '''
        return all_pts

    
    
    def close_win(self):
        '''
        close the window and reset everything so it can be redrawn
        '''
        self.win.close()
        self.win = None
        self.proto_label = None
        self.updating_label = None
        self.color_key = False

        

    def draw_win(self, l=""):
        '''sets self.win to a window with the vowel chart drawn'''
        self.win = self.formant_space(l)


    
    def show_displacement(self, label, protos, pause = 0):
        '''
        Calls draw_results() with the IPA prototypes as originals.
        label is the Label to be drawn in the window
        protos is a list of Vowels or Prototypes
        pause is the amount of time to wait before continuing (0 for getMouse)

        draws the current averages overlaid on the original IPA prototypes
        current centers are colored spots, originals are black spots

        To allow for phonological change, you would need to use different originals

        '''
        base_names = []
        for p in protos:
            p_class = (p.name.split("[")[2])[:-1]
            if p_class not in base_names:
                base_names.append(p_class)
                #self.base_proto_dict[p.name] = p
        base_protos = [self.ipa_dict[bp] for bp in base_names]
        self.draw_results(label, base_protos, protos, pause)

        

    def draw_results(self, s, originals, protos, pause):
        '''draws the original prototypes in black and current ones in gray
        label is a string which is printed in the lower part of the window
        originals is a list of prototypes
        protos is a list of prototypes
        pause is number of seconds to display (0 for getMouse)'''
        
        if (not self.win or self.win.isClosed()):
            self.win = self.formant_space()
            
        if self.curr_proto_pts:
            for p in self.curr_proto_pts:
                p.undraw()
        if self.curr_sampling:
            for p in self.curr_sampling:
                p.undraw()
        if self.updating_label:
            self.updating_label.undraw()
                
        ipa = self.ipa_dict
        pl = protos
        
        win = self.win
        gray = color_rgb(190, 200, 200)
        h = self.chart_h + 105#int(win.getHeight()*.88)
        tp = Point(win.getWidth()*.4, h)

        #draw the black spots
        self.draw_pts(originals, 7, 'black')
        
        #draw the colored spots
        self.draw_colored_pts(pl, 5)

        #print the caption and close the window
        line1 = "Original positions in black, current mean centers in color. Click to close."
        line2 = s
        line3 = self.param_str
        lines = "\n".join([line1, line2, line3])
        self.update_label(tp, lines, 'black')
        self.draw_color_map()
        if pause is 0:
            win.getMouse()
            self.close_win()

            

    def update_label(self, tp, message, color):
        if self.updating_label:
            self.updating_label.undraw()
        if not self.win:
            return
        win = self.win
        message1 = Text(tp, message)
        message1.setTextColor(color)
        message1.setSize(11)
        message1.draw(win)
        self.updating_label = message1

            

    def draw_pts(self, protos, radius, color):
        '''
        transcribe vowels (protos) to points
        all points will be the same color given with radius given
        '''
        if self.win:
            win = self.win
        coord = self.proto_to_xy
        cs = [coord(pt) for pt in protos]
        pts = [Circle(Point(x, y), radius) for (x, y) in cs]
        for p in pts:
            p.setOutline(color)
            p.setFill(color)
            p.draw(win)



    def set_formant_limits(self):
        '''
           Sets the limits in ERB for formant1 and formant2
           Limits are used to draw the window,
           and all graphic objects.
           Limits are NOT automatically synced with Agent limits,
           so if you change these, update the Agent limits too.

           This is where scaling is handled.
           
           NB: Alignment / scaling is done in ERB
               The hz labels are converted at each marker,
               so the hz labels are correct, but the axes are not aligned to hz.
               Don't visually gauge the distance between vowels in hz using the hz markers.
               But at least it is consistent with standard practice in Linguistics.
         '''

        #second formant (x axis)
        
        self.e2_closed_max = 24.5
        self.e2_min = 11.75
        e2_range = self.e2_closed_max - self.e2_min
        self.e2_open_max = self.e2_closed_max - (e2_range/8)

        #first formant (y axis)
        self.e1_max = 15.25
        self.e1_min = 6.75
        e1_range = self.e1_max - self.e1_min

        #if using color coding, make the window bigger
        co = self.color_on
        if co:
            self.win_width = 1100
            self.win_height = 650
            self.win_margin = 40
            self.chart_w = 800 - (self.win_margin*4)
            scaled_height = e1_range / e2_range
            self.chart_h = self.chart_w*(scaled_height)
        else:
            self.win_width = 800
            self.win_height = 655
            self.win_margin = 40
            self.chart_w = self.win_width - (self.win_margin*4)
            scaled_height = e1_range / e2_range
            self.chart_h = self.chart_w*(scaled_height)

        

    def draw_color_map(self, ipa = False):
        '''
        draws the vowel-color key on the side
        '''
        if (self.color_on and (not self.color_key) ):
            #make sure window is open and drawn
            if (not self.win or self.win.isClosed() ):
                self.win = self.formant_space()
            win = self.win
            
            h = self.win_margin 
            h2 = h #+ 15
            
            w = self.chart_w+(self.win_margin*2)+100
            
            #check to see if side label has been drawn already
            if not self.proto_label:
                self.proto_label = self.side_label("", w, h2)

            #get distinct prototype class names for side label
            protos = list(set([p.name.split("][")[1] for p in self.proto_dict.values()]))
            
            '''
            if "[" in protos[i]:
                p1 = (protos[i].split("][")[1])
            else:
                p1 = protos[i]
            '''

            if not protos:
                protos = [v for v in self.base_vowel_dict.keys()]
            '''
            if word_protos:
                for proto in word_protos:
                    p_name = "".join(re.findall("[a-zA-Z_:]+", proto.name))
                    if p_name not in protos:
                        protos.append(p_name)
            else:
                protos = [v.name for v in self.base_vowel_dict.values()]'''

            if len(protos) > 20: #Break into 2 columns
                
                for i in range(0, len(protos), 2):
                    p1 = protos[i]
                    p_color = self.color_map[p1]
                    if ipa:
                        ps = ipa_trans[protos[i]]
                    else:
                        ps = p1
                    message2 = self.side_label(ps, w+70, h2)
                    
                    message2.draw(win)
                    circle = Circle(Point(w, h2), 6.5)
                    circle.setFill(p_color)
                    circle.setOutline('black')
                    circle.draw(win)

                    if i < (len(protos) - 1):
                        if "[" in protos[i+1]:
                            p2 = protos[i+1].split("[")[2][:-1]
                            if ipa:
                                ps2 = ipa_trans[p2]
                            else:
                                ps2 = p2
                        else:
                            p2 = protos[i+1]
                            if ipa:
                                ps2 = ipa_trans[p2]
                            else:
                                ps2 = p2
                            w2 = w+155
                            p_color = self.color_map[p2]
                            message2 = self.side_label(ps2, w2+57, h2)#proto names
                            message2.draw(win)
                            circle = Circle(Point(w2, h2), 6.5)
                            circle.setFill(p_color)
                            circle.setOutline('black')
                            circle.draw(win)
                        h2 += 22 #LINE SPACING
                        
            else: #single column
                for i in range(len(protos)):
                    if "[" in protos[i]:
                        p1 = protos[i].split("[")[2][:-1]
                    else:
                        p1 = protos[i]
                        p_color = self.color_map[p1]
                        if ipa:
                            ps = ipa_trans[p1]
                        else:
                            ps = p1
                        message2 = self.side_label(ps, w+57, h2) #proto names
                        message2.draw(win)
                        circle = Circle(Point(w, h2), 7)
                        circle.setFill(p_color)
                        circle.setOutline('black')
                        circle.draw(win)
                        h2 += 22 #LINE SPACING
            self.color_key = True


            

    def formant_space(self, wl = ""):
        '''draws the window with the vowel chart and markers'''
        win_label = wl
        P = Prototype.Prototype
        hz = self.to_hz_praat
        coord = self.coord_erb

        win_width = self.win_width+self.win_margin
        win_height = self.win_height+self.win_margin

        e2_cm = self.e2_closed_max 
        e2_om = self.e2_open_max
        e2_min = self.e2_min
        f2_cm, f2_om = hz(e2_cm, e2_om)
        f2_min, t = hz(e2_min, 0)

        e1_min = self.e1_min
        e1_max = self.e1_max
        f1_min, f1_max = hz(e1_min, e1_max)

        top_left_corner = coord(e2_cm, e1_min)
        top_right_corner = coord(e2_min, e1_min)
        bottom_left_corner = coord(e2_om, e1_max)
        bottom_right_corner = coord(e2_min, e1_max)

        e2_closed_midpoint = (e2_cm - (e2_cm - e2_min)/2)
        e2_open_midpoint = (e2_om - (e2_om - e2_min)/2)
        f2_closed_midpoint, f2_open_midpoint = hz(e2_closed_midpoint, e2_open_midpoint)

        e1_third = e1_max - ((e1_max - e1_min)/3)
        e1_twothird = e1_max - (((e1_max - e1_min)/3) * 2)
        f1_third, f1_twothird = hz(e1_third, e1_twothird)

        right_mark1 = "{0:4}{1:1}{2:.2f}".format(int(f1_min), "/", e1_min)
        right_mark2 = "{0:4}{1:1}{2:.2f}".format(int(f1_third), "/", e1_third)
        right_mark3 = "{0:4}{1:1}{2:.2f}".format(int(f1_twothird), "/", e1_twothird)
        right_mark4 = "{0:4}{1:1}{2:.2f}".format(int(f1_max), "/", e1_max)

        top_mark1 = "{0:4}{1:1}{2:.2f}".format(int(f2_cm), "/", e2_cm)
        top_mark2 = "{0:4}{1:1}{2:.2f}".format(int(f2_closed_midpoint), "/", e2_closed_midpoint)
        top_mark3 = "{0:4}{1:1}{2:.2f}".format(int(f2_min), "/", e2_min)

        tlc_x, tlc_y = top_left_corner
        trc_x, trc_y = top_right_corner
        blc_x, blc_y = bottom_left_corner
        brc_x, brc_y = bottom_right_corner

        row2_left = e2_cm - (((e2_cm - e2_om)/3) * 2)
        row3_left = e2_cm - ((e2_cm - e2_om)/3)
        r2_x, r2_y = coord(row2_left, e1_third)
        r3_x, r3_y = coord(row3_left, e1_twothird)

        c2t_x, c2t_y = coord(e2_closed_midpoint, e1_min)
        c2b_x, c2b_y = coord(e2_open_midpoint, e1_min)
        
        win = GraphWin(win_label, win_width, win_height)
        win.setBackground('white')
        r1 = Line(Point(tlc_x, tlc_y-15), Point(trc_x, trc_y-15))    #closed, front/central/back
        r2 = Line(Point(r2_x+3, r2_y), Point(trc_x, r2_y))    #mid-closed, front/central/back
        r3 = Line(Point(r3_x+3, r3_y), Point(trc_x, r3_y))    #mid-open, front/central/back
        r4 = Line(Point(blc_x, blc_y), Point(brc_x, brc_y))    #open, front/central/back
        c1 = Line(Point(tlc_x, tlc_y-15), Point(blc_x, blc_y))    #column1: front, closed/mid-closed/mid-open/open
        c2 = Line(Point(c2t_x, c2t_y-15), Point(c2b_x, blc_y))    #column2: central, closed/mid-closed/mid-open/open
        c3 = Line(Point(trc_x, trc_y-15), Point(brc_x, brc_y))  #column3: back, closed/mid-closed/mid-open/open

        grey = color_rgb(100, 100, 100)
        r1.setOutline(grey)
        #r1.setWidth(2)
        r2.setOutline(grey)
        #r2.setWidth(2)
        r3.setOutline(grey)
        #r3.setWidth(2)
        r4.setOutline(grey)
        #r4.setWidth(2)
        c1.setOutline(grey)
        #c1.setWidth(2)
        c2.setOutline(grey)
        #c2.setWidth(2)
        c3.setOutline(grey)
        #c3.setWidth(2)
        
        r1.draw(win)
        r2.draw(win)
        r3.draw(win)
        r4.draw(win)
        c1.draw(win)
        c2.draw(win)
        c3.draw(win)

        #ruler markings: f2 max, mid, min left-right across top
        r2400 = Text(Point(tlc_x+15, tlc_y-25), top_mark1)
        r2400.setSize(9)
        r2400.setTextColor(grey)
        r1550 = Text(Point(c2t_x+5, c2t_y-25), top_mark2)
        r1550.setSize(9)
        r1550.setTextColor(grey)
        r700 = Text(Point(trc_x+5, trc_y-25), top_mark3)
        r700.setSize(9)
        r700.setTextColor(grey)
        r2400.draw(win)
        r1550.draw(win)
        r700.draw(win)

        #ruler markings: f1 min, mid1, mid2, max top-down on right side
        r300 = Text(Point(trc_x+30, trc_y-10), right_mark1)
        r300.setSize(9)
        r300.setTextColor(grey)
        r465 = Text(Point(trc_x+35, r2_y), right_mark2)
        r465.setSize(9)
        r465.setTextColor(grey)
        r635 = Text(Point(trc_x+30, r3_y), right_mark3)
        r635.setSize(9)
        r635.setTextColor(grey)
        r800 = Text(Point(trc_x+35, brc_y-5), right_mark4)
        r800.setSize(9)
        r800.setTextColor(grey)
        r300.draw(win)
        r465.draw(win)
        r635.draw(win)
        r800.draw(win)
        
        return win

    

    def coord_erb(self, e2, e1):
        '''returns (x, y) as a tuple, which can be used to create a point'''
        e1_max = self.e1_max
        e1_min = self.e1_min
        e2_max = self.e2_closed_max
        e2_min = self.e2_min
        e1_range = int(e1_max - e1_min)
        e2_range = int(e2_max - e2_min)

        margin = self.win_margin
        wh = self.chart_h
        ww = self.chart_w
        e2_scale = ww/e2_range
        e1_scale = wh/e1_range
        x = int( ( (e2_max - e2) * e2_scale ) + margin)
        y = int( ( (e1 - e1_min) * e1_scale ) + margin)
        return( (x, y) )

    
        
    def proto_to_xy(self, proto):
        e1 = proto.e1
        e2 = proto.e2
        return(self.coord_erb(e2, e1))

    
        
    def to_hz_praat(self, e1, e2):
            from math import exp
            d1 = exp ((e1 - 43) / 11.17)
            f1 = (14680*d1 - 312) / (1 - d1)

            d2 = exp ((e2 - 43) / 11.17)
            f2 = (14680*d2 - 312) / (1 - d2)
            return (f1, f2)



    def draw_agent_margins(self, agent):
        if (not self.win or self.win.isClosed()):
            self.win = self.formant_space()
        for p in self.curr_sampling:
            p.undraw()
        win = self.win
        vl = agent.repertoire
        pt_list = list()
        coord = self.coord_erb
        h = self.chart_h + self.win_margin + 85
        h2 = self.win_margin
        if not self.color_key:
            if self.proto_label:
                self.proto_label.undraw()
            self.proto_label = False
            self.draw_color_map()
        perc_radius = agent.perception
        prox = max([0, agent.prox_margin])
        inner_radius = perc_radius
        for v in vl:

            outer_radius = (perc_radius * v.weight) + prox
            e1, e2 = v.e1, v.e2
            prox_e1 = e1 - outer_radius
            perc_e1 = e1 - inner_radius
            
            prox_x, prox_y = coord(e2, prox_e1)
            prox_top = Point(prox_x, prox_y)
            perc_x, perc_y = coord(e2, perc_e1)
            perc_top = Point(perc_x, perc_y)

            c_x, c_y = self.proto_to_xy(v)
            cen_pt = Point(c_x, c_y)
            
            prox_r = c_y - prox_y
            prox_circle = Circle(cen_pt, prox_r)
            perc_r = c_y - perc_y
            perc_circle = Circle(cen_pt, perc_r)
#TURNING PROX OFF WHEN IT'S NEGATIVE
            if prox:
                prox_circle.draw(win)
            perc_circle.draw(win)

            cen = Circle(cen_pt, 2) #prototype
            
            vname = "".join(re.findall("[a-zA-Z_:]+", v.name))
            if self.color_on:
                p_color = self.color_map[vname]
#TURNING PROX OFF WHEN IT'S NEGATIVE
                if prox:
                    prox_circle.setOutline(p_color)
                perc_circle.setOutline(p_color)
                cen.setFill(p_color)
                cen.setOutline('black')
                cen.setWidth(2)
            else:
                prox_circle.setOutline('grey2')
                perc_circle.setOutline('grey')
                cen.setFill('black')
            self.curr_sampling.append(prox_circle)
            self.curr_sampling.append(perc_circle)
            self.curr_sampling.append(cen)
            cen.draw(win)

        tp = Point(win.getWidth()*.4, h)
        if len(vl) > 13:
            vl1 = "["+("], [".join([v.name for v in vl[:13]]))+"],"
            vl2 = "\n ["+("], [".join([v.name for v in vl[13:]]))+"]"
            v_names = vl1+vl2
        else:
            v_names = "["+("], [".join([v.name for v in vl]))+"]"
        if self.updating_label:
            self.updating_label.undraw()
        message = "Showing Agent "+agent.name+"'s repertoire (bolded) with exact perceptual / proximity margins."
        if vl:
            message += "\nAgent's Perception = "+str(inner_radius)+", Average Proximity Margin = "+str(outer_radius)
            message += " phone_radius = "+str(agent.phone_radius)
        message += "\nCommunity mean centers shown also."
        message1 = Text(tp, message)
        message1.setTextColor('black')
        message1.setSize(11)
        message1.draw(win)
        win.getMouse()
        print("Click to continue")
        self.updating_label = message1
        

        
    def draw_avg_margins(self, vd, perc, prox_addon, wait=False):
        '''draws the proximity margin around each vowel in v_list
        where margin is (perc*weight + prox)
        and weight is the average i.e. |lexicon| / |v_list| '''
        #to_hz = self.to_hz_praat
        prox = max([0, prox_addon])
        if (not self.win or self.win.isClosed()):
            self.win = self.formant_space()
        win = self.win
        vl = [v for v in vd]

        while self.circles and wait:
            circle = self.circles.pop()
            circle.undraw()
        
        pt_list = list()
        weight = (self.lex_size / len(vl))/self.lex_size
        inner_radius = perc
        outer_radius = (perc * weight) + prox
        #print(radius)
 
        coord = self.coord_erb
        h = self.chart_h + self.win_margin + 85
        h2 = self.win_margin
        #self.color_key = False
        #self.proto_label = False
        
        #if self.proto_label:
        #    self.proto_label.undraw()
            
        if not self.color_key:
            self.draw_color_map()

        self.circles = []
        ca = self.circles.append
        
        for v in vl:
            e1, e2 = v.e1, v.e2
            prox_e1 = e1 - outer_radius
            perc_e1 = e1 - inner_radius
            
            prox_x, prox_y = coord(e2, prox_e1)
            prox_top = Point(prox_x, prox_y)
            perc_x, perc_y = coord(e2, perc_e1)
            perc_top = Point(perc_x, perc_y)

            c_x, c_y = self.proto_to_xy(v)
            cen_pt = Point(c_x, c_y)
            
            prox_r = c_y - prox_y
            prox_circle = Circle(cen_pt, prox_r)
            perc_r = c_y - perc_y
            perc_circle = Circle(cen_pt, perc_r)

#TURNING OFF PROX CIRCLE WHEN ADDON IS NEGATIVE
            if prox:
                prox_circle.draw(win)
                ca(prox_circle)
                
            perc_circle.draw(win)
            #perc_circle.setWidth(1.5)
            cen = Circle(cen_pt, 6) #prototype

            
            ca(perc_circle)
            

            vname_l = v.name.split("][")
            if len(vname_l)> 1:
                vname = vname_l[1]
            else:
                vname = vname_l[0]
            if self.color_on:
                p_color = self.color_map[vname]
                prox_circle.setOutline(p_color)
                perc_circle.setOutline(p_color)
                cen.setFill(p_color)
                #cen.setWidth(1)
            else:
                prox_circle.setOutline('grey2')
                perc_circle.setOutline('grey')
                cen.setFill('black')
                
            cen.draw(win)
            ca(cen)


        tp = Point(win.getWidth()*.4, h)
        if len(vl) > 13:
            vl1 = "["+("], [".join([v.name for v in vl[:13]]))+"],"
            vl2 = "\n ["+("], [".join([v.name for v in vl[13:]]))+"]"
            v_names = vl1+vl2
        else:
            v_names = "["+("], [".join([v.name for v in vl]))+"]"
        #message = "Base Convention:\n"+v_names+"\n\nAgent Perception = "+str(inner_radius)+", Average Proximity Margin = "+str(outer_radius)
        #message1 = Text(tp, message)
        #message1.setTextColor('black')
        #message1.setSize(10)
        #message1.draw(win)

        if wait:
            print("Click the chart to continue.")
            win.getMouse()
            self.close_win()
        else:
            message1.undraw()

            
            
    def draw_base_margins(self, vd, perc, prox, wait=False):
        '''
        Draws the protos in the base convention with lexical load as weight
        for the proximity margins
        and agent base perception as perception margins.
        '''

        if (not self.win or self.win.isClosed()):
            self.win = self.formant_space()
        win = self.win
        vl = [v for v in vd]

        while self.circles and wait:
            circle = self.circles.pop()
            circle.undraw()
        
        pt_list = list()
        
        inner_radius = perc
 
        coord = self.coord_erb
        h = self.chart_h + self.win_margin + 85
        h2 = self.win_margin
            
        if not self.color_key:
            self.draw_color_map()

        self.circles = []
        ca = self.circles.append
        proto_weights = self.base_weights
        
        for v in vl:
            vname_l = v.name.split("][")
            if len(vname_l)> 1:
                vname = vname_l[1]
            else:
                vname = vname_l[0]
            weight = proto_weights[vname]
            outer_radius = weight + prox
            e1, e2 = v.e1, v.e2
            prox_e1 = e1 - outer_radius
            perc_e1 = e1 - inner_radius
            
            prox_x, prox_y = coord(e2, prox_e1)
            prox_top = Point(prox_x, prox_y)
            perc_x, perc_y = coord(e2, perc_e1)
            perc_top = Point(perc_x, perc_y)

            c_x, c_y = self.proto_to_xy(v)
            cen_pt = Point(c_x, c_y)
            
            prox_r = c_y - prox_y
            prox_circle = Circle(cen_pt, prox_r)
            perc_r = c_y - perc_y
            perc_circle = Circle(cen_pt, perc_r)
#TURNING PROX OFF WHEN IT'S NEGATIVE
            if prox > 0:
                prox_circle.draw(win)
                ca(prox_circle)
                
            perc_circle.draw(win)
            #perc_circle.setWidth(1.5)
            cen = Circle(cen_pt, 6) #prototype
            ca(perc_circle)
            
            if self.color_on:
                p_color = self.color_map[vname]

                prox_circle.setOutline(p_color)
                
                perc_circle.setOutline(p_color)
                cen.setFill(p_color)
                #cen.setWidth(1)
            else:
                prox_circle.setOutline('grey2')
                perc_circle.setOutline('grey')
                cen.setFill('black')
                
            cen.draw(win)
            ca(cen)


        tp = Point(win.getWidth()*.4, h)
        if len(vl) > 13:
            if "][" in vl[0].name:
                vl1 = "["+("], [".join([v.name.split("][")[1] for v in vl[:13]]))+"],"
                vl2 = "\n ["+("], [".join([v.name.split("][")[1] for v in vl[13:]]))+"]"
            else:
                vl1 = "["+("], [".join([v.name for v in vl[:13]]))+"],"
                vl2 = "\n ["+("], [".join([v.name for v in vl[13:]]))+"]"
            v_names = vl1+vl2
        else:
            v_names = "["+("], [".join([v.name for v in vl]))+"]"
        message = "Base Convention:\n"+v_names+"\n\nAgent Perception = "+str(inner_radius)+", Prox Addon = "+str(prox)
        message1 = Text(tp, message)
        message1.setTextColor('black')
        message1.setSize(11)
        #message1.draw(win)

        if wait:       
            win.getMouse()
            self.close_win()
        else:
            message1.undraw()

            
            
    def draw_proto_margins(self, perc, prox, wait):
        '''draws the prototypes and their margins'''
        pl = self.base_vowel_dict.values()
        self.draw_base_margins(pl, perc, prox, wait)

        

    def save_win(self, cfn = None):
        from time import ctime
        #from PIL import Image as NewImage

        if (not self.win or self.win.isClosed()):
            self.win = self.plot_protos()
            
        win = self.win
        if cfn:
            eps = cfn+".eps"
        else:
            eps = ctime().replace(" ", "_")+".eps"
            eps = eps.replace(":", "")
        #fn = ctime()+".gif"
        print("Saving image as", eps, " . . . ", end="")
        #if self.color_on:
        color = 'color'
        win.postscript(file=eps, colormode = color)
        #img = NewImage.open(eps)
        #img.save(fn, "gif")
        print("Finished.")

        
    
def euc(v, w):
    e1_dif = (v.e1 - w.e1)
    e2_dif = (v.e2 - w.e2)
    return ((e1_dif * e1_dif) + (e2_dif * e2_dif))**.5



def plot_protos(get_inp = False):
    c = Convention()
    cl = c.ipa_dict.values()
    if get_inp:
        cl_str = input("Prototype names:")
    else:
        cl_str = ", ".join([p.name for p in cl])
    c.str_to_protos(cl_str)
    c.draw_win(cl_str)
    c.plot()
    c.close_win()



def draw_win(wl=""):
    c = Convention()
    c.win = c.formant_space(wl)

def hz_dist(vf1, vf2, wf1, wf2):
    '''
    This returns the distance IN HERTZ between two vowels
    vf1 is the first formant of vowel v i.e. int
    vf2 is the second formant of vowel v i.e. int
    wf1 is the first formant of vowel w i.e. int
    wf2 is the second formant of vowel w i.e. int
    USE WITH CAUTION! Scaling and calculations are all done in ERB!!!

    If you want the ERB distance, use euc(v, w).
    '''
    f1_dif = vf1 - wf1
    f2_dif = vf2 - wf2
    return( ((f1_dif * f1_dif) + (f2_dif * f2_dif))**.5 )

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

def dist(p, q):
    from math import sqrt
    a = p[0] - q[0]
    b = p[1] - q[1]
    c_sqr = ((a*a) + (b*b))
    c = sqrt(c_sqr)
    return(c)


ipa_trans ={'i': "i", 'i:': "i\u02D0",
            'y': "y", 'y:': "y\u02D0",
            'I': "\u026A", 'I:': "\u026A\u02D0",
            'Y': "\u028F", 'Y:': "\u028F\u02D0",
            'e': "e", 'e:': "e\u02D0",
            'o_slash': '\u00F8', 'o_slash:': '\u00F8\u02D0',
            'epsilon': '\u03B5', 'epsilon:': '\u03B5\u02D0',
            'oe': '\u0153', 'oe:': '\u0153\u02D0',
            'ae': '\u00E6', 'ae:': '\u00E6\u02D0',
            'a': "a", 'a:': "a\u02D0",
            'OE': '\u0276', 'OE:': '\u0276\u02D0',
            'barred_i': '\u0268' , 'barred_i:': '\u0268\u02D0',
            'barred_u': '\u0289', 'barred_u:': '\u0289\u02D0',
            'rev_e': '\u0258', 'rev_e:': '\u0258\u02D0',
            'barred_o': '\u0275', 'barred_o:': '\u0275\u02D0',
            'schwa': '\u0259', 'schwa:': '\u0259\u02D0',
            'rev_eps': '\u025C', 'rev_eps:': '\u025C\u02D0',
            'lil_bum': '\u029A', 'lil_bum:': '\u029A\u02D0',
            'turned_a': '\u0250', 'turned_a:': '\u0250\u02D0',
            'retracted_a': 'a\u0320' , 'retracted_a:': 'a\u0320\u02D0' ,
            'turned_m': '\u026F', 'turned_m:': '\u026F\u02D0',
            'u': 'u', 'u:': 'u\u02D0',
            'horseshoe': '\u028A', 'horseshoe:': '\u028A\u02D0',
            'rams_horn': '\u0264', 'rams_horn:': '\u0264\u02D0',
            'o': 'o', 'o:': 'o\u02D0',
            'wedge': '\u028C', 'wedge:': '\u028C\u02D0',
            'open_o': '\u0254', 'open_o:': '\u0254\u02D0',
            'script_a': '\u0251', 'script_a:': '\u0251\u02D0',
            'rev_script_a': '\u0252', 'rev_script_a:': '\u0252\u02D0',

            #CONSONANTS
            't': 't',
            'p': 'p',
            'g': 'g',
            'h': 'h',
            's': 's',
            'd': 'd',
            'b': 'b',
            'k': 'k',
            'm': 'm',
            'agma': '\u014B',
            'f': 'f',
            'v': 'v',
            'theta': '\u03B8',
            'eth': '\u00F0',
            'esh': '\u0283',
            'ezh': '\u0292',
            '-': " "
            }


import Agent, Vowel, Game_fns, profile, time 
from tkinter import *

'''Created April 2014 HJMS
Last Update June 2015 HJMS
Computational Linguistics project to simulate the evololution of a vowel system
Uses evolutionary game theory, imitation game models
Agents are organized into generations who play imitation games
Conventions are tracked by generation to observe shifts
run with Agent.py, Vowel.py, Prototype.py Game_fns.py, also import Graphics.py
'''
def start_game():
        '''initialize a new game
        default parameters are overwritten if called by get_param()
        assigns old_english base convention to first generation'''
        default_game = Game_fns.Game_fns()
        default_game.game_driver()

def get_param():
        '''prompts user for number of generations, agents and whether output is printed
        initializes a new game using input'''
        custom_game = Game_fns.Game_fns(False)
        custom_game.game_driver()
        
def main():
        menu()

def reset():
        menu()

def menu():
        '''limited menu
        1: start a game with defaults ("quick start")
        2: prompt user for game paramets (control size, output)
        3: start a game with defaults and run profile (show time complexity)
        reset until user quits (any key other than 'r')'''
        
        while True:
                menu_prompt = "Options \n 1 -- run with default parameters \n 2 -- input parameters \n 3 -- show profile with default parameters\n"
                command = input(menu_prompt)
                options = {'1' : start_game,
                                '2' : get_param,
                                '3' : show_profile
                           }
                options[command]()


def show_profile():
        '''runs profile() on a game with default parameters.
        For testing purposes (complexity, identifying bottlenecks)
        Increases total runtime significantly, suggest using fewer gens/agents'''
        profile.run('start_game()')

def get_time():
         print(time.ctime())
         
class Application(Frame):

    def createWidgets(self):
        # Close window #
        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        # New game with default calls start_game()#
        quick_run = Button(self)
        quick_run["text"] = "Use defaults"
        quick_run["fg"]   = "blue"
        quick_run["command"] = start_game

        quick_run.pack({"side": "left"})
        
        # New game with user input calls get_param()   #
        user_param = Button(self)
        user_param["text"] = "Use input"
        user_param["fg"]   = "blue"
        user_param["command"] = get_param

        user_param.pack({"side": "left"})

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
#show_profile() #for finding bottlenecks
root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()


#testing method generates a new Vowel with random attributes
def dum_vowel(self):
        pos_lower = 700
        pos_upper = 2400
        pos = random.randint(pos_lower, pos_upper)
        closeLower = 275
        closeUpper = 800
        closed = random.randint(close_lower, close_upper)
        
        return Vowel.Vowel(pos, closed, random.randint(1, 250))
 
#testing method makes a list of vowels with random attributes for dummy repertoire
def dum_rep(self, size):
        vowels = list()
        if size > 0:
            #print("Randomly generating a set of", size, "vowels...")#
            for i in range(size):
                vowels.append(self.dum_vowel())
        return vowels 

#testing method creates a new agent with a random rep. of given size
def dum_agent(self, name):
        dummy = Agent.Agent(name)
        dummy.set_rep(self.dum_rep(10))
        return dummy

# voss
Complex system model of language change

GETTING STARTED
Installation and libraries
You'll need Python 3.4+ to run VoSS
You'll also need the TKinter library. 

Running the program
Linux
From the ".../Language-Science-Models-Lab/voss" directory, enter
>>python3 Game_fns.py

Using IDLE in Windows/Linux
Open "Game_fns.py".
Use the f5 key or "Run > Run Module" from the menu. 

The command menu will show in the terminal or IDLE shell. 
Use "run" to run a simulation using the default parameters. 
Use "demo" to get a walk-through and setthe various parmeters. 

Setting up simulations
(There is a much longer, more detailed file available on request
if you need more information on how the program works.)

PARAMETERS / COMMANDS

*run* 

Starts a new game with current settings. No arguments needed. 

New games begin with one group of agents with a starting age equivalent to half of an agent lifespan, and with repertoires of vowels which are close imitations to the base convention prototypes. These are generated using the guess_by_margin method, except that the margin is set to .1 x perception ERB. 

From a higher-level perspective, this is meant to be like a group of people who all speak the same dialect suddenly getting dumped into an isolated environment (say, an island) and immediately reproducing and growing a population there.

At every ‘time step,’ all agents advance in age by one. If the population size is less than the max population size limit, a new group of agents will be ‘born’ i.e. appended to the population with an age of zero. The game will pause after a number of cycles and show the results in a graphic output window, after which the menu will appear and accept commands again. 


*extend*

continue running the current game for another set of cycles. Does not reset any of the parameters or replace the agents. 

*save*

Saves 3 files: 1 .txt and 2 .eps
The ‘save’ command writes a condensed copy of the output to a txt file. The file will include the text step reports (assuming ‘show’ is turned on), the final text report showing the displacement values by word, and the lexicon report (if ‘report’ has been called prior to saving) and the ‘details’ report showing the agents’ repertoires (if that report has been called up already). 

*cycles* 

Set the number of agent groups tracked over lifespan. 
Input: int >= 1
Default: 1; set in Game_fns.init() 
This is a pretty safe parameter; the only danger is that if you set the cycles really high then it will take a long time to run and you may have to abort (ctrl+c). 

*size*

set the population peak limit. 

At every step, the population will either grow (if the number of live agents is less than the size limit) or stay the same if the population has reached the size limit. If the oldest group has reached the lifespan limit, it will be removed at the end of the step and a new group will be added at the beginning of the next. 

*details*

Shows the vocabularies of all live agents. 

*lifespan*

set the age at which agents are removed from population.

The age of maturity is (.10 * lifespan) + 1 and represents the point at which agents transition from being children to adults and from interactive listeners to speakers only. This is also where agents ‘purge’ their extraneous vowels so that adults have only vowels with a weight strictly greater than 0. 

*show*

shows live agents’ repertoires as layered points in the vowel space, followed by the mean centers for each prototype at the end of each step.

*Symbols*

Toggles the mean center markers to show the IPA symbols or spots. The symbols don’t save in the eps files, so if you save it will automatically use the spots instead. 

*protos*

specify the prototypes in the base convention.
input: string of prototype names separated by commas and spaces e.g. 
>>I, I:, retracted_a, u

*margin*

The perception defines the radius of the circle centered on an incoming signal and within which an agent will recognize that the incoming vowel matches a phone in its repertoire.  The agent ‘de-assimilates’ the vowel before matching it. If no match is found within perception margin, the agent will imitate the deassimilated vowel and store the imitation as a phone.

*prox*

set a supplement (in ERB) for the proximity margin. 
input: float (can be negative). The final margin will be vowel.weight + prox for each percept. If the result is a negative number, it will default to 0 ERB.

*phone* (imitation / phone_radius)

The ‘phone’ command sets the phone_radius variable, which is the radius of the circle within which an agent creates an imitation of a signal it couldn’t match. The circle’s center is the ‘corrected’ (de-assimilated) version of the signal. 

*noise* (vowel production / phone_radius_noise)

The ‘noise’ command sets the phone_radius_noise variable, which is the radius around an agent’s percept (after being coarticulated/assimilated), within which the  agent utters a vowel when saying a word.

*report*

prints a table with current stats from the game, including 
1. the active prototypes and their displacement from the starting positions, 
2. the words in the lexicon and the number of agents using each prototype to pronounce that word
3. the number of agents who have multiple variants of convention prototypes in their repertoires (i.e. “near splits”) 

*demo*

interactively set up a new game. 
The program will give a description of each parameter followed by a prompt for input, then run the game and pause for another command after the cycles have completed. 

*language*

use one of the preset lists of vowels defined in Game_fns. 

The program will list the names of the language presets available. To use one, enter the name as it appears in the list. A window will pop up showing a preview of the base convention for the preset with circles indicating the initial effective proximity margin around each class. 

Click in the window to close it. If you are satisfied with it and the rest of the parameters, enter “run” to start a game. Otherwise you can make any changes (including overriding the language preset to be used) before starting. 

The presets are based on research from wikipedia, the U of C Phonetic Inventory and a handy website “A Survey of some Vowel Systems.” They have not (yet) been corroborated by any expert and quite possibly contain some inaccuracies. 

*sampling*

options: "phones" or "vowels"
In the program, ‘sampling’ refers to the collection of the agents’ pronunciations of words in the lexicon, which are represented by colored dots in the chart. Sampling is shown at every step if ‘show’ is on, and at the end if ‘show’ is off. Sampling never includes babies’ vowels/phones--unless you’re in ‘micro’ mode, where it will show The Chosen One’s phones even when they are a baby. The sampling options are ‘phones’ and ‘vowels’. These have to be consistent (meaning, whichever one is used for sampling will also be used to get prototypes for the convention).

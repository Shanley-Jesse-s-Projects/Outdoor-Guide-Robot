#Author: Evan Maraist
#Email: emaraist1357@gmail.com
#TEAM BAST - ESET 420 Capstone

from Hologram.HologramCloud import Hologram
from multiprocessing import Process, Queue
from VALE_communication import *
import signal
from contextlib import contextmanager
from movement import movement as move_class

#Connect to internet via Nova hologram
def connect():
    result = False
    while(result == False):
        result = hologram.network.connect()

#this process will be responsible for moving Vale to its destination
def movement(dest, m2m, m2s, s2m):
    current = move_class(dest,m2m, m2s,s2m) #initialize movement object
    Keep_Going = True
    while Keep_Going is not False: #run until Vale arrives at target or is told to stop
        # Check speech-to-motor queue, see if any orders were received
        orders = current.checkQueue()
        if orders == 'STOP':
            #Vale was told to stop. Wait until told something else.
            current.stop()
            Keep_Waiting = True
            while Keep_Waiting is True:
                got = s2m.get() #read speech-to-motor queue
                if got == 'END':
                    Keep_Waiting = False
                    orders = 'END'
                if got == 'RESUME':
                    Keep_Waiting = False
        #Vale was told to reroute or stop running
        if orders == 'END':
            Keep_Going = False
        current.updateGeo() #get current GPS location, update waypts respectively
        current.launch() #hand off to PID and obstacle avoidance code
    # if we've exited the while loop that means we're not moving anymore
    current.stop() # make sure motors have stopped
    current.cleanUp() # delete created objects, save memory
    print("Motor thread ended.")

#this process will be responsible for listening to a user's input
def user_interface(s2main,s2move,m2s ): # listen for user input and react
    Keep_Going = True
    while Keep_Going is not False:
        status = m2s.get()
        if status == 'ARRIVED': #Vale has arrived at destination
            say('We have arrived. Thank you for using Vale.')
            break
        #listen for 'Hey Vale'
        speech = speech2text(r, talk)
        if hey_Vale(speech) is True: #User wants to issue input
            say('Hey User')
            s2move.put('STOP')
            listening = True
            while listening is True: # listen for orders
                speech = speech2text(r, talk)
                orders = command_check(speech)
                if orders == 'stop': # user said stop, wait for user to say resume
                    listening = False
                if orders == 'resume': # user wants to resume along path
                    s2move.put('RESUME')
                    listening = False
                if orders == 'reroute' or orders == 'end': # user wants to input a new destination or is done
                    s2move.put('REROUTE')
                    s2main.put('REROUTE')
                    listening = False
                    Keep_Going = False
                if orders == 'deactivate': #User told Vale to turn off
                    s2move.put('END')
                    s2main.put('DEACTIVATE')
                    listening = False
                    Keep_Going = False
    print("UI thread ended.")

#main code
if __name__ == '__main__':
    #connect to internet via Nova
    connect()

    #create data queues for communicating between processes and main
    #this many queues is probably unecessary, but I wanted to be safe *shrug*
    speech_to_move = Queue()
    speech_to_main = Queue()
    move_to_speech = Queue()
    move_to_main = Queue()


    #initial greeting
    begin()

    #Run until told to deactivate
    run = True
    while run == True:

        #request instructions
        say('The Vale autonomous guide is ready to begin guidance.')

        #Receive instructions
        have_job = False
        target_Bldg = None
        while have_job == False: #loop until user has input instructions
            speech = speech2text(r, talk)
            if hey_Vale(speech) == True: #if user says 'Hey vale'
                while target_Bldg == None: #until user inputs correct building name
                    speech = speech2text(r, talk)
                    target_Bldg, have_job = check_bldg(speech,have_job,target_Bldg)

        #Instructions received, create and initialize threads
        ui = Process(target= user_interface, args=(speech_to_main, speech_to_move, move_to_speech))
        move = Process(target = movement, args= (target_Bldg, move_to_main, move_to_speech, speech_to_move))

        #start threads
        ui.start()
        move.start()

        El_dorado = True #On the trail we blaze
        while El_dorado == True:
            # wait for responses from threads
            got = None
            if speech_to_main.empty() is False: #read from speech queue
                got = speech_to_main.get()
                if got == 'DEACTIVATE':
                    El_dorado = False
                    run = False
                if got == 'REROUTE': # user requested to change directions
                    EL_dorado = False
            if move_to_main.empty is False: # read from move queue
                got = speech_to_main.get()
                if got == 'ARRIVED':
                    # clean up old objects reset while loop and wait for new instructions
                    El_dorado = False

        #Gives processes five seconds to close before terminating
        ui.join(5)
        move.join(5)

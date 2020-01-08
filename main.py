from pynput import keyboard as kb
import keyboard
import time
import os
import csv
import pyperclip
from tkinter import Tk


##
##  May want to branch out different "type"s into functions
##
def phrase():
    return 1

def url():
    return 1

def dynamicPhrase(): ## Should this be subset of phrase function??
    return 1

##
##
##

def clipboardReplace(string,options):
    for o in options:
        if o[0] == 'clpb':
            r = Tk()     
            r.withdraw()     
            if r.clipboard_get() is not None:
                clpbrd = str(r.clipboard_get())
                if (int(o[1]) > len(clpbrd) > int(o[2])) and ((o[3] == "True" and clpbrd.isdigit()) or o[3] == "False") and (o[4] in clpbrd):
                    string = string.split('|')[int(o[5])].replace('{}',clpbrd)
    return(string.split('|')[0])
     


def processEvent(eventRow,keyCheck,dynamic=False):
    options = [] # Defining our options array then looping through them
    if eventRow['options'] != '':
        opts = eventRow['options'].split('|')
        for op in opts:
            options.append(op.split(','))

    if dynamic == True:
        phrase = str(eventRow['phrase'].replace('{}',keyCheck[keyCheck.index('{') + 1:keyCheck.index('}')]))
    else:
        phrase = str(clipboardReplace(eventRow['phrase'],options))

    if eventRow['type'] == 'url': # If it's a url
        url = phrase 

        os.system('start chrome "' + str(url) + '"') # Open the URL - May add browser selector later
        return True

    elif eventRow['type'] == 'p': # If it's a phrase
        for i in range(len(keyCheck) + 1): # Deleting the tigger because obviously we want the replaced by the phrase
            keyboard.send('backspace')
        
        b = pyperclip.paste()
        pyperclip.copy(phrase)
        try:
            keyboard.send('ctrl+v')
        except:
            print("Couldn't paste")
        finally:
            time.sleep(.8)
            pyperclip.copy(b)
    return True

def keyPressed(event):

    global released

    print(released)

    if released: # Only process key if it's due to genuine key press

        # Converting this stupid pynput object to a string that we can DO SOMETHING WITH
        event = str(event)
        if event[0:3] == "Key":
            event = event[4:] 
        else:
            print(event[0:2])
            event = event[1:-1]
        print(event)

        # Doing stuff
        if event == "backspace" and len(queue) > 0: # Allows us to correct mispelled keywords
            queue.pop(0)
        elif event not in modifiers:
            queue.insert(0," " if event == "space" else event) # Adding current keypress to queue - Also translating "space" into " ".
            if(len(queue) > 32): # We only want to track 32 recent presses (max length for hotkey) if larger pop off oldest one
                queue.pop()


        print(queue)
            
        if hotkeyTrigger in queue:
            keyCheck = queue[0 if queue.index(hotkeyTrigger) == 0 else queue.index(hotkeyTrigger)-1::-1] 
                # There's a lot going on here. We slice the array going backwards from where the trigger is
                # But there's a condition because we don't want to include the trigger so we need the starting index to be -1 of the trigger's index. But if trigger is index 0 then we just want 0
                # This might be overly complicated but it works so hush

            keyCheck = ''.join(keyCheck) # Converting our keypress queue into a string

            for key in hotkeyArray:
                if keyCheck in key: 
                    queue.clear() # Clearing to ensure there aren't two triggers
                    processEvent(key[keyCheck],keyCheck) # Do the stuff
                elif '{' in keyCheck and '}' in keyCheck:
                    print("at least we see the brackets")
                    if keyCheck[keyCheck.index('}') + 1:] in key:
                        queue.clear()
                        processEvent(key[keyCheck[keyCheck.index('}') + 1:]],keyCheck,True)

        released = False if event != "shift" else True # Setting released to false to ensure that no other keystrokes come in due to the key being held. resume() will swap this to true when the key is released

def resume(key):
    global released
    print(released)
    released = True

def loadSettings():
    with open('hotkey.csv', 'rt') as file:
        reader = iter(csv.reader(file, delimiter=','))
        hotkeyArray.clear()
        next(reader)
        for row in reader:
            hotkeyArray.append({
                row[0]:{
                    'type':row[1],
                    'phrase':row[2],
                    'options':row[3]
                }
            })
        print("Loaded Settings!")

if __name__ == "__main__":

    hotkeyTrigger = '$' # Sets hotkey trigger. Should be dynamic or configureable 
    hotkeyArray = []
    modifiers = ["caps_lock","cmd","cmd_l","cmd_r","ctrl","ctrl_r","delete","down","end","enter","esc","home","left","page_down","page_up","right","shift","shift_l","shift_r","space","tab","up","media_play_pause","media_volume_mute","media_volume_down","media_volume_up","media_previous","media_next","insert","menu","num_lock","pause","print_screen","scroll_lock","ctrl","alt","alt_l","alt_r","ctrl_l"]
    queue = [] # Initializes our keypress queue
    released = True # This is needed for the mac version (With Pynput) because if the key is held it will be added over and over to the queue. We stop this by tracking the release() event

    loadSettings() # Load CSV file with hotkeys and settings
    with kb.Listener(on_press=keyPressed,on_release=resume) as listener:
        listener.join()

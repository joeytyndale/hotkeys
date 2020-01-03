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
                else:
                    string = string.split('|')[0]
    return(string)
     


def processEvent(eventRow,keyCheck,dynamic=False):
    options = [] # Defining our options array then looping through them
    if eventRow['options'] != '':
        opts = eventRow['options'].split('|')
        for op in opts:
            options.append(op.split(','))

    if eventRow['type'] == 'url': # If it's a url
        url = clipboardReplace(eventRow['phrase'],options)
       
        os.system('start chrome "' + str(url) + '"') # Open the URL - May add browser selector later
        return True

    elif eventRow['type'] == 'p': # If it's a phrase
        for i in range(len(keyCheck) + 1): # Deleting the tigger because obviously we want the replaced by the phrase
            keyboard.send('backspace')
        if dynamic == True:
            phrase = str(eventRow['phrase'].replace('{}',keyCheck[keyCheck.index('{') + 1:keyCheck.index('}')]))
        else:
            phrase = str(clipboardReplace(eventRow['phrase'],options))
        
        b = pyperclip.paste()
        pyperclip.copy(phrase)
        try:
            keyboard.send('ctrl+v')
        except:
            print("Couldn't paste")
        finally:
            time.sleep(.3)
            pyperclip.copy(b)
    return True

def keyPressed(event):
    if event.name == "backspace" and len(queue) > 0: # Allows us to correct mispelled keywords
        queue.pop(0)
    elif event.name not in keyboard.all_modifiers:
        queue.insert(0,event.name) # Adding current keypress to queue
        if(len(queue) > 32): # We only want to track 32 recent presses (max length for hotkey) if larger pop off oldest one
            queue.pop()
        
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
                if keyCheck[keyCheck.index('}') + 1:] in key:
                    queue.clear()
                    processEvent(key[keyCheck[keyCheck.index('}') + 1:]],keyCheck,True)

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
    keyboard.add_word_listener("resetsetting",loadSettings,triggers=['s']) # Used to reload the csv file

    hotkeyTrigger = '$' # Sets hotkey trigger. Should be dynamic or configureable 
    hotkeyArray = []
    queue = [] # Initializes our keypress queue

    loadSettings() # Load CSV file with hotkeys and settings
    keyboard.on_press(keyPressed) # SOMEONE PRESSED SOMETHING
    keyboard.wait() # Don't close our program thanks

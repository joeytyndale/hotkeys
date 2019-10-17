import keyboard
import os
import csv
import pyperclip
from tkinter import Tk

def processEvent(eventRow):
    
    options = [] # Defining our options array then looping through them
    if eventRow['options'] != '':
        opts = eventRow['options'].split('|')
        for op in opts:
            options.append(op.split(','))

    # What's the type
    if eventRow['type'] == 'url': # If it's a url
        url = eventRow['phrase']
        for o in options:
            if o[0] == 'clpb':
                url = eventRow['phrase'].split('|')[0]
                r = Tk()     
                r.withdraw()     
                clpbrd = r.clipboard_get()     
                if (int(o[1]) > len(clpbrd) > int(o[2])) and ((o[3] == True and clpbrd.isdigit()) or o[3] != True) and (o[4] in clpbrd):
                    url = eventRow['phrase'].split('|')[1].replace('{}',clpbrd)
        
        os.system('start firefox ' + url) # Open the URL - May add browser selector later

    elif eventRow['type'] == 'p': # If it's a phrase
        return True
    
    # What are the options
        # Execute options in order? Yeah right?








def showCallback(event):
    if event.name == "backspace" and len(queue) > 0:
        queue.pop(0)
    else:
        queue.insert(0,event.name) # Adding current keypress to queue
    if(len(queue) > 32): # We only want to track 32 recent presses (max length for hotkey) if larger pop off oldest one
        queue.pop()
    if hotkeyTrigger in queue:
        keyCheck = queue[0 if queue.index(hotkeyTrigger) == 0 else queue.index(hotkeyTrigger)-1::-1] 
            # There's a lot going on here. We slice the array going backwards from where the trigger is
            # But there's a condition because we don't want to include the trigger so we need the starting index to be -1 of the trigger's index. But if trigger is index 0 then we just want 0
            # This might be overly complicated but it works so hush

        keyCheck = ''.join(keyCheck)

        for key in hotkeyArray:
            if keyCheck in key: 
                queue.clear() # Clearing to ensure there aren't two triggers
                processEvent(key[keyCheck]) ## Eventurally I want this to be the end of this if statement. The processEvent function should handle the rest from here


                ###
                ### THE MEAT AND POTATOS
                ###
                if key[keyCheck]['type'] == 'p':
                    for i in range(len(keyCheck) + 1):
                        keyboard.send('backspace')
                    pyperclip.copy(key[keyCheck]['phrase'])
                    keyboard.send('ctrl+v')
                ##elif key[keyCheck]['type'] == 'url':
                    ##url = key[keyCheck]['phrase']
                    ##os.system('start firefox {}'.format(url))

                ###
                ### OH YEAH
                ###


def loadSettings():
    with open('hotkey.csv', 'rt') as file:
        reader = csv.reader(file, delimiter=',')
        hotkeyArray.clear()
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
    keyboard.add_word_listener("/resetsetting",loadSettings,triggers=['s'])
    hotkeyTrigger = '/' # Sets hotkey trigger. Should be dynamic or configureable 
    hotkeyArray = []
    keyList = []
    queue = [] # Initializes our keypress queue
    loadSettings() # Load CSV file with hotkeys and settings
    keyboard.on_press(showCallback) # SOMEONE PRESSED SOMETHING
    keyboard.wait() # Don't close our program thanks

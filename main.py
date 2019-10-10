import keyboard
import os
import csv
import pyperclip
import webbrowser


def showCallback(event):
    queue.insert(0,event.name) # Adding current keypress to queue
    if(len(queue) > 32): # We only want to track 32 recent presses (max length for hotkey) if larger pop off oldest one
        queue.pop()
    if hotkeyTrigger in queue:
        keyCheck = queue[0 if queue.index(hotkeyTrigger) == 0 else queue.index(hotkeyTrigger)-1::-1] 
            # There's a lot going on here. We slice the array going backwards from where the trigger is
            # But there's a condition because we don't want to include the trigger so we need the starting index to be -1 of the trigger's index. But if trigger is index 0 then we just want 0
            # This might be overly complicated but it works so hush

        keyCheck = ''.join(keyCheck)
        ##print("Current Key: " + keyCheck)
        for key in hotkeyArray:
            if keyCheck in key: 
                queue.clear() # Clearing to ensure there aren't two triggers
                
                ###
                ### THE MEAT AND POTATOS
                ###
                if key[keyCheck]['type'] == 'p':
                    for i in range(len(keyCheck) + 1):
                        keyboard.send('backspace')
                    pyperclip.copy(key[keyCheck]['phrase'])
                    keyboard.send('ctrl+v')
                    print("Executed hotkey")
                    ##keyboard.write(key[keyCheck]['phrase'])
                    ##print(key[keyCheck]['phrase'])
                elif key[keyCheck]['type'] == 'url':
                    url = key[keyCheck]['phrase']
                    webbrowser.open(url)
                    print("Opened page")

                ###
                ### OH YEAH
                ###

    ##print(' '.join(queue))

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

from threading import Thread
import subprocess
import re
import os
import copy
import board
import adafruit_character_lcd.character_lcd as character_lcd
import digitalio
import RPi.GPIO as GPIO, time

#GPIO SETUP
#imports the RPi.GPIO library and maps to the buttons.
#Pull the resistors up so they trigger on low. This is my pin setup, yours can be different. 

GPIO.setmode(GPIO.BCM)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #Button 19 increments the disk #,  when it hits 7 it'll roll back to 1. 
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #Button 21 increments the track #, when it hits 15 it'll roll back to 15. You can increase this, just add more libraries. I currently don't have protections for it. 
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #Button 26 displays the selected disk/track. 
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #Button 22 locks the choice in, asks for an input frequency. 
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #Hmmm. 
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #Calls a function to wait for the button, and start the songs. 
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)   #Okay, I forgot. 
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)    #Whatever. 

currentDisk = 0
currentTrack = 0


#LCD SETUP PINS: 
#Find a setup guide for the controller here ###LINK###
lcd_rs = digitalio.DigitalInOut(board.D17)
lcd_en = digitalio.DigitalInOut(board.D27)
lcd_d7 = digitalio.DigitalInOut(board.D6)
lcd_d6 = digitalio.DigitalInOut(board.D5)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d4 = digitalio.DigitalInOut(board.D23)
lcd_backlight = digitalio.DigitalInOut(board.D4)


#Set your LCD Specs 
lcd_columns = 40
lcd_rows = 2


#Declare LCD
lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)


#Set up album track libraries
IsThisIt_dict = {



                1: "Is This It",

                 2: "The Modern Age",

                 3: "Soma",

                 4: "Barely Legal",

                 5: "Someday",

                 6: "Alone, Together",

                 7: "Last Nite",

                 8: "Hard To Explain",

                 9: "When It Happened",

                 10: "Trying Your Luck",

                 11: "Take It Or Leave It" }



RoomOnFire_dict = {



                1: "What Ever Happened",

                 2: "Reptilia",

                 3: "Automatic Stop",

                 4: "12:51",

                 5: "You Talk Way Too Much",

                 6: "Between Love And Hate",

                 7: "Meet Me in the Bathroom",

                 8: "Under Control",

                 9: "The Way It Is",

                 10: "The End Has No End",

                 11: "I Can't Win" }



FirstImpressionsofEarth_dict = {



                1: "You Only Live Once",

                 2: "Juicebox",

                 3: "Heart in a Cage",

                 4: "Razorblade",

                 5: "On the Other Side",

                 6: "Vision of Division",

                 7: "Ask me Anything",

                 8: "Electricityscape",

                 9: "Killing Lies",

                 10: "Fear of Sleep",

                 11: "15 Minutes",

                 12: "Ize of the World",

                 13: "Evening Sun",

                 14: "Red Light" }



Angles_dict = {



                1: "Machu Picchu",

                 2: "Under Cover of Darkness",

                 3: "Two Kinds of Happiness",

                 4: "You're So Right",

                 5: "Taken for a Fool",

                 6: "Games",

                 7: "Call Me Back",

                 8: "Gratisfaction",

                 9: "Metabolism",

                 10: "Life is Simple in the Moonlight" }



ComedownMachine_dict = {



                1: "Tap Out",

                 2: "All the Time",

                 3: "One Way Trigger",

                 4: "Welcome to Japan",

                 5: "80's Comedown Machine",

                 6: "50/50",

                 7: "Slow Animals",

                 8: "Partners in Crime",

                 9: "Chances",

                 10: "Happy Ending",

                 11: "Call It Fate, Call It Karma",

                 12: "Fast Animals" }



TheNewAbnormal_dict = {



                1: "The Adults Are Talking",

                 2: "Selfless",

                 3: "Brooklyn Bridge to Chorus",

                 4: "Bad Decisions",

                 5: "Eternal Summer",

                 6: "At the Door",

                 7: "Why are Sundays So Depressing",

                 8: "Not the Same Anymore",

                 9: "Ode to the Mets" }

#Declare a song library as well, these are just key pair matches I use later for the lrc files located in lrc_lib. 
song_lib = {

    "Is This It": "lrc_lib/Is_This_It.lrc",
    "The Modern Age": "lrc_lib/The_Modern_Age.lrc",
    "Soma": "lrc_lib/Soma.lrc",
    "Barely Legal": "lrc_lib/Barely_Legal.lrc",
    "Someday": "lrc_lib/Someday.lrc",
    "Alone, Together": "lrc_lib/Alone,_Together.lrc",
    "Last Nite": "lrc_lib/Last_Nite.lrc",
    "Hard To Explain": "lrc_lib/Hard_To_Explain.lrc",
    "When It Happened": "lrc_lib/When_It_Happened.lrc",
    "Trying Your Luck": "lrc_lib/Trying_Your_Luck.lrc",
    "Take It Or Leave It": "lrc_lib/Take_It_Or_Leave_It.lrc",
    "What Ever Happened": "lrc_lib/What_Ever_Happened.lrc",
    "Reptilia": "lrc_lib/Reptilia.lrc",
    "Automatic Stop": "lrc_lib/Automatic_Stop.lrc",
    "12:51": "lrc_lib/12:51.lrc",
    "You Talk Way Too Much": "lrc_lib/You_Talk_Way_Too_Much.lrc",
    "Between Love And Hate": "lrc_lib/Between_Love_And_Hate.lrc",
    "Meet Me in the Bathroom": "lrc_lib/Meet_Me_in_the_Bathroom.lrc",
    "Under Control": "lrc_lib/Under_Control.lrc",
    "The Way It Is": "lrc_lib/The_Way_It_Is.lrc",
    "The End Has No End": "lrc_lib/The_End_Has_No_End.lrc",
    "I Can't Win": "lrc_lib/I_Can't_Win.lrc",
    "You Only Live Once": "lrc_lib/You_Only_Live_Once.lrc",
    "Juicebox": "lrc_lib/Juicebox.lrc",
    "Heart in a Cage": "lrc_lib/Heart_in_a_Cage.lrc",
    "Razorblade": "lrc_lib/Razorblade.lrc",
    "On the Other Side": "lrc_lib/On_the_Other_Side.lrc",
    "Vision of Division": "lrc_lib/Vision_of_Division.lrc",
    "Ask me Anything": "lrc_lib/Ask_me_Anything.lrc",
    "Electricityscape": "lrc_lib/Electricityscape.lrc",
    "Killing Lies": "lrc_lib/Killing_Lies.lrc",
    "Fear of Sleep": "lrc_lib/Fear_of_Sleep.lrc",
    "15 Minutes": "lrc_lib/15_Minutes.lrc",
    "Ize of the World": "lrc_lib/Ize_of_the_World.lrc",
    "Evening Sun": "lrc_lib/Evening_Sun.lrc",
    "Red Light": "lrc_lib/Red_Light.lrc",
    "Machu Picchu": "lrc_lib/Machu_Picchu.lrc",
    "Under Cover of Darkness": "lrc_lib/Under_Cover_of_Darkness.lrc",
    "Two Kinds of Happiness": "lrc_lib/Two_Kinds_of_Happiness.lrc",
    "You're So Right": "lrc_lib/You're_So_Right.lrc",
    "Taken for a Fool": "lrc_lib/Taken_for_a_Fool.lrc",
    "Games": "lrc_lib/Games.lrc",
    "Call Me Back": "lrc_lib/Call_Me_Back.lrc",
    "Gratisfaction": "lrc_lib/Gratisfaction.lrc",
    "Metabolism": "lrc_lib/Metabolism.lrc",
    "Life is Simple in the Moonlight": "lrc_lib/Life_is_Simple_in_the_Moonlight.lrc",
    "Tap Out": "lrc_lib/Tap_Out.lrc",
    "All the Time": "lrc_lib/All_the_Time.lrc",
    "One Way Trigger": "lrc_lib/One_Way_Trigger.lrc",
    "Welcome to Japan": "lrc_lib/Welcome_to_Japan.lrc",
    "80's Comedown Machine": "lrc_lib/80's_Comedown_Machine.lrc",
    "50/50": "lrc_lib/50/50.lrc",
    "Slow Animals": "lrc_lib/Slow_Animals.lrc",
    "Partners in Crime": "lrc_lib/Partners_in_Crime.lrc",
    "Chances": "lrc_lib/Chances.lrc",
    "Happy Ending": "lrc_lib/Happy_Ending.lrc",
    "Call It Fate, Call It Karma": "lrc_lib/Call_It_Fate,_Call_It_Karma.lrc",
    "Fast Animals": "lrc_lib/Fast_Animals.lrc",
    "The Adults Are Talking": "lrc_lib/The_Adults_Are_Talking.lrc",
    "Selfless": "lrc_lib/Selfless.lrc",
    "Brooklyn Bridge to Chorus": "lrc_lib/Brooklyn_Bridge_to_Chorus.lrc",
    "Bad Decisions": "lrc_lib/Bad_Decisions.lrc",
    "Eternal Summer": "lrc_lib/Eternal_Summer.lrc",
    "At the Door": "lrc_lib/At_the_Door.lrc",
    "Why are Sundays So Depressing": "lrc_lib/Why_are_Sundays_So_Depressing.lrc",
    "Not the Same Anymore": "lrc_lib/Not_the_Same_Anymore.lrc",
    "Ode to the Mets": "lrc_lib/Ode_to_the_Mets.lrc"
}

#Reads a lrc file from a filename, in the Song_or_Title.lrc format
def read_lrc_file(filename):
    """Read an .lrc file and return a list of (time, line) tuples."""
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Regular expression pattern for matching time stamps
    pattern = re.compile(r'\[(\d+):(\d+\.\d+)\](.*)')

    parsed_lines = []

    for line in lines:
        match = pattern.match(line)
        if match:
            minutes, seconds, text = match.groups()
            total_seconds = int(minutes) * 60 + float(seconds)
            parsed_lines.append((total_seconds, text.strip()))

    return parsed_lines


#Uses GPIO 2 as an incrementer to choose the frequency. 
def get_frequency():
        freq = 96.0  # Starting frequency
        while True:
                if freq > 108.0:
                        freq = 88.0  # Reset to starting frequency if exceeds 108
                if GPIO.input(2) == False:
                        freq += 0.2
                lcd.clear()
                lcd.message = f"Broadcast Frequency: {freq} MHz"
                time.sleep(0.1)  # Debouncing and rate control
                if GPIO.input(20) == False:  # Check if pin 4 is high to exit frequency adjustment
                        break
        return freq



#Plays song lyrics in the library, otherwise it'll print no lyrics. 
def play_song_from_title(song_title):
    """
    Plays the lyrics of a song based on its title.
    """
    lrc_filename = song_lib.get(track)
    if lrc_filename:
        play_lrc(lrc_filename)
    else:
        lcd.message = f"No .lrc file found for song: {song_title}."


#plays a .lrc from a filename

def play_lrc(filename):
    """Display lyrics from an .lrc file on an LCD based on their timestamps."""
    lyrics = read_lrc_file(filename)
    start_time = time.time()

    for index, (timestamp, line) in enumerate(lyrics):
        while time.time() - start_time < timestamp:
            time.sleep(0.1)

        if line:  # Only print non-empty lines
            lcd.clear()  # Clear previous line
            lcd.message = line  # Print the lyric line on the LCD

        # Wait for the next timestamp or clear after the last line
        if index + 1 < len(lyrics):
            next_timestamp, _ = lyrics[index + 1]
            while time.time() - start_time < next_timestamp:
                time.sleep(0.1)
        else:
            time.sleep(2)  # Pause for a short duration after the last line
            lcd.clear()
#Transmits as root 
def transmit_song(track, freq):
        base_directory = os.path.expanduser('~/LCD/wav_lib')
        wav_file_path = os.path.join(base_directory, f"{track}.wav")
        args = ["sudo", "./transmit", "-f", f"{freq}", wav_file_path]
        subprocess.run(args)
#used in the wav lookup
def underscores(track: str) ->str:
        return track.replace(" ", "_")
#gets the album from the number 
def get_album(selectedDisk):

    if 0 <= selectedDisk < 7:

        if selectedDisk == 1:

            album = "Is This It"

        elif selectedDisk == 2:

            album = "Room On Fire"

        elif selectedDisk == 3:

            album = "First Impressions of Earth"

        elif selectedDisk == 4:

            album = "Angles"

        elif selectedDisk == 5:

            album = "Comedown Machine"

        else:

            album = "The New Abnormal"

        return album

    else:

        return "Invalid"


def clearLCD():
        lcd.message = "                                                                                "

def clearUpper():
        lcd.message = "                                        "

def clearLower():
        lcd.message = "\n                                        "


def get_track(selectedDisk, selectedTrack):

    if 0 <= selectedDisk < 7 and 0 <= selectedTrack < 15:

        if selectedDisk == 1:

           track = IsThisIt_dict[selectedTrack]

        elif selectedDisk == 2:

            track = RoomOnFire_dict[selectedTrack]

        elif selectedDisk == 3:

            track = FirstImpressionsofEarth_dict[selectedTrack]

        elif selectedDisk == 4:

            track = Angles_dict[selectedTrack]

        elif selectedDisk == 5:

            track = ComedownMachine_dict[selectedTrack]

        else:

            track = TheNewAbnormal_dict[selectedTrack]

        return track

    else:

        return "Invalid"

selected = 0


try:
        while True:
                if GPIO.input(12) == False:
                        os.system('sudo shutdown -h now')
                if GPIO.input(19) == False:
                        if currentDisk >= 6:
                                currentDisk = 0
                        currentDisk = currentDisk + 1
                        clearUpper()
                        lcd.message = f"Current Disk is {currentDisk}"
                        time.sleep(0.2)

                if GPIO.input(21) == False:
                        if currentTrack >= 15:
                                currentTrack = 0
                        currentTrack = currentTrack + 1
                        clearLower()
                        lcd.message = f"\nCurrent Track is {currentTrack}"
                        time.sleep(0.2)
                if GPIO.input(26) == False:
                        clearLCD()

                        selected = 1
                        selectedTrack = copy.deepcopy(currentTrack)
                        selectedDisk = copy.deepcopy(currentDisk)

                        album = get_album(selectedDisk)
                        track = get_track(selectedDisk, selectedTrack)

                        lcd.message = f"DiskID: {album}"
                        lcd.message = f"\nTrackID: {track}"
                if GPIO.input(22) == False:
                        lcd.clear()
                        freq = get_frequency()
                        time.sleep(0.2)
                        formatted_track = underscores(track)
                if GPIO.input(20) == False:
                        set_freq = copy.deepcopy(freq)
                        t1 = Thread(target=play_song_from_title, args=(track,))
                        t2 = Thread(target=transmit_song, args=(f"{formatted_track}", f"{set_freq}",))

                        t1.start()
                        t2.start()

                        t1.join()
                        t2.join()
except KeyboardInterrupt:
        GPIO.cleanup()
        lcd.clear()

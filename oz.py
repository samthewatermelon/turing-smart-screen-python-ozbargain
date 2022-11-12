#!/usr/bin/env python3
# A simple Python manager for "Turing Smart Screen" 3.5" IPS USB-C display
# https://github.com/mathoudebine/turing-smart-screen-python
 
import xml
import time
import xml.etree.ElementTree as ET
import inspect
import os
import signal
import sys
from urllib.request import Request, urlopen
from datetime import datetime
 
# Import only the modules for LCD communication
from library.lcd_comm_rev_a import LcdCommRevA, Orientation
from library.lcd_comm_rev_b import LcdCommRevB
from library.lcd_simulated import LcdSimulated
from library.log import logger
 
# Set your COM port e.g. COM3 for Windows, /dev/ttyACM0 for Linux, etc. or "AUTO" for auto-discovery
# COM_PORT = "/dev/ttyACM0"
# COM_PORT = "COM5"
COM_PORT = "AUTO"
 
# Display revision: A or B (for "flagship" version, use B) or SIMU for simulated LCD (image written in screencap.png)
# To identify your revision: https://github.com/mathoudebine/turing-smart-screen-python/wiki/Hardware-revisions
REVISION = "A"
 
stop = False
 
if __name__ == "__main__":
 
    def sighandler(signum, frame):
        global stop
        stop = True
 
 
   # Set the signal handlers, to send a complete frame to the LCD before exit
    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)
    is_posix = os.name == 'posix'
    if is_posix:
        signal.signal(signal.SIGQUIT, sighandler)
 
    # Build your LcdComm object based on the HW revision
    lcd_comm = None
    if REVISION == "A":
        logger.info("Selected Hardware Revision A (Turing Smart Screen)")
        lcd_comm = LcdCommRevA(com_port="AUTO",
                               display_width=320,
                               display_height=480)
    elif REVISION == "B":
        print("Selected Hardware Revision B (XuanFang screen version B / flagship)")
        lcd_comm = LcdCommRevB(com_port="AUTO",
                               display_width=320,
                               display_height=480)
    elif REVISION == "SIMU":
        print("Selected Simulated LCD")
        lcd_comm = LcdSimulated(display_width=320,
                                display_height=480)
    else:
        print("ERROR: Unknown revision")
        try:
            sys.exit(0)
        except:
            os._exit(0)
 
    # Reset screen in case it was in an unstable state (screen is also cleared)
    lcd_comm.Reset()
 
    # Send initialization commands
    lcd_comm.InitializeComm()
 
    # Set brightness in % (warning: screen can get very hot at high brightness!)
    lcd_comm.SetBrightness(level=40)
 
    # Set backplate RGB LED color (for supported HW only)
    lcd_comm.SetBackplateLedColor(led_color=(255, 255, 255))
 
    # Set orientation (screen starts in Portrait)
    orientation = Orientation.PORTRAIT
    lcd_comm.SetOrientation(orientation=orientation)
 
    # Define background picture
    #if orientation == Orientation.PORTRAIT or orientation == orientation.REVERSE_PORTRAIT:
    #    background = "res/backgrounds/example.png"
    #else:
    #    background = "res/backgrounds/example_landscape.png"
 
    # Display sample picture
    #lcd_comm.DisplayBitmap(background)
 
    # Display the current time and some progress bars as fast as possible
    #bar_value = 0
   
    tree = ET.parse('oz.xml')
    root = tree.getroot()   
    background = "logo.png"
   
    lcd_comm.DisplayBitmap(background, x=0, y=0)
 
    def get_topDeal():
        global topvotes
        global title
        global titleTrimmed
        global titleLength
        global desc
    
        topvotes = 0
    
        #req = Request(
        #    url='https://www.ozbargain.com.au/deals/feed', 
        #    headers={'User-Agent': 'Mozilla/5.0'}
        #)
        #webpage = urlopen(req).read()
            
        for child in root[0].iter('item'):
            meta = child.find('{https://www.ozbargain.com.au}meta')
            upvotes = int(meta.get('votes-pos'))
            if upvotes > topvotes:
                topvotes = upvotes       
                title = child[0].text          
                titleTrimmed = child[0].text
                titleLength = len(title)
                desc = child[2].text   
 
    get_topDeal()
   
    while not stop:
        
        titleTrimmed = titleTrimmed[1:] # trims first character
        titleTrimmed = titleTrimmed + ".."
        titleLength = titleLength - 1
        
        if titleLength == 0:
            titleTrimmed = title
            titleLength = len(title)
        
        # Deal Upvotes
        #lcd_comm.DisplayText("upvotes " + str(topvotes), 130, 0,
        #                    font_color=(255, 255, 255),
        #                    background_image=background)
   
        # Deal Title
        lcd_comm.DisplayText(titleTrimmed, 5, 90,
                            font="roboto/Roboto-Italic.ttf",
                            font_size=20,
                            font_color=(0, 0, 255))
                            #background_color=(255, 255, 255))
   
        # Deal Description
        lcd_comm.DisplayText(str(desc), 5, 115,
                            #font="geforce/GeForce-Bold.ttf",
                            font="roboto/Roboto-Thin.ttf",
                            font_size=12,
                            font_color=(0, 0, 0))
                            #background_color=(255, 255, 0))
                            #background_image=background)   
    
        #lcd_comm.DisplayText(str(datetime.now().time()), 160, 2,
        #                     font="roboto/Roboto-Bold.ttf",
        #                     font_size=20,
        #                     font_color=(255, 0, 0),
        #                     background_image=background)
        #
        #lcd_comm.DisplayProgressBar(10, 40,
        #                            width=140, height=30,
        #                            min_value=0, max_value=100, value=bar_value,
        #                            bar_color=(255, 255, 0), bar_outline=True,
        #                            background_image=background)
        #
        #lcd_comm.DisplayProgressBar(160, 40,
        #                            width=140, height=30,
        #                            min_value=0, max_value=19, value=bar_value % 20,
        #                            bar_color=(0, 255, 0), bar_outline=False,
        #                            background_image=background)
 
        #bar_value = (bar_value + 2) % 101   
        #time.sleep(1)
 
    # Close serial connection at exit
    lcd_comm.closeSerial()

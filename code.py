#For Adafruit Magtag 
#Circuit Python 7.1.0
#Displays USGS stream data from selected measurement stations. 

#press a to go to previous.
#press b to lights on/off.
#press c to refresh data without changing river.
#press d to go to next river.

import time
import json
from adafruit_magtag.magtag import MagTag

#Default State for the LEDs on the MagTag. 
#if you want them on change to True.
LightsOn = False
#Set to true show fahrenheit.
convertTemptoF = True
#Time betwee refreshing/advancing to next.
refreshDelay = 600 # 10 minutes

#StationIDs can be singular or multiple. 
StationID = ["11446500"]
#StationID = ["14361500","11446500","14158050"]

#Parameters to display/request
#list of all paramaters at https://help.waterdata.usgs.gov/parameter_cd?group_cd=%
#Some data/query paramaters for refrence:
#00010 temp c.
#00060 flow Cubic Feet per second.
#00065 gauge height in ft.
#72254 Water velocity reading from sensor, feet per second.
#Note: Most sites can only report a few parameters. 
#Check USGS site for the avilable parameters for the desired site(s)/stations(s). 
#Not recommended to use more than 3 or maybe 4 of these due to limited screen size on the magtag.
queryParams = "00060,00065,00010"

StationIndex = 0
riverData = []
magtag = MagTag()
#Setup the text positions for display later.  
#index0 Name of Station
magtag.add_text(text_font="/fonts/Arial-Bold-12.pcf",text_position=(05,10), is_data=False)
xPos = 10
yPos = 30
for items in queryParams:
    magtag.add_text(text_font="/fonts/Arial-12.bdf", text_position=(xPos,yPos), is_data=False)
    yPos = yPos + 20
magtag.add_text(text_font="/fonts/Arial-12.bdf", text_position=(xPos,yPos), is_data=False)
    
#index1 
#magtag.add_text(text_font="/fonts/Arial-12.bdf", text_position=(10,30), is_data=False)
#index2 Gague label
#magtag.add_text(text_font="/fonts/Arial-12.bdf", text_position=(10,50), is_data=False)
#index3
#magtag.add_text(text_font="/fonts/Arial-12.bdf", text_position=(10,70), is_data=False)
#index4 Date/time observed
#magtag.add_text(text_font="/fonts/Arial-12.bdf", text_position=(10,115), is_data=False)

def toggleLights():
    global LightsOn
    if LightsOn:
        print('LEDs: On')
        LightsOn = False
        magtag.peripherals.neopixel_disable = True
        magtag.peripherals.neopixels.fill(0x888888)
    else:
        print('LEDs: Off')
        LightsOn = True
        magtag.peripherals.neopixel_disable = False
        magtag.peripherals.neopixels.fill(0x888888)

if LightsOn == True and magtag.peripherals.neopixel_disable == True:
    magtag.peripherals.neopixel_disable = False
    magtag.peripherals.neopixels.fill(0x888888)
    
def GetRiverData(StIndex):
    global riverData
    siteDataURL = "http://waterservices.usgs.gov/nwis/iv/?format=json&indent=on&sites="+StationID[StIndex]+"&parameterCd="+queryParams+"&siteStatus=all"
    magtag.url = siteDataURL
    try:
        rawData = json.loads(magtag.fetch(auto_refresh=False))
    except:
        print('Problem updating data.')
        if len(riverData) > 0:
            print('Reusing last set of data. Will try again at refresh interval')
            rawData = riverData
        else:
            print('No previous data to use.')
            rawData['value']['timeSeries'][0]['sourceInfo']['siteName']="Unable to connect or update."
    #print (rawData)
    #riverData.clear()
    #Save the data out to a global variable so we can pull it back in later if we need it. 
    riverData = rawData
    print (rawData['value']['timeSeries'][0]['sourceInfo']['siteName'])
    count=1
    magtag.set_text(rawData['value']['timeSeries'][0]['sourceInfo']['siteName'], 0, False)
    for x in rawData['value']['timeSeries']:
        #convert temp to fahrenheit if flag is set and we see the "deg C" unit code. 
        if convertTemptoF and x['variable']['unit']['unitCode'] == "deg C":
            print('deg F : ' + str((float(x['values'][0]['value'][0]['value'])*9/5)+32))
            magtag.set_text('deg F : ' + str((float(x['values'][0]['value'][0]['value'])*9/5)+32),count,False)
        else:
            print(x['variable']['unit']['unitCode'] + " : " + str(x['values'][0]['value'][0]['value']))
            magtag.set_text(x['variable']['unit']['unitCode'] + " : " + str(x['values'][0]['value'][0]['value']),count,False)
        #    print (x['variable']['variableDescription'] + ': ' + x['values'][0]['value'][0]['value'])
        count = count + 1
        #print(count)
    print (x['values'][0]['value'][0]['dateTime'])
    magtag.set_text("At " + x['values'][0]['value'][0]['dateTime'],count,True)
    #sleep for a bit to let the display complete refreshing.
    time.sleep(3.5)
    
print('Monitoring '+str(len(StationID)) + ' stations.')
while True:
    if len(StationID) == 1:
        print('Polling for id'+ str(StationID[StationIndex]))
        GetRiverData(StationIndex) #should always be 0
    if len(StationID) > 1: 
        print('Polling for id: '+ str(StationID[StationIndex]))
        GetRiverData(StationIndex)
    #start regular time delay / button handling loop. 
    starttime = time.monotonic()
    now = time.monotonic()
    print('Seconds until refresh : '+str(refreshDelay - (now - starttime)))
    while now - starttime < refreshDelay:
        time.sleep(0.2)
        #print('Seconds until refresh : '+str(refreshDelay - (now - starttime)))
        #Previous or refresh if only one. 
        if magtag.peripherals.button_a_pressed:
            print('Button A pressed')
            if len(StationID) > 1:
                StationIndex = StationIndex - 1
                if StationIndex < 0:
                    StationIndex = llen(StationID)-1
            elif len(StationID) == 1:
                StationIndex = 0
            GetRiverData(StationIndex)
            starttime = time.monotonic()
        if magtag.peripherals.button_b_pressed:
            print('Button B pressed')
            toggleLights()
        if magtag.peripherals.button_c_pressed:
            print('Button C pressed')
            GetRiverData(StationIndex)
            starttime = time.monotonic()
        #Next or refresh if only one. 
        if magtag.peripherals.button_d_pressed:
            print('Button D pressed')
            if len(StationID) > 1:
                StationIndex = StationIndex + 1
                print(StationIndex)
                if StationIndex > len(StationID)-1:
                    StationIndex = 0
            elif len(StationID) == 1:
                StationIndex = 0
            GetRiverData(StationIndex)
            starttime = time.monotonic()
        now = time.monotonic()
    #after time loop finishes advance if there is something to advance to. 
    if len(StationID) > 1:
        StationIndex = StationIndex + 1
        if StationIndex > len(StationID)-1:
            StationIndex = 0

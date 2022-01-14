Displays info from USGS from a river monitoring station on an Adafruit MagTag.
Not all stations provide the same data points. 

Edit code.py to set the Station ID or IDs for a river and Parametrs. 

StationID = ["14361500"]
#or multiple sites/station IDs. 
`StationID = ["14361500","14158050"]`

Parameters:
00010 temp c
00060 flow Cubic Feet per second
00065 gauge height in ft.
list of all paramaters at https://help.waterdata.usgs.gov/parameter_cd?group_cd=%
note: Sites will only have a few parameters to check USGS site for the avilable parameters for that site. 
`queryParams = "00060,00065,00010"`

#Set convertTemptoF to true show fahrenheit.
`convertTemptoF = False`
`convertTemptoF = True`

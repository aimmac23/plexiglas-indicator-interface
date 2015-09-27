# plexiglas-indicator-interface
Python code to contol a USB plexiglas indicator

## Requirements
 * PyUSB - http://sourceforge.net/projects/pyusb/
 * libusb0 to be installed (native library). Does not currently work with libusb1.
 * For Linux, a new udev rule to be added to allow access to the device:
 
 In /etc/udev/rules.d/ add a new file called "70-usb-custom.rules", containing the following:

 ```
SUBSYSTEM=="usb", ATTR{idVendor}=="04d8", ATTR{idProduct}=="0f1c", MODE="0666"
 ```

 Then run:
 ```
 sudo service udev restart
 ```
## API commands

### Management commands

#### /plexiglas/
  
Enumerate all the names of the plexiglas indicators on the system. The names can then be used to send commands to the devices.
  
#### /plexiglas/writeName?name=\<newName\>
 
 Re-write the name of the device, stored in its EEPROM memory. Since this command is not associated with a particular device, you can only have one Plexiglas Indicator connected to the system when you use this.
 
 This was written a kludge to work-around unfortunately named devices (containing characters that cannot be addressed using a URL - for example containing "/" characters).
 
#### /plexiglas/device/<deviceName>/name?name=\<newName\>
 
 Change the name of the given device to <newName>, by re-writing some of the data stored in its EEPROM memory. All future commands to this device must use the new device name.
 
 ### LED Commands
 
 All commands accept the following parameters:
 
**brightness=\<value\>**
 
 The LED brightness value between 0-255 (default value is 255). Adjusts the PWM output such that the LED receives less/more power depending on the value, which changes its brightness. Note that the LED does not respond appear to respond linearly to this value.
 
 This value is persisted until the Plexiglas Indicator loses power.
 
**rate=\<value\>**
 
 How fast the LED should pulse, when in "blink" mode (values between 1-255, with 150 being the default). Other commands accept this value, but do not use it. This changes some PWM values to change how often the LED blinks. This isn't particularly well implemented, since the blink speed varies with brightness AND this value.
 
 This value is persisted until the Plexiglas Indicator loses power.
 
#### /plexiglas/device/\<deviceName\>/blink
 
 Sets the Plexiglas Indicator to "blink" mode. This smoothly transitions the LED between being "fully on" and "fully off", such that the brightness rises and falls smoothly.
 
#### /plexiglas/device/\<deviceName\>/on
 
 LED is set to be solidly on.
 
#### /plexiglas/device/\<deviceName\>/off
 
 LED is turned off.
 
 

# plexiglas-indicator-interface
Python code to contol a USB plexiglas indicator

Requirements:
 * PyUSB - http://sourceforge.net/projects/pyusb/
 * libusb0 to be installed (native library). Does not currently work with libusb1.
 * For Linux, a new udev rule to be added to allow access to the device:
 
 In /etc/udev/rules.d/ add a new file called "70-usb-custom.rules", containing the following:
 
    SUBSYSTEM=="usb", ATTR{idVendor}=="04d8", ATTR{idProduct}=="0f1c", MODE="0666"

 The run:
   sudo service udev restart

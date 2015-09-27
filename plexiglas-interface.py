# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 09:32:34 2015

@author: aim
"""

from wsgiref.simple_server import make_server
from cgi import parse_qs

import usb.core
import usb.util

import usb.backend.libusb0 as libusb0

from flask import Flask
from flask import request
from flask import make_response
import json

app = Flask(__name__)

def setup_device(device):
    '''Boiler-plate USB config before we send a command'''
    cfg = device.get_active_configuration()
    interface = cfg[(0,0)]
    in_endpoint = usb.util.find_descriptor(interface, custom_match = lambda e: 
    usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
    out_endpoint = usb.util.find_descriptor(interface, custom_match = lambda e: 
    usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
    
    return (in_endpoint, out_endpoint)

def get_device_name(device):
    try:        
        (in_endpoint, out_endpoint) = setup_device(device)
        
        out_endpoint.write("L")
        result = "".join(map(chr, in_endpoint.read(40, timeout=500)))
        print "result was: %s" % result
        if('L: ' not in result):
            raise Exception("Command not supported - result was: '%s'" % str(result))
        # Replacing * characters due to strange firmware wire protocol
        return result.replace("L: ", "").replace("*", "")
    finally:
        usb.util.dispose_resources(device)

def write_device_name(device, newName):
    try:        
        (in_endpoint, out_endpoint) = setup_device(device)
        
        out_endpoint.write("W:%s" % newName )
        result = "".join(map(chr, in_endpoint.read(40, timeout=500)))
        print "result was: %s" % result
        if('ACK' not in result):
            raise Exception("Command not supported - result was: '%s'" % str(result))
        return
    finally:
        usb.util.dispose_resources(device)
    
def enumerate_devices():
    devices = usb.core.find(find_all=True, idVendor=0x04d8, idProduct=0x0f1c, backend=libusb0.get_backend())
    toReturn = {}
    for device in devices:
        toReturn[get_device_name(device)] = device
    return toReturn

@app.route("/plexiglas/")
def list_devices():
    deviceMap = enumerate_devices()
    
    toReturn = []
    for key in deviceMap.keys():
        toReturn.append(key)
        
    return json.dumps(str(toReturn))

@app.route("/plexiglas/writeName")
def writeId():
    deviceMap = enumerate_devices()
    if len(deviceMap) > 1:
        return make_response("Too many devices attached - connect only the device to be renamed", 400)
    if len(deviceMap) < 1:
        return make_response("No devices attached - connect a device to proceed", 400)
    
    newName = request.args.get("name", None)
    if newName is None:
        return make_response("Parameter required: name")
    device = deviceMap.items()[0]
    write_device_name(device[1], newName)
    return "OK - new name set to %s" % newName

@app.route("/plexiglas/device/<name>")
@app.route("/plexiglas/device/<name>/")
def getDevice(name):
    deviceMap = enumerate_devices()
    if name not in deviceMap.keys():
        return make_response("Device not found", 400)
    return "OK"

@app.route("/plexiglas/device/<name>/blink")
def led_blink(name):
    deviceMap = enumerate_devices()
    if name not in deviceMap.keys():
        return make_response("Device not found", 400)
    
    device = deviceMap[name]
    try:
        (in_endpoint, out_endpoint) = setup_device(device)

        handle_brightness_and_rate(in_endpoint, out_endpoint)
        
        handle_usb_command(in_endpoint, out_endpoint, "P")
        

        return "OK"

    finally:
        usb.util.dispose_resources(device)

@app.route("/plexiglas/device/<name>/on")
def led_on(name):
    deviceMap = enumerate_devices()
    if name not in deviceMap.keys():
        return make_response("Device not found", 400)
    
    device = deviceMap[name]
    try:
        (in_endpoint, out_endpoint) = setup_device(device)
        
        handle_brightness_and_rate(in_endpoint, out_endpoint)

        handle_usb_command(in_endpoint, out_endpoint, "N")
        
        return "OK"

    finally:
        usb.util.dispose_resources(device)


@app.route("/plexiglas/device/<name>/off")
def led_off(name):
    deviceMap = enumerate_devices()
    if name not in deviceMap.keys():
        return make_response("Device not found", 400)
    
    device = deviceMap[name]
    try:
        (in_endpoint, out_endpoint) = setup_device(device)
        
        handle_brightness_and_rate(in_endpoint, out_endpoint)
        
        handle_usb_command(in_endpoint, out_endpoint, "F")
        
        return "OK"

    finally:
        usb.util.dispose_resources(device)

@app.route("/plexiglas/device/<name>/name")
def writeNewName(name):
    deviceMap = enumerate_devices()
    
    newName = request.args.get("name", None)
    if newName is None:
        return make_response("Parameter required: name")
    
    if name not in deviceMap.keys():
        return make_response("Device not found", 400)
    
    device = deviceMap[name]
    write_device_name(device, newName)
    return "OK - new name set to %s" % newName

def handle_usb_command(in_endpoint, out_endpoint, command):
    out_endpoint.write(command)
    result = "".join(map(chr, in_endpoint.read(40, timeout=500)))
    
    if result != "ACK":
        raise Exception("Device did not accept command '%s' - response: '%s'" % (command, result))

def handle_brightness_and_rate(in_endpoint, out_endpoint):
    if request.args.get("brightness", None) is not None:
            brightness = request.args["brightness"]
            handle_usb_command(in_endpoint, out_endpoint, "B" + str(brightness))
    if request.args.get("rate", None) is not None:
            rate = request.args["rate"]
            handle_usb_command(in_endpoint, out_endpoint, "R" + str(rate))
            
                
usb_command_map = {
    "on": 'N',
    "off": 'F',
    "blink": 'P'
}

if __name__ == "__main__":
   # Instantiate the WSGI server.
   app.run(debug=True)
   


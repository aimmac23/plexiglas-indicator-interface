# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 09:32:34 2015

@author: aim
"""

from wsgiref.simple_server import make_server
from cgi import parse_qs

import usb.core
import usb.util

usb_command_map = {
    "on": 'N',
    "off": 'F',
    "blink": 'P'
}

def send_response(start_response, status, response_body):

        content_type = "text/plain" 

        response_headers = [('Content-Type', content_type ),
                  ('Content-Length', str(len(response_body))),
                   ("Cache-Control",  "no-cache, must-revalidate")]  
                   
        start_response(status, response_headers)


def getParam(params, name):
    if name in params:
        return params[name][0]
    else:
        return None
        
def handleError(result, start_response):
    status = "500 Internal Server Error"
    response_body = "Inappropriate response from the USB device: %s" % result
    send_response(start_response, status, response_body)
    return [response_body]
        
# This is our application object. It could have any name,
# except when using mod_wsgi where it must be "application"
def application(environ, start_response):  
    
    params = parse_qs(environ['QUERY_STRING'])

    
    dev = usb.core.find(idVendor=0x04d8, idProduct=0x0f1c)
    
    if dev == None:
        status = '500 Internal Error'
        response_body = "The USB device is not plugged in!"
        send_response(start_response, status, response_body)
        return [response_body]

    else:
        try:
            
            cfg = dev.get_active_configuration()
            interface = cfg[(0,0)]
            in_endpoint = usb.util.find_descriptor(interface, custom_match = lambda e: 
            usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
            out_endpoint = usb.util.find_descriptor(interface, custom_match = lambda e: 
            usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)

            command = getParam(params, 'command');

            if command is not None:

                if command not in usb_command_map:
                    status = "400 Bad Request"
                    response_body = "Bad request - could not recognise command %s" % command
                    send_response(start_response, status, response_body);
                    return [response_body]
                
                usb_command = usb_command_map[command]

                                
                out_endpoint.write(usb_command)
                result = "".join(map(chr, in_endpoint.read(40, timeout=500)))
                if('ACK' not in result):
                    return handleError(result, start_response)
            
            brightness = getParam(params, "brightness")
            if brightness is not None:
                out_endpoint.write("B" + str(brightness))
                result = "".join(map(chr, in_endpoint.read(40, timeout=500)))
                if('ACK' not in result):
                    return handleError(result, start_response)
            
            
            rate = getParam(params, "rate")
            
            if rate is not None:
                out_endpoint.write("R" + str(rate))
                result = "".join(map(chr, in_endpoint.read(40, timeout=500)))
                if('ACK' not in result):
                    return handleError(result, start_response)
            
            response_body = "OK"
            status = "200 OK"
            send_response(start_response, status, response_body)
            return [response_body]
        
        finally:       
            # Release the device
            usb.util.dispose_resources(dev)



if __name__ == "__main__":
   # Instantiate the WSGI server.
   
   # It will receive the request, pass it to the application
   # and send the application's response to the client
    httpd = make_server(
    'localhost', # The host name.
    8052, # A port number where to wait for the request.
    application # Our application object name, in this case a function.
    )

    # Wait for a single request, serve it and quit.
    httpd.serve_forever()



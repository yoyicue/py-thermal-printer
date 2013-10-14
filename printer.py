#!/usr/bin/env python 
#coding=utf-8

import serial, time

#===========================================================#
# RASPBERRY PI (tested with Raspbian Jan 2012):
# - Ensure that ttyAMA0 is not used for serial console access:
# edit /boot/cmdline.txt (remove all name-value pairs containing 
# ttyAMA0) and comment out last line in /etc/inittab.
# - Fix user permissions with "sudo usermod -a -G dialout pi"
# - Reboot
# - Ensure that the SERIALPORT setting is correct below
#===========================================================#

    
class ThermalPrinter(object):


    # this might work better on a Raspberry Pi
    SERIALPORT = '/dev/ttyAMA0'

    BAUDRATE = 9600
    TIMEOUT = 3
    printer = None
    _ESC = chr(27)
    
    def __init__(self, speed=2, grayscale=2, font=0, serialport=SERIALPORT):
        self.printer = serial.Serial(serialport, self.BAUDRATE, timeout=self.TIMEOUT)
        self.printer.write(self._ESC) # ESC - command
        self.printer.write(chr(64)) # @   - initialize

        #Speed
        self.printer.write(self._ESC) # ESC - command
        self.printer.write(chr(115))
        self.printer.write(chr(speed))  # Low:0 Medium:1 High:2

        #Grayscale
        self.printer.write(self._ESC) # ESC - command
        self.printer.write(chr(109))
        self.printer.write(chr(grayscale))  # Light-Dark:1-8

        #Font
        self.printer.write(self._ESC) # ESC - command
        self.printer.write(chr(77))
        self.printer.write(chr(font))  # 0:24X24 1:16X16 2:12X12

        #Chinese Mode
        self.printer.write(chr(28)) # FS - Chinese mode
        self.printer.write(chr(38)) # & - Enable

        #Character
        self.printer.write(self._ESC) # ESC - command
        self.printer.write(chr(82)) # R
        self.printer.write(chr(15)) # Chinese Character

    def reset(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(64))

    def linefeed(self):
        self.printer.write(chr(10))

    def justify(self, align="L"):
        pos = 0
        if align == "L":
            pos = 0
        elif align == "C":
            pos = 1
        elif align == "R":
            pos = 2
        self.printer.write(self._ESC)
        self.printer.write(chr(97))
        self.printer.write(chr(pos))

    def bold_off(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(33))
        self.printer.write(chr(0))

    def bold_on(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(33))
        self.printer.write(chr(8))

    def font_b_off(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(33))
        self.printer.write(chr(0))

    def font_b_on(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(33))
        self.printer.write(chr(48))

    def underline_off(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(33))
        self.printer.write(chr(0))

    def underline_on(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(33))
        self.printer.write(chr(128)) # Light: 128 Dark: 136

    def inverse_off(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(33))
        self.printer.write(chr(0))

    def inverse_on(self):
        self.printer.write(self._ESC)
        self.printer.write(chr(33))
        self.printer.write(chr(64))
        
    def barcode_chr(self, msg):
        self.printer.write(chr(29)) # Leave
        self.printer.write(chr(72)) # Leave
        self.printer.write(msg)     # Print barcode # 1:Abovebarcode 2:Below 3:Both 0:Not printed
        
    def barcode_height(self, msg):
        self.printer.write(chr(29))  # Leave
        self.printer.write(chr(104)) # Leave
        self.printer.write(msg)      # Value 1-255 Default 50
        
    def barcode_height(self):
        self.printer.write(chr(29))  # Leave
        self.printer.write(chr(119)) # Leave
        self.printer.write(chr(2))   # Value 2,3 Default 2
        
    def barcode(self, msg):
        """ Please read http://www.adafruit.com/datasheets/A2-user%20manual.pdf
            for information on how to use barcodes. """
        # CODE SYSTEM, NUMBER OF CHARACTERS        
        # 65=UPC-A    11,12    #71=CODEBAR    >1
        # 66=UPC-E    11,12    #72=CODE93    >1
        # 67=EAN13    12,13    #73=CODE128    >1
        # 68=EAN8    7,8    #74=CODE11    >1
        # 69=CODE39    >1    #75=MSI        >1
        # 70=I25        >1 EVEN NUMBER           
        self.printer.write(chr(29))  # LEAVE
        self.printer.write(chr(107)) # LEAVE
        self.printer.write(chr(65))  # USE ABOVE CHART
        self.printer.write(chr(12))  # USE CHART NUMBER OF CHAR 
        self.printer.write(msg)
        
    def print_text(self, msg, chars_per_line=None):
        """ Print some text defined by msg. If chars_per_line is defined, 
            inserts newlines after the given amount. Use normal '\n' line breaks for 
            empty lines. """
        msg = msg.decode('utf-8').encode('gbk')
        if chars_per_line == None:
            self.printer.write(msg)
        else:
            l = list(msg)
            le = len(msg)
            for i in xrange(chars_per_line + 1, le, chars_per_line + 1):
                l.insert(i, '\n')
            self.printer.write("".join(l))
            print "".join(l)

    def print_bold(self, msg):
        self.bold_on()
        self.print_text(msg)
        self.bold_off()

    def print_b(self, msg):
        p.font_b_on()
        self.print_text(msg)
        p.font_b_off()



if __name__ == '__main__':
    import sys, os

    if len(sys.argv) == 2:
        serialport = sys.argv[1]
    else:
        serialport = ThermalPrinter.SERIALPORT

    if not os.path.exists(serialport):
        sys.exit("ERROR: Serial port not found at: %s" % serialport)

    print "Testing printer on port %s" % serialport
    p = ThermalPrinter(serialport=serialport)
    p.print_text("\n美团餐厅树莓派打印机\n")
    p.print_text("我要 ")
    p.print_bold("加粗\n")
    p.print_text("我也要")
    p.print_b("变大\n")
    p.justify("R")
    p.print_text("靠右\n")
    p.justify("C")
    p.print_text("居中\n")
    p.justify() # justify("L") works too
    p.print_text("靠左\n")
    p.linefeed()
    p.justify("C")
    p.barcode_chr("2")
    p.barcode("014633098808")
    p.linefeed()
    p.linefeed()
    p.linefeed()
    

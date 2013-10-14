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

    #test
    black_threshold = 48
    alpha_threshold = 127

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

    def print_underline(self, msg):
        p.underline_on()
        self.print_text(msg)
        p.underline_off()

    def print_inverse(self, msg):
        p.inverse_on()
        self.print_text(msg)
        p.inverse_off()

    def convert_pixel_array_to_binary(self, pixels, w, h):
        """ Convert the pixel array into a black and white plain list of 1's and 0's
            width is enforced to 384 and padded with white if needed. """
        black_and_white_pixels = [1] * 384 * h
        if w > 384:
            print "Bitmap width too large: %s. Needs to be under 384" % w
            return False
        elif w < 384:
            print "Bitmap under 384 (%s), padding the rest with white" % w

        print "Bitmap size", w

        if type(pixels[0]) == int: # single channel
            print " => single channel"
            for i, p in enumerate(pixels):
                if p < self.black_threshold:
                    black_and_white_pixels[i % w + i / w * 384] = 0
                else:
                    black_and_white_pixels[i % w + i / w * 384] = 1
        elif type(pixels[0]) in (list, tuple) and len(pixels[0]) == 3: # RGB
            print " => RGB channel"
            for i, p in enumerate(pixels):
                if sum(p[0:2]) / 3.0 < self.black_threshold:
                    black_and_white_pixels[i % w + i / w * 384] = 0
                else:
                    black_and_white_pixels[i % w + i / w * 384] = 1
        elif type(pixels[0]) in (list, tuple) and len(pixels[0]) == 4: # RGBA
            print " => RGBA channel"
            for i, p in enumerate(pixels):
                if sum(p[0:2]) / 3.0 < self.black_threshold and p[3] > self.alpha_threshold:
                    black_and_white_pixels[i % w + i / w * 384] = 0
                else:
                    black_and_white_pixels[i % w + i / w * 384] = 1
        else:
            print "Unsupported pixels array type. Please send plain list (single channel, RGB or RGBA)"
            print "Type pixels[0]", type(pixels[0]), "haz", pixels[0]
            return False

        return black_and_white_pixels


    def print_bitmap(self, pixels, w, h, output_png=False):
        """ Best to use images that have a pixel width of 384 as this corresponds
            to the printer row width. 
            
            pixels = a pixel array. RGBA, RGB, or one channel plain list of values (ranging from 0-255).
            w = width of image
            h = height of image
            if "output_png" is set, prints an "print_bitmap_output.png" in the same folder using the same
            thresholds as the actual printing commands. Useful for seeing if there are problems with the 
            original image (this requires PIL).

            Example code with PIL:
                import Image, ImageDraw
                i = Image.open("lammas_grayscale-bw.png")
                data = list(i.getdata())
                w, h = i.size
                p.print_bitmap(data, w, h)
        """
        counter = 0
        if output_png:
            import Image, ImageDraw
            test_img = Image.new('RGB', (384, h))
            draw = ImageDraw.Draw(test_img)

        self.linefeed()
        
        black_and_white_pixels = self.convert_pixel_array_to_binary(pixels, w, h)        
        print_bytes = []

        # read the bytes into an array
        for rowStart in xrange(0, h, 256):
            chunkHeight = 255 if (h - rowStart) > 255 else h - rowStart
            print_bytes += (18, 42, chunkHeight, 48)
            
            for i in xrange(0, 48 * chunkHeight, 1):
                # read one byte in
                byt = 0
                for xx in xrange(8):
                    pixel_value = black_and_white_pixels[counter]
                    counter += 1
                    # check if this is black
                    if pixel_value == 0:
                        byt += 1 << (7 - xx)
                        if output_png: draw.point((counter % 384, round(counter / 384)), fill=(0, 0, 0))
                    # it's white
                    else:
                        if output_png: draw.point((counter % 384, round(counter / 384)), fill=(255, 255, 255))
                
                print_bytes.append(byt)
        
        # output the array all at once to the printer
        # might be better to send while printing when dealing with 
        # very large arrays...
        for b in print_bytes:
            self.printer.write(chr(b))   
        
        if output_png:
            test_print = open('print-output.png', 'wb')
            test_img.save(test_print, 'PNG')
            print "output saved to %s" % test_print.name
            test_print.close()           


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
    p.print_text("我还要")
    p.print_underline("下划线\n")
    p.print_text("最后是")
    p.print_inverse("反白\n")
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
    
    # runtime dependency on Python Imaging Library
    import Image, ImageDraw
    i = Image.open("example-lammas.png")
    data = list(i.getdata())
    w, h = i.size
    p.print_bitmap(data, w, h, True)
    p.linefeed()
    p.linefeed()
    p.linefeed()
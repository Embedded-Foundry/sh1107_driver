"""
# ------------------------------------------------------------
# Project: SH1107 Adafruit 128x64 OLED FeatherWing Driver
# Author: Eric Gnoske
# License: MIT License
# Description: Complete SH1107 Micropython driver with landscape 
# mode (128x64) support For Adafruit 128x64 OLED FeatherWing.
# Tested on a Raspberry Pi Pico.
# ------------------------------------------------------------
Example usage:
    from machine import I2C, Pin
    from sh1107_driver import SH1107
    
    i2c = I2C(0, scl=Pin(1), sda=Pin(0))
    oled = SH1107(i2c)
    
    oled.text("Hello World!", 0, 0)
    oled.show()
"""

from micropython import const
import framebuf
import time

# SH1107 commands
_SET_CONTRAST = const(0x81)
_SET_ENTIRE_ON = const(0xA4)
_SET_NORM_INV = const(0xA6)
_SET_DISP = const(0xAE)
_SET_SCAN_DIR = const(0xC0)
_SET_SEG_REMAP = const(0xA0)
_SET_MUX_RATIO = const(0xA8)
_SET_DISP_OFFSET = const(0xD3)
_SET_DISP_START_LINE = const(0xDC)
_SET_DISP_CLK_DIV = const(0xD5)
_SET_PRECHARGE = const(0xD9)
_SET_VCOM_DESEL = const(0xDB)
_SET_PAGE_ADDR = const(0xB0)
_SET_COL_ADDR_LOW = const(0x00)
_SET_COL_ADDR_HIGH = const(0x10)
_SET_MEM_ADDR_MODE = const(0x20)


class SH1107(framebuf.FrameBuffer):
    """
    SH1107 OLED display driver for MicroPython
    
    The driver automatically handles rotation to present the display as 128x64 landscape
    when rotate=True (default), or as 64x128 portrait when rotate=False.
    """
    
    def __init__(self, i2c, addr=0x3C, rotate=True, external_vcc=False):
        """
        Initialize SH1107 display
        
        Args:
            i2c: I2C interface
            addr: I2C address (default 0x3C)
            rotate: True for 128x64 landscape, False for 64x128 portrait
            external_vcc: True if display has external power supply
        """
        self.i2c = i2c
        self.addr = addr
        self.external_vcc = external_vcc
        self.rotate = rotate
        
        # Physical dimensions (controller perspective)
        self.physical_width = const(64)
        self.physical_height = const(128)
        
        # Logical dimensions (user perspective)
        if rotate:
            self.width = 128
            self.height = 64
        else:
            self.width = 64
            self.height = 128
            
        # Create framebuffer
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        
        # Physical display buffer (only needed for rotation)
        if self.rotate:
            self.physical_buffer = bytearray(16 * 64)  # 16 pages * 64 columns
            
        self.init_display()
        
    def init_display(self):
        """Initialize display with recommended settings"""
        for cmd in (
            _SET_DISP | 0x00,  # Display off
            _SET_DISP_START_LINE, 0x00,  # Start line 0
            _SET_CONTRAST, 0x2F,  # Contrast
            _SET_MEM_ADDR_MODE,  # Vertical addressing mode
            _SET_SEG_REMAP | 0x00,  # Segment remap (0x00 or 0x01)
            _SET_SCAN_DIR | 0x00,  # Scan direction (0x00 or 0x08)
            _SET_MUX_RATIO, 0x7F,  # Multiplex ratio (128)
            _SET_DISP_OFFSET, 0x60,  # Display offset for FeatherWing
            _SET_DISP_CLK_DIV, 0x51,  # Clock divide
            _SET_PRECHARGE, 0x22,  # Precharge period
            _SET_VCOM_DESEL, 0x35,  # VCOMH deselect level
            _SET_ENTIRE_ON,  # Display follows RAM
            _SET_NORM_INV,  # Normal display
            _SET_DISP | 0x01,  # Display on
        ):
            self.write_cmd(cmd)
            
        self.fill(0)
        self.show()
        
    def write_cmd(self, cmd):
        """Send command to display"""
        self.i2c.writeto(self.addr, bytes([0x80, cmd]))
        
    def write_data(self, data):
        """Send data to display"""
        # Send data in chunks to avoid memory issues
        chunk_size = const(16)
        for i in range(0, len(data), chunk_size):
            self.i2c.writeto(self.addr, bytes([0x40]) + data[i:i + chunk_size])
            time.sleep_us(50)  # Small delay for reliability
            
    def show(self):
        """Update physical display with buffer contents"""
        if self.rotate:
            # Rotate buffer 90 degrees for landscape mode
            self._rotate_buffer()
            buffer_to_send = self.physical_buffer
        else:
            buffer_to_send = self.buffer
            
        # Send buffer to display using page addressing
        for page in range(16):  # SH1107 has 16 pages
            try:
                self.write_cmd(_SET_PAGE_ADDR | page)
                self.write_cmd(_SET_COL_ADDR_LOW | 0)
                self.write_cmd(_SET_COL_ADDR_HIGH | 0)
                
                start = page * 64
                self.write_data(buffer_to_send[start:start + 64])
                time.sleep_us(100)  # Small delay between pages
            except OSError:
                # If timeout occurs, wait a bit and retry
                time.sleep_ms(10)
                self.write_cmd(_SET_PAGE_ADDR | page)
                self.write_cmd(_SET_COL_ADDR_LOW | 0)
                self.write_cmd(_SET_COL_ADDR_HIGH | 0)
                
                start = page * 64
                self.write_data(buffer_to_send[start:start + 64])
            
    def _rotate_buffer(self):
        """Rotate 128x64 buffer to 64x128 for physical display"""
        # Clear physical buffer
        for i in range(len(self.physical_buffer)):
            self.physical_buffer[i] = 0
            
        # Rotate 90 degrees counter-clockwise
        # Process by bytes instead of pixels for efficiency
        for src_page in range(8):  # 8 pages in landscape buffer
            for src_col in range(128):  # 128 columns
                # Get byte from source buffer
                src_byte = self.buffer[src_page * 128 + src_col]
                
                if src_byte:  # Only process non-zero bytes
                    # Each bit in source byte goes to different position
                    for bit in range(8):
                        if src_byte & (1 << bit):
                            # Calculate source pixel position
                            src_y = src_page * 8 + bit
                            src_x = src_col
                            
                            # Calculate rotated position
                            dst_x = src_y
                            dst_y = 127 - src_x
                            
                            # Set pixel in physical buffer
                            dst_page = dst_y // 8
                            dst_bit = dst_y % 8
                            self.physical_buffer[dst_page * 64 + dst_x] |= (1 << dst_bit)
                    
    def contrast(self, value):
        """Set display contrast (0-255)"""
        self.write_cmd(_SET_CONTRAST)
        self.write_cmd(value)
        
    def invert(self, invert):
        """Invert display (True/False)"""
        self.write_cmd(_SET_NORM_INV | (invert & 1))
        time.sleep_ms(10)  # Small delay for command to take effect
        
    def poweroff(self):
        """Turn display off"""
        self.write_cmd(_SET_DISP | 0x00)
        
    def poweron(self):
        """Turn display on"""
        self.write_cmd(_SET_DISP | 0x01)
        
    # Graphics extensions
    def circle(self, x0, y0, r, c, f=False):
        """Draw circle. f=True for filled"""
        x = r
        y = 0
        err = 0
        
        if f:
            # Filled circle
            while y <= r:
                self.hline(x0 - x, y0 + y, 2 * x + 1, c)
                if y != 0:
                    self.hline(x0 - x, y0 - y, 2 * x + 1, c)
                err += 1 + 2 * y
                y += 1
                if 2 * err > 2 * x + 1:
                    x -= 1
                    err += 1 - 2 * x
        else:
            # Circle outline
            while x >= y:
                self.pixel(x0 + x, y0 + y, c)
                self.pixel(x0 + y, y0 + x, c)
                self.pixel(x0 - y, y0 + x, c)
                self.pixel(x0 - x, y0 + y, c)
                self.pixel(x0 - x, y0 - y, c)
                self.pixel(x0 - y, y0 - x, c)
                self.pixel(x0 + y, y0 - x, c)
                self.pixel(x0 + x, y0 - y, c)
                
                if err <= 0:
                    y += 1
                    err += 2 * y + 1
                if err > 0:
                    x -= 1
                    err -= 2 * x + 1
                    
    def ellipse(self, x0, y0, a, b, c, f=False):
        """Draw ellipse. a=width radius, b=height radius, f=True for filled"""
        if f:
            # Filled ellipse
            for y in range(-b, b + 1):
                x = int(a * ((1 - (y*y)/(b*b)) ** 0.5))
                self.hline(x0 - x, y0 + y, 2 * x + 1, c)
        else:
            # Ellipse outline using midpoint algorithm
            x = 0
            y = b
            a2 = a * a
            b2 = b * b
            d = b2 - a2 * b + a2 // 4
            dx = 0
            dy = 2 * a2 * y
            
            # Region 1
            while dx < dy:
                self.pixel(x0 + x, y0 + y, c)
                self.pixel(x0 - x, y0 + y, c)
                self.pixel(x0 + x, y0 - y, c)
                self.pixel(x0 - x, y0 - y, c)
                
                if d < 0:
                    x += 1
                    dx += 2 * b2
                    d += dx + b2
                else:
                    x += 1
                    y -= 1
                    dx += 2 * b2
                    dy -= 2 * a2
                    d += dx - dy + b2
                    
            # Region 2
            d = b2 * (x + 0.5) * (x + 0.5) + a2 * (y - 1) * (y - 1) - a2 * b2
            while y >= 0:
                self.pixel(x0 + x, y0 + y, c)
                self.pixel(x0 - x, y0 + y, c)
                self.pixel(x0 + x, y0 - y, c)
                self.pixel(x0 - x, y0 - y, c)
                
                if d > 0:
                    y -= 1
                    dy -= 2 * a2
                    d += a2 - dy
                else:
                    y -= 1
                    x += 1
                    dx += 2 * b2
                    dy -= 2 * a2
                    d += dx - dy + a2
                    
    def triangle(self, x0, y0, x1, y1, x2, y2, c, f=False):
        """Draw triangle. f=True for filled"""
        if f:
            # Filled triangle using horizontal line scanning
            # Sort vertices by y coordinate
            if y0 > y1: x0, y0, x1, y1 = x1, y1, x0, y0
            if y1 > y2: x1, y1, x2, y2 = x2, y2, x1, y1
            if y0 > y1: x0, y0, x1, y1 = x1, y1, x0, y0
            
            # Draw filled triangle
            for y in range(y0, y2 + 1):
                if y <= y1:
                    # Upper part
                    if y1 != y0:
                        xa = x0 + (x1 - x0) * (y - y0) // (y1 - y0)
                    else:
                        xa = x0
                    if y2 != y0:
                        xb = x0 + (x2 - x0) * (y - y0) // (y2 - y0)
                    else:
                        xb = x0
                else:
                    # Lower part
                    if y2 != y1:
                        xa = x1 + (x2 - x1) * (y - y1) // (y2 - y1)
                    else:
                        xa = x1
                    if y2 != y0:
                        xb = x0 + (x2 - x0) * (y - y0) // (y2 - y0)
                    else:
                        xb = x0
                
                if xa > xb: xa, xb = xb, xa
                self.hline(xa, y, xb - xa + 1, c)
        else:
            # Triangle outline
            self.line(x0, y0, x1, y1, c)
            self.line(x1, y1, x2, y2, c)
            self.line(x2, y2, x0, y0, c)


# Convenience class for portrait mode
class SH1107_Portrait(SH1107):
    """SH1107 in portrait mode (64x128)"""
    def __init__(self, i2c, addr=0x3C, external_vcc=False):
        super().__init__(i2c, addr, rotate=False, external_vcc=external_vcc)


# Convenience class for landscape mode  
class SH1107_Landscape(SH1107):
    """SH1107 in landscape mode (128x64)"""
    def __init__(self, i2c, addr=0x3C, external_vcc=False):
        super().__init__(i2c, addr, rotate=True, external_vcc=external_vcc)
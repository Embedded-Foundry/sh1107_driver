"""
# ------------------------------------------------------------
# Project: SH1107 Adafruit 128x64 OLED FeatherWing Driver
# Author: Eric Gnoske
# License: MIT License
# Description: Examples for SH1107 OLED display driver Tested 
# with Adafruit 128x64 OLED FeatherWing on a Raspberry Pi Pico.
# Uses GP9 on the Pico for reset control.
# ------------------------------------------------------------
"""

from machine import I2C, Pin
import time
from sh1107_driver import SH1107, SH1107_Landscape, SH1107_Portrait

# Hardware setup
RESET_PIN = 9  # Connect display RST to GPIO 9
I2C_ID = 0
SCL_PIN = 1
SDA_PIN = 0

def reset_display():
    """Hardware reset the display"""
    reset = Pin(RESET_PIN, Pin.OUT)
    reset.value(0)
    time.sleep_ms(10)
    reset.value(1)
    time.sleep_ms(50)

def example_basic():
    """Basic text display example"""
    print("Basic Example")
    reset_display()
    
    # Create I2C interface
    i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
    
    # Create display (defaults to landscape 128x64)
    oled = SH1107(i2c)
    
    # Draw text
    oled.fill(0)  # Clear screen
    oled.text("Hello World!", 0, 0)
    oled.text("MicroPython", 0, 16)
    oled.text("SH1107 OLED", 0, 32)
    oled.show()
    time.sleep(2)

def example_invert():
    """Display inversion example"""
    print("Invert Example")
    reset_display()
    
    i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
    oled = SH1107(i2c)
    
    # Create a simple pattern
    oled.fill(0)
    oled.text("NORMAL", 35, 20)
    oled.text("Display", 35, 35)
    oled.rect(10, 10, 108, 44, 1)  # Border
    oled.show()
    time.sleep(2)
    
    # Invert display
    print("Inverting display...")
    oled.invert(True)
    time.sleep(2)
    
    # Back to normal
    print("Back to normal...")
    oled.invert(False)
    time.sleep(2)
    
    print("Invert test complete!")  # Display for 2 seconds

def example_graphics():
    """Graphics demonstration"""
    print("Graphics Example")
    reset_display()
    
    i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
    oled = SH1107(i2c)
    
    # Draw various shapes
    oled.fill(0)
    
    # Rectangle
    oled.rect(10, 10, 30, 20, 1)
    
    # Filled rectangle
    oled.fill_rect(50, 10, 30, 20, 1)
    
    # Circle
    oled.circle(100, 20, 15, 1)
    
    # Lines
    oled.line(10, 40, 118, 40, 1)
    oled.hline(10, 50, 108, 1)
    oled.vline(64, 35, 20, 1)
    
    oled.show()
    time.sleep(2)  # Display for 2 seconds

def example_portrait():
    """Portrait mode example (64x128)"""
    print("Portrait Mode Example")
    reset_display()
    
    i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
    
    # Use portrait mode
    oled = SH1107_Portrait(i2c)
    
    oled.fill(0)
    oled.text("Portrait", 0, 0)
    oled.text("64x128", 5, 20)
    oled.text("Mode", 15, 40)
    oled.rect(0, 0, 64, 128, 1)  # Border
    oled.show()

def example_animation():
    """Simple animation example"""
    print("Animation Example")
    reset_display()
    
    i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
    oled = SH1107(i2c)
    
    # Bouncing ball animation
    ball_x = 10
    ball_y = 32
    dx = 2
    dy = 1
    
    for frame in range(100):
        oled.fill(0)
        
        # Draw ball
        oled.circle(ball_x, ball_y, 5, 1, f=True)
        
        # Update position
        ball_x += dx
        ball_y += dy
        
        # Bounce off edges
        if ball_x <= 5 or ball_x >= 123:
            dx = -dx
        if ball_y <= 5 or ball_y >= 59:
            dy = -dy
            
        oled.show()
        time.sleep_ms(50)
    
    # Final message
    oled.fill(0)
    oled.text("Animation", 30, 20)
    oled.text("Complete!", 30, 35)
    oled.show()

def example_contrast():
    """Contrast adjustment example"""
    print("Contrast Example")
    reset_display()
    
    i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
    oled = SH1107(i2c)
    
    oled.fill(0)
    oled.text("Contrast", 30, 20)
    oled.text("Test", 45, 35)
    oled.show()
    
    # Cycle through contrast levels
    for level in [0x01, 0x40, 0x80, 0xCF, 0xFF]:
        oled.contrast(level)
        time.sleep(1)
    
    # Reset to default
    oled.contrast(0x2F)

def example_shapes():
    """Advanced shapes demonstration"""
    print("Advanced Shapes Example")
    reset_display()
    
    i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
    oled = SH1107(i2c)
    
    # Draw triangles
    oled.fill(0)
    oled.text("Triangles", 30, 0)
    
    # Outline triangle
    oled.triangle(10, 55, 30, 20, 50, 55, 1, f=False)
    
    # Filled triangle
    oled.triangle(70, 55, 90, 20, 110, 55, 1, f=True)
    
    oled.show()
    time.sleep(2)
    
    # Draw ellipses
    oled.fill(0)
    oled.text("Ellipses", 35, 0)
    
    # Wide ellipse
    oled.ellipse(30, 35, 20, 10, 1, f=False)
    
    # Tall filled ellipse
    oled.ellipse(90, 35, 10, 20, 1, f=True)
    
    oled.show()
    time.sleep(2)
    
    # Combined shapes
    oled.fill(0)
    oled.text("Art", 55, 0)
    
    # Draw a simple house
    # House body
    oled.rect(30, 30, 40, 30, 1)
    # Roof
    oled.triangle(25, 30, 50, 15, 75, 30, 1, f=True)
    # Door
    oled.fill_rect(45, 45, 10, 15, 1)
    # Window
    oled.rect(35, 35, 8, 8, 1)
    # Sun
    oled.circle(100, 20, 8, 1, f=True)
    
    oled.show()
    time.sleep(2)
    """Display inversion example"""
    print("Invert Example")
    reset_display()
    
    i2c = I2C(I2C_ID, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=400000)
    oled = SH1107(i2c)
    
    # Create a simple pattern
    oled.fill(0)
    oled.text("NORMAL", 35, 20)
    oled.text("Display", 35, 35)
    oled.rect(10, 10, 108, 44, 1)  # Border
    oled.show()
    time.sleep(2)
    
    # Invert display
    print("Inverting display...")
    oled.invert(True)
    time.sleep(2)
    
    # Back to normal
    print("Back to normal...")
    oled.invert(False)
    time.sleep(2)
    
    print("Invert test complete!")

# Run all examples
if __name__ == "__main__":
    print("SH1107 OLED Examples")
    print("====================")
    
    examples = [
        ("Basic Text", example_basic),
        ("Graphics", example_graphics),
        ("Advanced Shapes", example_shapes),
        ("Portrait Mode", example_portrait),
        ("Animation", example_animation),
        ("Contrast", example_contrast),
        ("Invert", example_invert),
    ]
    
    for name, func in examples:
        print(f"\nRunning: {name}")
        func()
        time.sleep(2)
    
    print("\nAll examples complete!")
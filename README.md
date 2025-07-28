# SH1107 OLED Display Driver for MicroPython

A simple, efficient MicroPython driver for SH1107-based OLED displays, specifically designed for the Adafruit 128x64 OLED FeatherWing.

**Author:** Eric Gnoske  
**License:** MIT License  
**Tested on:** Raspberry Pi Pico with Adafruit 128x64 OLED FeatherWing

## Features

- 🔄 **Automatic rotation handling** - Use as 128x64 landscape or 64x128 portrait
- 🎨 **Full graphics support** - Lines, rectangles, circles, ellipses, triangles, and more
- 💾 **Memory efficient** - Optimized for microcontrollers
- 🔌 **Simple API** - Extends MicroPython's FrameBuffer
- ⚡ **Fast updates** - Hardware-optimized data transfer
- 🎯 **Zero dependencies** - Uses only built-in MicroPython modules

## Installation

1. Copy `sh1107_driver.py` to your MicroPython device
2. Connect your display via I2C
3. Connect the reset pin (recommended)
4. You're ready to go!

## Hardware Setup

### Wiring for Raspberry Pi Pico

| Pico Pin | OLED Pin | Description |
|----------|----------|-------------|
| 3V3      | VCC      | Power (3.3V) |
| GND      | GND      | Ground |
| GP0      | SDA      | I2C Data |
| GP1      | SCL      | I2C Clock |
| GP9      | RST      | Reset (required for reliable operation) |

### I2C Address

Default address is `0x3C`. Some displays may use `0x3D`.

## Quick Start

```python
from machine import I2C, Pin
from sh1107_driver import SH1107
import time

# Hardware reset (recommended)
reset = Pin(9, Pin.OUT)
reset.value(0)
time.sleep_ms(10)
reset.value(1)
time.sleep_ms(50)

# Initialize I2C
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# Create display object (128x64 landscape mode)
oled = SH1107(i2c)

# Draw something
oled.text("Hello World!", 0, 0)
oled.show()
```

## Usage Examples

### Basic Text Display

```python
# Clear screen and show text
oled.fill(0)  # Clear screen (0 = black)
oled.text("Line 1", 0, 0)
oled.text("Line 2", 0, 10)
oled.text("Line 3", 0, 20)
oled.show()  # Update display
```

### Drawing Shapes

```python
# Draw various shapes
oled.fill(0)  # Clear screen

# Rectangle (outline)
oled.rect(10, 10, 50, 30, 1)

# Filled rectangle
oled.fill_rect(70, 10, 50, 30, 1)

# Circle
oled.circle(30, 50, 10, 1)

# Filled circle
oled.circle(90, 50, 10, 1, f=True)

# Lines
oled.line(0, 60, 127, 60, 1)
oled.hline(0, 62, 128, 1)
oled.vline(64, 0, 64, 1)

oled.show()
```

### Advanced Shapes

```python
# Draw triangles
oled.triangle(10, 55, 30, 20, 50, 55, 1)  # Outline
oled.triangle(70, 55, 90, 20, 110, 55, 1, f=True)  # Filled

# Draw ellipses
oled.ellipse(30, 35, 20, 10, 1)  # Wide ellipse
oled.ellipse(90, 35, 10, 20, 1, f=True)  # Tall filled ellipse

oled.show()
```

### Portrait Mode (64x128)

```python
from sh1107_driver import SH1107_Portrait

# Use portrait orientation
oled = SH1107_Portrait(i2c)

oled.fill(0)
oled.text("Portrait", 0, 0)
oled.text("Mode", 10, 20)
oled.text("64x128", 5, 40)
oled.show()
```

### Animation Example

```python
import time

# Simple bouncing ball
x, y = 10, 32
dx, dy = 2, 1

for _ in range(100):
    oled.fill(0)
    oled.circle(x, y, 5, 1, f=True)
    
    x += dx
    y += dy
    
    # Bounce off edges
    if x <= 5 or x >= 122:
        dx = -dx
    if y <= 5 or y >= 58:
        dy = -dy
        
    oled.show()
    time.sleep_ms(50)
```

### Display Control

```python
# Adjust contrast (0-255)
oled.contrast(128)  # Medium brightness
oled.contrast(255)  # Maximum brightness

# Invert display
oled.invert(True)   # White background, black text
oled.invert(False)  # Normal display

# Power control
oled.poweroff()     # Turn off display
oled.poweron()      # Turn on display
```

## API Reference

### Constructor

#### `SH1107(i2c, addr=0x3C, rotate=True, external_vcc=False)`

Create a new SH1107 display instance.

**Parameters:**
- `i2c`: I2C interface object
- `addr`: I2C address (default: 0x3C)
- `rotate`: True for 128x64 landscape, False for 64x128 portrait
- `external_vcc`: True if display has external power supply

### Display Control Methods

| Method | Description |
|--------|-------------|
| `show()` | Update display with buffer contents |
| `fill(color)` | Fill entire display (0=black, 1=white) |
| `contrast(value)` | Set contrast/brightness (0-255) |
| `invert(state)` | Invert display (True/False) |
| `poweroff()` | Turn display off |
| `poweron()` | Turn display on |

### Drawing Methods

| Method | Description |
|--------|-------------|
| `pixel(x, y, color)` | Set a single pixel |
| `text(string, x, y, color=1)` | Draw 8x8 text |
| `hline(x, y, width, color)` | Draw horizontal line |
| `vline(x, y, height, color)` | Draw vertical line |
| `line(x1, y1, x2, y2, color)` | Draw line between points |
| `rect(x, y, w, h, color)` | Draw rectangle outline |
| `fill_rect(x, y, w, h, color)` | Draw filled rectangle |
| `circle(x, y, radius, color, f=False)` | Draw circle (f=True for filled) |
| `ellipse(x, y, a, b, color, f=False)` | Draw ellipse (a=width radius, b=height radius) |
| `triangle(x0, y0, x1, y1, x2, y2, color, f=False)` | Draw triangle by vertices |
| `scroll(dx, dy)` | Scroll display contents |

### Convenience Classes

- `SH1107_Landscape(i2c)` - Explicitly create 128x64 landscape display
- `SH1107_Portrait(i2c)` - Explicitly create 64x128 portrait display

## Important Notes

### Reset Pin Connection

The reset pin connection (GP9 in examples) is **highly recommended** for reliable operation. Without it, the display may not initialize properly.

### File Names

- Driver file: `sh1107_driver.py`
- Examples file: `sh1107_examples.py`

### Import Statement

```python
from sh1107_driver import SH1107
```

## Troubleshooting

### Display Not Working

1. **Check wiring** - Ensure all connections are secure
2. **Connect reset pin** - GP9 to RST is required for reliable operation
3. **Verify I2C address** - Use `i2c.scan()` to find devices:
   ```python
   devices = i2c.scan()
   print("I2C devices:", [hex(d) for d in devices])
   ```
4. **Hardware reset before init**:
   ```python
   reset = Pin(9, Pin.OUT)
   reset.value(0)
   time.sleep_ms(10)
   reset.value(1)
   time.sleep_ms(50)
   ```

### Display Shows Garbage

- Wrong controller? This driver is specifically for SH1107
- Try different initialization parameters
- Ensure stable power supply (3.3V)

### ETIMEDOUT Errors

- Reduce I2C frequency: `i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)`
- Add delays between operations
- Check for loose connections

### Text is Mirrored/Rotated

- The driver handles rotation automatically
- Use `rotate=True` (default) for landscape 128x64
- Use `rotate=False` for portrait 64x128

## Performance Tips

1. **Update only when needed** - Don't call `show()` in tight loops
2. **Use fill_rect for clearing areas** - Faster than multiple pixels
3. **Batch updates** - Draw everything, then call `show()` once
4. **Lower I2C frequency if unstable** - Try 100000 instead of 400000

## Memory Usage

- Display buffer: 1KB (128×64÷8)
- Additional rotation buffer: 1KB (if using landscape mode)
- Total RAM usage: ~2KB in landscape, ~1KB in portrait

## Examples

Run the included examples with:

```python
import sh1107_examples
# This will run all examples in sequence
```

Or run individual examples:

```python
from sh1107_examples import example_basic, example_graphics
example_basic()
example_graphics()
```

## License

MIT License - See source code for full license text

## Contributing

Contributions are welcome! Please submit issues and pull requests on the project repository.

## Acknowledgments

- Designed for Adafruit 128x64 OLED FeatherWing
- Based on SH1107 datasheet specifications
- Tested on Raspberry Pi Pico

## Version History

- 1.0.0 - Initial release with full graphics support including circles, ellipses, and triangles

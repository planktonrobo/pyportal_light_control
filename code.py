import time
import board
import microcontroller
import displayio
import busio
from analogio import AnalogIn
import neopixel
import adafruit_adt7410
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_button import Button
import adafruit_touchscreen
from adafruit_pyportal import PyPortal
import digitalio
# CircuitPython IO demo - analog output
import board
import adafruit_motor.servo


# ------------- Inputs and Outputs Setup ------------- #
adt = None
# ------------- Screen Setup ------------- #
display = board.DISPLAY
display.rotation = 270

def set_backlight(val):
    val = max(0, min(1.0, val))
    board.DISPLAY.auto_brightness = False
    board.DISPLAY.brightness = val

# Set the Backlight
set_backlight(0.1)
pyportal = PyPortal()
# Display an image until the loop starts
pyportal.set_background('/images/c.bmp')


pyportal.get_local_time()
outlet = digitalio.DigitalInOut(board.D4)
outlet.direction = digitalio.Direction.OUTPUT
outlet.value = False

refresh_time = None


# init. the light sensor
light_sensor = AnalogIn(board.LIGHT)

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=1)
WHITE = 0xffffff
RED = 0xff0000
YELLOW = 0xffff00
GREEN = 0x00ff00
BLUE = 0x0000ff
PURPLE = 0xff00ff
BLACK = 0x000000

# ---------- Sound Effects ------------- #
soundDemo = '/sounds/Coin.wav'
soundBeep = '/sounds/eep.wav'
soundTab = '/sounds/eep.wav'

# ------------- Other Helper Functions------------- #




# Touchscreen setup
# ------Rotate 270:
screen_width = 240
screen_height = 320
ts = adafruit_touchscreen.Touchscreen(board.TOUCH_YD, board.TOUCH_YU,
                                      board.TOUCH_XR, board.TOUCH_XL,
                                      calibration=((5200, 59000),
                                                   (5800, 57000)),
                                      size=(screen_width, screen_height))


# ------------- Display Groups ------------- #
splash = displayio.Group(max_size=15)  # The Main Display Group
view1 = displayio.Group(max_size=15)  # Group for View 1 objects

def hideLayer(hide_target):
    try:
        splash.remove(hide_target)
    except ValueError:
        pass

def showLayer(show_target):
    try:
        time.sleep(0.1)
        splash.append(show_target)
    except ValueError:
        pass

# ------------- Setup for Images ------------- #



bg_group = displayio.Group(max_size=1)
splash.append(bg_group)


icon_group = displayio.Group(max_size=1)
icon_group.x = 95
icon_group.y = 30
icon_group.scale = 1


# This will handel switching Images and Icons
def set_image(group, filename):
    """Set the image file for a given goup for display.
    This is most useful for Icons or image slideshows.
        :param group: The chosen group
        :param filename: The filename of the chosen image
    """
    print("Set image to ", filename)
    if group:
        group.pop()

    if not filename:
        return  # we're done, no icon desired

    image_file = open(filename, "rb")
    image = displayio.OnDiskBitmap(image_file)
    try:
        image_sprite = displayio.TileGrid(image, pixel_shader=displayio.ColorConverter())
    except TypeError:
        image_sprite = displayio.TileGrid(image, pixel_shader=displayio.ColorConverter(),
                                          position=(0, 0))
    group.append(image_sprite)

# ---------- Text Boxes ------------- #
# Set the font and preload letters
font = bitmap_font.load_font("/fonts/Arial-ItalicMT-17.bdf")
font.load_glyphs(b'abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()')

# Default Label styling:
TABS_X = 5
TABS_Y = 50

# Text Label Objects
feed1_label = Label(font, text="Text Wondow 1", color=0xFFFFFF, max_glyphs=200)
feed1_label.x = 0
feed1_label.y = 0
view1.append(feed1_label)

feed2_label = Label(font, text="Text Wondow 2", color=0xFFFFFF, max_glyphs=200)
feed2_label.x = TABS_X
feed2_label.y = TABS_Y + 60
view1.append(feed2_label)

set_image(icon_group, '/images/plant_icon.bmp')
view1.append(icon_group)

text_hight = Label(font, text="M", color=0x03AD31, max_glyphs=10)
# return a reformatted string with word wrapping using PyPortal.wrap_nicely
def text_box(target, top, string, max_chars):
    text = pyportal.wrap_nicely(string, max_chars)
    new_text = ""
    test = ""
    for w in text:
        new_text += '\n'+w
        test += 'M\n'
    text_hight.text = test  # Odd things happen without this
    glyph_box = text_hight.bounding_box
    target.text = ""  # Odd things happen without this
    target.y = int(glyph_box[3]/2)+top
    target.text = new_text

# ---------- Display Buttons ------------- #
# Default button styling:
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 80

# We want three buttons across the top of the screen
TAPS_HEIGHT = 40
TAPS_WIDTH = int(screen_width/3)
TAPS_Y = 0

# We want two big buttons at the bottom of the screen
BIG_BUTTON_HEIGHT = int(screen_height/3.2)
BIG_BUTTON_WIDTH = int(screen_width/2)
BIG_BUTTON_Y = int(screen_height-BIG_BUTTON_HEIGHT)

# This group will make it easy for us to read a button press later.
buttons = []

# Main User Interface Buttons


button_switch = Button(x=0, y=BIG_BUTTON_Y,
                       width=BIG_BUTTON_WIDTH * 2, height=BIG_BUTTON_HEIGHT,
                       label="Switch", label_font=font, label_color=GREEN,
                       fill_color=0x5c5b5c, outline_color=0x767676,
                       selected_fill=0x1a1a1a, selected_outline=0x2e2e2e,
                       selected_label=0x525252)
buttons.append(button_switch)  # adding this button to the buttons group


# Make a button to change the icon image on view2
button_icon = Button(x=2, y=155,
                     width=BUTTON_WIDTH -8, height=BUTTON_HEIGHT + 2,
                     label="12/12", label_font=font, label_color=0xffffff,
                     fill_color=0x525252, outline_color=0xbc55fd,
                     selected_fill=0xbc55fd, selected_outline=0xffffff,
                     selected_label=0xffffff, style=Button.ROUNDRECT)
buttons.append(button_icon)  # adding this button to the buttons group


button_icon2 = Button(x=BUTTON_WIDTH + 2 , y=155,
                     width=BUTTON_WIDTH -8, height=BUTTON_HEIGHT + 2,
                     label="18/6", label_font=font, label_color=0xffffff,
                     fill_color=0x525252, outline_color=0xbc55fd,
                     selected_fill=0xbc55fd, selected_outline=0xffffff,
                     selected_label=0xffffff, style=Button.ROUNDRECT)
buttons.append(button_icon2)  # adding this button to the buttons group

button_icon3 = Button(x=(BUTTON_WIDTH * 2) + 2, y=155,
                     width=BUTTON_WIDTH - 8, height=BUTTON_HEIGHT + 2,
                     label="20/4", label_font=font, label_color=0xffffff,
                     fill_color=0x525252, outline_color=0xbc55fd,
                     selected_fill=0xbc55fd, selected_outline=0xffffff,
                     selected_label=0xffffff, style=Button.ROUNDRECT)
  # adding this button to the buttons group
buttons.append(button_icon3)

view1.append(button_switch.group)
view1.append(button_icon.group)
view1.append(button_icon2.group)
view1.append(button_icon3.group)


#pylint: disable=global-statement
def switch_view(what_view):
    global view_live
    if what_view == 1:
        hideLayer(view2)
        hideLayer(view3)
        button_view1.selected = False
        button_view2.selected = True
        button_view3.selected = True
        showLayer(view1)
        view_live = 1
        print("View1 On")
    elif what_view == 2:
        # global icon
        hideLayer(view1)
        hideLayer(view3)
        showLayer(view2)
        view_live = 2
        print("View2 On")
    else:
        hideLayer(view1)
        hideLayer(view2)
        button_view1.selected = True
        button_view2.selected = True
        button_view3.selected = False
        showLayer(view3)
        view_live = 3
        print("View3 On")
#pylint: enable=global-statement

# Set veriables and startup states
showLayer(view1)

view_live = 1
icon = 1
button_mode = 1
switch_state = 0
switch_state1 = 0
switch_state2 = 0
switch_state3 = 1
button_switch.label = "OFF"
button_switch.selected = True
button_icon3.selected = True

# Update out Labels with display text.

text_box(feed1_label, 0,
        '{}/{}/{}'.format(time.localtime().tm_mon, time.localtime().tm_mday,time.localtime().tm_year), 12)

text_box(feed2_label, TABS_Y + 60, 'Light Hours (On/Off):', 32)

board.DISPLAY.show(splash)
localtime_refresh= time.monotonic()
# ------------- Code Loop ------------- #
while True:
    if (not localtime_refresh) or (time.monotonic() - localtime_refresh) > 600: # check internet time every 10 minutes
        print("Getting time from internet!")
        try:
            pyportal.get_local_time()
        except:
            pass
        localtime_refresh = time.monotonic()
        if switch_state == 1 and switch_state1 == 1 and time.localtime().tm_hour in range(6, 18):
            outlet.value = True
        elif switch_state == 1 and switch_state2 == 1 and time.localtime().tm_hour in range(6, 24):
            outlet.value = True
        elif switch_state == 1 and switch_state3 == 1 and time.localtime().tm_hour not in range(2, 6):
            outlet.value = True
        else:
            outlet.value = False
        text_box(feed1_label, 0,
        '{}/{}/{}'.format(time.localtime().tm_mon, time.localtime().tm_mday,time.localtime().tm_year), 12)
    else:
        pass

    touch = ts.touch_point

    # ------------- Handle Button Press Detection  ------------- #
    if touch:  # Only do this if the screen is touched
        # loop with buttons using enumerate() to number each button group as i
        for i, b in enumerate(buttons):
            if b.contains(touch):  # Test each button to see if it was pressed
                print('button%d pressed' % i)
                if i == 0:
                    pyportal.play_file(soundBeep)
                    # Toggle switch button type
                    if switch_state == 0:
                        switch_state = 1
                        b.label = "ON"
                        b.selected = False
                        pixel.fill(PURPLE)
                        print("Swich ON")
                        if switch_state1 == 1 and time.localtime().tm_hour in range(6, 18):
                            outlet.value = True
                        elif switch_state2 == 1 and time.localtime().tm_hour in range(6, 24):
                            outlet.value = True
                        elif switch_state3 == 1 and time.localtime().tm_hour not in range(2, 6):
                            outlet.value = True
                        else:
                            outlet.value = False
                    else:
                        switch_state = 0
                        b.label = "OFF"
                        b.selected = True
                        outlet.value = False
                        print("Swich OFF")
                        pixel.fill(BLACK)
                    # for debounce
                    while ts.touch_point:
                        pass
                    print("Swich Pressed")
                if i == 1:
                    pyportal.play_file(soundBeep)
                    # Toggle switch button type
                    if switch_state1 == 0:
                        switch_state1 = 1
                        switch_state2 = 0
                        switch_state3 = 0
                        b.selected = True
                        button_icon2.selected = False
                        button_icon3.selected = False
                        print("12/12")
                    else:
                        switch_state1 = 0
                        b.selected = False
                        print("Swich OFF")
                        button_icon2.selected = False
                        button_icon3.selected = False
                    # for debounce
                    while ts.touch_point:
                        pass
                if i == 2:
                    pyportal.play_file(soundBeep)
                    # Toggle switch button type
                    if switch_state2 == 0:
                        switch_state2 = 1
                        switch_state1 = 0
                        switch_state3 = 0
                        b.selected = True
                        button_icon.selected = False
                        button_icon3.selected = False
                        print("18/6")
                    else:
                        switch_state2 = 0
                        b.selected = False
                        button_icon.selected = False
                        button_icon3.selected = False
                        print("18/6")
                    # for debounce
                    while ts.touch_point:
                        pass
                if i == 3:
                    pyportal.play_file(soundBeep)
                    # Toggle switch button type
                    if switch_state3 == 0:
                        switch_state3 = 1
                        switch_state1 = 0
                        switch_state2 = 0
                        b.selected = True
                        button_icon.selected = False
                        button_icon2.selected = False
                        print("20/4")
                    else:
                        switch_state3 = 0
                        b.selected = False
                        button_icon.selected = False
                        button_icon2.selected = False
                        print("20/4 off")
                    # for debounce
                    while ts.touch_point:
                        pass
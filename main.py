from machine import Pin, SPI, ADC
import max7219
import time

from game1 import Game1

x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))
button = Pin(28, Pin.IN, Pin.PULL_UP)

spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19))
cs = Pin(17, Pin.OUT)

display = max7219.Matrix8x8(spi, cs, 1)
display.brightness(1)
display.fill(0)
display.show()

player_x = 0
player_y = 0

reset = [
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

loading = [
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,1],
    [1,0,0,0,1,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1],
]

games = [
    Game1
]

screen = [row[:] for row in reset]

slct_timer = 0
slct_threshold = 0.1

move_cooldown = 0.2
move_timer = 0

def direction(x_val, y_val, deadzone=8000):
    center = 32768
    dx = x_val - center
    dy = y_val - center
    
    direction = [0, 0]
    
    if(abs(dx) < deadzone and abs(dy) < deadzone):
        return direction
    
    if(dx > deadzone):
        direction[0] = 1
    elif(dx < -deadzone):
        direction[0] = -1
    
    if(dy > deadzone):
        direction[1] = 1
    elif(dy < -deadzone):
        direction[1] = -1
        
    return direction

def move(pos, movement, min_val=0, max_val=7):
    new_pos = pos + movement
    if(new_pos < min_val or new_pos > max_val):
        return pos
    return new_pos    

try:
    last = time.ticks_ms()
    
    while(True):
        now = time.ticks_ms()
        dt = (now - last) / 1000
        last = now
        
        x_val = x_axis.read_u16()
        y_val = y_axis.read_u16()
        btn_val = button.value()
        
        dir = direction(x_val, y_val)

        move_timer -= dt

        if(move_timer <= 0 and dir[0] != 0):
            player_x = move(player_x, dir[0], 0, len(games)-1)
            move_timer = move_cooldown
        
        screen = [row[:] for row in reset]

        screen[0][player_x] = 0

        display.fill(0)
        for y in range(8):
            for x in range(8):
                display.pixel(x, y, screen[y][x])
        
        display.show()
        
        if(btn_val == 0):
            slct_timer += dt
            if(slct_timer >= slct_threshold):
                games[player_x](display, x_axis, y_axis, button).main()
                slct_timer = 0
                
                cooldown = 0.5
                start = time.ticks_ms()
                
                while(time.ticks_ms() - start) < int(cooldown * 1000):
                    for y in range(8):
                        for x in range(8):
                            display.pixel(x, y, loading[y][x])
                    display.show()
        else:
            slct_timer = 0
        
        time.sleep(0.01)
finally:
    display.fill(0)
    display.show()
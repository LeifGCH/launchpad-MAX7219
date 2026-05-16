from machine import Pin, ADC
import time
import urandom

class Bullet:
    def __init__(self, x, y, dx, dy, speed=10):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = speed
        
        #self.flash_timer = 0
        #self.flash_interval = 0.3
        #self.visible = True

    def update(self, dt):
        self.x += self.dx * self.speed * dt
        self.y += self.dy * self.speed * dt

        #self.flash_timer += dt
        #if(self.flash_timer >= self.flash_interval):
        #    self.visible = not self.visible
        #    self.flash_timer = 0
            
    def is_offscreen(self):
        return self.x < 0 or self.x > 7 or self.y < 0 or self.y > 7

    def draw(self, display):
        #if(self.visible):
        display.pixel(int(self.x), int(self.y), 1)

class Game1:
    def __init__(self, display, x_axis, y_axis, button):
        self.display = display
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.button = button
        
        self.flash_timer = 0
        self.flash_interval = 0.2
        self.visible = True

        self.player_x = 3
        self.player_y = 4

        self.bullets = []

        self.reset = [[0]*8 for _ in range(8)]
        self.screen = [row[:] for row in self.reset]

    def random_bullet(self):
        edge = urandom.randint(0, 3)

        if(edge == 0):
            x = urandom.randint(0, 7)
            y = 0
            if(x == 0):
                dx, dy = 1, 1
            elif(x == 7):
                dx, dy = -1, 1
            else:
                dx, dy = 0, 1
        elif(edge == 1):
            x = urandom.randint(0, 7)
            y = 7
            if(x == 0):
                dx, dy = 1, -1
            elif(x == 7):
                dx, dy = -1, -1
            else:
                dx, dy = 0, -1
        elif(edge == 2):
            x = 0
            y = urandom.randint(0, 7)
            if(y == 0):
                dx, dy = 1, 1
            elif(y == 7):
                dx, dy = 1, -1
            else:
                dx, dy = 1, 0
        else:
            x = 7
            y = urandom.randint(0, 7)
            if(y == 0):
                dx, dy = -1, 1
            elif(y == 7):
                dx, dy = -1, -1
            else:
                dx, dy = -1, 0

        return x, y, dx, dy

    def direction(self, x_val, y_val, deadzone=8000):
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

    def move(self, pos, movement, min_val=0, max_val=7):
        new_pos = pos + movement
        if new_pos < min_val or new_pos > max_val:
            return pos
        return new_pos

    def create_bullet(self):
        x, y, dx, dy = self.random_bullet()
        bullet = Bullet(x, y, dx, dy, speed=3)
        self.bullets.append(bullet)

    def main(self):
        spawn_interval = 1.0
        spawn_timer = 0

        exit_timer = 0
        exit_threshold = 1.0
        
        move_cooldown = 0.1
        move_timer = 0

        last = time.ticks_ms()
        
        while(True):
            now = time.ticks_ms()
            dt = (now - last) / 1000
            last = now

            spawn_timer += dt
            if(spawn_timer >= spawn_interval):
                self.create_bullet()
                spawn_timer = 0

            for b in self.bullets:
                b.update(dt)

            self.bullets = [b for b in self.bullets if not b.is_offscreen()]

            x_val = self.x_axis.read_u16()
            y_val = self.y_axis.read_u16()
            btn_val = self.button.value()

            dir = self.direction(x_val, y_val)

            move_timer -= dt

            if(move_timer <= 0):
                if(dir[0] != 0):
                    self.player_x = self.move(self.player_x, dir[0])
                    move_timer = move_cooldown
                if(dir[1] != 0):
                    self.player_y = self.move(self.player_y, dir[1])
                    move_timer = move_cooldown

            self.display.fill(0)
            
            self.flash_timer += dt
            
            if(self.flash_timer >= self.flash_interval):
                self.visible = not self.visible
                self.flash_timer = 0
                
            if(self.visible):
                self.display.pixel(self.player_x, self.player_y, 1)

            for b in self.bullets:
                b.draw(self.display)

            self.display.show()

            if(btn_val == 0):
                exit_timer += dt
                if(exit_timer >= exit_threshold):
                    return
            else:
                exit_timer = 0

            time.sleep(0.01)
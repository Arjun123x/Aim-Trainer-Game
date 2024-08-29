import pygame
import math
import random
import time
pygame.init()
pygame.mixer.init()
# Load sound effects
hit_sound = pygame.mixer.Sound('sounds/eLaser.wav')  
bomb_sound = pygame.mixer.Sound('sounds/bomb_sound.mp3')
#bombs class
pygame.mixer.music.load('sounds/minecraft.mp3')
pygame.mixer.music.set_volume(0.5)
hit_sound.set_volume(0.5)
pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely

# Define window
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")
BOMB_SIZE = (50, 50)

bomb_image = pygame.image.load('bomb.png').convert_alpha()
bomb_image = pygame.transform.scale(bomb_image, BOMB_SIZE)

TARGET_INCREMENT = 600
#BOMB_INCREMENT = 1000
TARGET_EVENT = pygame.USEREVENT  # Fixed event type reference
#BOMB_EVENT = pygame.USEREVENT
TARGET_PADDING = 30
BG_COLOR = (30, 45, 57) 
LIVES = 15
FONT = pygame.font.SysFont("comicsans", 24)

class Bomb:
    def __init__(self, x, y, lifetime=3500):
        self.x = x
        self.y = y
        self.image = bomb_image
        self.size = BOMB_SIZE[1]/2
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.creation_time = pygame.time.get_ticks()  # Track the time when the bomb was created
        self.lifetime = lifetime  # Duration the bomb will stay on screen (in milliseconds)

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.creation_time > self.lifetime:
            return False  # Indicate that this bomb should be removed
        return True
    
    def draw(self, window):
        window.blit(self.image, (self.x, self.y))
    
    def collide(self, x, y):
        return self.rect.collidepoint(x, y)
    


class Target:
    MAX_SIZE = 35
    GROWTH_RATE = 0.7
    DECAY_RATE = 0.05
    COLOR = (200, 100, 0)
    SECOND_COLOR = (255, 255, 255)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True
        self.num_spokes = 10
        self.angle = 0
        self.speed = 2

    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False 

        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.DECAY_RATE

        self.angle += self.speed
        if self.angle >= 360:
            self.angle -= 360
        
        if self.size <= 0:
            return False
        return True

    def draw(self, window):
        pygame.draw.circle(window, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(window, self.SECOND_COLOR,
                           (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(window, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(window, self.SECOND_COLOR,
                           (self.x, self.y), self.size * 0.4)
        """
        # Draw the circular target
        pygame.draw.circle(window, self.COLOR, (self.x, self.y), int(self.size), 4)
        
        # Draw the spokes
        for i in range(self.num_spokes):
            spoke_angle = self.angle + (i * (360 / self.num_spokes))
            radians = math.radians(spoke_angle)
            end_x = self.x + self.size * math.cos(radians)  # Use self.size instead of self.radius
            end_y = self.y + self.size * math.sin(radians)
            pygame.draw.line(window, self.SECOND_COLOR, (self.x, self.y), (end_x, end_y), 3)
            """
            
    
    def collide(self, x, y):
        # Calculate the distance between the target's center and the point
        distance = math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
        return distance <= self.size

def draw(window, targets, bombs):
    window.fill(BG_COLOR)
    for target in targets:
        target.draw(window)
    for bomb in bombs:
        bomb.draw(window)


def format_time(secs):
    milli = math.floor(int(secs * 1000 % 1000) / 100)
    seconds = int(round(secs % 60, 1))
    minutes = int(secs // 60)

    return f"Time: {minutes:02d}:{seconds:02d}.{milli}"


def draw_top_bar(window, elapsed_time, target_pressed, misses, clicks):
    pygame.draw.rect(window, (137, 137, 137), (0, 0, WIDTH, 50))
    #render the font

    time_label = FONT.render(f"{format_time(elapsed_time)}", 1, "black")
    speed_label = FONT.render(f"Speed: {round(target_pressed / elapsed_time, 1)} t/s", 1, "black")
    accuracy_label = FONT.render(f"Accuracy: {round((target_pressed/clicks) * 100, 2)}%", 1, "black")
    lives_label = FONT.render(f"Lives: {LIVES - misses}", 1, "black")

    window.blit(time_label, (5, 5))
    window.blit(speed_label, (200, 5))
    window.blit(accuracy_label, (425, 5))
    window.blit(lives_label, (675, 5))


def end_screen(window, elapsed_time, target_pressed, misses, clicks):
    window.fill(BG_COLOR)

    time_label = FONT.render(f"{format_time(elapsed_time)}", 1, "white")
    speed_label = FONT.render(f"Speed: {round(target_pressed / elapsed_time, 1)} t/s", 1, "black")
    accuracy_label = FONT.render(f"Accuracy: {round((target_pressed/clicks) * 100, 2)}%", 1, "white")
    hits_label = FONT.render(f"Hits: {target_pressed}", 1, "black")
    

    window.blit(time_label, (get_middle(time_label), 100))
    window.blit(speed_label, (get_middle(speed_label), 200))
    window.blit(accuracy_label, (get_middle(accuracy_label), 300))
    window.blit(hits_label, (get_middle(hits_label), 400))


    pygame.display.update()

    run = True
    while run:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or event.type == pygame.KEYDOWN):
                quit()


def get_middle(surface):
    return (WIDTH/2) - (surface.get_width()/2)


def main():
    target_pressed = 0
    clicks = 1
    start_time = time.time()
    losses = 0
    misses = 0
    targets = []
    bombs = []

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)
    clock = pygame.time.Clock()
    proportion_of_bombs = 0

    run = True
    while run:
        click = False
        clock.tick(90)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == TARGET_EVENT:  # Fixed event reference

                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + 50, HEIGHT - TARGET_PADDING)
                target = Target(x, y)
                targets.append(target)

                if(proportion_of_bombs%3 == 0):
                    x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                    y = random.randint(TARGET_PADDING + 50, HEIGHT - TARGET_PADDING)
                    bomb = Bomb(x, y)
                    bombs.append(bomb)
                proportion_of_bombs += 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1


        
        
        for target in targets:
            if(target.collide(mouse_x, mouse_y) and click):
                hit_sound.play()
                targets.remove(target)
                target_pressed += 1


            target.update()
            if not target.update():
                misses += 1
                targets.remove(target)
        
        for bomb1 in bombs:
            if(bomb1.collide(mouse_x, mouse_y) and click):
                bomb_sound.play()
                time.sleep(5)  # Pause for 5 seconds
                end_screen(WIN, elapsed_time, target_pressed, misses, clicks)
                time_label = FONT.render(f"You hit a bomb!! Avoid them to stay alive longer :)", 1, "black")
                WIN.blit(time_label, (get_middle(time_label), 50))
            bool = bomb1.update()
            if(not bool):
                bombs.remove(bomb1)

            
    
            

        if(misses >= LIVES):
            end_screen(WIN, elapsed_time, target_pressed, misses, clicks) #end game here
        draw(WIN, targets, bombs)
        draw_top_bar(WIN, elapsed_time, target_pressed, misses, clicks)
        pygame.display.update()
        

    pygame.quit()

if __name__ == "__main__":
    main()

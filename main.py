

# main.py
import pygame
import random
import sys

# ---------- CONFIG ----------
WIDTH, HEIGHT = 480, 700
FPS = 60

PLAYER_WIDTH, PLAYER_HEIGHT = 50, 90
PLAYER_Y_OFFSET = 20  # distance from bottom

OBSTACLE_WIDTH_RANGE = (40, 80)
OBSTACLE_HEIGHT = 90
OBSTACLE_COLOR = (180, 40, 40)

BG_COLOR = (30, 30, 30)
ROAD_COLOR = (50, 50, 50)
LANE_MARK_COLOR = (230, 230, 230)
LANE_MARK_WIDTH = 6
LANE_MARK_GAP = 30

FONT_NAME = "freesansbold.ttf"

# ---------- INITIALIZE ----------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Dodger")
clock = pygame.time.Clock()
font_small = pygame.font.Font(FONT_NAME, 20)
font_big = pygame.font.Font(FONT_NAME, 48)

# ---------- GAME CLASSES ----------
class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - PLAYER_Y_OFFSET
        self.speed = 6
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = (40, 160, 200)

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            self.x -= self.speed
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.x += self.speed
        # keep inside screen
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        # windshield
        wind = pygame.Rect(self.x + 10, self.y + 10, self.width - 20, 18)
        pygame.draw.rect(surface, (200, 240, 255), wind, border_radius=4)

class Obstacle:
    def __init__(self, x, width, speed):
        self.width = width
        self.height = OBSTACLE_HEIGHT
        self.x = x
        self.y = -self.height
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt):
        # dt is time delta, but we move by speed per frame for simplicity
        self.y += self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        pygame.draw.rect(surface, OBSTACLE_COLOR, self.rect, border_radius=6)
        # simple window indicator
        win = pygame.Rect(self.x + 8, self.y + 10, self.width - 16, 24)
        pygame.draw.rect(surface, (200, 230, 255), win, border_radius=3)

# ---------- HELPERS ----------
def draw_road(surface, offset):
    # fill background
    surface.fill(BG_COLOR)
    # draw road rectangle with small margins
    margin = 40
    pygame.draw.rect(surface, ROAD_COLOR, (margin, 0, WIDTH - margin*2, HEIGHT))
    # center dashed lane marker
    lane_x = WIDTH // 2 - LANE_MARK_WIDTH // 2
    y = -offset % (LANE_MARK_GAP + 20)
    while y < HEIGHT:
        pygame.draw.rect(surface, LANE_MARK_COLOR, (lane_x, y, LANE_MARK_WIDTH, 40), border_radius=3)
        y += 40 + LANE_MARK_GAP

def draw_text(surface, text, font, color, center):
    img = font.render(text, True, color)
    rect = img.get_rect(center=center)
    surface.blit(img, rect)

# ---------- MAIN GAME LOOP ----------
def game_loop():
    player = Player()
    obstacles = []
    spawn_timer = 0.0
    spawn_interval = 1000  # ms between spawns (decreases over time)
    obstacle_speed = 4
    score = 0
    running = True
    last_time = pygame.time.get_ticks()

    while running:
        now = pygame.time.get_ticks()
        dt = now - last_time
        last_time = now
        # --- input ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player.update(keys)

        # --- spawning ---
        spawn_timer += dt
        # increase difficulty gradually by shrinking spawn_interval and increasing speed
        if spawn_timer >= spawn_interval:
            spawn_timer = 0
            w = random.randint(*OBSTACLE_WIDTH_RANGE)
            margin = 40
            x_min = margin
            x_max = WIDTH - margin - w
            x = random.randint(x_min, x_max)
            obstacles.append(Obstacle(x, w, obstacle_speed))

        # update obstacles
        for obs in obstacles:
            obs.update(dt)

        # remove off-screen obstacles and increase score
        removed = [o for o in obstacles if o.y > HEIGHT]
        for r in removed:
            obstacles.remove(r)
            score += 1

        # collision check
        for obs in obstacles:
            if player.rect.colliderect(obs.rect):
                return score  # game over, return final score

        # increase difficulty slowly
        if score and score % 10 == 0:
            # every 10 points, nudge speed and spawn rate slightly
            obstacle_speed = 4 + (score // 10) * 0.5
            spawn_interval = max(400, 1000 - (score * 10))

        # draw
        draw_road(screen, now // 10)
        # draw side borders (optional)
        pygame.draw.rect(screen, (40,40,40), (0,0,40,HEIGHT))
        pygame.draw.rect(screen, (40,40,40), (WIDTH-40,0,40,HEIGHT))

        # draw player and obstacles
        player.draw(screen)
        for obs in obstacles:
            obs.draw(screen)

        # HUD
        draw_text(screen, f"Score: {score}", font_small, (255,255,255), (70, 20))

        pygame.display.flip()
        clock.tick(FPS)

def game_over_screen(final_score):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # restart
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        draw_road(screen, 0)
        draw_text(screen, "GAME OVER", font_big, (255, 80, 80), (WIDTH//2, HEIGHT//2 - 60))
        draw_text(screen, f"Score: {final_score}", font_small, (255,255,255), (WIDTH//2, HEIGHT//2))
        draw_text(screen, "Press ENTER to play again or ESC to quit", font_small, (200,200,200), (WIDTH//2, HEIGHT//2 + 60))
        pygame.display.flip()
        clock.tick(15)

def main():
    while True:
        final_score = game_loop()
        game_over_screen(final_score)

if __name__ == "__main__":
    main()

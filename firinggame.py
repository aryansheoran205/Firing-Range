import pygame
import math
import time

# 1. SETUP - Initialize game and screen
pygame.init()
WIDTH, HEIGHT = 1200, 800 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Box Shooter - Smart Chaser BOT") 
clock = pygame.time.Clock() 

# 2. COLORS - Game color palette
BG_COLOR = (30, 30, 30)      
PLAYER_COLOR = (0, 128, 255) 
ENEMY_COLOR = (255, 50, 50)  
SHIELD_COLOR = (0, 255, 255) 
BULLET_COLOR = (255, 255, 0) 
WALL_COLOR = (200, 200, 200) 
WHITE = (255, 255, 255)      

# 3. FONTS - Text writing styles
font = pygame.font.SysFont(None, 40)       
name_font = pygame.font.SysFont(None, 25)  

# 4. GAME VARIABLES - Player and BOT details
player_name = "Mumbai" 
enemy_name = "BOT"     

player_x, player_y = 100, 300
player_size = 40 

# ---> BOT CODE: SETUP <---
# Initial spawn position of the Bot (X=800 keeps it within boundary)
enemy_x, enemy_y = 800, 400 

# --- Wall (Obstacles) Setup ---
walls = [
    pygame.Rect(300, 200, 500, 15), 
    pygame.Rect(200, 600, 500, 15), 
    pygame.Rect(900, 200, 15, 400)  
]

# --- Timers and Cooldowns ---
FIRE_COOLDOWN = 5.0    
SHIELD_COOLDOWN = 10.0 
SHIELD_DURATION = 3.0  

last_fire_time = -5.0   
last_shield_use_time = -10.0
is_shield_active = False 

bullets = []        
enemy_bullets = []  

# ---> BOT CODE: SHOOT TIMER <---
# Timer to track the last time the Bot fired a bullet
last_enemy_shot = time.time()

# Health Points (HP)
player_hp = 3
enemy_hp = 3 # Bot's Health

# Game Win/Loss status
game_over = False
win = False


# 5. MAIN GAME LOOP - Runs until the game is closed
running = True
while running:
    screen.fill(BG_COLOR) 
    current_time = time.time() 

    # --- Events (Keyboard and Mouse inputs) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
        
        # --- Player Firing Logic ---
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if current_time - last_fire_time >= FIRE_COOLDOWN:
                mx, my = pygame.mouse.get_pos() 
                angle = math.atan2(my - (player_y+20), mx - (player_x+20))
                bullets.append([player_x+20, player_y+20, math.cos(angle)*7, math.sin(angle)*7])
                last_fire_time = current_time 
            else:
                print("Wait! Gun reloading...")

        # --- Game Restart Logic ---
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                player_hp, enemy_hp = 3, 3
                player_x, player_y = 100, 300
                enemy_x, enemy_y = 800, 400 # Bot resets to 800 on restart
                bullets.clear()
                enemy_bullets.clear()
                game_over = False
                last_fire_time = -5
                last_shield_use_time = -10

    if not game_over:
        keys = pygame.key.get_pressed() 
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        
        # PLAYER MOVEMENT & COLLISION
        old_px = player_x
        if keys[pygame.K_a]: player_x -= 5 
        if keys[pygame.K_d]: player_x += 5 
        player_rect.x = player_x
        if player_rect.collidelist(walls) != -1: player_x = old_px 

        old_py = player_y
        if keys[pygame.K_w]: player_y -= 5 
        if keys[pygame.K_s]: player_y += 5 
        player_rect.y = player_y
        if player_rect.collidelist(walls) != -1: player_y = old_py 

        # Screen Borders
        if player_x < 0: player_x = 0
        if player_x > WIDTH - player_size: player_x = WIDTH - player_size
        if player_y < 0: player_y = 0
        if player_y > HEIGHT - player_size: player_y = HEIGHT - player_size

        # Shield Logic
        if keys[pygame.K_f]:
            if current_time - last_shield_use_time >= SHIELD_COOLDOWN:
                is_shield_active = True
                last_shield_use_time = current_time

        if is_shield_active and (current_time - last_shield_use_time > SHIELD_DURATION):
            is_shield_active = False

        
        # ---> BOT CODE: AI & MOVEMENT <---
        enemy_speed = 3 # Bot movement speed (Adjustable)
        # Create a rectangle for the Bot to check for collisions
        enemy_rect = pygame.Rect(enemy_x, enemy_y, player_size, player_size)

        # Bot X-Axis Movement (Chases player horizontally)
        old_ex = enemy_x
        if enemy_x < player_x: enemy_x += enemy_speed
        elif enemy_x > player_x: enemy_x -= enemy_speed
        enemy_rect.x = enemy_x
        # If Bot hits a wall, stop X-movement but allow Y-movement
        if enemy_rect.collidelist(walls) != -1: enemy_x = old_ex

        # Bot Y-Axis Movement (Chases player vertically)
        old_ey = enemy_y
        if enemy_y < player_y: enemy_y += enemy_speed
        elif enemy_y > player_y: enemy_y -= enemy_speed
        enemy_rect.y = enemy_y
        # If wall is hit, stop Y-movement (Slide logic)
        if enemy_rect.collidelist(walls) != -1: enemy_y = old_ey

        # Bot Screen Borders (Prevent Bot from leaving screen)
        if enemy_x < 0: enemy_x = 0
        if enemy_x > WIDTH - player_size: enemy_x = WIDTH - player_size
        if enemy_y < 0: enemy_y = 0
        if enemy_y > HEIGHT - player_size: enemy_y = HEIGHT - player_size


        # ---> BOT CODE: SHOOTING (TARGETING) <---
        # Fire a new bullet every 1.5 seconds
        if current_time - last_enemy_shot > 1.5: 
            # Calculate the exact angle towards the player using math.atan2
            angle = math.atan2(player_y - enemy_y, player_x - enemy_x)
            # Add bullet to list: [X-pos, Y-pos, X-Speed, Y-Speed]
            enemy_bullets.append([enemy_x+20, enemy_y+20, math.cos(angle)*7, math.sin(angle)*7])
            # Record the shooting time
            last_enemy_shot = current_time


        # BULLET LOGIC - Bullet processing
        
        # 1. Player Bullets
        for b in bullets[:]:
            b[0] += b[2] 
            b[1] += b[3] 
            bullet_rect = pygame.Rect(b[0], b[1], 10, 10)
            
            if bullet_rect.collidelist(walls) != -1:
                bullets.remove(b)
                continue 
                
            pygame.draw.rect(screen, BULLET_COLOR, bullet_rect) 
            
            # ---> BOT CODE: DAMAGE THE BOT <---
            enemy_rect_check = pygame.Rect(enemy_x, enemy_y, player_size, player_size)
            # If player bullet hits the bot
            if enemy_rect_check.collidepoint(b[0], b[1]):
                enemy_hp -= 1 # Reduce Bot HP
                bullets.remove(b)
            elif b[0] < 0 or b[0] > WIDTH or b[1] < 0 or b[1] > HEIGHT:
                bullets.remove(b)

        # 2. ---> BOT CODE: BOT BULLETS & DAMAGE <---
        player_rect_check = pygame.Rect(player_x, player_y, player_size, player_size)
        shield_rect = pygame.Rect(player_x - 10, player_y - 10, 60, 60) 

        for b in enemy_bullets[:]:
            b[0] += b[2] # Move bullet (X)
            b[1] += b[3] # Move bullet (Y)
            bullet_rect = pygame.Rect(b[0], b[1], 10, 10)
            
            # Remove bullet if it hits a wall
            if bullet_rect.collidelist(walls) != -1:
                enemy_bullets.remove(b)
                continue
                
            pygame.draw.rect(screen, ENEMY_COLOR, bullet_rect)

            # If Shield is ON, bullet is blocked without HP loss
            if is_shield_active and shield_rect.collidepoint(b[0], b[1]):
                enemy_bullets.remove(b) 
            # If Bot bullet hits the player
            elif player_rect_check.collidepoint(b[0], b[1]):
                player_hp -= 1 # Reduce Player HP
                enemy_bullets.remove(b)
            elif b[0] < 0 or b[0] > WIDTH or b[1] < 0 or b[1] > HEIGHT:
                enemy_bullets.remove(b)

        # Win/Lose Check (Death detection)
        if player_hp <= 0: game_over = True; win = False # Player died, Bot wins
        if enemy_hp <= 0: game_over = True; win = True   # Bot died, Player wins


        # DRAWING (Render all objects on screen)
        for wall in walls:
            pygame.draw.rect(screen, WALL_COLOR, wall)

        player_name_text = name_font.render(player_name, True, WHITE)
        enemy_name_text = name_font.render(enemy_name, True, WHITE)
        screen.blit(player_name_text, (player_x, player_y - 20))
        # ---> BOT CODE: DRAW BOT NAME <---
        screen.blit(enemy_name_text, (enemy_x, enemy_y - 20))

        pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, player_size, player_size))
        # ---> BOT CODE: DRAW BOT ON SCREEN <---
        pygame.draw.rect(screen, ENEMY_COLOR, (enemy_x, enemy_y, player_size, player_size))

        if is_shield_active:
            pygame.draw.rect(screen, SHIELD_COLOR, (player_x-5, player_y-5, 50, 50), 3)

        
        # UI & TEXT (Gun, Shield, and HP status)
        time_left_fire = max(0, FIRE_COOLDOWN - (current_time - last_fire_time))
        if time_left_fire == 0:
            fire_msg = font.render("GUN READY!", True, (0, 255, 0)) 
        else:
            fire_msg = font.render(f"Reload: {int(time_left_fire)}s", True, (255, 255, 0)) 
        screen.blit(fire_msg, (10, 10))

        time_left_shield = max(0, SHIELD_COOLDOWN - (current_time - last_shield_use_time))
        if is_shield_active:
            shield_msg = font.render("SHIELD ON!", True, SHIELD_COLOR)
        elif time_left_shield == 0:
            shield_msg = font.render("Shield Ready (F)", True, SHIELD_COLOR)
        else:
            shield_msg = font.render(f"Shield Wait: {int(time_left_shield)}s", True, (100, 100, 100))
        screen.blit(shield_msg, (10, 50))

        hp_msg = font.render(f"Player HP: {player_hp} | Enemy HP: {enemy_hp}", True, WHITE)
        screen.blit(hp_msg, (500, 10)) 

    # Game Over Menu
    else:
        msg = "YOU WIN" if win else "YOU LOSE"
        col = (0, 255, 0) if win else (255, 0, 0)
        screen.blit(font.render(msg, True, col), (550, 350))
        screen.blit(font.render("Press SPACE to Restart", True, WHITE), (480, 400))

    pygame.display.update()
    clock.tick(60)

pygame.quit()

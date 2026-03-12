import pygame
import math
import time

# 1. SETUP - Game ki shuruaat aur screen
pygame.init()
WIDTH, HEIGHT = 1200, 800 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Box Shooter - Smart Chaser BOT") 
clock = pygame.time.Clock() 

# 2. COLORS - Game ke saare rang
BG_COLOR = (30, 30, 30)      
PLAYER_COLOR = (0, 128, 255) 
ENEMY_COLOR = (255, 50, 50)  
SHIELD_COLOR = (0, 255, 255) 
BULLET_COLOR = (255, 255, 0) 
WALL_COLOR = (200, 200, 200) 
WHITE = (255, 255, 255)      

# 3. FONTS - Text ki writing style
font = pygame.font.SysFont(None, 40)       
name_font = pygame.font.SysFont(None, 25)  

# 4. GAME VARIABLES - Player aur BOT ki details
player_name = "Mumbai" 
enemy_name = "BOT"     

player_x, player_y = 100, 300
player_size = 40 

# ---> BOT CODE: SETUP <---
# Bot kahan se shuru hoga. X=800 rakha hai taaki wo line ke andar paida ho.
enemy_x, enemy_y = 800, 400 

# --- Deewar (Walls) Setup ---
walls = [
    pygame.Rect(300, 200, 500, 15), 
    pygame.Rect(200, 600, 500, 15), 
    pygame.Rect(900, 200, 15, 400)  
]

# --- Timers aur Cooldown ---
FIRE_COOLDOWN = 5.0    
SHIELD_COOLDOWN = 10.0 
SHIELD_DURATION = 3.0  

last_fire_time = -5.0   
last_shield_use_time = -10.0
is_shield_active = False 

bullets = []        
enemy_bullets = []  

# ---> BOT CODE: SHOOT TIMER <---
# Bot ne aakhri goli kab chalayi thi, usko yaad rakhne ke liye timer
last_enemy_shot = time.time()

# Health Points (HP)
player_hp = 3
enemy_hp = 3 # Bot ki Health

# Game jeetne ya haarne ka status
game_over = False
win = False


# 5. MAIN GAME LOOP - Jab tak game chalega
running = True
while running:
    screen.fill(BG_COLOR) 
    current_time = time.time() 

    # --- Events (Keyboard aur Mouse ka use) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
        
        # --- Player Goli Chalayega ---
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if current_time - last_fire_time >= FIRE_COOLDOWN:
                mx, my = pygame.mouse.get_pos() 
                angle = math.atan2(my - (player_y+20), mx - (player_x+20))
                bullets.append([player_x+20, player_y+20, math.cos(angle)*7, math.sin(angle)*7])
                last_fire_time = current_time 
            else:
                print("Wait! Gun reloading...")

        # --- Game Restart karna ---
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                player_hp, enemy_hp = 3, 3
                player_x, player_y = 100, 300
                enemy_x, enemy_y = 800, 400 # Restart par bot wapas 800 pe aayega
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
        enemy_speed = 3 # Bot ki bhagne ki speed (Isko bada/ghata sakte ho)
        # Bot ka box banaya check karne ke liye ki wo kahan takraya hai
        enemy_rect = pygame.Rect(enemy_x, enemy_y, player_size, player_size)



        #Gemini


        # Bot X-Axis Movement (Left-Right check karega aur player ki taraf aayega)
        old_ex = enemy_x
        if enemy_x < player_x: enemy_x += enemy_speed
        elif enemy_x > player_x: enemy_x -= enemy_speed
        enemy_rect.x = enemy_x
        # Agar bot deewar se takraya, toh X disha mein wahi ruk jayega (Par Y mein bhagta rahega)
        if enemy_rect.collidelist(walls) != -1: enemy_x = old_ex

        # Bot Y-Axis Movement (Up-Down check karega aur player ki taraf aayega)
        old_ey = enemy_y
        if enemy_y < player_y: enemy_y += enemy_speed
        elif enemy_y > player_y: enemy_y -= enemy_speed
        enemy_rect.y = enemy_y
        # Agar deewar aayi toh Y disha mein rukega (Slide logic)
        if enemy_rect.collidelist(walls) != -1: enemy_y = old_ey

        # Bot Screen Borders (Bot ko screen ke bahar jaane se rokne ka code)
        if enemy_x < 0: enemy_x = 0
        if enemy_x > WIDTH - player_size: enemy_x = WIDTH - player_size
        if enemy_y < 0: enemy_y = 0
        if enemy_y > HEIGHT - player_size: enemy_y = HEIGHT - player_size


        # ---> BOT CODE: SHOOTING (NISHANA LAGANA) <---
        # Agar 1.5 second ho gaye hain purani goli chalaye hue, toh nayi goli chalayega
        if current_time - last_enemy_shot > 1.5: 
            # math.atan2 se bot player ki exact direction (angle) nikalta hai
            angle = math.atan2(player_y - enemy_y, player_x - enemy_x)
            # Goli list mein add karta hai: [X, Y, X-Speed, Y-Speed]
            enemy_bullets.append([enemy_x+20, enemy_y+20, math.cos(angle)*7, math.sin(angle)*7])
            # Goli chalane ka time yaad kar leta hai
            last_enemy_shot = current_time

        # gemini end here


        # BULLET LOGIC - Goliyon ka hisaab kitab
        
        # 1. Player Ki Goliyaan
        for b in bullets[:]:
            b[0] += b[2] 
            b[1] += b[3] 
            bullet_rect = pygame.Rect(b[0], b[1], 10, 10)
            
            if bullet_rect.collidelist(walls) != -1:
                bullets.remove(b)
                continue 
                
            pygame.draw.rect(screen, BULLET_COLOR, bullet_rect) 
            
            # ---> BOT CODE: BOT KO DAMAGE DENA <---
            enemy_rect_check = pygame.Rect(enemy_x, enemy_y, player_size, player_size)
            # Agar player ki goli bot ko lag gayi
            if enemy_rect_check.collidepoint(b[0], b[1]):
                enemy_hp -= 1 # Bot ka 1 HP kam kar do
                bullets.remove(b)
            elif b[0] < 0 or b[0] > WIDTH or b[1] < 0 or b[1] > HEIGHT:
                bullets.remove(b)

        # 2. ---> BOT CODE: BOT KI GOLIYAAN AUR DAMAGE <---
        player_rect_check = pygame.Rect(player_x, player_y, player_size, player_size)
        shield_rect = pygame.Rect(player_x - 10, player_y - 10, 60, 60) 

        for b in enemy_bullets[:]:
            b[0] += b[2] # Goli aage badhao (X)
            b[1] += b[3] # Goli aage badhao (Y)
            bullet_rect = pygame.Rect(b[0], b[1], 10, 10)
            
            # Agar bot ki goli deewar par lag gayi, toh gayab kar do
            if bullet_rect.collidelist(walls) != -1:
                enemy_bullets.remove(b)
                continue
                
            pygame.draw.rect(screen, ENEMY_COLOR, bullet_rect)

            # Agar Shield ON hai aur bot ki goli takrayi, toh bina HP kam kiye goli gayab kar do
            if is_shield_active and shield_rect.collidepoint(b[0], b[1]):
                enemy_bullets.remove(b) 
            # Agar bot ki goli sidha player ko lag gayi
            elif player_rect_check.collidepoint(b[0], b[1]):
                player_hp -= 1 # Player ka HP kam kar do
                enemy_bullets.remove(b)
            elif b[0] < 0 or b[0] > WIDTH or b[1] < 0 or b[1] > HEIGHT:
                enemy_bullets.remove(b)

        # Win/Lose Check (Koi mar gaya kya?)
        if player_hp <= 0: game_over = True; win = False # Player mar gaya, bot jeet gaya
        if enemy_hp <= 0: game_over = True; win = True   # Bot mar gaya, player jeet gaya


        # DRAWING (Sab kuch screen par banana)
        for wall in walls:
            pygame.draw.rect(screen, WALL_COLOR, wall)

        player_name_text = name_font.render(player_name, True, WHITE)
        enemy_name_text = name_font.render(enemy_name, True, WHITE)
        screen.blit(player_name_text, (player_x, player_y - 20))
        # ---> BOT CODE: BOT KA NAAM DRAW KARNA <---
        screen.blit(enemy_name_text, (enemy_x, enemy_y - 20))

        pygame.draw.rect(screen, PLAYER_COLOR, (player_x, player_y, player_size, player_size))
        # ---> BOT CODE: BOT KO SCREEN PAR DRAW KARNA <---
        pygame.draw.rect(screen, ENEMY_COLOR, (enemy_x, enemy_y, player_size, player_size))

        if is_shield_active:
            pygame.draw.rect(screen, SHIELD_COLOR, (player_x-5, player_y-5, 50, 50), 3)

        
        # UI & TEXT (Gun, Shield aur HP ka status)
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

import pygame
import random

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 825
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Freak Bird")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

#imgs
start_img = pygame.image.load("/Users/fumakasagi/Documents/Knights Hack/final_start.png")
play_img = pygame.image.load("/Users/fumakasagi/Documents/Knights Hack/background.jpg")

start_img = pygame.transform.scale(start_img, (WIDTH, HEIGHT))
#resize the img to fix the window
original_width, original_height = play_img.get_size()
scaling_factor = HEIGHT / original_height
new_width = int(original_width * scaling_factor)
new_height = HEIGHT
play_img = pygame.transform.scale(play_img, (new_width, new_height)) 

#load pipe imgs
pipe_top_img = pygame.image.load("/Users/fumakasagi/Documents/Knights Hack/top_seaweed3.png")  
pipe_bottom_img = pygame.image.load("/Users/fumakasagi/Documents/Knights Hack/seaweed3.png")  

#load the bird img
bird_img = pygame.image.load("/Users/fumakasagi/Documents/Knights Hack/freak.png")  
bird_img = pygame.transform.scale(bird_img, (70, 70))  # Scale the bird image 

# Background movement variables
bg_x1 = 0  # Starting x position 
bg_x2 = new_width  # Starting x position of the second backgroun
bg_speed = 5  # Speed of background scrolling

# Clock
clock = pygame.time.Clock()
FPS = 30

# Bird variables
bird_x = 100
bird_y = HEIGHT // 2
bird_radius = 15
bird_dy = 0  # Bird's change in y 
gravity = 0.8
jump_strength = -10

# Pipe variables
pipe_width = 100  
pipe_gap = 250 
pipe_speed = 5
pipe_speed_increase_rate = 0.3  # Rate at which the speed increases per score
pipe_frequency = 2300  # Initial milliseconds between pipes
min_pipe_frequency = 900  # Minimum frequency limit (higher frequency)
pipe_list = []
last_pipe = pygame.time.get_ticks() - pipe_frequency

# Score
score = 0
font = pygame.font.SysFont(None, 36)

# Game status
game_state = 'start'  # 'start', 'play', 'game_over'


def create_pipe():
    min_pipe_height = 100
    max_pipe_height = HEIGHT - pipe_gap - 100
    pipe_height = random.randint(min_pipe_height, max_pipe_height)
    pipe_top_rect = pygame.Rect(WIDTH, 0, pipe_width, pipe_height)  
    pipe_bottom_rect = pygame.Rect(WIDTH, pipe_height + pipe_gap, pipe_width, HEIGHT - pipe_height - pipe_gap)
    return [pipe_top_rect, pipe_bottom_rect, False]


def move_pipes(pipes):
    global pipe_speed  
    for pipe in pipes:
        pipe_top_rect, pipe_bottom_rect, _ = pipe
        pipe_top_rect.x -= pipe_speed
        pipe_bottom_rect.x -= pipe_speed
    return pipes


def draw_pipes(pipes):
    for pipe in pipes:
        pipe_top_rect, pipe_bottom_rect, _ = pipe

        # Scale the pipe images wider while keeping the original height
        scaled_pipe_top_img = pygame.transform.scale(pipe_top_img, (pipe_top_rect.width + 50, pipe_top_rect.height))
        scaled_pipe_bottom_img = pygame.transform.scale(pipe_bottom_img, (pipe_bottom_rect.width + 50, pipe_bottom_rect.height))

        # Draw the wider pipe images using their scaled versions
        window.blit(scaled_pipe_top_img, (pipe_top_rect.x - 25, pipe_top_rect.y))  # Top pipe (centered)
        window.blit(scaled_pipe_bottom_img, (pipe_bottom_rect.x - 25, pipe_bottom_rect.y))  # Bottom pipe (centered)
        
        #debug (hitboxes for the pipe)
        #pygame.draw.rect(window, RED, pipe_top_rect, 2)  # Top pipe hitbox (red outline)
        #pygame.draw.rect(window, RED, pipe_bottom_rect, 2)  # Bottom pipe hitbox (red outline)


def check_collision(bird_rect, pipes):
    for pipe in pipes:
        pipe_top_rect, pipe_bottom_rect, _ = pipe
        if bird_rect.colliderect(pipe_top_rect) or bird_rect.colliderect(pipe_bottom_rect):
            return True
    if bird_y - bird_radius < 0 or bird_y + bird_radius > HEIGHT:
        return True
    return False


def remove_passed_pipes(pipes):
    return [pipe for pipe in pipes if pipe[0].x + pipe_width > 0]


def update_score(pipes, bird_x, score):
    global pipe_speed, pipe_frequency  
    for pipe in pipes:
        pipe_top_rect, pipe_bottom_rect, scored = pipe
        if pipe_top_rect.x + pipe_width < bird_x and not scored:
            score += 1
            pipe[2] = True
            pipe_speed += pipe_speed_increase_rate 
            
            # Adjust the pipe frequency, but don't let it go below the minimum limit
            pipe_frequency = max(min_pipe_frequency, pipe_frequency - 50)
            
    return score


def reset_game():
    global bird_y, bird_dy, pipe_list, score, last_pipe, game_state, pipe_speed, pipe_frequency
    bird_y = HEIGHT // 2
    bird_dy = 0
    pipe_list = []
    score = 0
    last_pipe = pygame.time.get_ticks() - pipe_frequency
    game_state = 'play'
    pipe_speed = 5  # Reset the pipe speed
    pipe_frequency = 2000  # Reset the pipe frequency


def draw_start_screen():
    window.blit(start_img, (0, 0))  # Display the start screen background

    # Create a "Start" button 
    button_font = pygame.font.SysFont(None, 70)

    # Create a surface for the text and make it transparent (fully invisible)
    start_button_surface = button_font.render("LLLLLLL", True, BLACK)
    start_button_surface.set_alpha(0)  # Set alpha to 0 to make it fully transparent
    start_button_rect = start_button_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
    start_button_rect.inflate_ip(0, 30)
    window.blit(start_button_surface, start_button_rect.topleft)

    pygame.display.update()

    return start_button_rect


def move_background():
    global bg_x1, bg_x2, bg_speed
    bg_x1 -= bg_speed  # Move the first background to the left
    bg_x2 -= bg_speed  # Move the second background to the left

    # If the first background goes off-screen, reset its position to the right
    if bg_x1 <= -new_width:
        bg_x1 = new_width

    # If the second background goes off-screen, reset its position to the right
    if bg_x2 <= -new_width:
        bg_x2 = new_width


HS = 0

# Main game loop
running = True
music_playing = False
while running:
    clock.tick(FPS)
    
    if game_state == 'start':
        # Draw the start screen
        start_button_rect = draw_start_screen()
        
        if not music_playing:
            pygame.mixer.music.load('spongebob-squarepants2.mp3')  # Load the start screen music
            pygame.mixer.music.play(-1)  # Play the music indefinitely (loop)
            music_playing = True
        # Check for events (clicking the start button)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    game_state = 'play'

    elif game_state == 'play':
        move_background()
        window.blit(play_img, (bg_x1, 0))  
        window.blit(play_img, (bg_x2, 0))  

        # Bird mechanics: apply gravity and update position
        bird_dy += gravity
        bird_y += bird_dy

        bird_rect = bird_img.get_rect(center=(bird_x, bird_y))  # Create a hitbox for the bird
        window.blit(bird_img, bird_rect.topleft)

        # Pipes: generate a new set of pipes at regular intervals
        if pygame.time.get_ticks() - last_pipe > pipe_frequency:
            pipe_list.append(create_pipe())
            last_pipe = pygame.time.get_ticks()

        pipe_list = move_pipes(pipe_list)
        pipe_list = remove_passed_pipes(pipe_list)
        draw_pipes(pipe_list)

        score = update_score(pipe_list, bird_x, score) # Update score based on passed pipes
        

        # Display score
        score_text = font.render(f"Freak Point: {score}", True, YELLOW)
        HS_text = font.render(f"Highest Freak Point: {HS}", True, YELLOW)

        window.blit(score_text, (10, 10))
        window.blit(HS_text, (325,10))

        if check_collision(bird_rect, pipe_list):
            game_state = 'game_over'
            pygame.mixer.music.load('freaky-bob-sad-made-with-Voicemod.mp3')
            pygame.mixer.music.play()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_dy = jump_strength
                    pygame.mixer.stop()
                    pygame.mixer.music.load('spongebob-laughing-sound-effect-[AudioTrimmer.com].mp3')
                    pygame.mixer.music.play()
        pygame.display.update()

    elif game_state == 'game_over':
        # Display game over screen
        end = pygame.image.load("/Users/fumakasagi/Documents/Knights Hack/special_Elite.png.png")
        window.blit(end, (0,0))
        pygame.display.update()
        

        #update HS
        if(score > HS):
            HS = score

        # Handle events for game over state
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reset_game()
                if event.key == pygame.K_ESCAPE: 
                    running = False                             

pygame.quit()
import pygame
from settings import *

class Bird(pygame.sprite.Sprite):
    def __init__(self, logger, game, bird_sprite, start_pos=(100, SCREEN_HEIGHT // 3)):
        super().__init__()
        self.logger = logger
        self.game = game 
        
        self.score = 0
        self.vertical_speed = 0
        self.initial_pos = start_pos
        self.is_started = False 
        
        try:
            self.image = pygame.transform.scale(bird_sprite, (PLAYER_SIZE, PLAYER_SIZE))
            hitbox_reduction = 10
            
            self.rect = self.image.get_rect(topleft=start_pos)
            self.rect.width -= hitbox_reduction * 2
            self.rect.height -= hitbox_reduction * 2
            self.rect.x += hitbox_reduction
            self.rect.y += hitbox_reduction
            
        except AttributeError:
            self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            self.image.fill(RED)
            self.rect = self.image.get_rect(topleft=start_pos)

    def apply_gravity(self):
        if self.is_started:
            self.vertical_speed += GRAVITY
            
            if self.vertical_speed > MAX_FALL_SPEED:
                self.vertical_speed = MAX_FALL_SPEED
                
            self.rect.y += int(self.vertical_speed)

    def flap(self):
        self.vertical_speed = FLAP_STRENGTH
        self.is_started = True 

    def update(self):
        self.apply_gravity()
        
    def reset(self):
        self.rect.topleft = self.initial_pos
        self.vertical_speed = 0 
        self.score = 0
        self.is_started = False 
        self.logger.log_info("Pássaro resetado para nova fase/jogo.")

    def point(self):
        self.score += 1
        self.logger.log_info(f"Pontuação: {self.score}")
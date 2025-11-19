import pygame
import random
from settings import *
import math

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, height, position, pipe_sprite, v_speed_mult):
        super().__init__()
        self.passed = False 
        
        h = max(SCREEN_HEIGHT * 1.5, height)
        self.position = position
        
        self.image = pygame.transform.scale(pipe_sprite, (PIPE_WIDTH, h))
        
        if position == 'top':
            self.image = pygame.transform.flip(self.image, False, True) 
            self.rect = self.image.get_rect(bottomleft=(x, y))
        else:
            self.rect = self.image.get_rect(topleft=(x, y))
            
        self.initial_y = self.rect.y
        self.v_speed_mult = v_speed_mult
        self.amplitude = 50 
        
        hitbox_reduction = 10 
        self.rect.left += hitbox_reduction
        self.rect.width -= hitbox_reduction * 2 
            
    def update(self, pipe_speed):
        self.rect.x -= pipe_speed
        
        if self.v_speed_mult > 0:
            time_factor = pygame.time.get_ticks() / 1000.0
            y_offset = self.amplitude * math.sin(time_factor * self.v_speed_mult * PIPE_V_SPEED)
            
            self.rect.y = self.initial_y + int(y_offset)


class PipeManager:
    def __init__(self, game, pipe_sprite):
        self.game = game
        self.pipe_sprite = pipe_sprite
        self.pipes = pygame.sprite.Group()
        self.last_pipe_time = pygame.time.get_ticks()
        
    def spawn_pipe(self):
        v_speed_mult = self.game.current_mechanic_setting['v_speed_mult']
        
        max_height = SCREEN_HEIGHT 
        gap_center_y = random.randint(int(max_height * 0.2), int(max_height * 0.8))
        
        top_y_align = gap_center_y - GAP_SIZE // 2 
        top_height = top_y_align
        pipe_top = Pipe(SCREEN_WIDTH, top_y_align, top_height, 'top', self.pipe_sprite, v_speed_mult) 
        
        bottom_y_align = gap_center_y + GAP_SIZE // 2 
        bottom_height = SCREEN_HEIGHT - bottom_y_align
        pipe_bottom = Pipe(SCREEN_WIDTH, bottom_y_align, bottom_height, 'bottom', self.pipe_sprite, v_speed_mult) 
        
        self.pipes.add(pipe_top, pipe_bottom)

    def update(self):
        current_time = pygame.time.get_ticks()
        
        pipe_speed = self.game.current_speed_setting['pipe_speed']
        
        if current_time - self.last_pipe_time > PIPE_SPAWN_TIME:
            self.spawn_pipe()
            self.last_pipe_time = current_time
            
        self.pipes.update(pipe_speed)
        
        for pipe in list(self.pipes):
            if pipe.rect.right < 0:
                pipe.kill()
            
            if not pipe.passed and pipe.rect.centerx < self.game.bird.rect.left:
                self.game.bird.point()
                pipe.passed = True
                
    def reset(self):
        self.pipes.empty()
        self.last_pipe_time = pygame.time.get_ticks()
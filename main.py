import pygame
import sys
import itertools 
import os 

from settings import *
from logger import GameLogger
from database import DatabaseManager
from player import Bird
from pipe import PipeManager
from scenes import MenuScene, RankingScene, UIScene, PhaseSelectScene 

class Game:
    def __init__(self):
        try:
            pygame.init()
            
            pygame.mixer.init() 
            
            if not pygame.font.get_init():
                pygame.font.init()
                
            self.SCREEN_WIDTH = SCREEN_WIDTH
            self.SCREEN_HEIGHT = SCREEN_HEIGHT
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.set_caption("BATMAN VOADOR GAME")
            self.clock = pygame.time.Clock()
            
            self.logger = GameLogger()
            self.db_manager = DatabaseManager()
            
            self.assets = self._load_assets()

            default_speed_key = "FÁCIL"
            default_mech_key = "ESTÁTICO"
            
            self.current_speed_setting = self._get_speed_setting(default_speed_key)
            self.current_mechanic_setting = self._get_mechanic_setting(default_mech_key)
            
            self.bird = Bird(self.logger, self, self.assets['bird_sprite']) 
            
            self.pipe_manager = None 
            
            self.menu_scene = MenuScene(self)
            self.ranking_scene = RankingScene(self)
            self.phase_select_scene = PhaseSelectScene(self)
            self.ui_scene = UIScene(self)
            
            self.current_state = STATE_MENU
            self.game_running = True
            self.logger.log_info("Jogo inicializado.")

            self._play_music()
            
        except Exception as e:
            print(f"Erro na Inicialização: {e}")
            self.logger.log_error(f"Erro na Inicialização: {e}")
            sys.exit() 

    def _load_assets(self):
        assets = {}
        base_path = os.path.dirname(__file__)
        
        try:
            bird_path = os.path.join(base_path, 'assets', 'bird.png')
            bird_img = pygame.image.load(bird_path).convert_alpha()
            assets['bird_sprite'] = bird_img 
            self.logger.log_info("Asset 'bird.png' carregado com sucesso.")
        except pygame.error as e:
            self.logger.log_error(f"Falha ao carregar asset 'bird.png': {e}")
            assets['bird_sprite'] = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE)); assets['bird_sprite'].fill(YELLOW)
            
        try:
            pipe_path = os.path.join(base_path, 'assets', 'pipe.png')
            pipe_img = pygame.image.load(pipe_path).convert_alpha()
            assets['pipe_sprite'] = pipe_img 
            self.logger.log_info("Asset 'pipe.png' carregado com sucesso.")
        except pygame.error as e:
            self.logger.log_error(f"Falha ao carregar asset 'pipe.png': {e}")
            assets['pipe_sprite'] = pygame.Surface((PIPE_WIDTH, 10)); assets['pipe_sprite'].fill(GREEN)

        try:
            sky_path = os.path.join(base_path, 'assets', 'ceu.png')
            sky_img = pygame.image.load(sky_path).convert()
            assets['background_sky'] = pygame.transform.scale(sky_img, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.logger.log_info("Asset 'ceu.png' carregado com sucesso.")
        except pygame.error as e:
            self.logger.log_error(f"Falha ao carregar asset 'ceu.png': {e}")
            assets['background_sky'] = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT)); assets['background_sky'].fill((135, 206, 235))

        try:
            game_over_path = os.path.join(base_path, 'assets', 'game_over.png')
            go_img = pygame.image.load(game_over_path).convert_alpha()
            assets['game_over_screen'] = pygame.transform.scale(go_img, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.logger.log_info("Asset 'game_over.png' carregado com sucesso.")
        except pygame.error as e:
            self.logger.log_error(f"Falha ao carregar asset 'game_over.png': {e}")
            assets['game_over_screen'] = None

        try:
            music_path = os.path.join(base_path, 'assets', 'music.mp3')
            pygame.mixer.music.load(music_path)
            self.logger.log_info("Asset 'music.mp3' carregado com sucesso.")
        except pygame.error as e:
            self.logger.log_error(f"Falha ao carregar asset 'music.mp3': {e}")
            
        return assets

    def _play_music(self):
        """Inicia a reprodução da música de fundo (loop infinito)."""
        try:
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            self.logger.log_error(f"Falha ao iniciar a música: {e}")
            
    def _get_speed_setting(self, key):
        data = DIFFICULTY_SPEEDS[key].copy()
        data['speed_name'] = key
        return data

    def _get_mechanic_setting(self, key):
        data = PHASE_MECHANICS[key].copy()
        data['mechanic_name'] = key
        return data

    def set_speed_difficulty(self, key):
        self.current_speed_setting = self._get_speed_setting(key)
        self.logger.log_info(f"Velocidade definida para: {key}")
        
    def set_mechanic_phase(self, key):
        self.current_mechanic_setting = self._get_mechanic_setting(key)
        self.logger.log_info(f"Mecânica de Fase definida para: {key}")

    def change_state(self, new_state):
        self.current_state = new_state
        if new_state == STATE_QUIT:
            self.game_running = False 
        
    def start_game(self):
        pipe_sprite = self.assets['pipe_sprite']
        if self.pipe_manager is None:
             self.pipe_manager = PipeManager(self, pipe_sprite)
             
        self.bird.reset()
        self.pipe_manager.reset()
        
        self.current_state = STATE_PLAYING

    def game_over(self):
        self.logger.log_info(f"GAME OVER. Pontuação final: {self.bird.score}. Mecânica: {self.current_mechanic_setting['mechanic_name']}. Velocidade: {self.current_speed_setting['speed_name']}")
        
        combined_difficulty = f"{self.current_mechanic_setting['mechanic_name']} ({self.current_speed_setting['speed_name']})"
        self.db_manager.save_score("Player Temp", self.bird.score, combined_difficulty)
        
        self.current_state = STATE_GAME_OVER
        pygame.time.set_timer(pygame.USEREVENT + 1, 3000) 

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.change_state(STATE_QUIT)
            
            if event.type == pygame.USEREVENT + 1:
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                if self.current_state == STATE_GAME_OVER:
                    self.current_state = STATE_MENU

            if self.current_state == STATE_MENU:
                self.menu_scene.handle_input(event)
            elif self.current_state == STATE_SELECT_PHASE:
                self.phase_select_scene.handle_input(event)
            elif self.current_state == STATE_RANKING:
                self.ranking_scene.handle_input(event)
            elif self.current_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.bird.flap()

    def check_collisions(self):
        if self.pipe_manager is None:
            return 
            
        if pygame.sprite.spritecollideany(self.bird, self.pipe_manager.pipes):
            self.game_over()
            return
            
        if self.bird.is_started:
            if self.bird.rect.top <= 0 or self.bird.rect.bottom >= self.SCREEN_HEIGHT:
                self.game_over()

    def run(self):
        while self.game_running:
            try:
                if self.current_state == STATE_QUIT:
                    break 

                self.handle_input()
                self.screen.fill(BLACK)
                
                fps_limit = FPS * self.current_speed_setting['fps_mult']
                self.clock.tick(fps_limit)

                if self.current_state == STATE_MENU:
                    self.menu_scene.draw()
                elif self.current_state == STATE_SELECT_PHASE:
                    self.phase_select_scene.draw()
                elif self.current_state == STATE_RANKING:
                    self.ranking_scene.draw()
                    
                elif self.current_state == STATE_PLAYING:
                    if self.pipe_manager:
                        self.screen.blit(self.assets['background_sky'], (0, 0)) 
                        
                        self.bird.update()
                        self.pipe_manager.update()
                        self.check_collisions()

                        for pipe in self.pipe_manager.pipes:
                            self.screen.blit(pipe.image, pipe.rect)
                            
                        self.screen.blit(self.bird.image, self.bird.rect)
                        self.ui_scene.draw(self.bird)
                    else:
                        self.start_game()
                        
                elif self.current_state == STATE_GAME_OVER:
                    if self.assets['game_over_screen']:
                        self.screen.blit(self.assets['game_over_screen'], (0, 0))
                    else:
                        self.menu_scene.draw_text("GAME OVER", self.menu_scene.big_font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
                
                pygame.display.flip()

            except Exception as e:
                self.logger.log_error(f"Exceção fatal no loop: {e}")
                self.game_over() 

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game()
    game.run()
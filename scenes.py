import pygame
from settings import *

class BaseScene:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        
        try:
            self.font = pygame.font.Font(None, 36)
            self.big_font = pygame.font.Font(None, 74)
        except pygame.error:
            self.font = pygame.font.Font(None, 36)
            self.big_font = pygame.font.Font(None, 74)


    def draw_text(self, text, font, color, x, y, center=False):
        text_surface = font.render(text, True, color)
        rect = text_surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(text_surface, rect)
        
    def draw(self):
        pass

class MenuScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.options = ["Iniciar Jogo", "Selecionar Nível", "Ver Ranking", "Sair"] 
        self.selected_index = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.execute_option()
    
    def execute_option(self):
        choice = self.options[self.selected_index]
        if choice == "Iniciar Jogo":
            self.game.start_game()
        elif choice == "Selecionar Nível":
            self.game.change_state(STATE_SELECT_PHASE) 
        elif choice == "Ver Ranking":
            self.game.change_state(STATE_RANKING)
        elif choice == "Sair":
            self.game.change_state(STATE_QUIT)
            
    def draw(self):
        self.screen.fill(BLACK) 
        self.draw_text("BATMAN VOADOR GAME", self.big_font, PURPLE, SCREEN_WIDTH // 2, 100, center=True) 
        
        for i, option in enumerate(self.options):
            color = RED if i == self.selected_index else WHITE
            
            if option == "Iniciar Jogo":
                speed_name = self.game.current_speed_setting['speed_name']
                mech_name = self.game.current_mechanic_setting['mechanic_name']
                display_text = f"Iniciar Jogo ({mech_name} | {speed_name})"
            else:
                display_text = option
            
            self.draw_text(display_text, self.font, color, SCREEN_WIDTH // 2, 250 + i * 50, center=True)

class PhaseSelectScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.speed_options = list(DIFFICULTY_SPEEDS.keys())
        self.mech_options = list(PHASE_MECHANICS.keys())
        
        self.speed_index = self.speed_options.index(game.current_speed_setting['speed_name'])
        self.mech_index = self.mech_options.index(game.current_mechanic_setting['mechanic_name'])
        
        self.options = ["Mecânica da Fase", "Velocidade (Dificuldade)", "Voltar ao Menu"]
        self.selected_index = 0
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            
            elif self.selected_index == 0: 
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    if event.key == pygame.K_LEFT:
                        self.mech_index = (self.mech_index - 1) % len(self.mech_options)
                    else:
                        self.mech_index = (self.mech_index + 1) % len(self.mech_options)
                    self.game.set_mechanic_phase(self.mech_options[self.mech_index])
                    
            elif self.selected_index == 1: 
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    if event.key == pygame.K_LEFT:
                        self.speed_index = (self.speed_index - 1) % len(self.speed_options)
                    else:
                        self.speed_index = (self.speed_index + 1) % len(self.speed_options)
                    self.game.set_speed_difficulty(self.speed_options[self.speed_index])
                    
            elif self.selected_index == 2: 
                if event.key == pygame.K_RETURN:
                    self.game.change_state(STATE_MENU)

    def draw(self):
        self.screen.fill(BLACK)
        self.draw_text("SELEÇÃO DE NÍVEL", self.big_font, YELLOW, SCREEN_WIDTH // 2, 80, center=True)
        
        y_offset = 150
        
        mech_name = self.mech_options[self.mech_index]
        color = RED if self.selected_index == 0 else WHITE
        self.draw_text(f"1. Mecânica: < {mech_name} >", self.font, color, SCREEN_WIDTH // 2, y_offset + 50, center=True)
        
        speed_name = self.speed_options[self.speed_index]
        color = RED if self.selected_index == 1 else WHITE
        self.draw_text(f"2. Velocidade: < {speed_name} >", self.font, color, SCREEN_WIDTH // 2, y_offset + 100, center=True)
        
        color = RED if self.selected_index == 2 else WHITE
        self.draw_text("Voltar ao Menu", self.font, color, SCREEN_WIDTH // 2, y_offset + 200, center=True)


class RankingScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.scores = [] 

    def load_scores(self):
        """Carrega as pontuações do banco de dados (chamando o DBManager implementado)."""
        self.scores = self.game.db_manager.get_top_scores()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state(STATE_MENU)

    def draw(self):
        self.load_scores() 
        
        self.screen.fill(BLACK)
        self.draw_text("RANKING - Top 10", self.big_font, GREEN, SCREEN_WIDTH // 2, 50, center=True)

        self.draw_text("Nome | Pontuação | Nível | Data", self.font, YELLOW, 50, 150)
        
        y_offset = 180
        if not self.scores:
            self.draw_text("Nenhum recorde salvo ainda.", self.font, WHITE, 50, 220)
            
        for i, score in enumerate(self.scores):
            nome, pontuacao, dificuldade, data_hora = score
            text = f"{i+1}. {nome} | {pontuacao} | {dificuldade} | {data_hora[:10]}"
            self.draw_text(text, self.font, WHITE, 50, y_offset + i * 30)
            
        self.draw_text("Pressione ESC para voltar.", self.font, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, center=True)

class UIScene:
    def __init__(self, game):
        self.game = game
        try:
            self.font = pygame.font.Font(None, 30)
        except pygame.error:
            self.font = pygame.font.Font(None, 30)

    def draw(self, bird):
        score_text = self.font.render(f"Pontuação: {bird.score}", True, WHITE)
        self.game.screen.blit(score_text, (10, 10)) 

        mech_name = self.game.current_mechanic_setting['mechanic_name']
        speed_name = self.game.current_speed_setting['speed_name']
        phase_text = self.font.render(f"Nível: {mech_name} ({speed_name})", True, YELLOW)
        self.game.screen.blit(phase_text, (SCREEN_WIDTH - phase_text.get_width() - 10, 10))
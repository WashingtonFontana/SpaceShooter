import pygame
from code.Const import (WIN_WIDTH, WIN_HEIGHT, C_WHITE, C_BLACK, C_LIGHT_GRAY,
                        MENU_OPTIONS, GAME_INSTRUCTIONS, C_CYAN, C_YELLOW)


class Button:
    """Gerencia a criação e interação de botões individuais."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 label: str, color: tuple, hover_color: tuple):
        """Configura posição, tamanho, cores e texto do botão."""
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def update(self, mouse_pos: tuple):
        """Verifica se o mouse está sobre o botão para mudar a cor."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Desenha o corpo do botão e o texto centralizado."""
        # Define a cor baseada no movimento do mouse
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, C_WHITE, self.rect, 2)

        # Renderiza o texto
        text_surface = font.render(self.label, True, C_WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos: tuple, mouse_pressed: bool) -> bool:
        """Confirma se o botão recebeu um clique do mouse."""
        return self.rect.collidepoint(mouse_pos) and mouse_pressed


class Menu:
    """Controla o menu principal, botões e instruções de tela."""

    def __init__(self, window: pygame.Surface):
        """Inicializa janelas, listas de botões e carrega as fontes."""
        self.window = window
        self.buttons = []
        self.selected_button = 0
        self.menu_data = MENU_OPTIONS
        self.game_instructions = GAME_INSTRUCTIONS

        # Configuração de tamanhos de fonte
        self.font_title = pygame.font.Font(None, 72)
        self.font_subtitle = pygame.font.Font(None, 36)
        self.font_button = pygame.font.Font(None, 32)
        self.font_instructions = pygame.font.Font(None, 20)

        self._create_buttons()

    def _create_buttons(self):
        """Instancia os botões centralizados e com espaçamento vertical."""
        button_width = 200
        button_height = 60
        button_x = (WIN_WIDTH - button_width) // 2
        button_y = 250
        spacing = 100

        for i, option in enumerate(self.menu_data['options']):
            button = Button(
                x=button_x,
                y=button_y + (i * spacing),
                width=button_width,
                height=button_height,
                label=option['label'],
                color=option['color'],
                hover_color=option['hover_color']
            )
            self.buttons.append(button)

    def handle_input(self):
        """Processa teclado e cliques do mouse para navegar ou selecionar opções."""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "exit"
                # Navegação por setas (Ciclo entre botões)
                elif event.key == pygame.K_UP:
                    self.selected_button = (self.selected_button - 1) % len(self.buttons)
                elif event.key == pygame.K_DOWN:
                    self.selected_button = (self.selected_button + 1) % len(self.buttons)
                # Seleção por teclado
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self.menu_data['options'][self.selected_button]['id']

            # Seleção por clique do mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(self.buttons):
                    if button.rect.collidepoint(mouse_pos):
                        return self.menu_data['options'][i]['id']

        return None

    def draw(self):
        """Limpa a tela e desenha todos os elementos visuais do menu."""
        self.window.fill(C_BLACK)

        # Cabeçalho (Título e Subtítulo)
        title_text = self.font_title.render(self.menu_data['title'], True, C_CYAN)
        title_rect = title_text.get_rect(center=(WIN_WIDTH // 2, 80))
        self.window.blit(title_text, title_rect)

        subtitle_text = self.font_subtitle.render(self.menu_data['subtitle'], True, C_YELLOW)
        subtitle_rect = subtitle_text.get_rect(center=(WIN_WIDTH // 2, 150))
        self.window.blit(subtitle_text, subtitle_rect)

        # Renderização dos botões e destaque do selecionado
        for i, button in enumerate(self.buttons):
            if i == self.selected_button:
                pygame.draw.rect(self.window, C_CYAN, button.rect, 3)

            button.draw(self.window, self.font_button)

        # Rodapé e Instruções
        pygame.draw.line(self.window, C_LIGHT_GRAY, (50, WIN_HEIGHT - 200), (WIN_WIDTH - 50, WIN_HEIGHT - 200), 2)
        self._draw_instructions()

        pygame.display.flip()

    def _draw_instructions(self):
        """Escreve as instruções de controle no canto inferior da tela."""
        x_offset = 20
        y_offset = WIN_HEIGHT - 180
        line_height = 22

        # Título das instruções
        title_text = self.font_instructions.render(self.game_instructions['title'], True, C_YELLOW)
        self.window.blit(title_text, (x_offset, y_offset))

        # Instruções
        y_offset += 25
        for instruction in self.game_instructions['instructions']:
            instruction_text = self.font_instructions.render(instruction, True, C_WHITE)
            self.window.blit(instruction_text, (x_offset, y_offset))
            y_offset += line_height

    def run(self):
        """Mantém o menu ativo em loop até que uma opção seja escolhida ou o jogo fechado."""
        clock = pygame.time.Clock()

        while True:
            option_id = self.handle_input()

            if option_id == "exit":
                return -1

            if option_id is not None:
                return option_id

            self.draw()
            clock.tick(60)

    def __repr__(self) -> str:
        """Representação curta para depuração."""
        return f"Menu(buttons={len(self.buttons)}, selected={self.selected_button})"
from src.game.roguelite_game import RogueliteGame
from src.model.dungeon_loader import DungeonLoader
from src.graphics.game_graphics import GameGraphics
from src.engine.pygame.pygame_application import PyGameApplication
from src.engine.pygame.camera import Camera
from src.editor.ui_utils import UIUtils

import pygame_gui
from pygame_gui.windows import UIFileDialog
import pygame
import glm
from OpenGL import GL

class EditorApplication(RogueliteGame):
    def __init__(self, config):
        RogueliteGame.__init__(self, config)
        self.camera_position = (0, 0)
        self.camera_ui = Camera(self.application_config.window_width, self.application_config.window_height,
                                glm.vec3(0, 0, 0))

    def _init_engine(self):
        RogueliteGame._init_engine(self)

        self.ui_surface = pygame.Surface(
            (self.application_config.window_width, self.application_config.window_height))
        self.ui_manager = pygame_gui.UIManager((self.application_config.window_width, self.application_config.window_height), 'editor/data/themes/quick_theme.json')

    def initialize(self):
        RogueliteGame.initialize(self)

        self.load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((5, 5), (100, 40)),
                                                    text='Load',
                                                    manager=self.ui_manager)

        self.save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((110, 5), (100, 40)),
                                                        text='Save',
                                                        manager=self.ui_manager)

        self.camera_movement_enabled = False

    def _on_button_pressed(self, event):
        ui_element = event.ui_element
        if ui_element == self.load_button:
            UIUtils.disable_all(self.ui_manager.get_root_container())
            self.file_dialog = UIFileDialog(pygame.Rect(5, 50, 440, 500), self.ui_manager,
                                            window_title='Load Dungeon...', initial_file_path='data/dungeons')
        elif ui_element == self.file_dialog:
            self.dungeon = DungeonLoader.load_from_tsv(event.text)
            UIUtils.enable_all(self.ui_manager.get_root_container())

    def _manage_camera(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.camera_movement_enabled = True
            self.last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            self.camera_movement_enabled = False
        elif event.type == pygame.MOUSEMOTION and self.camera_movement_enabled:
            movement_x = -(self.last_mouse_pos[0] - event.pos[0])
            movement_y = -(self.last_mouse_pos[1] - event.pos[1])
            self.last_mouse_pos = event.pos

            increase_factor = 1
            self.game_graphics.increase_target_camera_position(movement_x * increase_factor,
                                                               movement_y * increase_factor)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_KP_MINUS:
            self.add_zoom(-0.05)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_KP_PLUS:
            self.add_zoom(0.05)

    def _on_event(self, event):
        PyGameApplication._on_event(self, event)
        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            self._on_button_pressed(event)
        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            self._on_button_pressed(event)

        self._manage_camera(event)

        self.ui_manager.process_events(event)

    def _update(self):
        PyGameApplication._update(self)
        self.ui_manager.update(self.delta_time)
        self.game_graphics.update()

    def _on_render(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        self.main_surface.fill((0, 0.6 * 255, 0.75 * 255))
        self.ui_surface.fill(self.ui_manager.get_theme().get_colour(None, None, 'dark_bg'))

        self.ui_manager.draw_ui(self.ui_surface)
        GL.glViewport(0, 0, (int)(self.application_config.window_width),
                      (int)(self.application_config.window_height))
        self._render_game_texture(self.game_texture, self.ui_surface)

        self._render()
        GL.glViewport(0, 0, (int)(self.application_config.window_width * 0.9),
                      (int)(self.application_config.window_height * 0.9))

        self._render_game_texture(self.game_texture, self.main_surface)

    def _init_model(self):
        pass

    def _init_graphics(self):
        self.game_graphics = GameGraphics()

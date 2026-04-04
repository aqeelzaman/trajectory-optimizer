from abstract_scene import *
from pygame import quit, MOUSEBUTTONUP

class MainMenuScene(AbstractScene):
    """
    Starting scene when the game opens.
    Includes the main menu.
    """

    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.game_objects = []
        self.ui_objects = {}
        self.load_assets()
        self.create_ui()

    def load_assets(self):
        """
        Loads game assets for main menu.
        """
        self.background = import_assets(
            "assets/background.png", x_scale=600, y_scale=600
        )
        self.title = import_assets(
            "assets/title.png", alpha=True, x_scale=240, y_scale=240
        )
        self.ui_banner = import_assets(
            "assets/ui_banner.png", alpha=True, x_scale=200, y_scale=50
        )

        self.game_objects = [
            GameObject(
                id="background",
                type="image",
                surface=self.background,
                pos=(0, 0),
            ),
            GameObject(
                id="title",
                type="image",
                surface=self.title,
                pos=(180, 0),
            ),
        ]

    def create_ui(self):
        """
        Adds UI buttons to scene.
        """
        game_object = add_ui_element("start_button", self.ui_banner, "Start", (20, 250))
        game_object.special_tint((245, 222, 179))
        self.ui_objects["start_button"] = game_object
        self.game_objects.append(game_object)

        game_object = add_ui_element(
            "tutorial_button", self.ui_banner, "Tutorial", (20, 330)
        )
        game_object.special_tint((245, 222, 179))
        self.ui_objects["tutorial_button"] = game_object
        self.game_objects.append(game_object)

        game_object = add_ui_element("quit_button", self.ui_banner, "Quit", (20, 410))
        game_object.special_tint((245, 222, 179))
        self.ui_objects["quit_button"] = game_object
        self.game_objects.append(game_object)

    def check_ui_click(self, mouse_pos):
        """
        Check if mouse click event has occured over a particular UI object.
        If so, run custom code for that UI object.
        """
        for ui_id, ui_obj in self.ui_objects.items():
            if not ui_obj.enabled:
                continue
            ui_rect = ui_obj.surface.get_rect(topleft=ui_obj.pos)
            if ui_rect.collidepoint(mouse_pos):
                if ui_id == "start_button":
                    print("Course Select")
                    self.scene_manager.switch_scene("course_select")
                elif ui_id == "tutorial_button":
                    print("Show Tutorial!")
                elif ui_id == "quit_button":
                    print("Quit Game!")
                    quit()
                    exit()

    def handle_events(self, events, mouse_pos):
        """
        Handles interested events.
        Checks for mouse clicks on UI elements.
        """
        for event in events:
            if event.type == MOUSEBUTTONUP:
                self.check_ui_click(mouse_pos)
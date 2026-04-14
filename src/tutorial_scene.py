from abstract_scene import *
from pygame import MOUSEBUTTONUP

BROWN_TINT = (245, 222, 179)


class TutorialScene(AbstractScene):
    """
    This scene is to provide information about the app, navigation and the AI algorithm.
    """

    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.game_objects = []
        self.ui_objects = {}

        self.tut_texts = [
            "Course Selection",
            "How To Play",
            "Game UI",
            "Simulation Mode",
            "SA Algorithm",
        ]
        self.num_tuts = len(self.tut_texts)
        self.tutorials = {}
        self.selected_tut = None
        self.load_assets()
        self.add_buttons()

    def load_assets(self):
        """
        Load required assets for this screen.
        """
        self.background = import_assets(
            "assets/background.png", x_scale=600, y_scale=600
        )
        self.ui_banner = import_assets(
            "assets/ui_banner.png", alpha=True, x_scale=110, y_scale=40
        )
        self.ui_frame = import_assets(
            "assets/ui_frame.png", alpha=True, x_scale=300, y_scale=50
        )
        self.game_objects = [
            GameObject(
                id="background",
                type="image",
                surface=self.background,
                pos=(0, 0),
            ),
        ]

        for i in range(self.num_tuts):
            tut_surface = import_assets(
                f"assets/tutorial_{i}.png", x_scale=580, y_scale=464
            )
            tut_obj = GameObject(
                id=f"tutorial_{i}", type="image", surface=tut_surface, pos=(10, 60)
            )
            tut_obj.set_visibility(False)
            self.tutorials[f"tutorial_{i}"] = tut_obj
            self.game_objects.append(tut_obj)

    def add_buttons(self):
        """
        Add UI buttons for each tutorial part.
        """
        padding = 10
        last_x = 10
        for i in range(self.num_tuts):
            game_object = add_ui_element(
                f"tutorial_{i}_button",
                self.ui_banner,
                self.tut_texts[i],
                (last_x, padding),
                text_size=13,
            )
            game_object.special_tint(BROWN_TINT)
            self.ui_objects[f"tutorial_{i}_button"] = game_object
            self.game_objects.append(game_object)

            last_x += 115

        game_object = add_ui_element(
            "back_to_menu", self.ui_banner, "Main Menu", (padding, 550), text_size=15
        )
        game_object.special_tint(BROWN_TINT)
        self.ui_objects["back_to_menu"] = game_object
        self.game_objects.append(game_object)

    def check_ui_click(self, mouse_pos):
        """
        Check if mouse click event has occured over a particular UI object.
        If so, run custom code for that UI object.
        """
        deselected = True
        for ui_id, ui_obj in self.ui_objects.items():
            ui_rect = ui_obj.surface.get_rect(topleft=ui_obj.pos)
            if ui_rect.collidepoint(mouse_pos):
                if ui_id == "back_to_menu":
                    self.scene_manager.switch_scene("main_menu")
                else:
                    self.selected_tut = ui_id.rstrip("_button")
                deselected = False
                break

        if deselected:
            self.selected_tut = None

    def handle_events(self, events, mouse_pos):
        """
        Handle click events on this screen.
        """
        for event in events:
            if event.type == MOUSEBUTTONUP:
                self.check_ui_click(mouse_pos)

    def update(self):
        """
        Update screen to hide/unhide specific tutorial.
        """
        for ui_id in self.ui_objects.keys():
            if ui_id[:8] == "tutorial":
                self.tutorials[ui_id.rstrip("_button")].set_visibility(False)

        if self.selected_tut:
            self.tutorials[self.selected_tut].set_visibility(True)

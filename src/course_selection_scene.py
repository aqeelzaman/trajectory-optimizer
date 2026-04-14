from abstract_scene import *
from game_scene import CourseScene
from os import listdir
from pygame import Surface, font, draw, MOUSEBUTTONUP, SRCALPHA


BROWN_TINT = (245, 222, 179)


class CourseSelectionScene(AbstractScene):
    """
    Selection Menu for the different courses and custom level creation.
    """

    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.initiated = False
        self.game_objects = []
        self.ui_objects = {}
        self.load_assets()
        self.num_courses = 0

        self.selected_course = None
        self.data_area_obj = None
        self.update_ui = False

    def initiate(self):
        """
        Create UI elements when the scene is ready to be initiated.
        """
        if not self.initiated:
            self.initiated = True
            self.create_ui()

    def load_assets(self):
        """
        Loads game assets for scene.
        """
        self.background = import_assets(
            "assets/background.png", x_scale=600, y_scale=600
        )
        self.ui_banner = import_assets(
            "assets/ui_banner.png", alpha=True, x_scale=150, y_scale=40
        )
        self.ui_frame = import_assets(
            "assets/ui_frame.png", alpha=True, x_scale=300, y_scale=50
        )
        self.orange_button = import_assets(
            "assets/ui_button_orange.png", x_scale=110, y_scale=40
        )
        self.blue_button = import_assets(
            "assets/ui_button_blue.png", x_scale=110, y_scale=40
        )
        self.bot_button = import_assets(
            "assets/bot.png", alpha=True, x_scale=40, y_scale=40
        )
        self.course_details = import_assets(
            "assets/course_details.png", x_scale=410, y_scale=273
        )

        self.game_objects = [
            GameObject(
                id="background",
                type="image",
                surface=self.background,
                pos=(0, 0),
            )
        ]

    def create_ui(self):
        """
        Adds UI buttons to scene.
        """
        game_object = GameObject(
            id="select_text", type="message", surface=self.ui_frame, pos=(20, 20)
        )
        game_object.special_tint(BROWN_TINT)
        game_object.edit_text("Select Course To Play", 25, "black")
        self.game_objects.append(game_object)

        padding = 20
        last_y = 120
        course_file_list = sorted(listdir("courses"))
        for course_file in course_file_list:
            if course_file[:6] != "course":
                continue
            course_id = course_file.lstrip("course")
            if int(course_id) == 6:
                break

            self.num_courses += 1

            game_object = add_ui_element(
                course_file + "_button",
                self.ui_banner,
                "Course " + course_id,
                (padding, last_y),
                text_size=20,
            )
            game_object.special_tint(BROWN_TINT)
            self.ui_objects[course_file + "_button"] = game_object
            self.game_objects.append(game_object)

            game_object = GameObject(
                id=course_file + "_profile",
                type="ui",
                surface=self.course_details,
                pos=(180, 170),
            )
            game_object.hover_surface = game_object.base_surface
            game_object.set_visibility(False)
            draw.rect(
                game_object.surface,
                BROWN_TINT,
                (238, 130, 160, 95),
                border_radius=5,
            )
            self.ui_objects[course_file + "_profile"] = game_object
            self.game_objects.append(game_object)

            self.scene_manager.add_scene(
                course_file, CourseScene(self.scene_manager, course_file)
            )

            last_y += 70

        game_object = add_ui_element(
            "back_to_menu", self.ui_banner, "Main Menu", (padding, last_y), text_size=20
        )
        game_object.special_tint(BROWN_TINT)
        self.ui_objects["back_to_menu"] = game_object
        self.game_objects.append(game_object)

        padding = 250
        game_object = add_ui_element(
            "start_game", self.blue_button, "Start/Resume", (padding, 120), text_size=15
        )
        game_object.set_visibility(False)
        self.ui_objects["start_game"] = game_object
        self.game_objects.append(game_object)

        game_object = add_ui_element(
            "bot_button", self.bot_button, "", (padding + 115, 120), text_size=15
        )
        game_object.set_visibility(False)
        self.ui_objects["bot_button"] = game_object
        self.game_objects.append(game_object)

        game_object = add_ui_element(
            "reset_game",
            self.orange_button,
            "Reset Course",
            (padding + 160, 120),
            text_size=15,
        )
        game_object.set_visibility(False)
        self.ui_objects["reset_game"] = game_object
        self.game_objects.append(game_object)

    def check_ui_click(self, mouse_pos):
        """
        Check if mouse click event has occured over a particular UI object.
        If so, run custom code for that UI object.
        """
        self.update_ui = True
        deselected = True
        for ui_id, ui_obj in self.ui_objects.items():
            if not ui_obj.enabled or ui_id[-7:] == "profile":
                continue
            ui_rect = ui_obj.surface.get_rect(topleft=ui_obj.pos)
            if ui_rect.collidepoint(mouse_pos):
                if ui_id == "back_to_menu":
                    self.scene_manager.switch_scene("main_menu")
                elif ui_id == "start_game":
                    self.scene_manager.switch_scene(self.selected_course)
                elif ui_id == "bot_button":
                    self.scene_manager.scenes[self.selected_course] = CourseScene(
                        self.scene_manager, self.selected_course, True
                    )
                    self.scene_manager.switch_scene(self.selected_course)
                elif ui_id == "reset_game":
                    self.scene_manager.scenes[self.selected_course] = CourseScene(
                        self.scene_manager, self.selected_course
                    )
                else:
                    self.selected_course = ui_id.rstrip("_button")
                deselected = False
                break
        if deselected and self.selected_course:
            self.selected_course = None

    def handle_events(self, events, mouse_pos):
        """
        Handles interested events.
        Checks for mouse clicks on UI elements.
        """
        for event in events:
            if event.type == MOUSEBUTTONUP:
                self.check_ui_click(mouse_pos)

    def multiline_text(self, x, y, text_elements):
        """
        Utility function to add multiline text elements to UI.
        """
        text_size = 18
        for label in text_elements:
            FONT = font.SysFont("arial", text_size)
            text_surface = FONT.render(label, True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(x, y))
            self.data_area.blit(text_surface, text_rect)
            y += text_size

    def update(self):
        """
        Update UI for each selected course.
        """
        if not self.update_ui:
            return

        if not self.selected_course:
            if self.data_area_obj in self.game_objects:
                self.game_objects.remove(self.data_area_obj)

            for ui_id in self.ui_objects.keys():
                if ui_id in ["start_game", "reset_game", "bot_button"]:
                    self.ui_objects[ui_id].disable_ui()
                    self.ui_objects[ui_id].set_visibility(False)
                elif ui_id[-7:] == "profile":
                    self.ui_objects[ui_id].set_visibility(False)
        else:
            for ui_id in self.ui_objects.keys():
                if ui_id in ["start_game", "reset_game", "bot_button"]:
                    self.ui_objects[ui_id].enable_ui()
                    self.ui_objects[ui_id].set_visibility(True)
                elif ui_id == self.selected_course.rstrip("_button") + "_profile":
                    self.ui_objects[ui_id].set_visibility(True)

            if self.data_area_obj in self.game_objects:
                self.game_objects.remove(self.data_area_obj)

            self.data_area = Surface((600, 600), SRCALPHA)
            course_obj = self.scene_manager.scenes[self.selected_course]
            text_elements = [
                f'Course: {course_obj.course_id.lstrip("course")}',
                f'Current Hole: {course_obj.current_hole.hole_id.lstrip("hole")}',
                f'Best Score: {course_obj.current_hole.hole_data["best_score"]}',
                f'Best AI Score: {course_obj.current_hole.hole_data["best_bot_score"]}',
                f'Mode: {"Simulation" if course_obj.simulation_mode else "Manual"}',
            ]

            self.multiline_text(420, 300, text_elements)

            self.data_area_obj = GameObject(
                id="course_data", type="text", surface=self.data_area, pos=(0, 0)
            )
            self.game_objects.append(self.data_area_obj)

        self.update_ui = False

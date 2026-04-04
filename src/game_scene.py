from abstract_scene import *
from sa_algo import SimulatedAnnealer
from pygame import (
    Surface,
    SRCALPHA,
    draw,
    font,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    KEYDOWN,
    K_BACKSPACE,
)
from os import listdir
from json import load, dump
from golfball import GolfBall
from objects import Obstacle
from math import sqrt


class CourseScene(AbstractScene):
    """
    Scene that holds data for a particular course.
    Each course has multiple holes, a UI bar that displays hole info,
    and buttons for navigation and action.
    """

    def __init__(self, scene_manager, course_id, sim_mode=False):
        self.scene_manager = scene_manager
        self.course_id = course_id

        self.game_objects = []
        self.ui_objects = {}
        self.holes = {}
        self.current_hole = None
        self.simulation_mode = sim_mode
        self.simulation_started = False
        self.active_text_box = None

        self.data = {
            "cur_score": 0,
            "best_score": 1000,
            "best_bot_score": 1000,
            "dist_from_hole": 0,
            "power": 0,
            "angle": 0,
            "num_overshoots": 0,
            "surface_type": "grass",
            "friction": 1,
            "episode_num": 0,
            "iterations": 0,
            "temp": 0,
            "energy": 0,
            "score_threshold": 100,
            "max_episodes": 10,
            "max_iterations": 20,
            "initial_temperature": 100,
            # "schedule": "None",
            "grass_friction": 1,
            "sand_friction": 3,
            "ice_friction": 0.5,
            "animation_speed": 1,
        }

        self.default_hyperparameters = {
            "score_threshold": 100,
            "max_episodes": 10,
            "max_iterations": 20,
            "initial_temperature": 100,
            # "schedule": "None",
            "grass_friction": 1,
            "sand_friction": 3,
            "ice_friction": 0.5,
            "animation_speed": 1,
        }

        self.small_text_size = 11
        self.medium_text_size = 14
        self.large_text_size = 15

        self.data_text_elements = self.data_text_elements = [
            [f'Course #{self.course_id.lstrip("course")}', self.large_text_size],
            [f'Current Score: {self.data["cur_score"]}', self.medium_text_size],
            [f'Best Human Score: {self.data["best_score"]}', self.medium_text_size],
            [f'Best Bot Score: {self.data["best_bot_score"]}', self.medium_text_size],
            ["_Metrics", self.medium_text_size],
            [
                f'Distance from hole: {self.data["dist_from_hole"]}',
                self.small_text_size,
            ],
            [f'Power: {self.data["power"]}', self.small_text_size],
            [f'Angle: {self.data["angle"]}', self.small_text_size],
            [f'Overshoots: {self.data["num_overshoots"]}', self.small_text_size],
            [f'Current Surface: {self.data["surface_type"]}', self.small_text_size],
            [f'Current Friction: {self.data["friction"]}', self.small_text_size],
            [f'Episode Number: {self.data["episode_num"]}', self.small_text_size],
            [f'Iteration Number: {self.data["iterations"]}', self.small_text_size],
            [f'Current Temperature: {self.data["temp"]}', self.small_text_size],
            [f'Current Energy: {self.data["energy"]}', self.small_text_size],
            ["_Hyperparameters", self.medium_text_size],
            [f"Score Threshold: {self.data['score_threshold']}+", self.small_text_size],
            [f'Max Episodes: {self.data["max_episodes"]}+', self.small_text_size],
            [f'Max Iterations: {self.data["max_iterations"]}+', self.small_text_size],
            [
                f'Initial Temperature: {self.data["initial_temperature"]}+',
                self.small_text_size,
            ],
            # [f'Cooling Schedule: {self.data["schedule"]}', self.small_text_size],
            [f'Grass Friction: {self.data["grass_friction"]}+', self.small_text_size],
            [f'Sand Friction: {self.data["sand_friction"]}+', self.small_text_size],
            [f'Ice Friction: {self.data["ice_friction"]}+', self.small_text_size],
            [
                f'_Animation Speed: {self.data["animation_speed"]}',
                self.small_text_size,
            ],
            ["_Message Board", self.medium_text_size],
            ["_", self.small_text_size],
        ]
        self.data_area_obj = None

        self.load_assets()
        self.add_ui_elements()
        self.add_holes()
        self.default_hyperparameters["score_threshold"] = self.current_hole.hole_data[
            "best_bot_score"
        ]
        self.data_text_elements.insert(
            1,
            [
                f'Hole #{self.current_hole.hole_id.lstrip("hole")}',
                self.medium_text_size,
            ],
        )

    def load_assets(self):
        """
        Loads game assets for the course.
        """
        self.orange_button = import_assets(
            "assets/ui_button_orange.png", x_scale=150, y_scale=25
        )
        self.blue_button = import_assets(
            "assets/ui_button_blue.png", x_scale=150, y_scale=25
        )
        self.small_blue_button = import_assets(
            "assets/ui_button_blue.png", x_scale=73, y_scale=25
        )
        self.apply_button = import_assets(
            "assets/ui_apply_button.png", x_scale=73, y_scale=25
        )
        self.grass = import_assets("assets/grass.png", x_scale=600, y_scale=600)
        self.ui_frame = import_assets(
            "assets/ui_frame.png", x_scale=600, y_scale=200, degree=90
        )
        self.human_icon = import_assets(
            "assets/human.png", alpha=True, x_scale=40, y_scale=42
        )
        self.bot_icon = import_assets(
            "assets/bot.png", alpha=True, x_scale=40, y_scale=42
        )
        self.text_box = import_assets(
            "assets/ui_text_box.png", alpha=True, x_scale=30, y_scale=15
        )
        self.plus_icon = import_assets( "assets/ui_plus.png", alpha=True, x_scale=17, y_scale=17)
        self.minus_icon = import_assets( "assets/ui_minus.png", alpha=True, x_scale=17, y_scale=8)
        self.game_objects = [
            GameObject(
                id="grass",
                type="image",
                surface=self.grass,
                pos=(0, 0),
            ),
            GameObject(
                id="ui_frame",
                type="image",
                surface=self.ui_frame,
                pos=(400, 0),
            ),
        ]

        if self.simulation_mode:
            bot_button = add_ui_element(
                "bot_button",
                self.bot_icon,
                "",
                (550, 10),
            )
            self.ui_objects["bot_button"] = bot_button
            self.game_objects.append(bot_button)
        else:
            self.game_objects.append(
                GameObject(
                    id="human_icon",
                    type="image",
                    surface=self.human_icon,
                    pos=(550, 10),
                )
            )

    def add_ui_elements(self):
        """
        Adds UI box to course that displays hole info, simulation data,
        and action buttons.
        A shade is added to simulation data if game is not in simulation mode.
        """
        self.data_area = Surface((200, 600), SRCALPHA)
        self.data_val_coords = []

        last_y = self.add_to_ui(10, self.data_text_elements)
        self.add_buttons(last_y)

        self.data_area_obj = GameObject(
            id="course_ui",
            type="ui",
            surface=self.data_area,
            pos=(400, 0),
        )
        self.ui_objects["course_ui"] = self.data_area_obj
        self.game_objects.append(self.data_area_obj)

        shade = Surface((200, 600), SRCALPHA)
        start_y = self.data_val_coords[12][1]
        end_y = self.data_val_coords[len(self.data_val_coords) - 6][1] - start_y + 15
        draw.rect(
            shade,
            (0, 0, 0, 100),
            (8, start_y, 160, end_y),
            border_radius=5,
        )
        self.shade_obj = GameObject(
            id="shade",
            type="image",
            surface=shade,
            pos=(400, 0),
        )

        if not self.simulation_mode:
            self.game_objects.append(self.shade_obj)

    def add_to_ui(self, last_y, text_elements):
        """
        Utility function to add text elements to UI box at given coordinate
        and size.
        """
        padding = 10
        for i, (label, text_size) in enumerate(text_elements):
            add_text_box = False
            add_dropdown = False
            if label[0] == "_":
                draw.line(
                    self.data_area, (0, 0, 0), (0, last_y), (200, last_y), width=2
                )
                label = label.lstrip("_")
                last_y += padding / 2
            if label:
                if label[-1] == "+":
                    add_text_box = True
                    label = label.rstrip("+")
                if label[-1] == "*":
                    add_dropdown = True
                    label = label.rstrip("*")

            FONT = font.SysFont("arial", text_size)
            text_surface = FONT.render(label, True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(padding, last_y))
            self.data_area.blit(text_surface, text_rect)
            self.data_val_coords.append(
                [text_rect.topright[0] + padding, text_rect.topright[1]]
            )

            label = label.split(":")[0].replace(" ", "_").lower()
            if add_text_box:
                self.add_text_box(text_rect.topright[1], label)
            if add_dropdown:
                self.add_dropdown(
                    text_rect.topright[0] + padding, text_rect.topright[1], text_size
                )

            last_y += text_size + padding / 2

        return last_y

    def add_text_box(self, y, text):
        x_padding = 535
        y_padding = 15
        text_box_obj = GameObject(
            id=f"text_box_{text}",
            type="textbox",
            surface=self.text_box,
            pos=(x_padding, y + y_padding),
        )
        self.ui_objects[f"text_box_{text}"] = text_box_obj
        self.game_objects.append(text_box_obj)

    def add_dropdown(self, x, y, text_size):
        pass

    def add_buttons(self, last_y):
        """
        Add action buttons to the course scene.
        """
        padding = 415
        last_y += 3
        game_obj = add_ui_element(
            "back_to_course",
            self.small_blue_button,
            "Courses",
            (padding, last_y),
            text_size=self.medium_text_size,
        )
        self.ui_objects["back_to_course"] = game_obj
        self.game_objects.append(game_obj)

        game_obj = add_ui_element(
            "apply_button",
            self.apply_button,
            "Apply",
            (padding + 77, last_y),
            text_size=self.medium_text_size,
        )
        self.ui_objects["apply_button"] = game_obj
        self.game_objects.append(game_obj)

        last_y += 30
        game_obj = add_ui_element(
            "simulate_button",
            self.orange_button,
            "Start Simulation",
            (padding, last_y),
            text_size=self.medium_text_size,
            enabled=self.simulation_mode,
        )
        self.ui_objects["simulate_button"] = game_obj
        self.game_objects.append(game_obj)

        last_y += 30
        game_obj = add_ui_element(
            "prev_hole",
            self.small_blue_button,
            "Prev Hole",
            (padding, last_y),
            text_size=self.small_text_size,
            enabled=not self.simulation_mode,
        )
        self.ui_objects["prev_hole"] = game_obj
        self.game_objects.append(game_obj)

        game_obj = add_ui_element(
            "next_hole",
            self.small_blue_button,
            "Next Hole",
            (padding + 77, last_y),
            text_size=self.small_text_size,
            enabled=not self.simulation_mode,
        )
        self.ui_objects["next_hole"] = game_obj
        self.game_objects.append(game_obj)

        last_y = self.data_val_coords[-1][1] - 28
        game_obj = add_ui_element(
            "plus_button",
            self.plus_icon,
            "",
            (padding + 100, last_y),
            text_size=self.small_text_size,
        )
        self.ui_objects["plus_button"] = game_obj
        self.game_objects.append(game_obj)
        
        last_y += 5
        game_obj = add_ui_element(
            "minus_button",
            self.minus_icon,
            "",
            (padding + 120, last_y),
            text_size=self.small_text_size,
        )
        self.ui_objects["minus_button"] = game_obj
        self.game_objects.append(game_obj)

    def add_holes(self):
        """
        Uses json data for the current course to add holes as new scenes.
        """
        hole_file_path = "courses/" + self.course_id
        for hole_file in listdir(hole_file_path):
            if hole_file[:4] != "hole":
                continue
            default_hole = None
            if hole_file.endswith(".json"):
                with open(f"{hole_file_path}/{hole_file}", "r") as f:
                    hole_data = load(f)
                hole_id = hole_data["hole_id"]
                if not default_hole:
                    default_hole = hole_id
                self.holes[hole_id] = HoleScene(
                    self, hole_id, hole_data, self.simulation_mode
                )

        self.switch_hole(default_hole)

    def switch_hole(self, hole_id):
        """
        Switch between holes in the current course.
        """
        if hole_id in self.holes:
            self.ui_objects["next_hole"].disable_ui()
            self.ui_objects["prev_hole"].enable_ui()
            if self.current_hole in self.game_objects:
                self.game_objects.remove(self.current_hole)
            self.current_hole = self.holes[hole_id]
            self.game_objects.append(self.current_hole)

            if self.current_hole.next_hole_id not in self.holes:
                self.ui_objects["next_hole"].edit_text("End Course")
            if self.current_hole.prev_hole_id not in self.holes:
                self.ui_objects["prev_hole"].disable_ui()

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
                if ui_id == "simulate_button" and self.simulation_mode:
                    self.click_simulate(ui_id)
                elif ui_id == "back_to_course":
                    self.scene_manager.switch_scene("course_select")
                elif ui_id == "next_hole":
                    self.click_next_hole(ui_id)
                elif ui_id == "prev_hole":
                    self.click_prev_hole()
                elif ui_id == "bot_button" and self.simulation_mode:
                    self.click_bot_button()
                elif ui_id.startswith("text_box"):
                    self.handle_text_box_click(ui_id)
                elif ui_id == "apply_button":
                    self.click_apply_button()
                elif ui_id == "plus_button":
                    self.data["animation_speed"] = min(self.data["animation_speed"] + 0.5, 3)
                    self.scene_manager.fps_multiplier = self.data["animation_speed"]
                elif ui_id == "minus_button":
                    self.data["animation_speed"] = max(self.data["animation_speed"] - 0.5, 0.5)
                    self.scene_manager.fps_multiplier = self.data["animation_speed"]

    def click_simulate(self, ui_id):
        if not self.simulation_started:
            self.simulation_started = True
            self.current_hole.num_episodes = 1
            self.click_apply_button()
            self.ui_objects[ui_id].edit_text("End Simulation")
            self.current_hole.simulate()
        else:
            self.simulation_started = False
            self.current_hole.simulation_started = False
            if self.current_hole.SA:
                self.current_hole.game_objects.remove(self.current_hole.SA)
            self.current_hole.SA = None
            self.ui_objects[ui_id].edit_text("Start Simulation")

    def click_next_hole(self, ui_id):
        if self.ui_objects[ui_id].get_text() == "Next Hole":
            next_hole_id = "hole" + str(
                int(self.current_hole.hole_id.lstrip("hole")) + 1
            )
            self.switch_hole(next_hole_id)
        elif self.ui_objects[ui_id].get_text() == "End Course":
            self.scene_manager.switch_scene("course_select")

    def click_prev_hole(self):
        prev_hole_id = "hole" + str(int(self.current_hole.hole_id.lstrip("hole")) - 1)
        self.switch_hole(prev_hole_id)
        self.ui_objects["next_hole"].enable_ui()
        self.ui_objects["next_hole"].edit_text("Next Hole")

    def click_bot_button(self):
        self.simulation_started = False
        self.current_hole.simulation_started = False
        self.ui_objects["simulate_button"].edit_text("Start Simulation")
        (
            self.data["grass_friction"],
            self.data["sand_friction"],
            self.data["ice_friction"],
        ) = self.current_hole.hole_data["best_bot_params"]
        self.current_hole.retrace_bot_path()

    def click_apply_button(self):
        if self.simulation_mode:
            text_boxes = [
                ui_obj
                for ui_id, ui_obj in self.ui_objects.items()
                if ui_id.startswith("text_box")
            ]
        else:
            text_boxes = [
                ui_obj
                for ui_id, ui_obj in self.ui_objects.items()
                if ui_id.startswith("text_box") and ui_id.endswith("friction")
            ]

        for text_box in text_boxes:
            text_value = text_box.get_text()
            data_key = text_box.id.lstrip("text_box_")
            self.data[data_key] = (
                float(text_value)
                if text_value
                else self.default_hyperparameters[data_key]
            )

        for text_box in text_boxes:
            text_box.edit_text("")
            self.active_text_box = None

        if self.simulation_mode and self.current_hole.simulation_started:
            self.current_hole.simulation_started = False
            if self.current_hole.SA:
                self.current_hole.game_objects.remove(self.current_hole.SA)
            self.current_hole.SA = None
            self.ui_objects["simulate_button"].edit_text("Start Simulation")
            self.simulation_started = False
            self.current_hole.simulation_started = False

        self.current_hole.retrace_mode = False
        self.current_hole.add_golf_ball()

    def handle_text_box_click(self, ui_id):
        if not (ui_id.endswith("friction") or self.simulation_mode):
            return
        self.active_text_box = self.ui_objects[ui_id]

    def handle_keyboard_input(self, event):
        if not self.active_text_box:
            return

        if event.unicode.isdigit() or event.unicode == "." and self.active_text_box:
            input_text = self.active_text_box.get_text()
            input_text += event.unicode
            self.active_text_box.edit_text(input_text)

        elif event.key == K_BACKSPACE and self.active_text_box:
            input_text = self.active_text_box.get_text()
            input_text = input_text[:-1]
            self.active_text_box.edit_text(input_text)

    def handle_events(self, events, mouse_pos):
        """
        Handles interested events.
        Checks for mouse clicks on UI elements.
        Then call to handle events in current hole scene.
        """
        for event in events:
            if event.type == MOUSEBUTTONUP:
                self.check_ui_click(mouse_pos)
            if event.type == KEYDOWN:
                self.handle_keyboard_input(event)

        self.current_hole.handle_events(events, mouse_pos)

    def update(self):
        """
        Updates data for current hole and then updates UI elements with new data.
        """
        self.current_hole.update()
        if self.current_hole.hole_complete:
            self.data["dist_from_hole"] = 0
            if (
                not self.simulation_mode
                and self.data["best_score"] > self.data["cur_score"]
            ):
                self.data["best_score"] = self.data["cur_score"]
                updated_hole_data = self.current_hole.hole_data
                updated_hole_data["best_score"] = self.data["cur_score"]
                with open(
                    f"courses/{self.course_id}/{updated_hole_data['hole_id']}.json", "w"
                ) as f:
                    dump(updated_hole_data, f)
            elif (
                self.simulation_mode
                and self.data["best_bot_score"] > self.data["cur_score"]
            ):
                self.data["best_bot_score"] = self.data["cur_score"]
                updated_hole_data = self.current_hole.hole_data
                updated_hole_data["best_bot_score"] = self.data["cur_score"]
                updated_hole_data["best_bot_path"] = self.current_hole.golf_ball.path
                updated_hole_data["best_bot_params"] = [
                    float(self.data["grass_friction"]),
                    float(self.data["sand_friction"]),
                    float(self.data["ice_friction"]),
                ]

                with open(
                    f"courses/{self.course_id}/{updated_hole_data['hole_id']}.json", "w"
                ) as f:
                    dump(updated_hole_data, f)

            if self.data["score_threshold"] > self.data["cur_score"]:
                self.data["score_threshold"] = self.data["cur_score"]

        if self.current_hole.hole_complete or self.simulation_mode:
            if not self.ui_objects["next_hole"].enabled:
                self.ui_objects["next_hole"].enable_ui()

        self.update_data()

    def update_data(self):
        """
        Updates hole info on the UI box with new data.
        """
        if self.data_area_obj in self.game_objects:
            self.game_objects.remove(self.data_area_obj)

        self.data["friction"] = min(self.data["friction"], 10)
        self.data["grass_friction"] = min(self.data["grass_friction"], 10)
        self.data["sand_friction"] = min(self.data["sand_friction"], 10)
        self.data["ice_friction"] = min(self.data["ice_friction"], 10)
        self.data["score_threshold"] = min(self.data["score_threshold"], 50)
        self.data["max_episodes"] = min(self.data["max_episodes"], 50)
        self.data["max_iterations"] = min(self.data["max_iterations"], 25)
        self.data["initial_temperature"] = min(self.data["initial_temperature"], 200)

        self.data_text_elements = self.data_text_elements = [
            [f'Course #{self.course_id.lstrip("course")}', self.large_text_size],
            [
                f'Hole #{self.current_hole.hole_id.lstrip("hole")}',
                self.medium_text_size,
            ],
            [f'Current Score: {self.data["cur_score"]}', self.medium_text_size],
            [f'Best Human Score: {self.data["best_score"]}', self.medium_text_size],
            [f'Best Bot Score: {self.data["best_bot_score"]}', self.medium_text_size],
            ["_Metrics", self.medium_text_size],
            [
                f'Distance from hole: {self.data["dist_from_hole"]}',
                self.small_text_size,
            ],
            [f'Power: {self.data["power"]}', self.small_text_size],
            [f'Angle: {self.data["angle"]}', self.small_text_size],
            [f'Overshoots: {self.data["num_overshoots"]}', self.small_text_size],
            [f'Current Surface: {self.data["surface_type"]}', self.small_text_size],
            [f'Current Friction: {self.data["friction"]}', self.small_text_size],
            [f'Episode Number: {self.data["episode_num"]}', self.small_text_size],
            [f'Iteration Number: {self.data["iterations"]}', self.small_text_size],
            [f'Current Temperature: {self.data["temp"]}', self.small_text_size],
            [f'Current Energy: {self.data["energy"]}', self.small_text_size],
            ["_Hyperparameters", self.medium_text_size],
            [f"Score Threshold: {self.data['score_threshold']}", self.small_text_size],
            [f'Max Episodes: {self.data["max_episodes"]}', self.small_text_size],
            [f'Max Iterations: {self.data["max_iterations"]}', self.small_text_size],
            [
                f'Initial Temperature: {self.data["initial_temperature"]}',
                self.small_text_size,
            ],
            # [f'Cooling Schedule: {self.data["schedule"]}', self.small_text_size],
            [f'Grass Friction: {self.data["grass_friction"]}', self.small_text_size],
            [f'Sand Friction: {self.data["sand_friction"]}', self.small_text_size],
            [f'Ice Friction: {self.data["ice_friction"]}', self.small_text_size],
            [f'_Animation Speed: {self.data["animation_speed"]}', self.small_text_size],
            ["_Message Board", self.medium_text_size],
            ["_", self.small_text_size],
        ]

        self.data_area = Surface((200, 600), SRCALPHA)
        self.add_to_ui(10, self.data_text_elements)

        self.data_area_obj = GameObject(
            id="course_ui", type="text", surface=self.data_area, pos=(400, 0)
        )
        self.game_objects.append(self.data_area_obj)

        if self.active_text_box:
            self.active_text_box.surface = self.active_text_box.hover_surface


class HoleScene(CourseScene):
    """
    Scene that holds data for a particular hole in a course.
    """

    def __init__(self, course, hole_id, hole_data, sim_mode=False):
        self.course = course
        self.hole_id = hole_id
        self.hole_data = hole_data
        self.prev_hole_id = "hole" + str(int(hole_id.lstrip("hole")) - 1)
        self.next_hole_id = "hole" + str(int(hole_id.lstrip("hole")) + 1)

        self.retrace_mode = False
        self.path = []

        self.simulation_mode = sim_mode
        self.simulation_started = False
        self.SA = None
        self.episode_num = 1
        self.max_episodes = 3

        self.game_objects = []
        self.golf_ball = None
        self.pin = None
        self.obstacles = []
        self.sand = []
        self.ice = []

        self.score = 0
        self.hole_complete = False

        self.load_assets()

    def load_assets(self):
        """
        Loads game assets for this hole.
        This includes the pin, fairway, obstacles and the golf balls.
        """
        pin_surface = import_assets(
            "assets/pin.png", alpha=True, x_scale=70, y_scale=70
        )
        self.pin = GameObject(
            id="pin",
            type="image",
            surface=pin_surface,
            pos=(self.hole_data["pin_pos"][0] - 35, self.hole_data["pin_pos"][1] - 70),
        )
        fairway = Surface((600, 600), SRCALPHA)
        draw.circle(
            fairway,
            (34, 139, 34, 128),
            self.hole_data["pin_pos"],
            self.hole_data["ball_radius"] * 1.5,
        )
        self.game_objects.append(
            GameObject(
                id="fairway",
                type="image",
                surface=fairway,
                pos=(0, 0),
            )
        )
        self.game_objects.append(self.pin)

        tee = Surface(
            (self.hole_data["ball_radius"] * 2, self.hole_data["ball_radius"] * 2),
            SRCALPHA,
        )
        draw.circle(
            tee,
            (255, 0, 0),
            (self.hole_data["ball_radius"], self.hole_data["ball_radius"]),
            5,
        )
        self.game_objects.append(
            GameObject(
                id="tee",
                type="image",
                surface=tee,
                pos=(
                    self.hole_data["ball_pos"][0] - self.hole_data["ball_radius"],
                    self.hole_data["ball_pos"][1] - self.hole_data["ball_radius"],
                ),
            )
        )

        for snd in self.hole_data["sand"]:
            sand_surface = import_assets(
                "assets/sand.png",
                alpha=True,
                x_scale=snd[2] - snd[0],
                y_scale=snd[3] - snd[1],
            )
            sand_obj = Obstacle(
                x=snd[0],
                y=snd[1],
                width=snd[2] - snd[0],
                height=snd[3] - snd[1],
                surface=sand_surface,
            )
            self.sand.append(sand_obj)
            self.game_objects.append(sand_obj)

        for i in self.hole_data["ice"]:
            ice_surface = import_assets(
                "assets/ice.png",
                alpha=True,
                x_scale=i[2] - i[0],
                y_scale=i[3] - i[1],
            )
            ice_obj = Obstacle(
                x=i[0],
                y=i[1],
                width=i[2] - i[0],
                height=i[3] - i[1],
                surface=ice_surface,
            )
            self.ice.append(ice_obj)
            self.game_objects.append(ice_obj)

        for obs in self.hole_data["obstacles"]:
            obs_surface = import_assets(
                "assets/obstacle.png",
                alpha=True,
                x_scale=obs[2] - obs[0],
                y_scale=obs[3] - obs[1],
            )
            obs_obj = Obstacle(
                x=obs[0],
                y=obs[1],
                width=obs[2] - obs[0],
                height=obs[3] - obs[1],
                surface=obs_surface,
            )
            self.obstacles.append(obs_obj)
            self.game_objects.append(obs_obj)

        self.add_golf_ball()

    def add_golf_ball(self):
        """
        Adds playable golf ball to the scene.
        """
        if self.golf_ball and self.golf_ball in self.game_objects:
            self.game_objects.remove(self.golf_ball)
        ball_pos = self.hole_data["ball_pos"]
        self.golf_ball = GolfBall(
            ball_pos[0], ball_pos[1], radius=self.hole_data["ball_radius"]
        )
        self.golf_ball.set_environment(
            (self.hole_data["pin_pos"][0], self.hole_data["pin_pos"][1]),
            self.obstacles,
            self.sand,
            self.ice,
        )
        self.golf_ball.surface_strength["grass"] = self.course.data["grass_friction"]
        self.golf_ball.surface_strength["sand"] = self.course.data["sand_friction"]
        self.golf_ball.surface_strength["ice"] = self.course.data["ice_friction"]
        self.game_objects.append(self.golf_ball)

    def handle_events(self, events, mouse_pos):
        """
        Handles interested events.
        Checks mouse interactions on a golf ball.
        """
        for event in events:
            if not self.golf_ball:
                continue
            if event.type == MOUSEBUTTONDOWN and not self.simulation_mode:
                self.handle_mouse_down(mouse_pos)

            if event.type == MOUSEMOTION and not self.simulation_mode:
                self.handle_mouse_motion(mouse_pos)

            if event.type == MOUSEBUTTONUP and not self.simulation_mode:
                self.handle_mouse_up(mouse_pos)

    def handle_mouse_down(self, mouse_pos):
        """
        If mouse clicked down on a golf ball, show guide circle.
        """
        if self.golf_ball.rect.collidepoint(mouse_pos) and self.golf_ball.interactable:
            self.golf_ball.mouse_down = True
            self.golf_ball.draw_guide_circle()
            self.game_objects.append(self.golf_ball.guide_circle)

    def handle_mouse_motion(self, mouse_pos):
        """
        If mouse drags while holding on golf ball, show power and direction line.
        """
        if self.golf_ball.mouse_down:
            if self.golf_ball.power_line in self.game_objects:
                self.game_objects.remove(self.golf_ball.power_line)
            self.golf_ball.draw_power_line(mouse_pos)
            self.game_objects.append(self.golf_ball.power_line)

    def handle_mouse_up(self, mouse_pos):
        """
        If mouse release after clicking on golf ball, set the
        release position of golf ball and update score for taking a swing.
        """
        if self.golf_ball.mouse_down:
            self.golf_ball.mouse_down = False
            self.golf_ball.set_release_position(mouse_pos)
            self.score = self.golf_ball.shots_taken

            if self.golf_ball.guide_circle in self.game_objects:
                self.game_objects.remove(self.golf_ball.guide_circle)
            if self.golf_ball.power_line in self.game_objects:
                self.game_objects.remove(self.golf_ball.power_line)

    def update(self):
        """
        Run game loop on the curent golf ball, if a swing has been taken then
        move the ball in direction and power of swing until it is in the hole.
        """
        if self.retrace_mode:
            if self.golf_ball.interactable and self.path:
                release_pos = self.path.pop(0)
                self.golf_ball.set_release_position(release_pos)
                self.score = self.golf_ball.shots_taken
            self.golf_ball.loop()
            if self.golf_ball.in_hole and not self.path:
                self.retrace_mode = False
            return

        if not self.simulation_mode and not self.golf_ball.in_hole:
            self.golf_ball.loop()
            if self.golf_ball.in_hole:
                self.hole_complete = True

        if (
            self.SA
            and self.simulation_mode
            and self.simulation_started
            and not self.retrace_mode
        ):
            self.SA.step()
            self.score = self.SA.current_golf_ball.shots_taken
            self.golf_ball = self.SA.current_golf_ball
            if (
                self.SA.hole_completed
                or self.score > self.course.data["score_threshold"] - 1
            ):
                self.hole_complete = True
                self.golf_ball = self.SA.final_ball
                self.simulation_started = False
                self.simulate()
                print(f"Episode {self.episode_num} completed with score {self.score}.")
                self.episode_num += 1
            else:
                self.hole_complete = False

        if self.episode_num > self.max_episodes and self.simulation_mode:
            print(f"Simulation ended after {self.episode_num} episodes.")
            self.episode_num = 1
            self.simulation_started = False
            self.game_objects.remove(self.SA)
            self.SA = None
            self.course.ui_objects["simulate_button"].edit_text("Start Simulation")

        self.update_course_data()

    def simulate(self):
        """
        Start the SA algorithm by initializing the SA class and adding it to game objects.
        """
        if self.simulation_started:
            return

        if self.SA:
            self.game_objects.remove(self.SA)
            self.SA = None

        self.simulation_started = True
        self.retrace_mode = False

        if self.golf_ball in self.game_objects:
            self.game_objects.remove(self.golf_ball)
        if self.SA in self.game_objects:
            self.game_objects.remove(self.SA)

        self.SA = SimulatedAnnealer(self.hole_data["pin_pos"])
        self.SA.initialize(self.hole_data, self.obstacles, self.sand, self.ice)
        self.game_objects.append(self.SA)

        self.max_episodes = int(self.course.data["max_episodes"])
        self.SA.max_iterations = int(self.course.data["max_iterations"])
        self.SA.surface_strength["grass"] = float(self.course.data["grass_friction"])
        self.SA.surface_strength["sand"] = float(self.course.data["sand_friction"])
        self.SA.surface_strength["ice"] = float(self.course.data["ice_friction"])
        self.SA.initial_temperature = float(self.course.data["initial_temperature"])
        # self.SA.cooling_schedule = self.course.data["cooling_schedule"]

    def update_course_data(self):
        """
        Update the course scene data for each upate cycle by setting the
        hole info for the interested keys.
        """

        self.course.data["cur_score"] = self.score
        self.course.data["best_score"] = self.hole_data["best_score"]
        self.course.data["best_bot_score"] = self.hole_data["best_bot_score"]

        if self.simulation_mode and self.SA:
            self.course.data["dist_from_hole"] = self.dist_from_hole_calculation(
                self.SA.least_energy_ball
            )
            self.course.data["power"] = round(self.SA.least_energy_ball.power, 2)
            self.course.data["angle"] = round(self.SA.least_energy_ball.angle, 2)
            self.course.data["num_overshoots"] = self.SA.least_energy_ball.overshoots
            self.course.data["surface_type"] = self.SA.least_energy_ball.surface_type
            self.course.data["friction"] = self.SA.least_energy_ball.surface_strength[
                self.SA.least_energy_ball.surface_type
            ]
            self.course.data["episode_num"] = self.episode_num
            self.course.data["iterations"] = self.SA.iteration
            self.course.data["temp"] = round(self.SA.temperature, 2)
            self.course.data["energy"] = round(self.SA.energy, 2)

            self.course.data["max_episodes"] = self.max_episodes
            self.course.data["max_iterations"] = self.SA.max_iterations
            self.course.data["grass_friction"] = (
                self.SA.least_energy_ball.surface_strength["grass"]
            )
            self.course.data["sand_friction"] = (
                self.SA.least_energy_ball.surface_strength["sand"]
            )
            self.course.data["ice_friction"] = (
                self.SA.least_energy_ball.surface_strength["ice"]
            )
            self.course.data["initial_temperature"] = round(
                self.SA.initial_temperature, 2
            )
            self.course.data["schedule"] = self.SA.cooling_schedule
            return

        if self.golf_ball:
            self.course.data["dist_from_hole"] = self.dist_from_hole_calculation(
                self.golf_ball
            )
            self.course.data["power"] = round(self.golf_ball.power, 2)
            self.course.data["angle"] = round(self.golf_ball.angle, 2)
            self.course.data["num_overshoots"] = self.golf_ball.overshoots
            self.course.data["surface_type"] = self.golf_ball.surface_type
            self.course.data["friction"] = self.golf_ball.surface_strength[
                self.golf_ball.surface_type
            ]

    def dist_from_hole_calculation(self, golf_ball):
        """
        Utility function to calculate distance from hole for given golf ball.
        """

        if golf_ball.in_hole:
            return 0
        else:
            return round(
                sqrt(
                    (self.pin.pos[0] - golf_ball.x) ** 2
                    + (self.pin.pos[1] - golf_ball.y) ** 2
                ),
                2,
            )

    def retrace_bot_path(self):
        """
        Function to show best bot path from all simulated iterations.
        """
        if self.retrace_mode:
            return

        self.path = self.hole_data.get("best_bot_path", [])[:]
        if not self.path:
            print("No bot path data available for this hole.")
            return

        self.retrace_mode = True

        if self.SA in self.game_objects:
            self.game_objects.remove(self.SA)
            self.SA = None

        if self.golf_ball in self.game_objects:
            self.game_objects.remove(self.golf_ball)

        self.add_golf_ball()

    def draw(self, win):
        """
        Draws all game objects in this hole scene.
        """
        for obj in self.game_objects:
            obj.draw(win)

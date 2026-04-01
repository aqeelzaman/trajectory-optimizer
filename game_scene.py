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

        self.data = {
            "score": 0,
            "best_score": 0,
            "dist_from_hole": 0,
            "power": 0,
            "angle": 0,
            "num_overshoots": 0,
            "iterations": 0,
            "temp": 0,
            "friction": 9.8,
            "dist_weight": 0,
            "shots_weight": 0,
            "overshots_weight": 0,
        }
        self.data_text_elements = self.data_text_elements = [
            [f'Course #{self.course_id.lstrip("course")}', 25],
            [f'Score: {self.data["score"]}', 20],
            [f'Best Score: {self.data["best_score"]}', 20],
            ["_Metrics", 20],
            [f'Dist from hole: {self.data["dist_from_hole"]}', 15],
            [f'Power: {self.data["power"]}', 15],
            [f'Angle: {self.data["angle"]}', 15],
            [f'Overshoots: {self.data["num_overshoots"]}', 15],
            ["_Simulation Info", 20],
            [f'# of iterations: {self.data["iterations"]}', 15],
            [f'Temperature: {self.data["temp"]}', 15],
            [f'Friction: {self.data["friction"]}', 15],
            ["_Heuristic Weights", 20],
            [f'Distance: {self.data["dist_weight"]}', 15],
            [f'Stroke weight: {self.data["shots_weight"]}', 15],
            [f'Overshoots weight: {self.data["overshots_weight"]}', 15],
            ["_", 15],
        ]
        self.data_area_obj = None

        self.load_assets()
        self.add_ui_elements()
        self.add_holes()
        self.data_text_elements.insert(
            1, [f'Hole #{self.current_hole.hole_id.lstrip("hole")}', 23]
        )

    def load_assets(self):
        """
        Loads game assets for the course.
        """
        self.orange_button = import_assets(
            "assets/ui_button_orange.png", x_scale=150, y_scale=50
        )
        self.blue_button = import_assets(
            "assets/ui_button_blue.png", x_scale=150, y_scale=50
        )
        self.grass = import_assets("assets/grass.png", x_scale=600, y_scale=600)
        self.ui_frame = import_assets(
            "assets/ui_frame.png", x_scale=600, y_scale=200, degree=90
        )
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
        start_y = self.data_val_coords[9][1] + 3
        end_y = self.data_val_coords[len(self.data_val_coords) - 1][1] - start_y + 21
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
            if label[0] == "_":
                draw.line(
                    self.data_area, (0, 0, 0), (0, last_y), (200, last_y), width=2
                )
                label = label.lstrip("_")
                last_y += padding / 2

            FONT = font.SysFont("arial", text_size)
            text_surface = FONT.render(label, True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(padding, last_y))
            self.data_area.blit(text_surface, text_rect)
            self.data_val_coords.append(
                [text_rect.topright[0] + padding, text_rect.topright[1]]
            )
            last_y += text_size + padding / 2

        return last_y

    def add_buttons(self, last_y):
        """
        Add action buttons to the course scene.
        """
        padding = 415
        last_y += 10
        game_obj = add_ui_element(
            "simulate_button",
            self.orange_button,
            "Start Simulation",
            (padding, last_y),
            text_size=18,
            enabled=self.simulation_mode,
        )
        self.ui_objects["simulate_button"] = game_obj
        self.game_objects.append(game_obj)

        last_y += 57
        game_obj = add_ui_element(
            "back_to_course",
            self.blue_button,
            "Back To Courses",
            (padding, last_y),
            text_size=18,
        )
        self.ui_objects["back_to_course"] = game_obj
        self.game_objects.append(game_obj)

        last_y += 57
        game_obj = add_ui_element(
            "next_hole",
            self.blue_button,
            "Next Hole!",
            (padding, last_y),
            text_size=18,
            enabled=not self.simulation_mode,
        )
        self.ui_objects["next_hole"] = game_obj
        self.game_objects.append(game_obj)

    def add_holes(self):
        """
        Uses json data for the current course to add holes as new scenes.
        """
        hole_file_path = "courses/" + self.course_id
        for hole_file in listdir(hole_file_path):
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
            if self.current_hole in self.game_objects:
                self.game_objects.remove(self.current_hole)
            self.current_hole = self.holes[hole_id]
            self.game_objects.append(self.current_hole)

            if self.current_hole.next_hole_id not in self.holes:
                self.ui_objects["next_hole"].edit_text("End This Course")

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
                    if not self.simulation_started:
                        self.simulation_started = True
                        self.ui_objects[ui_id].edit_text("End Simulation")
                        self.current_hole.simulate()
                    else:
                        self.simulation_started = False
                        self.ui_objects[ui_id].edit_text("Start Simulation")
                        self.current_hole.simulation_started = False
                elif ui_id == "back_to_course":
                    self.scene_manager.switch_scene("course_select")
                elif ui_id == "next_hole":
                    if self.ui_objects[ui_id].get_text() == "Next Hole!":
                        next_hole_id = "hole" + str(
                            int(self.current_hole.hole_id.lstrip("hole")) + 1
                        )
                        self.switch_hole(next_hole_id)
                    elif self.ui_objects[ui_id].get_text() == "End This Course":
                        self.scene_manager.switch_scene("course_select")

    def handle_events(self, events, mouse_pos):
        """
        Handles interested events.
        Checks for mouse clicks on UI elements.
        Then call to handle events in current hole scene.
        """
        for event in events:
            if event.type == MOUSEBUTTONUP:
                self.check_ui_click(mouse_pos)
        self.current_hole.handle_events(events, mouse_pos)

    def update(self):
        """
        Updates data for current hole and then updates UI elements with new data.
        """
        self.current_hole.update()
        self.update_data()
        if self.current_hole.hole_complete:
            if self.data["best_score"] > self.data["score"]:
                self.data["best_score"] = self.data["score"]
                updated_hole_data = self.current_hole.hole_data
                updated_hole_data["best_score"] = self.data["score"]
                with open(
                    f"courses/{self.course_id}/{updated_hole_data['hole_id']}.json", "w"
                ) as f:
                    dump(updated_hole_data, f)

        if self.current_hole.hole_complete or self.simulation_mode:
            if not self.ui_objects["next_hole"].enabled:
                self.ui_objects["next_hole"].enable_ui()

    def update_data(self):
        """
        Updates hole info on the UI box with new data.
        """
        if self.data_area_obj in self.game_objects:
            self.game_objects.remove(self.data_area_obj)

        self.data_text_elements = [
            [f'Course #{self.course_id.lstrip("course")}', 25],
            [f'Hole #{self.current_hole.hole_id.lstrip("hole")}', 23],
            [f'Score: {self.data["score"]}', 20],
            [f'Best Score: {self.data["best_score"]}', 20],
            ["_Metrics", 20],
            [f'Dist from hole: {self.data["dist_from_hole"]}', 15],
            [f'Power: {self.data["power"]}', 15],
            [f'Angle: {self.data["angle"]}', 15],
            [f'Overshoots: {self.data["num_overshoots"]}', 15],
            ["_Simulation Info", 20],
            [f'# of iterations: {self.data["iterations"]}', 15],
            [f'Temperature: {self.data["temp"]}', 15],
            [f'Friction: {self.data["friction"]}', 15],
            ["_Heuristic Weights", 20],
            [f'Distance: {self.data["dist_weight"]}', 15],
            [f'Stroke weight: {self.data["shots_weight"]}', 15],
            [f'Overshoots weight: {self.data["overshots_weight"]}', 15],
            ["_", 15],
        ]

        self.data_area = Surface((200, 600), SRCALPHA)
        self.add_to_ui(10, self.data_text_elements)

        self.data_area_obj = GameObject(
            id="course_ui", type="text", surface=self.data_area, pos=(400, 0)
        )
        self.game_objects.append(self.data_area_obj)


class HoleScene(CourseScene):
    """
    Scene that holds data for a particular hole in a course.
    """

    def __init__(self, course, hole_id, hole_data, sim_mode=False):
        self.course = course
        self.hole_id = hole_id
        self.hole_data = hole_data
        self.next_hole_id = "hole" + str(int(hole_id.lstrip("hole")) + 1)

        self.simulation_mode = sim_mode
        self.simulation_started = False
        self.SA = None

        self.game_objects = []
        self.golf_ball = None
        self.pin = None
        self.obstacles = []
        self.sand = []

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
        ball_pos = self.hole_data["ball_pos"]
        self.golf_ball = GolfBall(
            ball_pos[0], ball_pos[1], radius=self.hole_data["ball_radius"]
        )
        self.golf_ball.set_environment(
            (self.hole_data["pin_pos"][0], self.hole_data["pin_pos"][1]),
            self.obstacles,
            self.sand,
        )
        self.game_objects.append(self.golf_ball)

    def handle_events(self, events, mouse_pos):
        """
        Handles interested events.
        Checks mouse interactions on a golf ball.
        """
        for event in events:
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
        if not self.simulation_mode and not self.golf_ball.in_hole:
            self.golf_ball.loop()
            if self.golf_ball.in_hole:
                self.hole_complete = True

        if self.SA and self.simulation_mode and self.simulation_started:
            self.SA.step()
            if self.SA.hole_completed:
                final_ball = self.SA.final_ball
                self.game_objects.remove(self.SA)
                self.game_objects.append(final_ball)
                self.SA = None

        self.update_course_data()

    def simulate(self):
        """
        Start the SA algorithm by initializing the SA class and adding it to game objects.
        """
        if self.simulation_started:
            return

        self.simulation_started = True
        if self.golf_ball in self.game_objects:
            self.game_objects.remove(self.golf_ball)
        if self.SA in self.game_objects:
            self.game_objects.remove(self.SA)

        self.SA = SimulatedAnnealer(self.hole_data["pin_pos"])
        self.SA.initialize(self.hole_data, self.obstacles, self.sand)
        self.game_objects.append(self.SA)

    def update_course_data(self):
        """
        Update the course scene data for each upate cycle by setting the
        hole info for the interested keys.
        """

        self.course.data["score"] = self.score

        if self.golf_ball.in_hole:
            self.course.data["dist_from_hole"] = 0
        else:
            self.course.data["dist_from_hole"] = round(
                sqrt(
                    (self.pin.pos[0] - self.golf_ball.x) ** 2
                    + (self.pin.pos[1] - self.golf_ball.y) ** 2
                ),
                2,
            )

        if self.simulation_mode:
            self.course.data["best_score"] = self.hole_data["best_bot_score"]
        else:
            self.course.data["best_score"] = self.hole_data["best_score"]

        self.course.data["power"] = round(self.golf_ball.power, 2)
        self.course.data["angle"] = round(self.golf_ball.angle, 2)
        self.course.data["friction"] = self.golf_ball.friction
        self.course.data["num_overshoots"] = self.golf_ball.overshoots

    def draw(self, win):
        """
        Draws all game objects in this hole scene.
        """
        for obj in self.game_objects:
            obj.draw(win)

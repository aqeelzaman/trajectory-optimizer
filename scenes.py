import json
import os
import pygame
from math import sqrt
from golfball import GolfBall
from utils import import_assets, add_ui_element
from objects import GameObject, Obstacle


class AbstractScene:
    """
    Abstract class that is the parent of all scene classes.
    Includes shared functions among all scenes.
    """

    def check_ui_hover(self, mouse_pos):
        """
        Check if mouse hovers over a UI element to show shading effect.
        """
        for ui_obj in self.ui_objects.values():
            if not ui_obj.enabled:
                continue
            ui_rect = ui_obj.surface.get_rect(topleft=ui_obj.pos)
            if ui_rect.collidepoint(mouse_pos):
                ui_obj.surface = ui_obj.hover_surface
            else:
                ui_obj.surface = ui_obj.base_surface

    def draw(self, win):
        """
        Super class that draws all objects on the scene.
        Calls the draw function for each game object on current scene.
        """
        win.fill((255, 255, 255))
        for obj in self.game_objects:
            obj.draw(win)


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
        game_object, text_object = add_ui_element(
            "start_button", self.ui_banner, "Start", (20, 250)
        )
        game_object.special_tint((245, 222, 179))
        self.ui_objects["start_button"] = game_object
        self.game_objects.append(game_object)
        self.game_objects.append(text_object)

        game_object, text_object = add_ui_element(
            "tutorial_button", self.ui_banner, "Tutorial", (20, 330)
        )
        game_object.special_tint((245, 222, 179))
        self.ui_objects["tutorial_button"] = game_object
        self.game_objects.append(game_object)
        self.game_objects.append(text_object)

        game_object, text_object = add_ui_element(
            "quit_button", self.ui_banner, "Quit", (20, 410)
        )
        game_object.special_tint((245, 222, 179))
        self.ui_objects["quit_button"] = game_object
        self.game_objects.append(game_object)
        self.game_objects.append(text_object)

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
                    print("Start Game!")
                    self.scene_manager.switch_scene("course1")
                elif ui_id == "tutorial_button":
                    print("Show Tutorial!")
                elif ui_id == "quit_button":
                    print("Quit Game!")
                    pygame.quit()
                    exit()

    def handle_events(self, events, mouse_pos):
        """
        Handles interested events.
        Checks for mouse clicks on UI elements.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                self.check_ui_click(mouse_pos)

    def update(self):
        """
        No scene updates for main menu.
        """
        pass


class CourseScene(AbstractScene):
    """
    Scene that holds data for a particular course.
    Each course has multiple holes, a UI bar that displays hole info,
    and buttons for navigation and action.
    """

    def __init__(self, scene_manager, course_id):
        self.scene_manager = scene_manager
        self.course_id = course_id

        self.game_objects = []
        self.ui_objects = {}
        self.holes = {}
        self.current_hole = None
        self.simulation_running = False

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
            "overshoots_weight": 0,
        }
        self.ui_val_area_obj = None

        self.load_assets()
        self.add_ui_elements()
        self.add_holes()

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
            "assets/ui_frame.png", x_scale=600, y_scale=200, rotate=90
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
        self.ui_area = pygame.Surface((200, 600), pygame.SRCALPHA)
        self.ui_val_coords = []
        last_y = self.add_to_ui(
            10,
            [
                ["Course #", 25],
                ["Hole #", 23],
                ["Score: ", 20],
                ["Best Score: ", 20],
                ["break", 0],
                ["Metrics", 20],
                ["Dist from hole: ", 15],
                ["Power: ", 15],
                ["Angle: ", 15],
                ["Overshoots: ", 15],
                ["break", 0],
                ["Simulation Info", 20],
                ["# of iterations: ", 15],
                ["Temperature: ", 15],
                ["Friction: ", 15],
                ["break", 0],
                ["Heuristic Weights", 20],
                ["Distance: ", 15],
                ["Stroke weight: ", 15],
                ["Overshoots weight: ", 15],
                ["break", 0],
            ],
        )

        self.data_to_coord_map = {
            "score": 2,
            "best_score": 3,
            "dist_from_hole": 5,
            "power": 6,
            "angle": 7,
            "num_overshoots": 8,
            "iterations": 10,
            "temp": 11,
            "friction": 12,
            "dist_weight": 14,
            "shots_weight": 15,
            "overshoots_weight": 16,
        }

        self.add_buttons(last_y)

        ui_obj = GameObject(
            id="course_ui",
            type="ui",
            surface=self.ui_area,
            pos=(400, 0),
        )
        self.ui_objects["course_ui"] = ui_obj
        self.game_objects.append(ui_obj)

        shade = pygame.Surface((200, 600), pygame.SRCALPHA)
        start_y = self.ui_val_coords[9][1]
        end_y = self.ui_val_coords[len(self.ui_val_coords) - 1][1] - start_y + 17
        pygame.draw.rect(
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

        if not self.simulation_running:
            self.game_objects.append(self.shade_obj)

    def add_to_ui(self, last_y, text_elements):
        """
        Utility function to add text elements to UI box at given coordinate
        and size.
        """
        padding = 10
        for i, (label, text_size) in enumerate(text_elements):
            if label == "break":
                pygame.draw.line(
                    self.ui_area, (0, 0, 0), (0, last_y), (200, last_y), width=2
                )
                last_y += padding / 2
                continue

            FONT = pygame.font.SysFont("arial", text_size)
            text_surface = FONT.render(label, True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(padding, last_y))
            self.ui_area.blit(text_surface, text_rect)
            self.ui_val_coords.append(
                [text_rect.topright[0] + padding, text_rect.topright[1]]
            )
            last_y += text_size + padding / 2

        return last_y

    def add_buttons(self, last_y):
        """
        Add action buttons to the course scene.
        """
        padding = 415
        last_y += 5

        game_obj, text_obj = add_ui_element(
            "simulate_button",
            self.orange_button,
            "Start Simulation",
            (padding, last_y),
            text_size=18,
            enabled=False,
        )
        self.ui_objects["simulate_button"] = game_obj
        self.game_objects.append(game_obj)
        self.game_objects.append(text_obj)

        last_y += 57
        game_obj, text_obj = add_ui_element(
            "back_to_course",
            self.blue_button,
            "Back To Courses",
            (padding, last_y),
            text_size=18,
        )
        self.ui_objects["back_to_course"] = game_obj
        self.game_objects.append(game_obj)
        self.game_objects.append(text_obj)

        last_y += 57
        game_obj, text_obj = add_ui_element(
            "next_hole",
            self.blue_button,
            "Next Hole!",
            (padding, last_y),
            text_size=18,
            enabled=False,
        )
        self.ui_objects["next_hole"] = game_obj
        self.game_objects.append(game_obj)
        self.game_objects.append(text_obj)

    def add_holes(self):
        """
        Uses json data for the current course to add holes as new scenes.
        """
        for hole_file in os.listdir(self.course_id):
            default_hole = None
            if hole_file.endswith(".json"):
                with open(f"{self.course_id}/{hole_file}", "r") as f:
                    hole_data = json.load(f)
                hole_id = hole_data["hole_id"]
                if not default_hole:
                    default_hole = hole_id
                self.holes[hole_id] = HoleScene(self, hole_id, hole_data)

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
                if ui_id == "simulate_button" and self.simulation_running:
                    print("Simulate")
                elif ui_id == "back_to_course":
                    print("Back to courses")
                    self.scene_manager.switch_scene("main_menu")
                elif ui_id == "next_hole":
                    next_hold_id = "hole" + str(
                        int(self.current_hole.hole_id.lstrip("hole")) + 1
                    )
                    self.switch_hole(next_hold_id)

    def handle_events(self, events, mouse_pos):
        """
        Handles interested events.
        Checks for mouse clicks on UI elements.
        Then call to handle events in current hole scene.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                self.check_ui_click(mouse_pos)
        self.current_hole.handle_events(events, mouse_pos)

    def update(self):
        """
        Updates data for current hole and then updates UI elements with new data.
        """
        self.current_hole.update()
        self.update_data()
        if self.current_hole.hole_complete and not self.ui_objects["next_hole"].enabled:
            self.ui_objects["next_hole"].enable_ui()

    def update_data(self):
        """
        Updates hole info on the UI box with new data.
        """
        if self.ui_val_area_obj in self.game_objects:
            self.game_objects.remove(self.ui_val_area_obj)

        ui_val_area = pygame.Surface((200, 600), pygame.SRCALPHA)

        FONT = pygame.font.SysFont("arial", 25)
        text_surface = FONT.render(self.course_id.lstrip("course"), True, (0, 0, 0))
        [x_pos, y_pos] = self.ui_val_coords[0]
        x_pos -= 10
        text_rect = text_surface.get_rect(topleft=(x_pos, y_pos))
        ui_val_area.blit(text_surface, text_rect)

        FONT = pygame.font.SysFont("arial", 23)
        text_surface = FONT.render(
            self.current_hole.hole_id.lstrip("hole"), True, (0, 0, 0)
        )
        [x_pos, y_pos] = self.ui_val_coords[1]
        x_pos -= 10
        text_rect = text_surface.get_rect(topleft=(x_pos, y_pos))
        ui_val_area.blit(text_surface, text_rect)

        for d in self.data.keys():
            idx = self.data_to_coord_map[d]
            [x_pos, y_pos] = self.ui_val_coords[idx]
            x_pos -= 10

            if d == "score" or d == "best_score":
                text_size = 20
            else:
                text_size = 15

            FONT = pygame.font.SysFont("arial", text_size)
            text_surface = FONT.render(str(self.data[d]), True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(x_pos, y_pos))
            ui_val_area.blit(text_surface, text_rect)

        self.ui_val_area_obj = GameObject(
            id="ui_val_area", type="text", surface=ui_val_area, pos=(400, 0)
        )
        self.game_objects.append(self.ui_val_area_obj)


class HoleScene(CourseScene):
    """
    Scene that holds data for a particular hole in a course.
    """

    def __init__(self, course, hole_id, hole_data):
        self.course = course
        self.game_objects = []
        self.hole_id = hole_id
        self.hole_data = hole_data

        self.simulation_running = False
        self.golf_balls = []
        self.golf_ball = None
        self.pin = None
        self.obstacles = []

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
        fairway = pygame.Surface((600, 600), pygame.SRCALPHA)
        pygame.draw.circle(
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

        self.add_golf_balls()

    def add_golf_balls(self):
        """
        Adds playable golf ball to the scene.
        If in simulation mode, it adds all the golf balls per iteration.
        """
        if not self.simulation_running:
            ball_pos = self.hole_data["ball_pos"]
            self.golf_ball = GolfBall(
                ball_pos[0], ball_pos[1], radius=self.hole_data["ball_radius"]
            )
            self.golf_ball.set_environment(
                (self.hole_data["pin_pos"][0], self.hole_data["pin_pos"][1]),
                self.obstacles,
            )
            self.game_objects.append(self.golf_ball)
        else:
            # Add more balls as the simulation requires.
            pass

    def handle_events(self, events, mouse_pos):
        """
        Handles interested events.
        Checks mouse interactions on a golf ball.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and not self.simulation_running:
                self.handle_mouse_down(mouse_pos)

            if event.type == pygame.MOUSEMOTION and not self.simulation_running:
                self.handle_mouse_motion(mouse_pos)

            if event.type == pygame.MOUSEBUTTONUP and not self.simulation_running:
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
            self.score += 1

            self.game_objects.remove(self.golf_ball.guide_circle)
            self.game_objects.remove(self.golf_ball.power_line)

    def update(self):
        """
        Run game loop on the curent golf ball, if a swing has been taken then
        move the ball in direction and power of swing until it is in the hole.
        """
        if not self.simulation_running and not self.golf_ball.in_hole:
            self.golf_ball.loop()
            if self.golf_ball.in_hole:
                self.hole_complete = True

        self.update_course_data()

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

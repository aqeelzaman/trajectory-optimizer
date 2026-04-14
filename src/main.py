from pygame import init, time, event, QUIT, quit, display, mouse, SCALED
from main_menu_scene import MainMenuScene
from course_selection_scene import CourseSelectionScene
from tutorial_scene import TutorialScene

init()

class SceneManager:
    """
    Main scene manager for the game instance.
    It keeps track of all windows in the game and will run the game loop
    on the current selected scene. Able to switch scenes as needed.
    """
    def __init__(self):
        self.scenes = {
            "main_menu": MainMenuScene(self),
            "course_select": CourseSelectionScene(self),
            "tutorial": TutorialScene(self)
        }
        self.current_scene = self.scenes["main_menu"]
        self.fps_multiplier = 3

    def switch_scene(self, new_scene):
        """
        Switch on screen scenes with given scene name.
        """
        self.current_scene = self.scenes[new_scene]
        self.current_scene.initiate()

    def add_scene(self, scene_id, scene_obj):
        """
        Add a new scene object with a scene ID.
        """
        self.scenes[scene_id] = scene_obj

    def run(self):
        """
        Main runner game loop that calls functional parts of current scene.
        """
        RUNNING = True
        CLOCK = time.Clock()

        while RUNNING:
            CLOCK.tick(60 * self.fps_multiplier)
            events = event.get()
            for e in events:
                if e.type == QUIT:
                    RUNNING = False
                    break

            mouse_pos = mouse.get_pos()
            self.current_scene.check_ui_hover(mouse_pos)
            self.current_scene.handle_events(events, mouse_pos)
            self.current_scene.update()
            self.current_scene.draw(WIN)
            display.flip()

        quit()

WIN = display.set_mode((600, 600), SCALED)
display.set_caption("Hot Takes, Cold Putts")

if __name__ == "__main__":
    scene_manager = SceneManager()
    scene_manager.run()

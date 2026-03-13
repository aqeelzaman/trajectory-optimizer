import pygame
from scenes import MainMenuScene, CourseScene

pygame.init()


class SceneManager:
    """
    Main scene manager for the game instance.
    It keeps track of all windows in the game and will run the game loop
    on the current selected scene. Able to switch scenes as needed.
    """

    def __init__(self):
        self.scenes = {
            "main_menu": MainMenuScene(self),
            "course1": CourseScene(self, "course1"),
        }
        self.current_scene = self.scenes["main_menu"]

    def switch_scene(self, new_scene):
        self.current_scene = self.scenes[new_scene]

    def run(self):
        RUNNING = True
        CLOCK = pygame.time.Clock()
        FPS = 60

        while RUNNING:
            CLOCK.tick(FPS)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    RUNNING = False
                    break

            mouse_pos = pygame.mouse.get_pos()
            self.current_scene.check_ui_hover(mouse_pos)
            self.current_scene.handle_events(events, mouse_pos)
            self.current_scene.update()
            self.current_scene.draw(WIN)
            pygame.display.flip()

        pygame.quit()


WIN = pygame.display.set_mode((600, 600), pygame.SCALED)
pygame.display.set_caption("Hot Takes, Cold Putts")


def main():
    scene_manager = SceneManager()
    scene_manager.run()


if __name__ == "__main__":
    main()

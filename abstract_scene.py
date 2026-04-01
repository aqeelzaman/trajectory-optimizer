from utils import import_assets, add_ui_element
from objects import GameObject


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

    def update(self):
        pass

    def initiate(self):
        pass

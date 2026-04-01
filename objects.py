from pygame import BLEND_RGBA_MULT, font
from pygame.sprite import Sprite
from pygame.mask import from_surface


class GameObject:
    """
    An abstract instance in the game that has its own details.
    This can be any game elements, surfaces or UI.
    """

    def __init__(self, id, type, surface, pos):
        self.id = id
        self.type = type
        self.surface = surface
        self.rect = surface.get_rect(topleft=pos)
        self.pos = pos
        self.visible = True
        self.text_obj = None
        self.text = None

        if self.type == "ui":
            self.hover_surface = get_tinted_surface(surface)
            self.base_surface = surface
            self.tint_color = "grey70"
            self.enabled = True

    def edit_text(self, text, text_size=None, text_color=None):
        self.text = text
        self.text_size = text_size if text_size is not None else self.text_size
        self.text_color = text_color if text_color is not None else self.text_color
        FONT = font.SysFont("arial", self.text_size)
        text_surface = FONT.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.text_obj = GameObject(
            id=f"{self.id}_text",
            type="text",
            surface=text_surface,
            pos=text_rect.topleft,
        )
    
    def get_text(self):
        return self.text

    def enable_ui(self):
        """
        If an UI object, this will enable click and hover functions.
        """
        if not self.type == "ui":
            return
        self.enabled = True
        self.special_tint(self.tint_color)
        self.surface = self.base_surface

    def disable_ui(self):
        """
        If an UI object, this will disable click and hover functions.
        """
        if not self.type == "ui":
            return
        self.enabled = False
        self.special_tint("grey30")
        self.surface = self.hover_surface

    def toggle_visibility(self):
        self.visible = not self.visible

    def set_visibility(self, visible):
        self.visible = visible

    def special_tint(self, color):
        """
        Adds a custom tint on hover for visual effect.
        """
        if not self.type == "ui":
            return
        self.hover_surface = get_tinted_surface(self.base_surface, tint_color=color)

    def draw(self, win):
        """
        Draws this game object onto the given window.
        """
        if not self.visible:
            return
        win.blit(self.surface, self.pos)
        if self.text_obj:
            self.text_obj.draw(win)


class Obstacle(Sprite):
    """
    An obstacle instance that interacts with golf ball on a hole.
    """

    def __init__(self, x, y, width, height, surface):
        super().__init__()
        self.image = surface
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = from_surface(self.image)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, win):
        """
        Draws this game object onto the given window.
        """
        win.blit(self.image, self.rect.topleft)


def get_tinted_surface(surface, tint_color="grey70"):
    """
    Utility function for producing a custom surface with a tint for hover effect.
    """
    tinted_surface = surface.copy()
    tinted_surface.fill(tint_color, special_flags=BLEND_RGBA_MULT)
    return tinted_surface

import pygame


class GameObject:
    """
    An abstract instance in the game that has its own details.
    """

    def __init__(self, id, type, surface, pos):
        self.id = id
        self.type = type
        self.surface = surface
        self.pos = pos
        if self.type == "ui":
            self.hover_surface = get_tinted_surface(surface)
            self.base_surface = surface
            self.enabled = True
            self.tint_color = "grey70"

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
        win.blit(self.surface, self.pos)


class Obstacle:
    """
    An obstacle instance that interacts with golf ball on a hole.
    """

    def __init__(self, x, y, width, height, surface):
        self.image = surface
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
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
    tinted_surface.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted_surface

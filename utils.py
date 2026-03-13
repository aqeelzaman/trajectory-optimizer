import pygame

from objects import GameObject

pygame.font.init()


def import_assets(path, alpha=False, x_scale=100, y_scale=100, rotate=0):
    """
    Utility function to import a given surface with custom transform.
    """
    if alpha:
        image = pygame.image.load(path).convert_alpha()
    else:
        image = pygame.image.load(path).convert()

    return pygame.transform.rotate(
        pygame.transform.scale(image, (x_scale, y_scale)), rotate
    )


def add_ui_element(
    id, surface, text, position, text_color=(0, 0, 0), text_size=28, enabled=True
):
    """
    Utility function to add a UI surface and an attached text with custom detailing.
    """
    FONT = pygame.font.SysFont("arial", text_size)
    ui_surface = surface.copy()
    ui_rect = ui_surface.get_rect(topleft=position)
    text_surface = FONT.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=ui_rect.center)

    game_obj = GameObject(
        id=id,
        type="ui",
        surface=ui_surface,
        pos=position,
    )

    if not enabled:
        game_obj.disable_ui()

    text_obj = GameObject(
        id=f"{id}_text",
        type="text",
        surface=text_surface,
        pos=text_rect.topleft,
    )
    text_obj.parent_id = id

    return game_obj, text_obj

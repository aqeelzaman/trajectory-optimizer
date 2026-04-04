from pygame.transform import scale, rotate
from pygame.image import load
from pygame import font
from objects import GameObject

font.init()


def import_assets(path, alpha=False, x_scale=100, y_scale=100, degree=0):
    """
    Utility function to import a given surface with custom transform.
    """
    if alpha:
        image = load(path).convert_alpha()
    else:
        image = load(path).convert()

    return rotate(scale(image, (x_scale, y_scale)), degree)


def add_ui_element(
    id,
    surface,
    text,
    position,
    text_color=(0, 0, 0),
    text_size=28,
    enabled=True,
    visible=True,
):
    """
    Utility function to add a UI surface and an attached text with custom detailing.
    """
    ui_surface = surface.copy()

    game_obj = GameObject(
        id=id,
        type="ui",
        surface=ui_surface,
        pos=position,
    )

    game_obj.edit_text(text, text_size, text_color)

    if not enabled:
        game_obj.disable_ui()
    if not visible:
        game_obj.toggle_visibility()

    return game_obj

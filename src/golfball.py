from pygame.sprite import Sprite, collide_rect
from pygame.math import Vector2
from pygame import Surface, SRCALPHA, draw
from utils import import_assets
from objects import GameObject


class GolfBall(Sprite):
    """
    Golf ball object, holds info of each ball.
    It also has functionality pertaining to this ball object.
    """

    def __init__(self, x, y, radius):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = radius

        self.image = import_assets(
            "assets/golf_ball.png", alpha=True, x_scale=radius, y_scale=radius
        )
        self.rect = self.image.get_rect(center=(x, y))

        self.x_velocity = 0
        self.y_velocity = 0
        self.release_position = self.rect.center
        self.power = 0
        self.angle = 0
        self.overshoots = 0

        self.base_friction = 0.98
        self.surface_strength = {"grass": 1, "sand": 3, "ice": 0.5}
        self.surface_type = "grass"
        self.total_friction = 0.98

        self.interactable = True
        self.mouse_down = False
        self.dropping_into_hole = False
        self.in_hole = False
        self.overshot = False

        self.halo = None
        self.power_line = None
        self.guide_circle = None
        self.radius_factor = 6
        self.energy = 0
        self.shots_taken = 0

        self.pin = None
        self.obstacles = []
        self.sand = []
        self.ice = []
        self.path = []

    def set_environment(self, pin, obstacles, sand, ice):
        """
        Set the goal and obstacles to interact with.
        """
        self.pin = pin
        self.obstacles = obstacles
        self.sand = sand
        self.ice = ice

    def get_info(self):
        """
        Return the information of this golf ball.
        Includes position, radius and max radius of effect.
        """

        return (self.x, self.y), self.radius, self.radius * (self.radius_factor / 2)

    def set_ghost_color(self, halo_color):
        """
        Set halo color for this golf ball to indicate relative energy level.
        """
        halo_surface = Surface((self.radius * 2, self.radius * 2), SRCALPHA)
        draw.circle(
            halo_surface,
            halo_color,
            (self.radius, self.radius),
            self.radius / 1.6,
            width=2,
        )
        self.halo = GameObject(
            id="halo",
            type="circle",
            surface=halo_surface,
            pos=(
                self.rect.centerx - self.radius,
                self.rect.centery - self.radius,
            ),
        )

    def draw_guide_circle(self):
        """
        Draw a guide circle showing the max area of effect for swing power.
        """
        max_radius = self.radius * (self.radius_factor / 2)
        guide_surface = Surface((max_radius * 2, max_radius * 2), SRCALPHA)
        draw.circle(
            guide_surface,
            (255, 255, 255, 128),
            (max_radius, max_radius),
            max_radius,
            width=2,
        )
        self.guide_circle = GameObject(
            id="guide_circle",
            type="circle",
            surface=guide_surface,
            pos=(
                self.rect.centerx - max_radius,
                self.rect.centery - max_radius,
            ),
        )

    def draw_power_line(self, mouse_pos):
        """
        Draw a line that shows the power and direction of swing.
        """
        max_length = self.radius * self.radius_factor
        center = Vector2(self.rect.center)
        power_offset = (Vector2(mouse_pos) - center) * -2

        if power_offset.length() > max_length:
            power_offset.scale_to_length(max_length)

        local_center = Vector2(max_length, max_length)
        line_surface = Surface((max_length * 2, max_length * 2), SRCALPHA)
        draw.line(
            line_surface,
            (255, 255, 255, 200),
            local_center,
            local_center + power_offset,
            width=2,
        )
        self.power_line = GameObject(
            id="power_line",
            type="line",
            surface=line_surface,
            pos=(center.x - max_length, center.y - max_length),
        )

    def set_release_position(self, mouse_drag_end_pos):
        """
        Set the power, angle, velocities once a swing has been taken.
        """
        self.shots_taken += 1
        max_radius = self.radius * (self.radius_factor / 2)
        center = Vector2(self.rect.center)
        drag_vector = Vector2(mouse_drag_end_pos) - center
        if drag_vector.length() > max_radius:
            drag_vector.scale_to_length(max_radius)

        self.power = drag_vector.length()
        self.angle = 180 - drag_vector.as_polar()[1]

        self.release_position = center + drag_vector
        self.x_velocity = (
            self.rect.centerx - self.release_position.x
        ) / self.radius_factor
        self.y_velocity = (
            self.rect.centery - self.release_position.y
        ) / self.radius_factor
        self.interactable = False

        self.path.append(mouse_drag_end_pos)

    def check_collision(self):
        """
        Check if golf ball is colliding on any obstacles in the way.
        """
        self.surface_type = "grass"

        for snd in self.sand:
            if collide_rect(self, snd):
                self.surface_type = "sand"
                break
        
        for ice in self.ice:
            if collide_rect(self, ice):
                self.surface_type = "ice"
                break

        for obs in self.obstacles:
            if collide_rect(self, obs):
                # TODO: Change this so that it can support non-square collisions
                if abs(self.rect.centerx - obs.rect.centerx) > abs(
                    self.rect.centery - obs.rect.centery
                ):
                    self.x_velocity *= -1
                else:
                    self.y_velocity *= -1
                break

        if self.x - self.radius / 2 < 0 or self.x + self.radius / 2 > 400:
            self.x_velocity *= -1
        if self.y - self.radius / 2 < 0 or self.y + self.radius / 2 > 600:
            self.y_velocity *= -1

    def move(self):
        """
        Move the ball in the direction with given velocity. Reduce velocity each loop
        to account for friction. If ball is moving below threshold velocity, make it stop completely.
        """
        self.x += self.x_velocity
        self.y += self.y_velocity

        self.rect.center = (self.x, self.y)

        self.total_friction = self.base_friction ** self.surface_strength[self.surface_type]
        self.x_velocity *= self.total_friction
        self.y_velocity *= self.total_friction

        if abs(self.x_velocity) < 0.05:
            self.x_velocity = 0
        if abs(self.y_velocity) < 0.05:
            self.y_velocity = 0

        if self.x_velocity == 0 and self.y_velocity == 0:
            self.interactable = True

    def check_win_condition(self):
        """
        See if golf ball is in the fairway and under a threshold velocity to set win condition.
        """
        pin_vector = Vector2(self.pin) - Vector2(self.rect.center)
        if pin_vector.length() < (self.radius * 1.5):
            if abs(self.x_velocity) < 1 and abs(self.y_velocity) < 1:
                self.dropping_into_hole = True
            else:
                if not self.overshot:
                    self.overshot = True

    def loop(self):
        """
        Runs game loop for this golf ball.
        It checks for overshoots, collisions, moves the ball and checks win condition.
        """
        if self.interactable and self.overshot:
            self.overshoots += 1
            self.overshot = False

        if not self.interactable and not self.dropping_into_hole:
            self.check_collision()
            self.move()
            self.check_win_condition()

        if self.dropping_into_hole:
            if self.image.get_alpha() <= 0.001:
                self.image.set_alpha(0)
                self.in_hole = True
                self.dropping_into_hole = False
            else:
                self.image.set_alpha(self.image.get_alpha() * 0.7)

    def draw(self, win):
        """
        Draw the game objects on scene.
        """
        win.blit(self.image, self.rect.topleft)

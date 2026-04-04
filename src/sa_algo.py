import random
import math
from golfball import GolfBall

NUM_CANDIDATES = 12
INITIAL_TEMPERATURE = 100.0
COOLING_RATE = 0.97
MIN_TEMPERATURE = 0.1
MAX_ITERATIONS = 20


class SimulatedAnnealer:
    """
    Simulated Annealing class which holds the algorithm, heuristics, 
    and the running functionality which attaches to the game loop.
    """

    def __init__(self, hole_position):
        self.hole_position = hole_position

        self.initial_temperature = INITIAL_TEMPERATURE
        self.temperature = INITIAL_TEMPERATURE
        self.iteration = 0
        self.max_iterations = MAX_ITERATIONS
        self.cooling_schedule = "None"

        self.current_golf_ball = None
        self.least_energy_ball = None
        self.energy = None
        self.num_shots = 0

        self.surface_strength = {"grass": 1, "sand": 3, "ice": 0.5}

        self.w_distance = 1.0
        self.w_shots = 5.0
        self.w_overshot = 50.0

        self.candidates = []
        self.hole_completed = False
        self.final_ball = None

        self.ready = True
        self.step_count = 0
        self.switch_step = {0: self.step0, 1: self.step1, 2: self.step2, 3: self.step3}

    def initialize(self, hole_data, obstacles, sand, ice):
        """
        Obtains the environment data to initialize for the current hole.
        """

        start_position = hole_data["ball_pos"]
        radius = hole_data["ball_radius"]
        self.obstacles = obstacles
        self.sand = sand
        self.ice = ice

        initial_energy = self.compute_energy(
            position=start_position, shots_taken=0, n_overshots=0
        )

        self.energy = initial_energy
        self.current_golf_ball = GolfBall(start_position[0], start_position[1], radius)
        self.current_golf_ball.set_environment(self.hole_position, obstacles, sand, ice)
        self.current_golf_ball.surface_strength = self.surface_strength
        self.least_energy_ball = self.current_golf_ball

    def generate_candidate_shots(self, center_pos, radius, max_radius):
        """
        Generates next neighbors for current golf ball by choosing random angle and power values.
        """

        self.num_shots += 1
        self.candidates = []

        for _ in range(NUM_CANDIDATES):
            angle = random.uniform(0, 2 * math.pi)
            power = random.uniform(0, max_radius)

            dx = math.cos(angle) * power
            dy = math.sin(angle) * power

            release_pos = (center_pos[0] + dx, center_pos[1] + dy)
            cand = GolfBall(center_pos[0], center_pos[1], radius)
            cand.set_environment(self.hole_position, self.obstacles, self.sand, self.ice)
            cand.path = self.current_golf_ball.path[:]
            cand.shots_taken = self.num_shots
            cand.surface_strength = self.surface_strength
            cand.set_release_position(release_pos)
            self.candidates.append(cand)

    def compute_energy(self, position, shots_taken, n_overshots):
        """
        Energy function that calculates the energy of a given candidate golf ball
        by using weights and metrics.
        """
        x, y = position
        hx, hy = self.hole_position

        distance = math.dist((x, y), (hx, hy))

        energy = (
            self.w_distance * distance
            + self.w_shots * shots_taken
            + self.w_overshot * n_overshots
        )

        return energy

    def choose_candidate(self, candidate):
        """
        From the possible candidates, choose one for the next step.
        Then update the current golf ball to be this chosen candidate.
        """

        self.current_golf_ball = candidate
        pos = (candidate.x, candidate.y)
        shots = candidate.shots_taken
        overshots = candidate.overshoots
        self.energy = self.compute_energy(pos, shots, overshots)

    def step(self):
        """
        Main step function of the SA algorithm which is called every game loop.
        Depending on the current step, calls the corresponding function to run that step.
        """
        
        self.switch_step[self.step_count]()
        if self.hole_completed:
            print(
                f"Found winning golf ball {self.final_ball} with {self.final_ball.shots_taken - 1} shots."
            )
            return
        if self.ready:
            self.step_count += 1
            self.step_count = self.step_count % len(self.switch_step)

    def step0(self):
        """
        Get current golf ball information and generate next neighbors.
        """

        center_pos, radius, max_radius = self.current_golf_ball.get_info()
        self.generate_candidate_shots(center_pos, radius, max_radius)

    def step1(self):
        """
        For each candidate, run a simulation step and compute energy.
        Set ghost color and wait till all golf balls have come to a stop.
        """

        self.ready = True
        least_energy = self.energy
        self.least_energy_ball = self.current_golf_ball

        for golf_ball in self.candidates:
            golf_ball.loop()

            if golf_ball.dropping_into_hole:
                self.hole_completed = True
                self.final_ball = golf_ball
                return

            golf_ball.energy = self.compute_energy(
                (golf_ball.x, golf_ball.y),
                golf_ball.shots_taken,
                golf_ball.overshoots,
            )

            if golf_ball.energy <= least_energy:
                least_energy = golf_ball.energy
                self.least_energy_ball = golf_ball

            if golf_ball.energy <= self.energy:
                golf_ball.set_ghost_color((255, 255, 0))
            else:
                golf_ball.set_ghost_color((255, 0, 0))

            if not golf_ball.interactable:
                self.ready = False

        self.least_energy_ball.set_ghost_color((0, 255, 0))
        self.current_golf_ball.set_ghost_color((0, 0, 255))

    def step2(self):
        """
        Find the better candidates and choose one at random.
        If no best candidates, then choose one based on acceptance probability.
        """

        better = [g for g in self.candidates if g.energy < self.energy]
        if better:
            self.choose_candidate(random.choice(better))
            return

        while self.candidates:
            chosen = random.choice(self.candidates)
            delta = chosen.energy - self.energy

            acceptance_prob = math.exp(-delta / self.temperature)

            if random.random() < acceptance_prob:
                self.choose_candidate(chosen)
                return

            self.candidates.remove(chosen)

    def step3(self):
        """
        Update temperature and iteration count.
        """

        #TODO: Temperature cooling needs to be changed to a different type
        self.temperature *= COOLING_RATE
        self.iteration += 1

    def draw(self, win):
        for golf_ball in self.candidates:
            golf_ball.draw(win)
            if golf_ball.halo:
                golf_ball.halo.draw(win)

        self.current_golf_ball.draw(win)
        if self.current_golf_ball.halo:
            self.current_golf_ball.halo.draw(win)

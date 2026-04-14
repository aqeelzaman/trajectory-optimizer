# Trajectory Optimizer: AI-Powered Mini Golf

**Hot Takes, Cold Putts** is a Python-based mini golf game that leverages **Simulated Annealing**, a sophisticated local search algorithm, to intelligently compute optimal golf shot trajectories for custom levels. This project combines game design with artificial intelligence to demonstrate how optimization algorithms can solve complex real-world problems. The name of the game is a pun based on the cooling schedule of a Simulated Annealing algorithm (Hot to Cold), and golf terms.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How to Play](#how-to-play)
- [Navigation Guide](#navigation-guide)
- [Game Mechanics](#game-mechanics)
- [Simulated Annealing Algorithm](#simulated-annealing-algorithm)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [Controls & UI](#controls--ui)
- [Course Editor](#course-editor)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

---

## Overview

**Trajectory Optimizer** is an interactive mini golf simulator that demonstrates the power of optimization algorithms in gaming. Rather than relying on predefined pathfinding or brute-force solutions, the game employs **Simulated Annealing (SA)** to intelligently explore the space of possible shots and find near-optimal golf trajectories.

The game models each golf hole as a continuous optimization problem where the AI agent must discover shots that:
- Minimize the distance from the ball to the hole
- Use the fewest number of shots possible
- Avoid overshooting the hole
- Account for different surface types (grass, sand, ice) with varying friction

This approach showcases how nature-inspired algorithms can tackle complex spatial reasoning tasks in interactive environments.

---

## Features

✨ **AI-Powered Shot Optimization**: Simulated Annealing algorithm automatically computes shot angles and power levels to reach the hole efficiently

🎮 **Interactive Gameplay**: Play mini golf levels manually or watch the AI demonstrate optimal strategies

🗺️ **Multiple Courses**: Navigate through custom-designed golf courses with varying difficulty levels

🎨 **Diverse Environments**: Experience different surface types including grass, sand, and ice—each affecting ball movement

📊 **Real-time Visualization**: Watch candidate shots displayed as ghost balls to understand how the algorithm explores possibilities

⚙️ **Simulation Mode**: Let the AI autonomously solve levels without manual intervention

🛠️ **Custom Level Editor**: Design your own courses with obstacles, sand traps, and ice patches

🎓 **Educational**: Learn how optimization algorithms work through interactive visualization

---

## How to Play

### Main Menu
When you launch the game, you'll be presented with the main menu offering several options:

1. **Play**: Select a course and start playing manually or switch to simulation mode
2. **Tutorial**: Learn the basics and controls
3. **Exit**: Close the game

### Gameplay Basics

#### Manual Mode
- **Aim**: Hold and move your cursor to set the shot angle
- **Power**: Adjust the power (0-100) to control distance
- **Shoot**: Release to take your shot
- **Goal**: Get the ball into the hole in as few shots as possible

#### Simulation Mode (AI)
- **Watch**: The algorithm automatically computes and executes optimal shots
- **Observe**: Ghost balls show candidate trajectories being evaluated
- **Learn**: See how Simulated Annealing explores the solution space in real-time

### Scoring
- **Current Score**: Number of shots taken on the current hole
- **Best Score**: Your best performance on this hole
- **Best Bot Score**: The AI's best solution for this hole

---

## Navigation Guide

### Main Menu Navigation
- Use **mouse clicks** to select menu options
- Hover over buttons to highlight them

### Course Selection
- Browse available courses
- Click a course to load it

### In-Game Navigation
- **To the next hole**: Click the "Next Hole" button after completing a hole
- **Back to course select**: Click the "Back" button
- **To the main menu**: Press the back button from course selection
- **In-game interactions**: Use the UI bar at the top for hole information and navigation buttons

---

## Game Mechanics

### Ball Physics
- The golf ball has realistic physics including:
  - **Friction**: Slows the ball based on surface type
  - **Momentum**: Ball continues moving until friction brings it to rest
  - **Collision**: Ball bounces off obstacles appropriately
  - **Surface Interaction**: Different materials (grass, sand, ice) affect ball speed differently

### Surface Types

| Surface | Effect | Example Use |
|---------|--------|---|
| **Grass** | Standard friction (1.0x) | Default playing surface |
| **Sand** | High friction (3.0x) | Slower ball movement, hazard areas |
| **Ice** | Low friction (0.5x) | Slippery surfaces, speed zones |

### Obstacles
- **Static Walls**: Fixed barriers that block ball movement
- **Layout**: Hole positions vary per level to create unique challenges

### Hole Completion
- Ball must land within the hole radius
- Multiple shots allowed (like real golf)
- Score is the total number of shots taken

---

## Simulated Annealing Algorithm

### What is Simulated Annealing?

Simulated Annealing (SA) is a probabilistic optimization algorithm inspired by the annealing process in metallurgy. Just as metals are heated and slowly cooled to reach lower energy states and create stronger structures, SA gradually reduces its "temperature" parameter to escape local optima and converge toward better solutions.

### Algorithm Overview

```
1. Initialize with a random solution (shot angle and power)
2. Compute its "energy" (cost function measuring solution quality)
3. Generate neighboring solutions (slightly different shots)
4. Probabilistically accept moves based on:
   - Temperature (higher temp = more exploration)
   - Energy difference (better solutions always accepted)
5. Cool down over time (reduce temperature)
6. Repeat until convergence or max iterations reached
```

### Application to Mini Golf

In our mini golf game, Simulated Annealing solves the **Shot Optimization Problem**:

**Input**: Current ball position, hole location, obstacles, surface types

**Output**: Optimal shot angle and power to move the ball closer to the hole

#### Energy Function (Cost Function)

The algorithm minimizes a weighted combination of three factors:

$$ \text{Energy} = w_d \cdot d + w_s \cdot s + w_o \cdot o $$

Where:
- **$d$** = Distance from ball to hole (primary goal)
- **$s$** = Number of shots taken (fewer is better)
- **$o$** = Number of overshoots (penalty for going past the hole)
- **$w_d$, $w_s$, $w_o$** = Configurable weights that prioritize different objectives

**Default Weights**:
- Distance weight: 1.0
- Shots weight: 5.0 (prioritize efficiency)
- Overshoot weight: 50.0 (strongly penalize bad shots)

#### Algorithm Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Initial Temperature | 100.0 | Controls initial exploration range |
| Cooling Rate | 0.97 | How quickly temperature decreases (3% per iteration) |
| Minimum Temperature | 0.1 | Algorithm stops when temperature drops below this |
| Max Iterations | 20 | Maximum shots the algorithm will consider per hole |
| Candidate Shots | 12 | Number of neighbor solutions generated each step |

#### Why Simulated Annealing for Golf?

1. **Continuous Problem Space**: Golf shots exist in a continuous 2D space (angle, power), not discrete options
2. **Multiple Objectives**: Must balance distance, shot efficiency, and overshooting—goals may conflict
3. **Local Optima**: Simple greedy approaches get stuck; SA explores widely before converging
4. **Real-time Performance**: SA finds good solutions quickly, enabling interactive gameplay
5. **Transparency**: Ghost balls show the exploration process, making the algorithm visible

#### How the Algorithm Runs in the Game

The SA algorithm integrates seamlessly with the game loop:

1. **Step 0 - Generate Candidates**: Create 12 random neighboring shots from the current ball position
2. **Step 1 - Simulate**: Run physics simulation for each candidate shot; compute their energies
3. **Step 2 - Evaluate & Accept**: 
   - Find the best candidate (lowest energy)
   - Probabilistically accept moves based on Metropolis criterion: 
   $$P(\text{accept}) = \begin{cases} 1 & \text{if } \Delta E \leq 0 \\ e^{-\Delta E / T} & \text{otherwise} \end{cases}$$
   - Higher temperature allows acceptance of worse solutions (exploration)
4. **Step 3 - Cool Down**: Reduce temperature; repeat until converged

**Visual Feedback**:
- Ghost balls appear for each candidate being evaluated
- Colors indicate quality: greener = better energy, redder = worse energy
- Watch the algorithm narrow in on the best shot over iterations

---

## Installation & Setup

### Prerequisites

- **Python 3.8+**
- **Pygame** (for graphics and event handling)
- **pip** (Python package manager)

### Installation Steps

1. **Clone or download the project**:
   ```bash
   git clone <repository-url>
   cd trajectory-optimizer
   ```

2. **Install dependencies**:
   ```bash
   pip install pygame
   ```

3. **Run the game**:
   ```bash
   python src/main.py
   ```

### Troubleshooting Installation

- **Pygame not found**: Make sure Python is in your PATH. Try `pip3 install pygame`
- **Game won't start**: Verify Python 3.8+ is installed with `python --version`
- **Graphics issues**: Update your GPU drivers

---

## Project Structure

```
trajectory-optimizer/
├── README.md                    # This file
├── src/                         # Main source code
│   ├── main.py                  # Entry point; initializes the game
│   ├── abstract_scene.py        # Base class for all game scenes
│   ├── main_menu_scene.py       # Main menu screen
│   ├── course_selection_scene.py # Course selection screen
│   ├── tutorial_scene.py        # Tutorial/help screen
│   ├── game_scene.py            # Core gameplay scene
│   ├── golfball.py              # Golf ball physics and movement
│   ├── objects.py               # Game objects (obstacles, holes, etc.)
│   ├── sa_algo.py               # Simulated Annealing algorithm implementation
│   └── utils.py                 # Utility functions
├── courses/                     # Course data files
│   ├── hole_template.json       # Template for creating new holes
│   ├── course1/                 # First course
│   │   ├── hole1.json
│   │   ├── hole2.json
│   │   └── hole3.json
│   └── course2/                 # Second course
│       ├── hole1.json
│       └── hole2.json
└── assets/                      # Game assets (graphics)
```

### Key Files

- **sa_algo.py**: Contains the `SimulatedAnnealer` class and algorithm logic
- **golfball.py**: Implements ball physics and trajectory simulation
- **game_scene.py**: Main gameplay loop integrating SA with game rendering
- **main.py**: Scene manager that orchestrates all game screens

---

## Controls & UI

### Game Controls

| Action | Control |
|--------|---------|
| Move cursor (aim) | Mouse movement |
| Adjust power | Mouse click and drag |
| Take shot | Click release |
| Return to menu | Back button |
| Simulation mode | Available from course selection |

### UI Components

- **Top Bar**: Displays hole number, current score, best score, bot score
- **Distance Display**: Current distance to the hole
- **Surface Indicator**: Shows the surface type under the ball
- **Navigation Buttons**: "Next Hole", "Back", "Reset", "Simulate"

---

## Course Editor

### Creating Custom Courses

Courses are defined in JSON format. Use the [hole_template.json](/courses/hole_template.json) as a starting point.

### Hole Template Structure

```json
{
  "hole_id": "hole_id",
  "ball_pos": [x, y],
  "ball_radius": r,
  "pin_pos": [x, y],
  "obstacles": [[x0, y0, x1, y1]],
  "sand": [[x0, y0, x1, y1]],
  "ice": [[x0, y0, x1, y1]],
  "best_score": 100,
  "best_bot_score": 100,
  "best_bot_path": [],
  "best_bot_params": []
}
```

### Adding a New Course

1. Create a new folder in `/courses/` (e.g., `course{N}/`)
2. Add JSON files for each hole (hole1.json, hole2.json, etc.)
3. The course will automatically appear in the course selection menu

---

## Advanced Features

### Simulation Mode

Run the AI solver on a hole without manual input:
1. Select a hole
2. Click "Simulate" button
3. Watch the algorithm solve the hole automatically
4. AI score is saved and compared to your best

### Algorithm Parameter Tuning

Advanced users can modify SA parameters in [sa_algo.py](src/sa_algo.py):

```python
NUM_CANDIDATES = 12              # Number of neighbors per iteration
INITIAL_TEMPERATURE = 100.0      # Starting temperature
COOLING_RATE = 0.97              # Multiplicative cooling factor
MIN_TEMPERATURE = 0.1            # Convergence threshold
MAX_ITERATIONS = 20              # Max shots to consider
```

### Weight Adjustments

Customize what the algorithm prioritizes by modifying weights in `SimulatedAnnealer`:

```python
self.w_distance = 1.0            # Distance importance
self.w_shots = 5.0               # Shot efficiency importance
self.w_overshot = 50.0           # Overshoot penalty
```

---

## Troubleshooting

### Game Won't Start

**Problem**: `ModuleNotFoundError: No module named 'pygame'`

**Solution**: 
```bash
pip install pygame
```

### AI Solver Takes Too Long

**Problem**: Algorithm doesn't finish in reasonable time

**Solution**: Reduce `MAX_ITERATIONS` or `NUM_CANDIDATES` in [sa_algo.py](src/sa_algo.py)

### Ball Behavior Seems Wrong

**Problem**: Ball moves unexpectedly or feels unresponsive

**Solution**: 
- Check surface parameters in [sa_algo.py](src/sa_algo.py)
- Verify hole design in course JSON (ensure hole_pos is reachable)
- Try resetting the hole

### Holes Aren't Loading

**Problem**: Course selection empty or holes missing

**Solution**:
- Ensure JSON files are in correct folder structure: `courses/courseN/holeN.json`
- Validate JSON syntax (no trailing commas, all quotes matched)
- Restart the game

---

## Future Improvements

Potential enhancements for future versions:

- 🎬 **Replay System**: Save and replay manual shot sequences
- 🏆 **Leaderboards**: Local high score tracking per user
- 🎯 **Level Difficulty Scaling**: Automatically adjust course complexity
- 🤖 **Algorithm Variants**: Compare SA with Genetic Algorithms, Particle Swarm
- 🌐 **Multiplayer**: Compete against players or AI in real-time
- 🎨 **Graphics Enhancement**: Improved visuals and 3D perspectives

---

## Questions & Feedback

For questions about the Simulated Annealing algorithm or how it's applied to the mini golf game, refer to the [Simulated Annealing Algorithm](#simulated-annealing-algorithm) section above.

Enjoy exploring optimization through gameplay! ⛳🤖 

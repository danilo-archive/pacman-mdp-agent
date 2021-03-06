# Pac-Man MDP Agent
This work shows the implementation and statistical analysis of an AI agent capable of winning the arcade game of Pac-Man using an MDP solver that follows a policy based on Value Iteration.

A full report can be found [here](docs/report.pdf).

The game itself is also modelled as a stochastic variation of the Pac-Man game, meaning that some transitionsare probabilistic. In the context of the Pac-Man game, the agent has an 80% probability of going in the direction specified by the policy, and a 10% change of going to either direction perpendicular to that.If the agent hits a wall, it will not move.

 The sole file here is mean to be used with Berkley's [Pac-Man Projects
](http://ai.berkeley.edu/project_overview.html). It therefore only contains the logic associated with a MDP agent trying to win the Pac-Man game.


## Example Game

<div align="center">
<img with="60%" src="docs/game.gif">
</div>

## Environment

The code is meant to be run on [Python 2.7](https://www.python.org/download/releases/2.7/)
## Instructions

Run the agent on a small grid:

```zsh
python pacman.py -p MDPAgent -l smallGrid
```

### Additional tags

#### Game tags
- `-q` to run without UI
- `-l` to specify the layout (the code was written for `-l smallGrid` and `-l mediumClassic`)
- `-n` to specify how many times to run the game (e.g.: `-n 25`)

#### Custom Constant tags
These tags modify the default value of the constants used to generate the utiliy values
| Argument | Constant              | Default |
|----------|-----------------------|---------|
| --ELR    | EMPTY_LOCATION_REWARD | -0.04   |
| --FR     | FOOD_REWARD           | 10      |
| --CR     | CAPSULE_REWARD        | 100     |
| --GR     | GHOST_REWARD          | -1000   |
| --GA     | GAMMA                 | 0.9     |
| --DZR    | DANGER_ZONE_RATIO     | 6       |
| --DG     | DANGER                | 500     |
| --IT     | ITERATIONS            | 10      |

### Example with custom tags

Running the MDPAgent 23 times without the UI with custom values for GHOST_REWARD and FOOD_REWARD on mediumClassic:

```zsh
python pacman.py -l mediumClassic -p MDPAgent -n 25 -q --GR -123 --FR 34
```

# Pac-Man MDP Agent
A pacman agent using observable Markov decision process. The sole file here is mean to be used with Berkley's [Pac-Man Projects
](http://ai.berkeley.edu/project_overview.html). It therefore only contains the logic associated with a MDP agent trying to win the Pac-Man game.

The full report can be found [here](docs/report.pdf).

## Environment

The code is meant to be run on [Python 2.7](https://www.python.org/download/releases/2.7/)

## Instructions

Run the agent on a small grid:

```zsh
python pacman.py -p MDPAgent
```

### Additional tags

- `-q` to run without UI
- `-l` to specify the layout (the code was written for `-l smallGrid` and `-l mediumClassic`)
- `-n` to specify how many times to run the game (e.g.: `-n 25`)


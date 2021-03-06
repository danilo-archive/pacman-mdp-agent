import api
import util
from game import Agent
from pacman import Directions

EMPTY_LOCATION_REWARD = -0.04
FOOD_REWARD = 10
CAPSULE_REWARD = 100
GHOST_REWARD = -1000

GAMMA = 0.9
DANGER_ZONE_RATIO = 6
DANGER = 500
ITERATIONS = 10


class MDPAgent(Agent):
    def __init__(self):
        self.map = self.walls = self.corners = None

    def registerInitialState(self, state):
        self.walls = api.walls(state)
        self.corners = api.corners(state)
        self.map = initial_map(self.corners, self.walls)

    def getAction(self, state):
        if self.map is None:
            self.registerInitialState(state)

        self.map = value_iteration(self.map, state)
        legal = api.legalActions(state)

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        pacman = api.whereAmI(state)
        [scores, actions] = get_action_scores(legal, self.map, pacman[0], pacman[1])
        max_score_index = scores.index(max(scores))
        choice = actions[max_score_index]
        return api.makeMove(choice, legal)


def get_action_scores(legal, pacman_map, x, y):
    """
    Get an array containing two arrays: scores and actions.
    Scores contains the bellmann scores corresponding to each action.
    Both arrays use the same indexing order (i.e.: the first element in scores
    contains the score for the first element in actions)
    @param legal: the legal moves
    @type legal: list
    @param pacman_map: the map containing the bellmann scores (doubly dimensional array [y][x])
    @type pacman_map: list
    @param x: the x position of pacman
    @type x : int
    @param y: the y position of pacman
    @type y : int
    @return: The list containing scores and actions results [scores, actions]
    @rtype: list
    """
    scores = []
    actions = []
    for action in legal:
        value = None
        if action is Directions.NORTH:
            value = pacman_map[y + 1][x]
        elif action is Directions.SOUTH:
            value = pacman_map[y - 1][x]
        elif action is Directions.EAST:
            value = pacman_map[y][x + 1]
        elif action is Directions.WEST:
            value = pacman_map[y][x - 1]
        if value is not None:
            scores.append(value)
            actions.append(action)

    return [scores, actions]


def value_iteration(m, state):
    """
    Apply value iteration to the given map m. The number of iterations is set to the global
    constant ITERATIONS
    @param m: the map to apply value iteration to
    @type m: list
    @param state: the state of the game
    @type state: state
    @return: the map with the new values
    @rtype: list
    """
    iterations = ITERATIONS
    corners = api.corners(state)
    food = api.food(state)
    walls = api.walls(state)
    ghosts = api.ghosts(state)
    capsules = api.capsules(state)

    r_map = reward_map(corners, food, walls, ghosts, capsules)

    h = corners[1][0] + 1
    w = corners[2][1] + 1

    pacman = api.whereAmI(state)
    pacman = (pacman[1], pacman[0])
    update_reward_map(r_map, pacman, ghosts, h, w)

    while iterations > 0:
        new_m = initial_map(corners, walls)

        for i in range(w):
            for j in range(h):
                r = r_map[i][j]
                new_m[i][j] = bellmann(m, (i, j), w, h, r)
        m = new_m
        iterations -= 1

    return m


def bellmann(m, cell, w, h, r):
    """
    Get the updated value of a cell using the Bellman equation. The probabilities are hardcoded to be
    80% for forward movement and 10% for other lateral movements.
    @param m: the map containing the previous values for other cells
    @type m: list
    @param cell: the cell to retrieve the new value for
    @type cell: Tuple[int, int]
    @param w: the width of the map
    @type w: int
    @param h: the height of the map
    @type h: int
    @param r: the reward value of the given cell as described in the reward function
    @type r: int
    @return: the new value for the cell using the Bellmann equation
    @rtype: float
    """
    x = cell[0]
    y = cell[1]
    # reward function
    if r is None:  # wall
        return None
    east = west = north = south = None
    current = m[x][y]
    # can go
    if x < w - 1:
        east = m[x + 1][y]
    if x > 0:
        west = m[x - 1][y]
    if y < h - 1:
        north = m[x][y + 1]
    if y > 0:
        south = m[x][y - 1]

    if east is None:
        east = -1
    if west is None:
        west = -1
    if north is None:
        north = -1
    if south is None:
        south = -1

    # region probabilities
    if north is not None:
        north_val = north * 0.8 + (east + west) * 0.1
    else:
        north_val = current
    if south is not None:
        south_val = south * 0.8 + (east + west) * 0.1
    else:
        south_val = current
    if east is not None:
        east_val = east * 0.8 + (north + south) * 0.1
    else:
        east_val = current
    if west is not None:
        west_val = west * 0.8 + (north + south) * 0.1
    else:
        west_val = current
    # endregion
    max_val = max([north_val, south_val, east_val, west_val])
    return float(float(r) + float(GAMMA) * float(max_val))


def update_reward_map(r_map, pacman, ghosts, h, w):
    """
    Update the reward map by applying mali to the cells that are close to pacman. The closest said
    cell is to a ghost, the greater the malus is that is applied to the reward value of the cell.
    Only a certain number of cells is taken into consideration. Specifically the same amount as the value
    of the global constant DANGER_ZONE
    @param r_map: the reward map without any malus
    @type r_map: list
    @param pacman: pacman's position
    @type pacman: Tuple[int, int]
    @param ghosts: a list of ghost positions
    @type ghosts: list
    @param h: the height of the map
    @type h: int
    @param w: the width of the map
    @type w: int
    """
    for n in get_neighbours(pacman, h, w):
        if n is not None and r_map[n[0]][n[1]] is not None:
            [distance, cells] = distance_to_closest_ghost(n, ghosts, h, w)
            if distance > 0:
                # the further away we are from pacman, the less impactful the malus is
                r_map[n[0]][n[1]] -= (DANGER / distance)
                for cell in cells:
                    if r_map[cell[0]][cell[1]] is not None:
                        r_map[cell[0]][cell[1]] -= (DANGER / distance)


def distance_to_closest_ghost(cell, ghosts, h, w):
    """
    Calculate the distance to the closest ghost as the value of cells explored before reaching the same position
    as the closest ghost, using a frontier traversing algorithm.
    @param cell: the cell from which to calculate the distance
    @type cell: list
    @param ghosts: the list containing the positions of ghosts
    @type ghosts: list
    @param h: the height of the map
    @type h: int
    @param w: the width of the map
    @type w: w
    @return: the distance to the ghost
    @rtype: int
    """
    frontier = util.Queue()
    frontier.push(cell)
    came_from = dict()
    came_from[cell] = None
    distance = 0
    found = False
    cells = []
    while not frontier.isEmpty() and distance < (h*w / DANGER_ZONE_RATIO):
        current = frontier.pop()
        cells.append(current)
        distance += 1
        if (current[1], current[0]) in ghosts:
            found = True
            break

        for neighbour in get_neighbours(current, h, w):
            if neighbour is not None and neighbour not in came_from:
                frontier.push(neighbour)
                came_from[neighbour] = current
    if found:
        return [distance, cells]
    else:
        return [0, cells]


def get_neighbours(cell, h, w):
    """
    Get the adjacent cells
    @param cell: the cell for which to retrieve the neighbours
    @type cell: list
    @param h: the height of the map
    @type h: int
    @param w: the width of the map
    @type w: int
    @return: list of the neighbours' coordinates
    @rtype: list
    """
    x = cell[0]
    y = cell[1]
    north = south = east = west = None
    if y + 1 < h:
        north = (x, y + 1)
    if y - 1 > 0:
        south = (x, y - 1)
    if x + 1 < w:
        east = (x + 1, y)
    if x - 1 > 0:
        west = (x - 1, y)

    return [north, south, east, west]


def reward_map(corners, food, walls, ghosts, capsules):
    """
    Get a double dimensional list containing values corresponding to the reward function
    @param corners: a list of the corners of the map
    @type corners: list
    @param food: a list of the food of the map
    @type food: list
    @param walls: a list of the walls of the map
    @type walls: list
    @param ghosts: a list of the ghosts of the map
    @type ghosts: list
    @param capsules: a list of the capsules of the map
    @type capsules: list
    @return: the reward map
    @rtype: list
    """
    m = initial_map(corners, walls)
    h = corners[1][0] + 1
    w = corners[2][1] + 1

    for i in range(w):
        for j in range(h):
            cell = (j, i)
            if cell in food:
                m[i][j] = FOOD_REWARD
            elif cell in walls:
                m[i][j] = None
            elif cell in ghosts:
                m[i][j] = GHOST_REWARD
            elif cell in capsules:
                m[i][j] = CAPSULE_REWARD
            elif cell in [(7, 6), (10, 6)]:
                m[i][j] = -100
            else:
                m[i][j] = EMPTY_LOCATION_REWARD
    return m


def initial_map(corners, walls):
    """
    Get an empty copy of the map. All values are either None if there is a wall, or the value of the
    global constant EMPTY_LOCATION_REWARD otherwise.
    @param corners: the corners of the map
    @type corners: list
    @param walls: the walls of the map
    @type walls: list
    @return: a virtually empty copy of the map
    @rtype: list
    """
    h = corners[1][0] + 1
    w = corners[2][1] + 1
    pacman_map = []
    for i in range(w):
        pacman_map.append([])
        for j in range(h):
            pacman_map[i].append("  ")

    for i in range(w):
        for j in range(h):
            if (j, i) in walls:
                pacman_map[i][j] = None
            else:
                pacman_map[i][j] = EMPTY_LOCATION_REWARD
    return pacman_map

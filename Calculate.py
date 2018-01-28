def policyEvaluation(Gridworld):
    '''
    calculates the updated value function:
     - iterates over grid
     - for each field (state) calculates the new value
     - by adding the reward to the discounted sum of possible next states
    '''
    # fill array with non-values for all fields we need to start
    copiedValues = [[None for x in range(len(Gridworld.grid[0]))] for y in range(len(Gridworld.grid))]

    # iterate over grid
    for i in range(len(Gridworld.grid)):
        for j in range(len(Gridworld.grid[0])):
            # only if state is Free (not obstacle ...)
            if (Gridworld.grid[i][j] == "F"):
                # use function to get weighted sum
                sum = possibleStates(Gridworld, Gridworld.policy[i][j], i, j)
                # update value function with reward and GAMMA
                copiedValues[i][j] = Gridworld.REWARD + Gridworld.GAMMA * sum
            else:
                copiedValues[i][j] = Gridworld.values[i][j]
    Gridworld.values = copiedValues


def possibleStates(Gridworld, policyValue, i, j):
    '''
    iterates over possible states that can be reached from state
    :param policyValue: what action should I take?
    :param i: index of grid
    :param j: index of grid
    :return: sum of all probabilities * expected reward for ending up in a certain state
    '''
    # calculate the action that can be done with small chance
    if (policyValue == "up"):
        clockwise_action = "right"
        counterclockwise_action = "left"
    elif (policyValue == "down"):
        clockwise_action = "left"
        counterclockwise_action = "right"
    elif (policyValue == "left"):
        clockwise_action = "up"
        counterclockwise_action = "down"
    elif (policyValue == "right"):
        clockwise_action = "down"
        counterclockwise_action = "up"

    # get the indices of the next state, if ...
    # ... action is performed correctly
    wanted_i, wanted_j = nextState(Gridworld, policyValue, i, j)

    # ... clockwise action is performed
    clockwise_i, clockwise_j = nextState(Gridworld, clockwise_action, i, j)
    # ... counterclockwise action is performed
    counterclockwise_i, counterclockwise_j = nextState(Gridworld, counterclockwise_action, i, j)
    # calculate the sum of the values with the probability to reach it
    sum = Gridworld.values[wanted_i][wanted_j] * 0.8
    sum = sum + Gridworld.values[clockwise_i][clockwise_j] * 0.1
    sum = sum + Gridworld.values[counterclockwise_i][counterclockwise_j] * 0.1

    # return the weighted sum of possible states and thei respective values
    return sum


def nextState(Gridworld, policyValue, i, j):
    '''
    Returns next state, taking into consideration invalid states.
    Invalid states are fields in which obstacles are as well as fields beyond
    the theoretical borders of our grid.
    :param policyValue: current policy value
    :param i: index i of grid
    :param j: index j of grid
    :return: new indices i and j after performing policy
    '''
    if (policyValue == "up" and i != 0):
        if (Gridworld.grid[i - 1][j] != "O"):
            i = i - 1
    elif (policyValue == "down" and i != len(Gridworld.grid) - 1):
        if (Gridworld.grid[i + 1][j] != "O"):
            i = i + 1
    elif (policyValue == "left" and j != 0):
        if (Gridworld.grid[i][j - 1] != "O"):
            j = j - 1
    elif (policyValue == "right" and j != len(Gridworld.grid[0]) - 1):
        if (Gridworld.grid[i][j + 1] != "O"):
            j = j + 1

    return i, j


def makePolicy(Gridworld):
    '''
    Updates the policy according to the greedy action.
    '''
    # go through the whole policy to update it
    for row in range(len(Gridworld.policy)):
        for col in range(len(Gridworld.policy[0])):
            # only get policy for fields which aren't an obstacle
            if(Gridworld.policy[row][col] in Gridworld.actions):
                temp = [None, None, None, None]

                for i in range(len(temp)):
                    temp[i] = possibleStates(Gridworld, Gridworld.actions[i], row, col)

                max = temp[0]
                ind = 0

                for i in range(len(temp)):
                    if max < temp[i]:
                        max = temp[i]
                        ind = i

                Gridworld.policy[row][col] = Gridworld.actions[ind]

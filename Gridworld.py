import fileinput
import sys
import random
import math
from copy import deepcopy
from array import array
import Calculations


class Gridworld:
    '''
    @Todo: jeder eigene Methode(n) optimieren
    @Todo: Policy visualization (Pfeile drucken)
    @Todo: value function visualization
    @Todo: more try/catch for input errors (Value Errors)?
    '''

    def __init__(self):
        self.actions = ["up", "down", "left", "right"]
        self.arrows = {"up": "\u2B06", "down": "\u2B07", "left": "\u2B05", "right": "\u2B95"}
        self.gamma = 1
        self.processingMode = "m"
        self.grid = ""
        self.policy = []
        self.valueFunction = []
        self.REWARD = -0.4
        self.PITFALL = -1
        self.GOAL = 1
        self.iterations = 1
        self.neighbourind = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def read(self):
        '''
        Reads a grid file from command line arguments

        :return: grid as list of lists
        each sublist is a row
        e.g. grid[0][1] accesses the second element in the first sublist aka the second element in row 0
        grid[0][1] corresponds to (1,0) in "point notation" (x,y)
        '''

        file = ""
        try:
            # access command line arguments, if not empty string
            # (sys.argv[0] is program file, sys.argv[1] ist first argument)
            if sys.argv[1]:
                file += sys.argv[1]
        except IndexError:  # sys.argv[1] unspecified means that no further argument is given
            print("Please specify a grid file")
            exit(1)  # stop execution of program

        grid = []  # empty list as grid

        try:
            # open file
            with open(file, "r") as f:
                line = f.readline()  # read first line

                # while line not empty (still new line to read)
                while line:
                    stripped_line = line.strip("\n")  # remove line break
                    splitted_line = stripped_line.split(" ")  # split line at whitespace to get elements
                    grid.append(splitted_line)  # append to grid to make list of lists
                    line = f.readline()  # read next line

        except IOError:  # catch IO error from opening file
            print("Gridfile could not be found: Please specify a valid file (with path)")
            exit(1)

        self.grid = grid


    def readUserInput(self):
        '''
        Reads in processing mode and gamma value
        '''

        # read in processing mode from user (a or m)

        processingMode = input("Please choose between manual and automated processing (a/m): ")
        while (not (processingMode is "a" or processingMode is "m")):
            processingMode = input("Please choose between manual and automated processing (a/m): ")

        # if automated processing mode is choosen, get number of evaluation steps (n)
        iterations = 1
        if (processingMode == "a"):
            iterations = int(input("Please specify a number of iterations for each evaluation phase: "))
            while (iterations <= 0):  # has to be bigger than zero
                iterations = int(input("Please specify a number of iterations for each evaluation phase: "))

        # read in gamma as float
        gamma = float(input("Please specify a gamma value between 0 and 1: "))
        while gamma > 1.0 or gamma < 0.0:
            gamma = float(input("Please specify a gamma value between 0 and 1: "))

        self.processingMode = processingMode
        self.iterations = iterations
        self.gamma = gamma

        # @TODO maybe implement goal > pitfall?
        self.REWARD = float(input("Please specify the reward (or penalty) for each step: "))
        self.GOAL = float(input("Please specify the reward of the goal state: "))
        self.PITFALL = float(input("Please specify the penalty for the pitfall state: "))

    def randomPolicyInit(self):
        '''
        Initializes random policy by assigning random value from self.actions to every state (F)
        '''
        # print(self.actions)
        i = 0
        j = 0

        self.policy = [[None for x in range(len(self.grid[0]))] for y in range(len(self.grid))]

        for i in range(len(self.grid)):
            # print("row", row)
            for j in range(len(self.grid[0])):
                # print("elem", elem)
                if (self.grid[i][j] == "F"):
                    self.policy[i][j] = random.choice(self.actions)
                elif (self.grid[i][j] == "E"):
                    self.policy[i][j] = "+"
                elif (self.grid[i][j] == "P"):
                    self.policy[i][j] = "-"
                else:
                    self.policy[i][j] = "X"
        # print("policy: ", self.policy)

    def valueFunctionInit(self):
        '''
        Initializes value function
        Empty fields are given a value of 0, pitfalls are given the punishment-value determined by the user
        and a goal state is given the reward-value determined by the user
        '''
        i = 0
        j = 0

        self.valueFunction = [[0 for x in range(len(self.grid[0]))] for y in range(len(self.grid))]

        for i in range(len(self.grid)):
            # print("row", row)
            for j in range(len(self.grid[0])):
                # print("elem", elem)
                if (self.grid[i][j] == "O"):
                    self.valueFunction[i][j] = None

        # print("valueFunction", self.valueFunction)

    def policyEvaluation(self):

        '''
        calculates the updated value function:
         - iterates over grid
         - for each field (state) calculates the new value
         - by adding the reward to the discounted sum of possible next states
        '''

        i = 0
        j = 0
        copiedValueFunction = [[None for x in range(len(self.grid[0]))] for y in range(len(self.grid))]

        # iterate over grid
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                # only if state is Free (not obstacle ...)
                if (self.grid[i][j] == "F"):
                    # use function to get weighted sum
                    sum = self.possibleStates(self.grid[i][j], self.policy[i][j], i, j)
                    # print("sum in policy iteration", sum)

                    # update value function with reward and gamma
                    copiedValueFunction[i][j] = self.REWARD + self.gamma * sum

                elif (self.grid[i][j] == "O"):
                    copiedValueFunction[i][j] = None
                elif (self.grid[i][j] == "E"):
                    copiedValueFunction[i][j] = self.GOAL
                elif (self.grid[i][j] == "P"):
                    copiedValueFunction[i][j] = self.PITFALL

        self.valueFunction = copiedValueFunction
        # print("new value function", self.valueFunction)

    def possibleStates(self, state, policyValue, i, j):
        '''
        iterates over possible states that can be reached from state
        :param state: current state
        :param policyValue: what action should I take?
        :param i: index of grid
        :param j: index of grid
        :return: sum of all probabilities * expected reward for ending up in a certain state
        '''

        # calculate the action that can be done with small chance
        clockwise_action = ""
        counterclockwise_action = ""

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
        wanted_i, wanted_j = self.nextState(state, policyValue, i, j)
        # print("wanted i", wanted_i, "wanted j", wanted_j)

        # ... clockwise action is performed
        clockwise_i, clockwise_j = self.nextState(state, clockwise_action, i, j)
        # ... counterclockwise action is performed
        counterclockwise_i, counterclockwise_j = self.nextState(state, counterclockwise_action, i, j)
        sum = 0
        # calculate the sum of the values with the probability to reach it
        # print("self.valueFunction wanted", self.valueFunction[wanted_i][wanted_j])
        sum = self.valueFunction[wanted_i][wanted_j] * 0.8
        sum = sum + self.valueFunction[clockwise_i][clockwise_j] * 0.1
        sum = sum + self.valueFunction[counterclockwise_i][counterclockwise_j] * 0.1
        # print("sum", sum)

        # return the weighted sum of possible states and thei respective values
        return sum

    def nextState(self, state, policyValue, i, j):
        '''
        :param state: current state on the grid
        :param policyValue: current policy value
        :param i: index i of grid
        :param j: index j of grid
        :return: new indices i and j after performing policy
        '''
        if (policyValue == "up" and i != 0):
            if (self.grid[i - 1][j] != "O"):
                i = i - 1
        elif (policyValue == "down" and i != len(self.grid) - 1):
            if (self.grid[i + 1][j] != "O"):
                i = i + 1
        elif (policyValue == "left" and j != 0):
            if (self.grid[i][j - 1] != "O"):
                j = j - 1
        elif (policyValue == "right" and j != len(self.grid[0]) - 1):
            if (self.grid[i][j + 1] != "O"):
                j = j + 1

        return i, j

    def makePolicy(self):
        # go through the whole policy to update it
        for row in range(len(self.policy)):
            for col in range(len(self.policy[0])):
                # only get policy for fields which aren't a obstacle
                if (self.policy[row][col] != None):

                    # array to save the values for all neighbours
                    neighbours = []

                    # loop to look through the 4-neighbourhood
                    for i in range(4):
                        # we ignore the border cases and just catch the error instead
                        try:
                            # get the index shift for the next neighbour
                            a, b = self.neighbourind[i]
                            # update the indices
                            rowind = row + a
                            colind = col + b

                            if rowind == -1:
                                raise IndexError
                            if colind == -1:
                                raise IndexError

                                # get the value of the neighbour
                            value = self.valueFunction[rowind][colind]
                            # save the value if it is not an obstacle and the action done
                            if value != None:
                                neighbours.append((value, self.actions[i]))
                        except(IndexError):
                            pass

                    # set a preliminary maximum and move
                    max = neighbours[0][0]
                    move = neighbours[0][1]

                    # go through all neigbours
                    for i in range(len(neighbours)):
                        # check if the value is greater than the current max
                        if max < neighbours[i][0]:
                            # update max and move
                            max = neighbours[i][0]
                            move = neighbours[i][1]

                    # save the greedy action in the policy
                    self.policy[row][col] = move

        self.printPolicy()

    def runPolicyIteration(self):
        '''
        runs policy iteration in one of two modes
        a: automatic mode
            - runs evaluation phase for self.iterations-times
            - stops when there is no change in policy anymore
        m: manual mode
            - runs evaluation phase for a designated amount of iterations
            - user input for number of iterations for eval after each iteration
            - stops when there is no change in policy anymore
        '''

        # automatic mode
        if (self.processingMode == "a"):

            # termination condition: until policy does not change anymore
            eq = False
            while not eq:
                oldPolicy = deepcopy(self.policy)  # copy current policy
                self.runEvaluation(self.iterations)  # run evaluation
                print("values: ")
                self.printValueFunction()

                self.makePolicy()  # run iteration
                eq = self.comparePolicies(self.policy, oldPolicy)  # reassign equality "measure"

        # manual mode
        elif (self.processingMode == "m"):

            # compare two policies
            eq = False
            # as long as the new one differs from the old policy
            while not eq:
                # ask user input for iterations again
                try:
                    iterations = int(input("How many iterations should policy evaluation make? "))
                except ValueError:
                    print("Please put in a number")
                    iterations = int(input("How many iterations should policy evaluation make? "))

                while iterations <= 0:
                    print("Please put in a positive number")
                    iterations = int(input("How many iterations should policy evaluation make? "))

                oldPolicy = deepcopy(self.policy)  # copy policy again
                self.runEvaluation(iterations)  # run evaluation
                print("values: ")
                self.printValueFunction()
                self.makePolicy()  # run iteration
                eq = self.comparePolicies(self.policy, oldPolicy)  # update equality-"measure"
                # @Todo: print policy and value function

    def runEvaluation(self, iterations):
        '''
        runs policy evaluation for a designated amount of iterations
        :param iterations: how often should evaluation be repeated
        '''
        i = 0
        while (i <= iterations):
            self.policyEvaluation()
            i = i + 1

    def comparePolicies(self, policyOne, policyTwo):
        '''
        compares two policies to check if they are the same
        :param policyOne:
        :param policyTwo:
        :return: boolean equal
        '''
        equal = True
        i = 0
        j = 0
        for i in range(len(policyOne)):
            for j in range(len(policyOne[0])):
                if policyOne[i][j] != policyTwo[i][j]:
                    equal = False
        return equal

    def printPolicy(self):
        '''
        Prints policy for each field in the grid correctly formatted in rows and columns
        '''

        for i in range(len(self.policy)):
            for j in range(len(self.policy[0])):

                if (self.policy[i][j] == "up"):
                    print("\u2B06", end="  ")
                elif (self.policy[i][j] == "down"):
                    print("\u2B07", end="  ")
                elif (self.policy[i][j] == "left"):
                    print("\u2B05", end=" ")
                elif (self.policy[i][j] == "right"):
                    print("\u2B95", end=" ")
                else:
                    print(self.policy[i][j], end=" ")

            print("\n", end="")

    def printValueFunction(self):
        '''
        Prints value for each field in the grid correctly formatted in rows and columns
        '''
        for i in range(len(self.valueFunction)):
            for j in range(len(self.valueFunction[0])):
                if (self.valueFunction[i][j] == "None" or self.valueFunction[i][j] is None):
                    print("  x  ", end=" ")
                else:
                    print("{0:5}".format(math.ceil(self.valueFunction[i][j]*1000)/1000), end=" ")
            print("\n", end="")

    def printGrid(self):
        '''
        Prints grid correctly formatted in rows and columns
        :param grid: grid to be printed
        '''

        # for each row aka sublist
        for row in self.grid:
            # select every element in that sublist (row) and print it
            for elem in row:
                print(elem, end="")  # end="" to substitute the default end of print which is \n by nothing

            print("\n", end="")  # line break after each row


if __name__ == '__main__':
    test = Gridworld()
    test.read()
    test.printGrid()
    test.readUserInput()
    test.randomPolicyInit()
    test.valueFunctionInit()
    test.runPolicyIteration()

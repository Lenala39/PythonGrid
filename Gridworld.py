import fileinput
import sys
import random
from array import array
import Calculations


class Gridworld:
    '''
    @Todo: manueller/automatischer Modus: Funktion für Ausführen Eval und Iter
    @Todo: jeder eigene Methode(n) optimieren
    @Todo: Policy visualization (Pfeile drucken)
    @Todo: value function visualization
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

    def readUserInput(self):
        '''
        Reads in processing mode and gamma value
        '''

        # read in processing mode from user (a or m)
        processingMode = input("Please choose between manual and automated processing (a/m): ")
        while not processingMode == "a" or processingMode == "m":
            processingMode = input("Please choose between manual and automated processing (a/m): ")

        # read in gamma as float
        gamma = float(input("Please specify a gamma value between 0 and 1: "))
        while gamma > 1.0 or gamma < 0.0:
            gamma = float(input("Please specify a gamma value between 0 and 1: "))

        self.processingMode = processingMode
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
        print("policy: ", self.policy)

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

        print("valueFunction", self.valueFunction)

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
        print("new value function", self.valueFunction)

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
        @TODO implement 80:10:10 chances?
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
                if(self.policy[row][col] != None):
                    # array to save the values for all neighbours
                    neighbours = []

                    # if the index is not out of bounds, save the values of the neighbours
                    try:
                        value = self.valueFunction[row - 1][col]
                        if value != None:
                            neighbours.append((value, "up"))
                    except(IndexError):
                        pass

                    try:
                        value = self.valueFunction[row + 1][col]
                        if value != None:
                            neighbours.append((value, "down"))
                    except(IndexError):
                        pass

                    try:
                        value = self.valueFunction[row][col - 1]
                        if value != None:
                            neighbours.append((value, "left"))
                    except(IndexError):
                        pass

                    try:
                        value = self.valueFunction[row][col + 1]
                        if value != None:
                            neighbours.append((value, "right"))
                    except(IndexError):
                        pass

                    max = neighbours[0][0]

                    for i in range(len(neighbours)):
                        if max < neighbours[i]:
                            max = neighbours[i]
                            move = neighbours[i][1]

                    # save the greedy action in the policy
                    self.policy[row][col] = move

        print(self.policy)


def printPolicy(self):
    '''
    for row in self.grid:
        for elem in row:

            if(elem == "F"):
    '''


if __name__ == '__main__':
    test = Gridworld()
    test.read()
    test.printGrid()
    # test.readUserInput()
    test.randomPolicyInit()
    test.valueFunctionInit()
    for i in range(20):
        test.policyEvaluation()

    test.makePolicy()

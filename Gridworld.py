import fileinput
import sys
import random
from array import array
import Calculations


class Gridworld:

    def __init__(self):
        self.actions = ["up", "down", "left", "right"]
        self.arrows = {"up": "\u2B06", "down": "\u2B07", "left": "\u2B05", "right": "\u2B95"}
        self.gamma = 1
        self.processingMode = "m"
        self.grid = ""
        self.policy = []
        self.valueFunction = []

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
        i, j = 0
        for i in range(len(self.grid)):
            # print("row", row)
            for j in range(len(self.grid[0])):
                # print("elem", elem)
                if (self.grid[i][j] == "F"):
                    self.policy[i][j] == random.choice(self.actions)
        print(self.policy)


    def valueFunctionInit(self):
        '''
        Initializes value function
        Empty fields are given a value of 0, pitfalls are given the punishment-value determined by the user
        and a goal state is given the reward-value determined by the user
        '''
        i, j = 0
        for i in range(len(self.grid)):
            # print("row", row)
            for j in range(len(self.grid[0])):
                # print("elem", elem)
                if (self.grid[i][j] == "F"):
                    self.valueFunction[i][j] = 0
                elif (self.grid[i][j] == "P"):
                    self.valueFunction[i][j] = self.PITFALL
                elif (self.grid[i][j] == "E"):
                    self.valueFunction[i][j] = self.GOAL

        print(self.valueFunction)

    def policyEvaluation(self):

        '''
        calculates the updated value function:
         - iterates over grid
         - for each field (state) calculates the new value
         - by adding the reward to the discounted sum of possible next states
        '''
        i = 0
        j = 0
        # iterate over grid
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                # only if state is Free (not obstacle ...)
                if (self.grid[i][j] == "F"):
                    # use function to get weighted sum
                    sum = self.possibleStates(self.grid[i][j], self.policy[i][j], i, j)
                    print("sum", sum)

                    # update value function with reward and gamma
                    self.valueFunction[i][j] = self.REWARD + self.gamma * sum
                    print("value function", self.valueFunction)

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
            clockwise_action = "up"

        # get the indices of the next state, if ...
        # ... action is performed correctly
        wanted_i, wanted_j = self.nextState(state, policyValue, i, j)
        print("wanted i", wanted_i,"wanted j", wanted_j)
        # ... clockwise action is performed
        clockwise_i, clockwise_j = self.nextState(state, clockwise_action, i, j)
        # ... counterclockwise action is performed
        counterclockwise_i, counterclockwise_j = self.nextState(state, counterclockwise_action, i, j)

        # calculate the sum of the values with the probability to reach it
        sum = self.valueFunction[wanted_i][wanted_j] * 0.8
        print(sum)
        sum = sum + self.valueFunction[clockwise_i][clockwise_j] * 0.1
        sum = sum + self.valueFunction[counterclockwise_i][counterclockwise_j] * 0.1
        print(sum)

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
            i = i - 1
        elif (policyValue == "down" and i != len(self.grid[i])):
            i = i + 1
        elif (policyValue == "left" and j != 0):
            j = j - 1
        elif (policyValue == "right" and j != len(self.grid)):
            j = j + 1

        return i, j

    def makePolicy(self):
    # go through the whole policy to update it
    for row in self.policy:
        for col in row:
            # array to save the values for all neighbours
            neighbours = [None, None, None, None]

                # if the index is not out of bounds, save the values of the neighbours
                try:
                    neighbours[0] = self.valueFunction[row-1][col]
                except(IndexError):
                    pass

                try:
                    neighbours[1] = self.valueFunction[row+1][col]
                except(IndexError):
                    pass

                try:
                    neighbours[2] = self.valueFunction[row][col-1]
                except(IndexError):
                    pass

                try:
                    neighbours[3] = self.valueFunction[row][col+1]
                except(IndexError):
                    pass

                # get index of the neighbour with the maximal value
                ai = neighbours.index(max(neighbours))
                # save the greedy action in the policy
                self.policy[row][col] = self.actions[ai]

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
    print(len(test.grid[1]))
    test.policyEvaluation()
    print()

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
            print("Gridfile could not be found: Please specify a valid file (with path).")
            exit(1)

        self.grid = grid


    def readUserInput(self):
        '''
        Reads in processing mode and gamma value
        '''

        # read in processing mode from user (a or m)
        processingMode = input("Please choose between manual and automated processing (a/m): ")
        # case insensitivity by accepting capitalized letters as well
        # using .lower() on input string did not work; resulted in always meeting the while-condition
        while (not (processingMode is "a" or processingMode is "A" or processingMode is "m" or processingMode is "M")):
            if ("exit" in processingMode.lower()):
                sys.exit()
            processingMode = input("Please enter either \"a\" or \"m\": ")


        # if automated processing mode is choosen, get number of evaluation steps (n)
        iterations = 1
        if (processingMode == "a"):
            iterations = input("Please specify a number of iterations for each evaluation phase: ")
            if ("exit" in iterations.lower()):
                sys.exit()
            try:
                iterations = int(iterations)
                while (iterations <= 0):  # has to be bigger than zero
                    # checking if user wants to exit
                    if ("exit" in iterations.lower()):
                        sys.exit()
                    iterations = input("Please specify a positive integer for number of iterations for each evaluation phase: ")
            except ValueError:
                print("Stop this tomfoolery and enter a positive integer! Try again next time.")
                sys.exit()

        # read in gamma as float
        gamma = input("Please specify a gamma value between 0 and 1: ")
        # check initial input for wish to end program
        if ("exit" in gamma.lower()):
            sys.exit()
        try:
            # make sure input has acceptable value
            while (float(gamma) > 1.0 or float(gamma) < 0.0):
                gamma = input("Please specify a gamma value between 0 and 1: ")
                if ("exit" in gamma.lower()):
                    sys.exit()
            gamma = float(gamma)
        except ValueError:
            print("Stop this tomfool ery and enter a float value between 0 and 1! Try again next time.")
            sys.exit()

        self.processingMode = processingMode
        self.iterations = iterations
        self.gamma = gamma

        # @TODO maybe implement goal > pitfall?
        # check for correctness of input
        # since it is absolutely up to the user which values these variables take
        # we only check for input type
        try:
            self.REWARD = input("Please specify the reward (or penalty) for each step: ")
            if ("exit" in self.REWARD.lower()):
                sys.exit()
            self.REWARD = float(self.REWARD)
            self.GOAL = input("Please specify the reward of the goal state: ")
            if ("exit" in self.GOAL.lower()):
                sys.exit()
            self.GOAL = float(self.GOAL)
            self.PITFALL = input("Please specify the penalty for the pitfall state: ")
            if ("exit" in self.PITFALL.lower()):
                sys.exit()
            self.PITFALL = float(self.PITFALL)
        except ValueError:
            print("Stop this tomfool ery and enter a float value between 0 and 1! Try again next time.")
            sys.exit()

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
                    sum = self.possibleStates(self.policy[i][j], i, j)
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

    def possibleStates(self, policyValue, i, j):
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
        wanted_i, wanted_j = self.nextState(policyValue, i, j)
        # print("wanted i", wanted_i, "wanted j", wanted_j)

        # ... clockwise action is performed
        clockwise_i, clockwise_j = self.nextState(clockwise_action, i, j)
        # ... counterclockwise action is performed
        counterclockwise_i, counterclockwise_j = self.nextState(counterclockwise_action, i, j)
        sum = 0
        # calculate the sum of the values with the probability to reach it
        # print("self.valueFunction wanted", self.valueFunction[wanted_i][wanted_j])
        sum = self.valueFunction[wanted_i][wanted_j] * 0.8
        sum = sum + self.valueFunction[clockwise_i][clockwise_j] * 0.1
        sum = sum + self.valueFunction[counterclockwise_i][counterclockwise_j] * 0.1
        # print("sum", sum)

        # return the weighted sum of possible states and thei respective values
        return sum

    def nextState(self, policyValue, i, j):
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
                if(self.policy[row][col] != '+'):
                    if(self.policy[row][col] != '-'):
                        if(self.policy[row][col] != 'X'):

                            temp = [None, None, None, None]

                            for i in range(len(temp)):
                                temp[i] = self.possibleStates(self.actions[i], row, col)

                            max = temp[0]
                            ind = 0

                            for i in range(len(temp)):
                                if max < temp[i]:
                                    max = temp[i]
                                    ind = i

                            self.policy[row][col] = self.actions[ind]
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
                    iterations = input("How many iterations should policy evaluation make? ")
                    if ("exit" in iterations.lower()):
                        sys.exit()
                    iterations = int(iterations)
                    while (iterations <= 0):
                        iterations = input("Please enter a positive integer! Number of iterations: ")
                        if ("exit" in iterations.lower()):
                            sys.exit()
                        iterations = int(iterations)

                except ValueError:
                    print("Stop this tomfoolery and enter a positive integer! Try again next time.")

                oldPolicy = deepcopy(self.policy)  # copy policy again
                self.runEvaluation(iterations)  # run evaluation
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
                # prints a symbol representing the direction that the policy for a given field in the grid
                # is indicating
                if (self.policy[i][j] == "up"):
                    print("^", end=" ")
                elif (self.policy[i][j] == "down"):
                    print("v", end=" ")
                elif (self.policy[i][j] == "left"):
                    print("<", end=" ")
                elif (self.policy[i][j] == "right"):
                    print(">", end=" ")
                else:
                    print(self.policy[i][j], end=" ")
            print("\n", end="")
        print("\n", end="")

    def printValueFunction(self):
        '''
        Prints value for each field in the grid correctly formatted in rows and columns
        '''
        # iterate over value function
        for i in range(len(self.valueFunction)):
            for j in range(len(self.valueFunction[0])):
                # checking if nothing (or a placeholder) was written in this position of the array
                if (self.valueFunction[i][j] == "None" or self.valueFunction[i][j] is None):
                    print("  x  ", end=" ")
                # printing the value of current position in the array
                # use of ceiling function for rounding up to three decimals is used instead of
                # Python's "round" function since it delivered better results in this program
                else:
                    print("{0:5}".format(math.ceil(self.valueFunction[i][j]*1000)/1000), end=" ")
            print("\n", end="")
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
    print("Welcome to Gridworld!\nYou may terminate the program by typing \'exit\' anytime you are asked for input.")
    test.read()
    test.printGrid()
    test.readUserInput()
    test.randomPolicyInit()
    test.valueFunctionInit()
    test.runPolicyIteration()

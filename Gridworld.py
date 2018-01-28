import fileinput
import sys
import random
import math
from copy import deepcopy
from array import array
import calculate
import visualize


class Gridworld:
    '''
    Finds policies for the best way from each field of a grid through a
    Markov Decision Process.
    '''

    def __init__(self):
        self.actions = ["up", "down", "left", "right"]
        self.processingMode = "m"
        self.grid = ""
        self.policy = []
        self.values = []
        self.GAMMA = 1
        self.REWARD = -0.4
        self.PITFALL = -1
        self.GOAL = 1
        self.ITERATIONS = 1


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
        Reads in processing mode and GAMMA value
        '''

        # read in processing mode from user (a or m)
        processingMode = input("Please choose between manual and automated processing (a/m): ")
        # case insensitivity by accepting capitalized letters as well
        # using .lower() on input string did not work; resulted in always meeting the while-condition
        while (not (processingMode is "a" or processingMode is "A" or processingMode is "m" or processingMode is "M")):
            if ("exit" in processingMode.lower()):
                sys.exit()
            processingMode = input("Please enter either \"a\" or \"m\": ")
        self.processingMode = processingMode

        # if automated processing mode is choosen, get number of evaluation steps (n)
        if (processingMode == "a" or processingMode == "A"):
            ITERATIONS = input("Please specify a number of iterations for each evaluation phase: ")
            if ("exit" in ITERATIONS.lower()):
                sys.exit()
            try:
                ITERATIONS = int(ITERATIONS)
                while (ITERATIONS <= 0):  # has to be bigger than zero
                    # checking if user wants to exit
                    if ("exit" in ITERATIONS.lower()):
                        sys.exit()
                    ITERATIONS = input("Please specify a positive integer for number of iterations for each evaluation phase: ")
            except ValueError:
                print("Stop this tomfoolery and enter a positive integer! Try again next time.")
                sys.exit()
            self.ITERATIONS = ITERATIONS

        # read in GAMMA as float
        GAMMA = input("Please specify a gamma value between 0 and 1: ")
        # check initial input for wish to end program
        if ("exit" in GAMMA.lower()):
            sys.exit()
        try:
            # make sure input has acceptable value
            while (float(GAMMA) > 1.0 or float(GAMMA) < 0.0):
                GAMMA = input("Please specify a gamma value between 0 and 1: ")
                if ("exit" in GAMMA.lower()):
                    sys.exit()
            GAMMA = float(GAMMA)
        except ValueError:
            print("Stop this tomfool ery and enter a float value between 0 and 1! Try again next time.")
            sys.exit()
        self.GAMMA = GAMMA

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
        # write None-values into all the fields we need in the new array
        self.policy = [[None for x in range(len(self.grid[0]))] for y in range(len(self.grid))]

        # iterate over array (which has the same form of the grid)
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                # write random initial policy into all fields that are free
                if (self.grid[i][j] == "F"):
                    self.policy[i][j] = random.choice(self.actions)
                # mark specia fields as such
                elif (self.grid[i][j] == "E"):
                    self.policy[i][j] = "+"
                elif (self.grid[i][j] == "P"):
                    self.policy[i][j] = "-"
                else:
                    self.policy[i][j] = "X"


    def valuesInit(self):
        '''
        Initializes value function
        Empty fields are given a value of 0, pitfalls are given the punishment-value determined by the user
        and a goal state is given the reward-value determined by the user
        '''
        # write None-values into all the fields we need in the new array
        self.values = [[0 for x in range(len(self.grid[0]))] for y in range(len(self.grid))]

        # iterate over array (which has the same form of the grid)
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                # mark obstacle fields as non-value fields
                if (self.grid[i][j] == "O"):
                    self.values[i][j] = None
                # give pitfall field its value
                if (self.grid[i][j] == "P"):
                    self.values[i][j] = self.PITFALL
                # give exit field its value
                if (self.grid[i][j] == "E"):
                    self.values[i][j] = self.GOAL


    def runPolicyIteration(self):
        '''
        runs policy iteration in one of two modes
        a: automatic mode
            - runs evaluation phase for self.ITERATIONS-times
            - stops when there is no change in policy anymore
        m: manual mode
            - runs evaluation phase for a designated amount of ITERATIONS
            - user input for number of ITERATIONS for eval after each iteration
            - stops when there is no change in policy anymore
        '''
        # automatic mode
        if (self.processingMode == "a"):

            # termination condition: until values do not change anymore
            # changed from "until policies do not change anymore" since this sometimes
            # happened before the exactly correct values were found
            eq = False
            while not eq:
                oldValues = deepcopy(self.values)  # copy current values
                self.runEvaluation(self.ITERATIONS)  # run evaluation
                calculate.makePolicy(self)  # run iteration
                eq = self.compareValues(self.values, oldValues)  # reassign equality "measure"
            visualize.printValues(self)
            visualize.printPolicy(self)

        # manual mode
        elif (self.processingMode == "m"):

            # compare two values
            # as long as the new one differs from the old value
            # ask user input for ITERATIONS again
            eq = False
            while not eq:
                try:
                    ITERATIONS = input("How many iterations should policy evaluation make? ")
                    if ("exit" in ITERATIONS.lower()):
                        sys.exit()
                    ITERATIONS = int(ITERATIONS)
                    while (ITERATIONS <= 0):
                        ITERATIONS = input("Please enter a positive integer! Number of iterations: ")
                        if ("exit" in ITERATIONS.lower()):
                            sys.exit()
                        ITERATIONS = int(ITERATIONS)
                    self.ITERATIONS = ITERATIONS

                except ValueError:
                    print("Stop this tomfoolery and enter a positive integer! Try again next time.")


                # compare values until they do not change anymore
                oldValues = deepcopy(self.values)  # copy values again
                self.runEvaluation(self.ITERATIONS)  # run evaluation
                calculate.makePolicy(self)  # run iteration
                eq = self.compareValues(self.values, oldValues)  # update equality-"measure"

                # print the resulting values and policies
                visualize.printValues(self)
                visualize.printPolicy(self)


    def runEvaluation(self, ITERATIONS):
        '''
        runs policy evaluation for a designated amount of ITERATIONS
        :param ITERATIONS: how often should evaluation be repeated
        '''
        for i in range(ITERATIONS):
            calculate.policyEvaluation(self)


    def compareValues(self, valueOne, valueTwo):
        '''
        compares two value arrays to check if they are the same
        :param valueOne:
        :param valueTwo:
        :return: boolean equal
        '''
        for i in range(len(valueOne)):
            for j in range(len(valueOne[0])):
                if valueOne[i][j] != valueTwo[i][j]:
                    return False
        return True


if __name__ == '__main__':
    test = Gridworld()
    print("Welcome to Gridworld!\nYou may terminate the program by typing \'exit\' anytime you are asked for input.")
    test.read()
    visualize.printGrid(test)
    test.readUserInput()
    test.randomPolicyInit()
    test.valuesInit()
    test.runPolicyIteration()

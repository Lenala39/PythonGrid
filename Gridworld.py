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

        #@TODO maybe implement goal > pitfall?
        self.REWARD = float(input("Please specify the reward (or penalty) for each step: "))
        self.GOAL = float(input("Please specify the reward of the goal state: "))
        self.PITFALL = float(input("Please specify the penalty for the pitfall state: "))

    def randomPolicyInit(self):
        '''
        Initializes random policy by assigning random value from self.actions to every state (F)
        '''
        # print(self.actions)
        for row in self.grid:
            # print("row", row)
            for elem in row:
                # print("elem", elem)
                if (elem == "F"):
                    self.policy.append(random.choice(self.actions))
        print(self.policy)


    def valueFunctionInit(self):
        '''
        Initializes value function
        Empty fields are given a value of 0, pitfalls are given the punishment-value determined by the user
        and a goal state is given the reward-value determined by the user
        '''
        for i in range(len(self.grid)):
            # print("row", row)
            for j in range(len(self.grid[0])):
                # print("elem", elem)
                if (self.grid[i][j] == "F"):
                    self.valueFunction[i][j] = 0;
                elif (self.grid[i][j] == "P"):
                    self.valueFunction[i][j] = self.PITFALL;
                elif (self.grid[i][j] == "E"):
                    self.valueFunction[i][j] = self.GOAL;

        print(self.valueFunction)

    def policyEvaluation(self):
        value_array = []

        for row in self.grid:
            for elem in row:
                if (elem == "F"):
                    value_array.append(0)

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
    test.readUserInput()
    test.randomPolicyInit()

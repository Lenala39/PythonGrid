import fileinput
import sys
from array import array


class Gridworld:

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
            print("Gridfile could not be found")

        return grid


    def printGrid(self, grid):
        '''
        Prints grid correctly formatted in rows and columns
        :param grid: grid to be printed
        '''

        # for each row aka sublist
        for row in grid:
            # select every element in that sublist (row) and print it
            for elem in row:
                print(elem, end="") # end="" to substitute the default end of print which is \n by nothing
            print("\n", end="") # line break after each row


if __name__ == '__main__':
    test = Gridworld()
    example_grid = test.read()
    test.printGrid(example_grid)
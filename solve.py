"""Sudoku solver.
Kid coding project.
Requires python 3.8+
"""
import re
import sys
import itertools

def xy(x:int, y:int) -> int:
    """Converts coordinates [x,y] in [(0-8),(0-8)] to [0-80] array location
    """
    return y*9 + x

class Puzzle():
    """The state of the puzzle board, and the solver code.
    Internal values are 0-based.
    Starts out empty.
    """

    def __init__(self):
        self.known = ['?']*81
        self.couldbe = []
        for _ in range(81):
            self.couldbe.append([True]*9)

    def print(self):
        for y in range(9):
            for x in range(9):
                if (v := self.known[xy(x,y)]) == "?":
                    print(".", end='')
                else:
                    print(v+1, end='')
                if x%3 == 2:
                    print(" ", end='')
            print('')  # newline
            if y%3 == 2:
                print("")  # extra newline

    def print_couldbe(self, val:int):
        val -= 1
        assert (val>=0) and (val<=8), "Invalid number"
        for y in range(9):
            for x in range(9):
                v = self.couldbe[xy(x,y)][val]
                if v:
                    print("#", end='')
                else:
                    print(".", end='')
            print('')

    def setyx(self, y:int, x:int, val:int):
        self.set(x,y,val)

    def set(self, x:int, y:int, val:int):
        """Sets a value on the puzzle.
         `val` is 1-based.
         `x` and `y` are 0-based
        """
        val -= 1  # make it 0-based
        # Check
        assert (val>=0) and (val<=8), "Invalid number"
        assert (x>=0) and (x<9), f"Invalid coordinate {x=}"
        assert (y>=0) and (y<9), f"Invalid coordinate {y=}"
        assert self.known[xy(x,y)] == "?", "Attempt to set value already set"
        assert self.couldbe[xy(x,y)][val], "Attempt to set impossible value"

        # set it as known
        self.known[xy(x,y)] = val

        # Set the rows & cols to be impossible.
        for i in range(9):
            self.couldbe[xy(i,y)][val] = False
            self.couldbe[xy(x,i)][val] = False

        # Set everything in the 3x3 area to be impossible
        base_x = (x // 3) * 3
        base_y = (y // 3) * 3
        for i in range(3):
            for j in range(3):
                self.couldbe[xy(base_x+i,base_y+j)][val] = False

        # set its own couldbe
        self.couldbe[xy(x,y)] = [False]*9
        self.couldbe[xy(x,y)][val] = True

    def could_not_be(self, x:int, y:int, val:int):
        """Clears a could-be value on the puzzle.
         `val` is 1-based.
         `x` and `y` are 0-based
        """
        val -= 1  # make it 0-based
        # Check
        assert (val>=0) and (val<=8), "Invalid number"
        assert (x>=0) and (x<9), f"Invalid coordinate {x=}"
        assert (y>=0) and (y<9), f"Invalid coordinate {y=}"
        assert self.known[xy(x,y)] == "?", "Attempt to remove could-be value when previously set"

        self.couldbe[xy(x,y)][val] = False

    def set_row_string(self, line:str, y:int):
        """Takes a string like "..2...45." and sets all the values
        """
        assert len(line) == 9
        for x, char in enumerate(line):
            if char in "123456789":
                n = int(char)
                self.set(x, y, n)

    def possibilities(self, x:int, y:int) -> set:
        """Returns a set of all the possible values (1-based) that are
        allowed in this space
        """
        out = set()
        for n in range(9):
            if self.couldbe[xy(x,y)][n]:
                out.add(n+1)
        return out

    def all_groups(self) -> list:
        """Returns a list of groups.  Groups are rows,
        columns or boxes.  Each group is represented as a list of
        coordinate pairs (x,y).
        """
        out = []
        for i in range(9):
            row = []
            col = []
            for j in range(9):
                row.append([i,j])
                col.append([j,i])
            out.append(row)
            out.append(col)
        for i in range(3):
            for j in range(3):
                box = []
                for ii in range(3):
                    for jj in range(3):
                        box.append([i*3+ii, j*3+jj])
                out.append(box)
        return out

    def scan(self):
        """Looks for places where there's only one possibility.
        Returns tuples that would be passed into set()
        """
        out = []
        # Look for squares where there's only 1 possibility
        for x in range(9):
            for y in range(9):
                if len(p := self.possibilities(x,y)) == 1:
                    v = list(p)[0]
                    if self.known[xy(x,y)] == "?":
                        out.append([x,y,v])

        # Scan every group to see if any number is only possible
        # in a single place.
        for grp in self.all_groups():
            for val in range(1,10):
                places_which_can_have_this_val = []
                for pxy in grp:
                    if val in self.possibilities(*pxy):
                        places_which_can_have_this_val.append(pxy)
                if len(places_which_can_have_this_val) == 1:
                    x,y = places_which_can_have_this_val[0]
                    if self.known[xy(x,y)] == "?":
                        if [x, y, val] not in out:
                            out.append([x, y, val])

        return out

    def scan_could_not_be(self):
        """Looks for places where squares in groups could not be certains values.
         Returns tuples to be passed into could_not_be."""
        # Looks for groups where there are N squares that can only be the same set of N
        # values. No other square may contain those values.
        # TODO: there are even more strategies that are sometimes necessary for complex
        # puzzles. Examples:
        # 1. If 3 squares in a group could only be (1,3), (1,5), and (3,5) then no other
        #    square in the group can be 1, 3, or 5. (This expands to larger sets of values
        #    with decreasing utility).
        # 2. If there are exactly two squares whose possibilities include 4 and 5 (among
        #    others), then the other possibilities for those squares can be eliminated.
        #    I believe this expands to more than 2 numbers as well, but I can't visualize
        #    it when solving so I've never found one.
        could_not_be = []
        for v in range(2, 9):
            for c in itertools.combinations([1,2,3,4,5,6,7,8,9], v):
                combo = set(c)
                for grp in self.all_groups():
                    not_exact = []
                    for pxy in grp:
                        poss = self.possibilities(*pxy)
                        if poss != combo:
                            not_exact.append([pxy, poss])

                    if 9 - len(not_exact) == len(combo):
                        for pxy, poss in not_exact:
                            for val in combo:
                                if val in poss:
                                    could_not_be.append([pxy[0], pxy[1], val])

        return could_not_be

    def num_unknown(self) -> int:
        cnt = 0
        for n in range(81):
            if self.known[n] == "?":
                cnt += 1
        return cnt

    def solve(self):
        for i in range(82):
            unknown = self.num_unknown()
            print(f"\nIteration {i}: {unknown} left")
            self.print()
            if unknown == 0:
                print("Done!")
                return
            print("Scanning...")
            scan_results = self.scan()
            print(f"Found {len(scan_results)} squares that are unambigous")
            for fill_in in scan_results:
                print(f"Setting {fill_in}")
                self.set(*fill_in)

            if self.num_unknown() == unknown:
                # Nothing new set. Try eliminating possibilities
                could_not_be_results = self.scan_could_not_be()
                print(f"Found {len(could_not_be_results)} that eliminate possibilities")
                for cnb in could_not_be_results:
                    print(f"Could not be {cnb}")
                    self.could_not_be(*cnb)
                if len(could_not_be_results) == 0:
                    # Give up.
                    break
        print("Solver failed.")


def _load_line(fh) -> str:
    """Loads a line from the file,
    skipping blank lines.  Validates
    format, and removes whitespace.
    """
    while True:
        line = fh.readline()
        line = line.rstrip()
        line = re.sub(" ", "", line)
        if line:
            # Not blank.
            assert len(line)==9, f"Invalid {line=}"
            return line
        # else blank line, keep reading

def load_puzzle_from_file(filename:str) -> Puzzle:
    p = Puzzle()
    print(f"Loading puzzle from {filename=}")
    with open(filename, "rt") as fh:
        y = 0
        for y in range(9):
            line = _load_line(fh)
            try:
                p.set_row_string(line, y)
            except:
                print(f"Error parsing {line=} for {y=}")
                raise
    return p


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Specify the name of the file with the puzzle in it.")
        sys.exit(1)
    p = load_puzzle_from_file(sys.argv[1])
    p.solve()

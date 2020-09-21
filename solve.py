
def xy(x:int, y:int) -> int:
    return y*9 + x

class Puzzle():
    """Internal values are 0-based.
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
            print('')

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
        val -= 1  # make it 0-based
        # Check
        assert (val>=0) and (val<=8), "Invalid number"
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
                # Nothing new set.
                break
        print("Solver failed.")


def fill_nyt_sept20(p:Puzzle):
    p.setyx(0,0,5)
    p.setyx(0,4,3)
    p.setyx(0,6,4)

    p.setyx(1,3,2)
    p.setyx(1,4,8)
    p.setyx(1,7,1)

    p.setyx(2,2,1)
    p.setyx(2,4,9)

    p.setyx(3,2,3)
    p.setyx(3,4,6)
    p.setyx(3,6,1)
    p.setyx(3,8,5)

    p.setyx(4,0,7)
    p.setyx(4,3,8)
    p.setyx(4,5,1)
    p.setyx(4,8,2)

    p.setyx(5,0,2)
    p.setyx(5,2,5)
    p.setyx(5,4,4)
    p.setyx(5,6,9)

    p.setyx(6,4,1)
    p.setyx(6,6,2)

    p.setyx(7,1,3)
    p.setyx(7,4,2)
    p.setyx(7,5,6)

    p.setyx(8,2,9)
    p.setyx(8,4,7)
    p.setyx(8,8,4)


if __name__ == "__main__":
    p = Puzzle()
    fill_nyt_sept20(p)
    p.solve()

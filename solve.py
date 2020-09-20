
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
                    print("?", end='')
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
                
    def couldbe1(self, x:int, y:int):
        """Returns a number if there's only one possibility here.
        Else returns "?"
        """
        cnt = 0
        answer = "?"
        for n in range(9):
            if self.couldbe[xy(x,y)]:
                cnt += 1
                answer = n
        if cnt == 1:
            return answer
        if cnt == 0:
            print(f"Warning! Impossible combination at {x=} {y=}")
        return "?"
                

    def scan_couldbe(self):
        """Looks for places where there's only one possibility.
        """
        for x in range(9):
            for y in range(9):
                if (v := self.couldbe1(x,y)) != "?":
                    print(f"At {x=} {y=} must be {v+1}")

                

if __name__ == "__main__":
    p = Puzzle()
    p.set(0,0,5)
    p.set(0,4,3)
    p.set(0,6,4)
    p.set(1,3,2)
    p.set(1,4,8)
    p.set(1,7,1)
    p.set(2,2,1)
    p.set(2,4,9)
    p.set(3,2,3)
    p.set(3,4,6)
    p.set(3,6,1)
    p.print()
    p.scan_couldbe()

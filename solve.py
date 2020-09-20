
def xy(x:int, y:int) -> int:
    return y*9 + x

class Puzzle():

    def __init__(self):
        self.known = ['?']*81
        self.couldbe = []
        for _ in range(81):
            self.couldbe.append([True]*9)


    def print(self):
        for x in range(9):
            for y in range(9):
                print(self.known[xy(x,y)], end='')
            print('')
                

p = Puzzle()
p.print()

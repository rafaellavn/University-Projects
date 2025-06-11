
class LifeGeneration:

    def __init__(self, state):
        self.state = state
        self.width = len(state[0])
        self.height = len(state) 
        self.next_generation_list = [ [False]*(self.width) for i in range(self.height)]
        self.edges = [[0,0],[0,self.width-1], [self.height-1, 0], [self.height-1, self.width-1]]

    def is_alive(self, x,y):
        neighbours = 0 
        if [x,y] in self.edges:
            if (x == 0 and y ==0):
                for i in range(0,2):     # First edge case
                    for j in range(0,2):
                        if self.state[i][j] and [i,j] != [x,y]:
                            neighbours +=1 
            elif (x == 0 and y == self.width -1): # Second edge case
                    for i in range(0, 2):
                        for j in range(self.width-2, self.width):
                            if self.state[i][j] and [i,j] != [x,y]:
                                neighbours +=1 
            elif (x == self.height - 1 and y == 0): 
                    for i in range(self.height - 2, self.height): # Third edge case
                        for j in range(0,2): 
                            if self.state[i][j] and [i,j] != [x,y]:
                                neighbours +=1 
            elif (x == self.height -1 and y == self.width -1): # Fourth edge case
                for i in range(self.height - 2, self.height): 
                    for j in range(self.width-2, self.width):
                        if self.state[i][j]and [i,j] != [x,y]:
                            neighbours +=1 
        elif x == 0:                # Upper edge border 
            for i in range(0, 2):
                for j in range(-1, 2):
                    if self.state[x+ i][y + j] and [x + i,y +j] != [x,y]:
                        neighbours +=1
        elif x == self.height -1: # Down edge border  
             for i in range(-1, 1):
                for j in range(-1, 2):
                    if self.state[x+ i][y + j] and [x + i,y +j] != [x,y]:
                        neighbours +=1
        elif y == 0: # Left edge border 
            for i in range(-1, 2):
                for j in range(0, 2):
                    if self.state[x+ i][y + j ] and [x + i,y +j] != [x,y]:
                        neighbours +=1
        elif y == self.width -1: # Right edge border 
            for i in range(-1, 2):
                for j in range(-1, 1):
                    if self.state[x+ i][y + j] and [x + i,y +j] != [x,y]:
                        neighbours +=1  
        else: # Case for a "normal" coordinate 
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if self.state[x+ i][y + j] and [x + i,y +j] != [x,y]:
                        neighbours +=1
        if neighbours == 2 and self.state[x][y] == True:
            self.next_generation_list[x][y] = True
        elif neighbours == 3:
            self.next_generation_list[x][y] = True
        else:
            self.next_generation_list[x][y] = False
    def next_generation(self):
        for i in range(self.height):
            for j in range(self.width):
                self.is_alive(i,j)
        return LifeGeneration(self.next_generation_list)

    def is_all_dead(self):
        for i in range((self.height)):
            for j in range((self.width)):
                 if self.state[i][j]:
                     return False
        return True 
        
    def board(self):
        return self.state

class LifeHistory:

    def __init__(self, initial_gen):
        self.inital_gen = initial_gen
        self.next_generation = initial_gen.next_generation()
        self.history = [self.inital_gen]
        self.bords = [initial_gen.board(), initial_gen.next_generation().board()]
        
    def play_step(self):
        self.bords.append(self.next_generation.next_generation().board())
        self.next_generation = self.next_generation.next_generation()

    def nr_generations(self):
        return len(self.history)

    def get_generation(self, i):
        return self.history[i].board()

    def dies_out(self):
        if (self.history[-1].is_all_dead()):
            return True
        return False

    def period(self):
        
        for i in range(len(self.history)-1):
            if self.history[i].board() == self.history[-1].board():
                return len(self.history)-1 - i 
        return None

    def play_out(self, max_steps):

        for i in range(max_steps):
            self.history.append(self.next_generation)
            if self.dies_out() or self.period() is not None:
                break
            self.play_step()

    def all_boards(self):
        return self.bords






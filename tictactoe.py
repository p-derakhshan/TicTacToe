import pygame, sys
from pygame.locals import *
import numpy as np

pygame.init()

'''CONSTANTS'''
WIDTH, HEIGHT = 600, 600 #screen's size
LINE = 15 #line's width
SIZE = 3 #number of rows and columns
CELL = 200 #cell's size
O_RADIUS, O_WIDTH = 60, 15 #circle
X_WIDTH = 25 #cross
SPACE= 55
MIN, MAX = -1000, 1000

'''COLORS'''
BG_COLOR = (30,170,160)
LINE_COLOR = (25, 145, 135)
O_COLOR, X_COLOR = (240,230,200), (65,65,65)
TXT_COLOR1, TXT_COLOR2, TXT_COLOR3 = (50,50,255), (145,60,170), (0,85,80)

font = pygame.font.SysFont(None, 40)

'''setup screen'''
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(BG_COLOR)
pygame.display.set_caption('Tic Tac Toe')

def show_text(text,color,size,pos): #shows score and high score
    f = pygame.font.SysFont(None, size)
    t=f.render(text, True ,color)
    screen.blit(t, pos)

class Game:
    def __init__(self, user_symbol, agent_symbol):
        self.user = user_symbol
        self.agent = agent_symbol
        self.board = np.array([['-','-','-'], ['-','-','-'], ['-','-','-']])
    
    '''check if there is any empty cell left on the board'''
    def move_left(self):
        if '-' in self.board: return True
        return False

    '''check if player has won'''
    def check_won(self, player):
        diag = self.board.diagonal()
        anti_diag = np.fliplr(self.board).diagonal()
        if np.all(diag == player): return ('d',1)
        elif np.all(anti_diag== player): return ('a',1)
        for i in range(SIZE):
            row, col = self.board[i, :], self.board[:, i]
            if np.all(row == player): return ('h',i)
            elif np.all(col == player): return ('v',i)
        return 0

    '''agent's utility function'''
    def get_utility(self):
        u = self.check_won(self.user)
        if u: return -1 #user has won
        a = self.check_won(self.agent)
        if a: return 1 #agent has won
        return 0 #neither has won yet
    
    def minimax(self, state):
        #get agent's utility
        utility = self.get_utility()

        #terminal state
        if utility: #a player has won (1 or -1)
            return utility
        elif not self.move_left(): #tie (0)
            return 0
        
        #non-terminal state: minimizer/maximizer's move
        if state == 'max': #maximizer's move (agent)
            value = MIN #init value
            #successors
            for i in range(SIZE):
                for j in range(SIZE):
                    if self.board[i,j] == '-': #empty cell
                        self.board[i,j] = self.agent #current state's neighbor
                        value = max(value, self.minimax('min'))
                        self.board[i,j] = '-' #undo the move
            return value
        
        else: # state='min' minimizer's move (user)
            value = MAX #init value
            #successor
            for i in range(SIZE):
                for j in range(SIZE):
                    if self.board[i,j] == '-': #empty cell
                        self.board[i,j]= self.user
                        value = min(value, self.minimax('max')) #current state's neighbor
                        self.board[i,j] = '-' #undo the move
            return value

    def agent_action(self): #agent's best action
        best_score, best_action = MIN, (-1,-1) #init value
        for i in range(SIZE):
            for j in range(SIZE):
                if self.board[i,j] == '-': #empty cell
                    self.board[i,j] = self.agent #current state's neighbor
                    score = self.minimax('min')
                    self.board[i,j] = '-' #undo the move
                    if score> best_score:
                        best_score, best_action = score, (i,j)
                        if score == 1: break #choose the first winning move 
        return best_action

    def valid_move(self, x, y):
        if self.board[x,y] != '-' or x not in range(SIZE) or y not in range(SIZE): 
            return False #non-empty cell was chosen
        return True

    def play(self, x, y, player):
        self.board[x,y]= player
        if self.check_won(player): 
            return 'won' #won
        if not self.move_left(): 
            return 'tie' #tie
        return 'continue' #empty cells left

class Board:
    def __init__(self):
        screen.fill(BG_COLOR)
    
    def game(self):
        self.draw_lines()

    def options(self):
        show_text('SELECT PLAYER', TXT_COLOR2, 55, (WIDTH/4-10, 2*CELL+20))
        show_text('(please wait for my answers during the game. I\'m a little slow)', TXT_COLOR3, 25, (55, HEIGHT-25))
        self.draw_circle(1,0)
        self.draw_cross(1,2)

    def draw_lines(self):
        #horizontal 1
        pygame.draw.line(screen, LINE_COLOR, (0, CELL), (WIDTH, CELL), LINE)
        #horizontal 2
        pygame.draw.line(screen, LINE_COLOR, (0, 2*CELL), (WIDTH, 2*CELL), LINE)
        #vertical 1
        pygame.draw.line(screen, LINE_COLOR, (CELL, 0), (CELL,HEIGHT), LINE)
        #vertical 2
        pygame.draw.line(screen, LINE_COLOR, (2*CELL, 0), (2*CELL,HEIGHT), LINE)

    def draw_circle(self, row,col):
        r, c = int(row*CELL+CELL//2), int(col*CELL + CELL//2)
        pygame.draw.circle(screen,O_COLOR,(c,r), O_RADIUS, O_WIDTH)

    def draw_cross(self, row,col):
        r, c = row*CELL, col*CELL
        pygame.draw.line(screen, X_COLOR, (c+SPACE, r+CELL-SPACE), (c+CELL-SPACE, r+SPACE), X_WIDTH)    
        pygame.draw.line(screen, X_COLOR, (c+SPACE, r+SPACE), (c+CELL-SPACE, r+CELL-SPACE), X_WIDTH)

    def draw_mark(self,row, col, player):
        if player == 'o': 
            self.draw_circle(row, col)
        elif player == 'x': 
            self.draw_cross(row, col)

    def draw_won_line(self, i, winner, angle):
        if winner == 'x': color = X_COLOR
        else: color = O_COLOR

        if angle =='h': #horizontal
            y = i * CELL + CELL//2 #i = row
            x1,y1, x2,y2 = 15, y, (WIDTH-15), y
        elif angle =='v': #vertical
            x = i * CELL + CELL//2 #i = column
            x1,y1, x2,y2 = x, 15, x, (HEIGHT-15)
        elif angle == 'd': #diagonal
            x1,y1, x2,y2 = 15, 15, (WIDTH-15), (HEIGHT-15)
        else: #anti diagonal
            x1,y1, x2,y2 = 15, (HEIGHT-15), (WIDTH-15), 15

        pygame.draw.line(screen, color, (x1, y1), (x2,y2),LINE)

    def over(self, txt):
        if not txt:
            show_text('It\'s a tie!', TXT_COLOR2, 120, (CELL-50, CELL+40))
        else:
            show_text(txt+' won!', TXT_COLOR2, 120, (CELL-30, CELL+40))
        show_text('hit space to play again', TXT_COLOR1, 25, (CELL+11, 2*CELL-80))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos[0], event.pos[1]
            row, col = int(y//CELL), int(x//CELL)
            return (row, col)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                return 'reset'


def play(x, y, player, game, board):
    state = game.play(x,y, player)
    board.draw_mark(x, y, player)
    pygame.display.update()
    if state =='continue':
        return game, board, False
    if state == 'won':
        text = player.upper()
        angle, i = game.check_won(player)
        board.draw_won_line(i, player, angle)
        pygame.display.update()
    elif state == 'tie':
        text = ''
    board.over(text)
    return game, board, True

def game_wait(): # when game is over waits for a key to be pressed to start again or quit
    while True:
        for event in pygame.event.get():
            if  event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                pygame.quit()
                sys.exit()
                return False #quit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True #start again

def intro():
    done = False
    board = Board()
    board.options()
    user, agent = '', ''

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            h = board.handle_event(event)
            if not h: continue
            elif h == 'reset':break           
            x, y = h[0],h[1]
            if y == 0: user, agent = 'o', 'x'
            else: user, agent = 'x', 'o'
            done = True
            break
                
        pygame.display.update()
    return user, agent

if __name__ == '__main__':
    running = True
    while running:
        user, agent = intro()    
        if not user: break
        game, board  = Game(user,agent), Board()
        board.game()
        game_over , agent_first= False, True
        
        
        while not game_over:
            if user=='o' and agent_first: #agent plays first
                agent_first= False                    
                game, board, game_over = play(0, 0, agent, game, board)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running, game_over = False, False
                h = board.handle_event(event)

                if not h: continue
                elif h == 'reset':
                    game_over = True
                    break           

                x, y = h[0],h[1]
                if not game.valid_move(x,y):             
                    #print('invalid cell, try again!')
                    continue

                game, board, game_over = play(x, y, user, game, board)
                
                if game_over: break
                
                else: #can continue
                    x, y = game.agent_action()
                    game, board, game_over = play(x, y, agent, game, board)
                    if game_over: break
                break
            
            pygame.display.update()
        game_over = game_wait()

    pygame.quit()
    sys.exit()

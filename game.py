import pygame, random, sys, json, os

from utils import Player, IDK, Maze

class Game:
    def __init__(self, config):
        self.config = config

        self.window = pygame.display.set_mode((1280,720))                                                                                                                                                                     
        self.clock = pygame.time.Clock()
        self.sprites = pygame.sprite.Group()
        self.player = Player(app = self)

        self.running = False
        self.paused = False
        self.debug = config['DEBUG']
        
        self.maze = Maze(self, rows = 20, cols = 40)
        self.maze.create_maze()

    def debug_neighbours(self):
        pos = pygame.mouse.get_pos()

        cur = self.maze.get_cell(pos = pos)
        
        if not cur:
            return

        for neighbour, direction in self.maze.get_neighbours(cur.pos, filter_cant_move=True):
            pygame.draw.rect(
                self.window,
                color = (0, 0, 255),
                rect = neighbour.rect.copy(),
            )
            self.window.blit(pygame.font.SysFont('ariel', 70).render(direction, True, (0, 255, 0)), neighbour.rect.center)
            

    def run(self, ):
        self.running = True

        
        self.maze.find_path(self.maze.grid[0][0], self.maze.grid[-1][-1])
        row, col = random.randint(1, self.maze.rows - 1), random.randint(1, self.maze.cols - 1)
        self.sprites.add(IDK(
            app = self,
            pos = self.maze.grid[col][row].rect.center))

        self.sprites.add(self.player)
        self.player.rect.center = self.maze.grid[0][0].rect.center

        while self.running:
                                        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

            delta_time = self.clock.tick(60) / 1000 # convert to milli sec

            self.window.fill((0, 0, 0))
            self.sprites.update(delta_time = delta_time)
            self.sprites.draw(self.window)
            self.maze.draw_grid()

            if self.debug:      
                self.debug_neighbours()

            pygame.display.flip()

if __name__ == '__main__':
    pygame.init()

    with open(os.path.join('game', 'config.json')) as f:
        config = json.loads(f.read())

    app = Game(config = config)
    app.run()

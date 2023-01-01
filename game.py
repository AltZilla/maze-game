import sys
import random
import json 
import os
import time
import typing
import threading

try:
    import pygame
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
    '-r', 'requirements.txt'])
    import pygame

# from PIL import Image

from utils import Player, IDK, Maze

class Game:
    def __init__(self, config):
        self.config = config

        self.window = pygame.display.set_mode((1280, 720))    
        self.window_size = self.window.get_size()   
        self.background = pygame.transform.scale(pygame.image.load('assets/background.jpg').convert_alpha(), size = self.window.get_size())                                                                                                                                                            
        self.clock = pygame.time.Clock()
        self.sprites = pygame.sprite.Group()

        self.running = False
        self.paused = False
        self.debug = config['debug']
        self.match_time = config['match_time']
        self.status: typing.Literal['won', 'playing', 'lost'] = 'playing'
        
        self.maze = Maze(self, rows = 10, cols = 22)
        self.maze.create_maze()
        self.started_at = time.time()

        self.assets = {}
        self.load_assets()

        self.player = Player(app = self)

    @property
    def remaining_time(self):
        return int(self.started_at + self.match_time - time.time()) if self.status == 'playing' else 1

    def load_assets(self, size = (40, 40)):
        for folder in ['player', 'minotaur']:
            self.assets.setdefault(folder, {})
            for subfolder in ['left', 'right']:
                self.assets[folder].setdefault(subfolder, [])
                for file in os.listdir(os.path.join('assets', folder, subfolder)):
                    self.assets[folder][subfolder].append(
                        pygame.transform.scale(
                            pygame.image.load(os.path.join('assets', folder, subfolder, file)).convert_alpha(), 
                            size = size
                        )
                    )

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

    def draw_text(self, text: str, rect_function, **kwargs):
        font = pygame.font.Font('assets\crisium.ttf', kwargs.get('size', 40))
        cords = rect_function(font.size(text))
        self.window.blit(
            font.render(text, True, kwargs.get('color', (0, 0, 0))), cords
        )

    def update_screen(self, delta_time: float):
        self.window.fill(self.config['background_color'][self.status])
        if self.status == 'playing':
            self.sprites.update(delta_time = delta_time)
            self.window.blit(self.background, dest = (0, 0))
        self.sprites.draw(self.window)
        self.maze.draw_grid()
        if self.status == 'playing':
            remaining = ':'.join([str(_) for _ in divmod(self.remaining_time, 60)])
            self.draw_text('Remaining Time -> ' + remaining, rect_function = lambda size: (self.window_size[0] - size[0], size[1] // 2), color = (255, 0, 0))
        elif self.status == 'won':
            self.draw_text(self.config['text']['won'], rect_function = lambda size: (self.window_size[0] // 2 - size[0] // 2, self.window_size[1] // 2 - size[1] // 2))
        elif self.status == 'lost':
            self.draw_text(self.config['text']['lost'], rect_function = lambda size: (self.window_size[0] // 2 - size[0] // 2, self.window_size[1] // 2 - size[1] // 2))

    def run(self):
        self.running = True
        
        self.maze.find_path(self.maze.grid[0][0], self.maze.grid[-1][-1])

        for _ in range(self.config["n_minotaurs"]):
            row, col = random.randint(self.maze.rows // 2, self.maze.rows - 1), random.randint(self.maze.cols // 2, self.maze.cols - 1)
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

            if self.player.rect.collidelist([m.rect for m in self.sprites.sprites() if isinstance(m, IDK)]) != -1:
                self.status = 'lost'
            elif self.remaining_time <= 0:
                self.status = 'won'
                
            self.update_screen(delta_time = delta_time)

            if self.debug:
                self.debug_neighbours()

            pygame.display.flip()

if __name__ == '__main__':
    
    pygame.init()

    # with Image.open('assets/Mini-Knights.gif') as im:
    #     for frame_index in range(im.n_frames):
    #         im.seek(frame_index)
    #         _im = im.crop((50, 40, 130, 130)).convert('RGBA')
    #         pixels = _im.load()

    #         for i in range(_im.width):
    #             for j in range(_im.height):
    #                 r, g, b, a = pixels[i, j]
    #                 if r== g == b == 102 or r == g == b == 255:
    #                     pixels[i, j] = (0,) * 4 # transparent

    #         _im.save('assets/player/right/{}.png'.format(frame_index))
    #         _im = _im.transpose(Image.FLIP_LEFT_RIGHT)
    #         _im.save('assets/player/left/{}.png'.format(frame_index))

    # with Image.open('assets/min.gif') as im:
    #     for frame_index in range(0, im.n_frames, 6):
    #         im.seek(frame_index)
    #         _im = im.crop((140, 120, 520, 430)).convert('RGBA')
    #         pixels = _im.load()

    #         for i in range(_im.width):
    #             for j in range(_im.height):
    #                 r, g, b, a = pixels[i, j]
    #                 if (r, g , b) in [(252, 252, 170), (216, 216, 255), (252, 252, 255), (255, 255, 255)]:
    #                     pixels[i, j] = (0,) * 4 # transparent

    #         _im.save('assets/minotaur/right/{}.png'.format(frame_index // 6))
    #         _im = _im.transpose(Image.FLIP_LEFT_RIGHT)
    #         _im.save('assets/minotaur/left/{}.png'.format(frame_index // 6))

    with open('config.json') as f:
        config = json.loads(f.read())

    app = Game(config = config)
    app.run()

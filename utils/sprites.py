import pygame, math, random

from pygame.sprite import Group, Sprite
from typing import NamedTuple, List, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game

__all__ = (
    "Player",
    "Wall",
    "Cell",
    "IDK"
)

class Movable(Sprite):
    app: "Game"
    rect: "pygame.Rect"
    direction: "pygame.math.Vector2"
    speed: "int"

    def _reposition(self):
        width, height = pygame.display.get_window_size()
        x, y, w, h = self.rect
        if x < 0:
            self.rect.x = 0
        if y < 0:
            self.rect.y = 0
            
        if y > height - h:
            self.rect.y = height - h
            
        if x > width - w:
            self.rect.x = width - w

    def move(self, delta_time: float):

        if self.app.paused:
            return

        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        new_pos = self.rect.copy()
        new_pos.centerx += self.direction.x * self.speed * delta_time # type: ignore
        if self.app.maze.can_move(self.rect, new_pos):
            self.rect = new_pos
        else:
            self.has_collided = True

        new_pos = self.rect.copy()
        new_pos.centery += self.direction.y * self.speed * delta_time # type: ignore
        if self.app.maze.can_move(self.rect, new_pos):
            self.rect = new_pos
        else:
            self.has_collided = True
        self._reposition()

class Player(Movable):
    def __init__(self, app):
        self.app = app
        self.image = pygame.Surface(size = (15, 15))
        self.image.fill((255, 255, 255))
        self.rect: pygame.Rect = self.image.get_rect() #type: ignore

        # movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 150
        super().__init__()
            
    def _collision(self, direction) -> bool:
        for wall in filter(lambda s: isinstance(s, Wall), self.app.sprites.sprites()):
            if self.rect.colliderect(wall.rect):
                new_pos, diff = self.rect.copy(), 5
                if direction == 'horizontal':
                    if self.direction.x < 0: # moving left
                        new_pos.left = wall.rect.right 
                    if self.direction.x > 0: # moving right
                        new_pos.right = wall.rect.left
                    
                if direction == 'vertical':
                    if self.direction.y < 0: # moving upw
                        new_pos.top = wall.rect.bottom
                    if self.direction.y > 0: # moving down
                        new_pos.bottom = wall.rect.top
                return new_pos

    def update(self, delta_time) -> None:
        pressed = pygame.key.get_pressed()
            
        # Left & right
        if pressed[pygame.K_RIGHT]:
            self.direction.x = 1
        elif pressed[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

        # Up & Down
        if pressed[pygame.K_UP]:
            self.direction.y = -1
        elif pressed[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0
        
        self.move(delta_time = delta_time)
        self._reposition()

class IDK(Movable):
    def __init__(self, app, pos: tuple):
        self.app = app
        self.image = pygame.Surface(size = (15, 15))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        # Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 70

        self.last_updated_at = 0
        self.has_collided = False

        self.path = []
        super().__init__()

    def update_path(self):
        my_cell = self.app.maze.get_cell(self.rect.center)
        player_cell = self.app.maze.get_cell(self.app.player.rect.center)
        if self.path == [] or self.path[-1] != player_cell:
            self.path = self.app.maze.find_path(
                my_cell, player_cell
            )

        while self.path and self.path[0].rect.inflate(- self.app.maze.cell_size / 1.5, - self.app.maze.cell_size / 1.5).collidepoint(self.rect.center):
            self.path.pop(0)

    def update(self, delta_time):
        self.update_path()
        self.direction = pygame.math.Vector2(
            self.path[0].rect.centerx - self.rect.centerx, self.path[0].rect.centery - self.rect.centery
        )

        self.move(delta_time = delta_time)
        
        if self.rect.colliderect(self.app.player.rect):
            self.app.paused = True
            self.app.window.fill((255, 0, 0))
            self.app.window.blit(pygame.font.SysFont('ariel', 70).render('GAME OVER!!! ', True, (0, 255, 0)), (1280 // 2, 720 // 2))
            
class Wall(Sprite):
    def __init__(self, x, y, w, h, face):
        self.image = pygame.Surface(size = (w, h))
        self.image.fill((255, 255, 255))
        self.rect: pygame.Rect = self.image.get_rect() #type: ignore
        
        self.rect.centerx = x
        self.rect.centery = y
        self.face =  face
        
        super().__init__()

class Cell(NamedTuple):
    pos: tuple
    open_faces: List[Literal['N', 'E', 'S', 'W']]
    rect: pygame.Rect

    def matrix(self):
        mat = [
          [0, 0, 0],
          [0, 0, 0],
          [0, 0, 0]
        ]
        if 'N' in self.open_faces:
            mat[0] = [1, 1, 1]
        if 'E' in self.open_faces:
            for i in range(3):
                mat[i][2] = 1
        if 'S' in self.open_faces:
            mat[2] = [1, 1, 1]
        if 'W' in self.open_faces:
            for i in range(3):
                mat[i][0] = 1
        return mat


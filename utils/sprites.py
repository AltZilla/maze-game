import pygame

from pygame.sprite import Sprite
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game import Game

__all__ = (
    "Player",
    "IDK"
)

class Movable(Sprite):
    app: "Game"
    rect: "pygame.Rect"
    direction: "pygame.math.Vector2"
    speed: "int"

    @property
    def face(self):
        return 'right' if self.direction.x > 0 else 'left'

    def _reposition(self):
        width, height = self.app.window_size
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
        new_pos.centerx += self.direction.x * (self.speed * delta_time) # type: ignore
        if self.app.maze.can_move(self.rect, new_pos):
            self.rect = new_pos
        else:
            self.has_collided = True

        new_pos = self.rect.copy()
        new_pos.centery += self.direction.y * (self.speed * delta_time) # type: ignore
        if self.app.maze.can_move(self.rect, new_pos):
            self.rect = new_pos
        else:
            self.has_collided = True
        self._reposition()

class Player(Movable):
    def __init__(self, app):
        self.app = app
        self.images = self.app.assets['player']
        self.frame_index = 0
        self.image = self.images['right'][self.frame_index]
        
        self.rect: pygame.Rect = self.image.get_rect() #type: ignore
        # movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 150
        super().__init__()

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
        
        self.frame_index += delta_time * 10
        self.frame_index = self.frame_index if self.frame_index <= len(self.images[self.face]) else 0
        self.image = self.images[self.face][int(self.frame_index)]
        self.move(delta_time = delta_time)

class IDK(Movable):
    def __init__(self, app, pos: tuple):
        self.app = app
        self.images = self.app.assets['minotaur']
        self.image = self.images['right'][0]
        self.rect: pygame.Rect = self.image.get_rect().inflate(-5, -5)
        self.rect.center = pos
        # Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 150

        self.last_updated_at = 0
        self.frame_index = 0
        self.has_collided = False
        self.times_edited_path = 0
        self.moving_to = None

        self.path = []
        super().__init__()

    def update_path(self):
        my_cell = self.app.maze.get_cell(self.rect.center)
        player_cell = self.app.maze.get_cell(self.app.player.rect.center)
        prev_path = self.path.copy()
        updated = False
        if self.path == [] or self.path[-1] != player_cell:
            if self.path and player_cell in self.path:
                del self.path[self.path.index(player_cell) + 1:]
                return
            elif self.path and self.times_edited_path < 3:
                neighbours = self.app.maze.get_neighbours(target_pos = self.path[-1].pos, filter_cant_move = True)
                if player_cell in neighbours:
                    self.path.append(player_cell)
                    self.times_edited_path += 1
                    return
            self.times_edited_path = 0
            self.path = self.app.maze.find_path(
                my_cell, player_cell
            )
            updated = True

        if self.path:
            if updated and my_cell not in prev_path: # Check if its ald moving to the next cell, so it doesnt move back
                 self.path.pop(0)

            if self.path[0].rect.center == self.rect.center:
                self.path.pop(0)

    def update(self, delta_time):
        self.update_path()
        self.direction = pygame.math.Vector2(
            self.path[0].rect.centerx - self.rect.centerx, self.path[0].rect.centery - self.rect.centery
        )

        self.move(delta_time = delta_time)

        self.frame_index += delta_time * 5
        self.frame_index = self.frame_index if self.frame_index <= len(self.images[self.face]) else 0
        self.image = self.images[self.face][int(self.frame_index)]

# class Wall(Sprite):
#     def __init__(self, x, y, w, h, face):
#         self.image = pygame.Surface(size = (w, h))
#         self.image.fill((255, 255, 255))
#         self.rect: pygame.Rect = self.image.get_rect() #type: ignore
        
#         self.rect.centerx = x
#         self.rect.centery = y
#         self.face =  face
        
#         super().__init__()

# class Cell(NamedTuple):
#     pos: tuple
#     open_faces: List[Literal['N', 'E', 'S', 'W']]
#     rect: pygame.Rect

#     def matrix(self):
#         mat = [
#           [0, 0, 0],
#           [0, 0, 0],
#           [0, 0, 0]
#         ]
#         if 'N' in self.open_faces:
#             mat[0] = [1, 1, 1]
#         if 'E' in self.open_faces:
#             for i in range(3):
#                 mat[i][2] = 1
#         if 'S' in self.open_faces:
#             mat[2] = [1, 1, 1]
#         if 'W' in self.open_faces:
#             for i in range(3):
#                 mat[i][0] = 1
#         return mat


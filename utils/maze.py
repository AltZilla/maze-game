import pygame
import typing
import random

PosType = typing.Tuple[int, int]
Direction = typing.Literal['N', 'E', 'S', 'W']

class Cell:
    def __init__(self, app, pos: PosType, cell_size: typing.Optional[int] = None) -> None:
        self.app = app
        self.pos = pos # col, row
        self.rect = None
        self.open_sides = set()
        self.previous = None

        self.cell_size = cell_size
        self.set_rect(cell_size = cell_size or 50)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} pos={self.pos!r}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)

    def set_rect(self, cell_size: int):
        x_offset, y_offset = self.app.maze.offset
        self.rect = pygame.Rect( (self.pos[0] - 1) * cell_size + x_offset, (self.pos[1] - 1) * cell_size + y_offset, cell_size, cell_size)

    def open_side(self, side: Direction):
        self.open_sides.add(side)

    def draw(self, window):

        points = [point for *point, face in 
                [
                    (self.rect.topleft, self.rect.topright, 'N'),
                    (self.rect.bottomleft, self.rect.bottomright, 'S'),
                    (self.rect.topright, self.rect.bottomright, 'E'),
                    (self.rect.bottomleft, self.rect.topleft, 'W')
                ]   if not face in self.open_sides
            ]
        for point in points:
            yield pygame.draw.line(
                surface = window,
                color = self.app.config['cell_color'],
                start_pos = point[0],
                end_pos = point[1],
                width = 3
            )

class Maze:
    def __init__(self, app, rows = 10, cols = 22) -> None:
        self.app = app
        self.rows = rows
        self.cols = cols

        self.grid: typing.List[typing.List["Cell"]] = []
        self.rects: typing.List[pygame.Rect] = []
        self.loop_precent = 20
        self.path = []

    def _init_grid(self):
        self.set_attrs()
        self.grid.clear()
        for x in range(1, self.cols + 1):
            self.grid.append([])
            for y in range(1, self.rows + 1):
                self.grid[x - 1].append(Cell(pos = (x, y), cell_size = self.cell_size, app = self.app))
    
    def set_attrs(self):
        self.cell_size = min(
            (pygame.display.get_window_size()[0] - 50) // self.cols,
            (pygame.display.get_window_size()[1] - 100) // self.rows
        )

        self.offset = pygame.math.Vector2(
            (pygame.display.get_window_size()[0] - self.cols * self.cell_size) // 2,
            (pygame.display.get_window_size()[1] - self.rows * self.cell_size) // 2
        )

    def get_cell(self, pos: PosType) -> "Cell":
        try:
            return self.grid[int((pos[0] - self.offset.x) // self.cell_size)][int((pos[1] - self.offset.y) // self.cell_size)]
        except IndexError:
            return None

    def get_neighbours(self, target_pos: PosType, filter_cant_move: bool = False) -> typing.List[typing.Tuple["Cell", Direction]]:
        neighbours = (
            (target_pos[0] - 1, target_pos[1], 'W'),
            (target_pos[0] + 1, target_pos[1], 'E'),
            (target_pos[0], target_pos[1] - 1, 'N'),
            (target_pos[0], target_pos[1] + 1, 'S')
        )
        ret = []
        for col, row, direction in neighbours:
            if (1 <= row <= self.rows) and (1 <= col <= self.cols):
                cell = self.grid[col - 1][row - 1]
                if filter_cant_move and self.reverse_direction(direction) not in cell.open_sides:
                    continue
                ret.append((cell, direction))

        return ret

    def find_path(self, start_cell: "Cell", end_cell: "Cell"):

        class Node:
            cell: "Cell"
            f_score: "int"
            g_score: "int"
            previous = None

            def __init__(self, cell: "Cell", f_score: "int", g_score: "int", previous: "Cell" = None) -> None:
                self.cell = cell
                self.f_score = f_score
                self.g_score = g_score
                self.previous = previous
                

        def heuristic(cell_1, cell_2):
            return abs(cell_2.pos[0] - cell_1.pos[0]) + abs(cell_2.pos[1] + cell_1.pos[1])

        nodes = [Node(cell = cell, f_score = float('inf'), g_score = float('inf')) for row in self.grid for cell in row if cell != start_cell]
        nodes.append(Node(cell = start_cell, f_score = heuristic(start_cell, end_cell), g_score = 0))

        visited = []
        unvisited = nodes.copy()
        path = []

        while unvisited:
            current_node = sorted(unvisited, key = lambda node: node.f_score)[0] # least f_score

            if current_node.cell == end_cell:
                path.append(current_node.cell)

                while current_node.previous:
                    path.append(current_node.previous.cell)
                    current_node = [node for node in nodes if node == current_node.previous][0]

                path.reverse()
                break

            for neighbour, _ in self.get_neighbours(target_pos = current_node.cell.pos, filter_cant_move = True):
                neighbour_node = [node for node in nodes if node.cell == neighbour][0]
                
                if neighbour_node in visited:
                    continue

                g_score = current_node.g_score + 1 # Cost is always 1
                f_score = g_score + heuristic(neighbour, end_cell)

                if g_score < neighbour_node.g_score:
                    neighbour_node.g_score = g_score; neighbour_node.f_score = f_score; neighbour_node.previous = current_node

            unvisited.remove(current_node)
            visited.append(current_node)

            if self.app.debug:
                self._debug_draw_path(open_set = visited, current = current_node)

        return path

    def _debug_draw_path(self, open_set, current):
        for node in open_set:
                pygame.draw.rect(
                    surface = self.app.window,
                    color = (0, 255, 0) if node != current else (255, 0, 0),
                    rect = node.cell.rect.copy(),
                )
                self.app.window.blit(pygame.font.SysFont('ariel', self.cell_size // 2).render(str(node.f_score), True, (0, 0, 255)), node.cell.rect.center)

        self.draw_grid()
        pygame.display.flip()
        pygame.time.delay(5)
        self.app.window.fill((0, 0, 0))


    def reverse_direction(self, direction: Direction) -> typing.Optional[Direction]:
        return 'N' if direction == 'S' else 'S' if direction == 'N' else 'E' if direction == 'W' else 'W' if direction == 'E' else None

    def draw_grid(self):
        self.rects.clear()
        for row in self.grid:
            for cell in row:
                self.rects.extend(
                    cell.draw(self.app.window)
                )

        for i, cell in enumerate(self.path[:-1]):
            pygame.draw.line(
                surface = self.app.window,
                color = (255, 0, 0),
                start_pos = cell.rect.center,
                end_pos = self.path[i + 1].rect.center,
                width = 5
            )

    def can_move(self, old_pos: pygame.Rect, new_pos: pygame.Rect) -> bool:
        if new_pos.collidelist(self.rects) == -1:
            return True
        return False

    def _draw_debug_generation(self, visited, history, old, new):
        self.app.window.fill((0, 0, 0))

        for cell in history:
            pygame.draw.rect(
                self.app.window,
                color = (0, 0, 255) if cell != new else (255, 0, 0),
                rect = cell.rect.copy(),
            )

        pygame.draw.line(
            self.app.window,
            color = (0, 255, 0),
            start_pos = old.rect.center,
            end_pos = new.rect.center,
            width = 4
        )

        self.draw_grid()
        pygame.display.flip()
        pygame.time.delay(10)

    def create_maze(self, start_cell = (1, 1)):
        if self.grid == []:
            self._init_grid()

        start_cell = self.grid[start_cell[0] - 1][start_cell[1] - 1]
        visited = {start_cell}
        history = [start_cell]

        while len(visited) < (self.rows * self.cols):
            current = history[-1]

            neighbours = self.get_neighbours(target_pos = current.pos)

            if random.randint(0, 100) > self.loop_precent:
                neighbours = list(filter(lambda n: n[0] not in visited, neighbours))

            if not neighbours:
                history.pop()
            else:
                neighbour, direction = random.choice(neighbours)

                current.open_side(side = direction)
                reversed_side = self.reverse_direction(direction = direction)

                if not reversed_side:
                    raise ValueError("Invalid Direction -> {}".format(direction))

                neighbour.open_side(side = reversed_side)
                visited.add(neighbour)
                history.append(neighbour)
            
            if self.app.debug:
                self._draw_debug_generation(visited = visited, history = history, old = current, new = neighbour)
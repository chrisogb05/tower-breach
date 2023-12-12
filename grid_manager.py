import pygame, sys
import heapq
from settings import *
from entity_class import Entity
import random

playerspawnpos = None

# converts list to Vector2
def toVector(l):
	return pygame.math.Vector2(tuple(l))

# define the heuristic function
def heuristic(node, end_node):
	return abs(node.row - end_node.row) + abs(node.col - end_node.col)

def totatldist(start, end):
	return heuristic(start, end)

# get the position in grid of a Node
def get_node_pos(node):
	return (node.row, node.col)


# define the A* pathfinding function
def a_star(start_node, end_node, grid, diagonalmovement):
	open_set = [start_node]
	closed_set = set()

	while len(open_set) > 0:
		current_node = heapq.heappop(open_set)
		if current_node == start_node:
			current_node.g = 0

		if current_node == end_node:
			# found the path
			path = []
			while current_node != start_node:
				path.append(current_node)
				current_node = current_node.parent
			# returns the reverse of the 'path' list
			return path[::-1]

		closed_set.add(current_node)

		for neighbor in current_node.get_neighbors(grid, diagonalmovement, False):
			if neighbor in closed_set:
				continue
			# if neighbor is diagonal set the cost of movement to root 2 multiplied by the cost to move horizontally
			if abs(neighbor.row - current_node.row) == 1 and abs(neighbor.col - current_node.col) == 1:
				tent_g_score = current_node.g + 14
			else:
				tent_g_score = current_node.g + 10
			
			if tent_g_score < neighbor.g:
				neighbor.parent = current_node
				neighbor.g = tent_g_score
				neighbor.h = heuristic(neighbor, end_node)
				neighbor.f = neighbor.g + neighbor.h
				if neighbor not in open_set:
					heapq.heappush(open_set, neighbor)
	return None

# define the Grid class
class Grid(pygame.sprite.Sprite):
	def __init__(self, nrows, ncols, tilesize, game, stage, gridposition, border, walkersize):
		super().__init__()
		self.nrows = nrows
		self.ncols = ncols
		self.tilesize = tilesize
		self.startpos = None
		self.border = border
		self.walkersize = walkersize

		self.nodes = [[Node(row, col, self) for col in range(ncols)] for row in range(nrows)]


		self.image = pygame.Surface((self.get_grid_dimensions()[0], self.get_grid_dimensions()[1]))
		self.rect = self.image.get_rect()

		self.game = game
		self.stage = stage
		self.gridposition = gridposition


		self.drunkard_walk()
		self.spawn_walls()
		self.startpos = self.toWorldPos(playerspawnpos.x, playerspawnpos.y, "topleft")

	def drunkard_walk(self):
		walkerrow = random.randint(self.border+1,self.nrows-self.border-2)
		walkercol = random.randint(self.border+1,self.ncols-self.border-2)
		self.gridstartpos = pygame.math.Vector2(walkerrow, walkercol)

		
		self.startpos = pygame.math.Vector2(self.toWorldPos(self.gridstartpos.x + self.walkersize/2, self.gridstartpos.y + self.walkersize/2, "topleft"))
		Walker(walkerrow, walkercol, 15, 0.35, 0.55, True, 4, False, self, self.stage, self.walkersize, True) 

		

	# create walls everywhere there is a blocked tile
	def spawn_walls(self):
		global playerspawnpos
		for row in range(self.nrows):
			for col in range(self.ncols):
				node = self.get_node(row, col)
				if not node.blocked:
					for neighbor in node.get_neighbors(self, True, True, row, col):
						if self.is_blocked(list(neighbor)[0], list(neighbor)[1]):
							Wall(self.tilesize, DEEPORANGE, self.toWorldPos(list(neighbor)[0], list(neighbor)[1], "topleft").x, self.toWorldPos(list(neighbor)[0], list(neighbor)[1], "topleft").y, self, [self.stage.visible_sprites, self.stage.obstacles])

	def get_nrows(self):
		return self.nrows

	def get_ncols(self):
		return self.ncols
	
	def set_blocked(self, row, col, blocked):
		self.nodes[row][col].blocked = blocked

	def is_blocked(self, row, col):
		return self.nodes[row][col].blocked

	def get_grid_dimensions(self):
		width = (self.ncols) * self.tilesize
		height = (self.nrows) * self.tilesize
		return [width, height]

	def get_node(self, row, col):
		return self.nodes[row][col]

	def draw_grid(self, showsquares, colorslist, gridindexlist):
		for row in range(self.nrows):
			for col in range(self.ncols):
				node = self.get_node(row, col)

				if node.blocked:
					color = WHITE
				elif node.parent:
					color = BLUE
				else:
					color = DARKGREY				

				# draw tiles of grid in their respective colors calculated above
				pygame.draw.rect(self.image, color, (col * self.tilesize, row * self.tilesize, self.tilesize, self.tilesize))

				if colorslist:
					for c_index, c in enumerate(colorslist):
						pygame.draw.rect(self.image, c, (gridindexlist[c_index].y * self.tilesize, gridindexlist[c_index].x * self.tilesize,  self.tilesize, self.tilesize))
				if showsquares:
					# draw grid lines
					pygame.draw.rect(self.image, DARKGREYHIGHLIGHT, (col * self.tilesize, row * self.tilesize,  self.tilesize, self.tilesize), 1)
		
		# draws the Grid (which the squares are already drawn on) onto the screen at gridposition which can be changed in Stage
		self.game.screen.blit(self.image, self.gridposition)
				
	def toGridIndex(self, posx, posy):
		row = int((posy - self.rect.y - self.gridposition.y) // self.tilesize)
		col = int((posx - self.rect.x - self.gridposition.x) // self.tilesize)
		return row, col 
	
	def toWorldPos(self, row, col, anchor):
		if anchor == "topleft":
			y = (row * self.tilesize) + self.gridposition.y
			x = (col * self.tilesize) + self.gridposition.x
		elif anchor == "center":
			y = (row * self.tilesize) + self.gridposition.y + (self.walkersize-1)*self.tilesize/2
			x = (col * self.tilesize) + self.gridposition.x + (self.walkersize-1)*self.tilesize/2

		return pygame.math.Vector2(x, y)
	
# define the Node class. A Node is created for each grid cell
class Node(Grid):
	def __init__(self, row, col, grid_class):
		self.grid_class = grid_class
		self.row = row
		self.col = col
		self.g = float("inf")
		self.h = 0
		self.f = float("inf")
		self.parent = None
		self.blocked = True

	def get_row(self):
		return self.row

	def get_col(self):
		return self.col

	def __lt__(self, other):
		return self.f < other.f

	def __eq__(self, other):
		return self.row == other.row and self.col == other.col

	def __hash__(self):
		return hash((self.row, self.col))
	
	def dirToNode(self, other):
		ydir = self.row - other.row
		xdir = self.col - other.col
		return pygame.math.Vector2(xdir, ydir)

	def get_neighbors(self, grid, includediagonal, includeblocked, *nodecoord):
		neighbors = []
		for i in range(-1, 2):
			for j in range(-1, 2):
				if i == 0 and j == 0:
					continue
				if not includediagonal:
					if (abs(i)+abs(j)) == 2:
						continue
				if not nodecoord:
					row = self.row + i
					col = self.col + j
				else:
					row = nodecoord[0] + i
					col = nodecoord[1] + j

				if includeblocked:
					if row >= 0 and row < self.grid_class.nrows and col >= 0 and col < self.grid_class.ncols:
						neighbors.append((grid.nodes[row][col].row, grid.nodes[row][col].col))
				else:
					if row >= 0 and row < self.grid_class.nrows and col >= 0 and col < self.grid_class.ncols and not grid[row][col].blocked:
						neighbors.append(grid.nodes[row][col])
		return neighbors
	

# define the Wall class
class Wall(Entity):
	def __init__(self, size, color, posx, posy, grid, groups):
		super().__init__(groups)
		self.image = pygame.Surface((size, size))
		self.rect = self.image.get_rect(topleft=(posx,posy))
		self.hitbox = self.rect.copy()
		self.image.fill(color)
		self.grid = grid
		self.initialpos = self.rect.topleft

terminal = []


# define the Walker class. The shape of the level is dependent on the attributes passed into the first walker created
class Walker():
	def __init__(self, row, col, steplimit, dirchance, newchance, backtrack, bulksize, bulked, grid, stage, walkersize, first):
		self.clock = pygame.time.Clock()
		self.pos = pygame.math.Vector2(row,col)
		
		self.steplimit = steplimit
		self.initialstep = steplimit 
		self.dirchance = dirchance
		self.newchance = newchance
		self.backtrack = backtrack
		self.grid = grid
		self.bulksize = bulksize
		self.bulked = bulked

		self.stage = stage
		self.border = self.stage.border
		self.walkersize = walkersize
		self.direction = [-walkersize, 0]

		self.first = first
		self.playerspawnpos = None


		self.grid.draw_grid(True, None, None)
		pygame.display.update()
		self.run()


	def get_random_cardinal_dir(self, prevdir, backtrack):
		r1 = random.randint(-1,1) 
		r2 = random.randint(-1,1)

		if backtrack:
			while pygame.math.Vector2(r1,r2).magnitude() != 1 or pygame.math.Vector2(r1,r2).magnitude() == 0:
				r1 = random.randint(-1,1) 
				r2 = random.randint(-1,1)
		else:
			while (pygame.math.Vector2(r1,r2).magnitude() != 1 or pygame.math.Vector2(r1,r2).magnitude() == 0) or pygame.math.Vector2(r1,r2) == toVector(prevdir):
				r1 = random.randint(-1,1) 
				r2 = random.randint(-1,1)

		return [r1*self.walkersize, r2*self.walkersize]
	
	def subtract(self):
		for i in range(self.walkersize):
			for j in range(self.walkersize):
				self.grid.set_blocked(int(self.pos.x + i), int(self.pos.y + j), False)


	def move(self):
		self.pos = self.pos + toVector(self.direction)
		#self.steplimit = self.steplimit - 1

	def updatevisual(self):
		self.grid.draw_grid(True, [RED], self.pos)
		pygame.display.update()

	def updateplaceholders(self):
		self.topedge = self.pos.x
		self.leftedge = self.pos.y
		self.bottomedge = self.pos.x + self.walkersize
		self.rightedge = self.pos.y + self.walkersize

		self.bottomborderindex = self.grid.get_nrows() - self.border
		self.topborderindex = self.border
		self.rightborderindex = self.grid.get_ncols() - self.border
		self.leftborderindex = self.border


	def changedir(self):
		self.updateplaceholders()

		self.direction = self.get_random_cardinal_dir(self.direction, self.backtrack)
		self.clampwalkerinbounds()
		
	# makes sure that no part of each walker will go outside of set border
	def clampwalkerinbounds(self):
		while (self.bottomedge + self.direction[0] > self.bottomborderindex or self.topedge + self.direction[0] < self.topborderindex) or (self.rightedge + self.direction[1] > self.rightborderindex or self.leftedge + self.direction[1] < self.leftborderindex):
			self.direction = self.get_random_cardinal_dir(self.direction, self.backtrack)
			
	

	def change_modifier(self, mod, value):
			if mod == "dir":
				if self.dirchance + value > 1:
					self.dirchance = 1
				elif self.dirchance + value < 0:
					self.dirchance = 0
				else:
					self.dirchance = self.dirchance + value

			if mod == "new":
				if self.newchance + value > 1:
					self.newchance = 1
				elif self.newchance + value < 0:
					self.newchance = 0
				else:
					self.newchance = self.newchance + value
				
			if mod == "siz":
				if self.walkersize + value < 0:
					self.walkersize = 0
				else:
					self.walkersize = self.walkersize + value


	def run(self):
		global playerspawnpos

		self.changedir()
		while self.steplimit > 0:
			self.updateplaceholders()

			if (self.bottomedge <= self.bottomborderindex and self.topedge >= self.topborderindex) and (self.rightedge <= self.rightborderindex and self.leftedge >= self.leftborderindex):
				self.subtract()

				if self.first:
					if self.steplimit == self.initialstep:					
						playerspawnpos = self.pos

				self.changedir()
				self.move()
				
			else:
				self.changedir()
				self.move()
				self.subtract()

				if self.first:
					if self.steplimit == self.initialstep:
						playerspawnpos = self.pos

			self.steplimit = self.steplimit - 1

			if random.randint(1,1000) <= self.dirchance * 1000:
				self.changedir()
				self.change_modifier("dir", -0.05)

			if random.randint(1,1000) <= self.newchance * 1000:
				self.change_modifier("new", -0.1)
				self.change_modifier("dir", -0.3)

				if self.bulked == False:
					for i in range(self.bulksize):
						Walker(self.pos.x, self.pos.y, self.initialstep, 0.1, 0.1, False, False, True, self.grid, self.stage, self.walkersize, False)	
				else:
					Walker(self.pos.x, self.pos.y, self.steplimit, 0.1, 0, False, self.bulksize, True, self.grid, self.stage, self.walkersize, False)

		terminal.append(self.pos)

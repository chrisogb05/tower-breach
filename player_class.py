import pygame, math, os
from directories import *
from settings import *
from entity_class import Entity

class Player(Entity):
	def __init__(self, stage, startpos, obstacles, harmful):
		super().__init__(stage.visible_sprites)
		self.tag = "player"
		self.image = pygame.image.load(os.path.join(assets_dir, 'player.png')).convert()
		self.image.set_colorkey((0,0,0))
		self.base_image = self.image
		self.rect = self.image.get_rect()
		self.rect.topleft = startpos
		self.hitbox = self.rect.copy()
		self.stage = stage
		self.lookdir = None
		self.obstacles = obstacles
		self.harmful = harmful

		self.speed = 9
		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(startpos)
		self.moving = [False, False]

		self.bulletsize = 5
		self.bulletspeed = 20
		self.firerate = 1.0

	def input(self):
		keys = pygame.key.get_pressed()

		yflag = 0
		xflag = 0

		# movement input
		if keys:
			self.moving[1] = False
			self.moving[0] = False
			
			if keys[pygame.K_UP] or keys[pygame.K_w]:
				self.moving[1] = True
				yflag -= 1			
			if keys[pygame.K_DOWN] or keys[pygame.K_s]:
				self.moving[1] = True
				yflag += 1
				
			self.direction.y = yflag
			

			if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				self.moving[0] = True
				xflag += 1
			if keys[pygame.K_LEFT] or keys[pygame.K_a]:
				self.moving[0] = True
				xflag -= 1
				
			self.direction.x = xflag

		# mouse input
		if pygame.mouse.get_pressed()[0]:
			Bullet(self.bulletsize, self.bulletspeed, self.rect.center, self.lookdir, self.stage, self.obstacles)



	def update(self):
		mx, my = pygame.mouse.get_pos()
		ychange = (WINDOW_SIZE/2) - my
		xchange = mx - (WINDOW_SIZE/2)

		lookdirx = xchange
		lookdiry = ychange

		

		self.lookdir = (pygame.math.Vector2(lookdirx, -lookdiry)).normalize()
		self.angle = math.degrees(math.atan2(lookdiry, lookdirx)) - 90
		self.input()

		self.move(self.speed)

		self.image = pygame.transform.rotate(self.base_image, self.angle)
		self.rect = self.image.get_rect(center = self.hitbox.center)

	def collision(self,direction):
		if direction == 'horizontal':
			for sprite in self.obstacles:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.x > 0: # moving right
						self.hitbox.right = sprite.hitbox.left
					if self.direction.x < 0: # moving left
						self.hitbox.left = sprite.hitbox.right
			for sprite in self.harmful:
				if sprite.hitbox.colliderect(self.hitbox):
					if sprite.tag == "bullet":
						# remove health
						self.harmful.remove(sprite)

		if direction == 'vertical':
			for sprite in self.obstacles:
				if sprite.hitbox.colliderect(self.hitbox):
					if self.direction.y > 0: # moving down
						self.hitbox.bottom = sprite.hitbox.top
					if self.direction.y < 0: # moving up
						self.hitbox.top = sprite.hitbox.bottom

		
	
	def get_player_dir(self):
		return self.direction

class Bullet(Entity):
	def __init__(self, size, speed, startpos, direction, stage, walls):
		super().__init__(stage.harmful)
		self.tag = "bullet"
		self.image = pygame.Surface((size, size))
		self.image.fill(RED)
		self.rect = self.image.get_rect()
		self.rect.center = startpos
		self.hitbox = self.rect.copy()
		self.obstacles = walls

		self.speed = speed
		self.direction = direction

	def update(self):
		self.move(self.speed)

	



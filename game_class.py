import pygame, sys, math, os
from settings import *
from state_manager import *
from player_class import *
from directories import *
import state_manager
from grid_manager import *

playing = True

# handles game quit events
def quit_events():
   global playing
   keys = pygame.key.get_pressed()
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         state_manager.states.pop()
         playing = False
         pygame.quit()
         
      
   if keys[pygame.K_ESCAPE]:
      state_manager.states.pop()
      playing = False
      pygame.quit()


class Game:
   # initialising attributes of a Game
   def __init__(self):
      self.openmenu = False
      pygame.init()
      self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
      self.screen.fill(BG_COLOR)
      self.finished = False

      # creating game window
      pygame.display.set_caption(GAME_NAME)
      pygame.event.set_grab(True)

      # defines a crosshair image as the cursor
      self.crosshair_image = pygame.image.load(os.path.join(assets_dir, 'crosshair.png')).convert_alpha()
      crosshair = pygame.cursors.Cursor((20, 20), self.crosshair_image)
      pygame.mouse.set_cursor(crosshair)

      # instantiates stage 1
      Stage(self, 54, 54, 18, 1, 4)

      self.run()

   # runs the game
   def run(self):
      while playing:
         # checks if game has been quit
         quit_events()


# draws text to a surface
def draw_text(anchor, coor, fontname, fontsize, text, fgcolor, surface, *bgcolor):
   font = pygame.font.Font(os.path.join(fonts_dir, fontname), fontsize)
   txtsurface = font.render(text, True, fgcolor, *bgcolor)
   txtrect = txtsurface.get_rect()
   if anchor == "center":
      txtrect.center = coor
   elif anchor == "topleft":
      txtrect.topleft = coor

   surface.blit(txtsurface, txtrect)


class Stage:
   def __init__(self, game, rows, cols, tilesize, border, walkersize):
      self.gridposition = pygame.math.Vector2(0,0)
      self.rows = rows
      self.cols = cols
      self.tilesize = tilesize
      self.visible_sprites = pygame.sprite.Group()
      self.obstacles = pygame.sprite.Group()
      self.harmful = pygame.sprite.Group()
      self.clock = pygame.time.Clock()
      self.finished = False
      self.complete = False
      self.game = game
      self.border = border
      self.walkersize = walkersize
     

      self.g = Grid(self.rows,self.cols, self.tilesize, game, self, self.gridposition, self.border, self.walkersize)
      self.player = Player(self, self.g.startpos, self.obstacles, self.harmful)
      
      self.run()

   
   def run(self):
      while not self.complete:
         self.game.screen.fill(DARKGREY)
         keys = pygame.key.get_pressed()
         for event in pygame.event.get():
            if event.type == pygame.QUIT:
               self.finished = True
               state_manager.states.pop()
               pygame.quit()
         if keys[pygame.K_ESCAPE]:
            self.complete = True
            self.game.finished = True



         if self.complete:
            break

         self.harmful.draw(self.game.screen)
         self.harmful.update()
         
         self.visible_sprites.draw(self.game.screen)
         self.visible_sprites.update()


         draw_text("center", (WINDOW_SIZE/2, WINDOW_SIZE-27), 'built titling lt.ttf', 40, "SCORE: 2550", WHITE, self.game.screen)
         draw_text("topleft", (8, 3), 'built titling lt.ttf', 45, "username", WHITE, self.game.screen)
         draw_text("topleft", (8, 52), 'built titling lt.ttf', 29, "HEALTH: 8", WHITE, self.game.screen)
         draw_text("topleft", (8, 82), 'built titling lt.ttf', 29, "AMMO: 153", WHITE, self.game.screen)

         pygame.display.flip()
         self.clock.tick(MAXFPS)
      
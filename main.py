import pygame, sys
from settings import * 
from player import Player
from pygame.math import Vector2 as vector
from pytmx.util_pygame import load_pygame
from sprite import Sprite, Bullet
from monster import Coffin, Cactus
import time

class Allsprites(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.offset = vector()
		self.display_surface = pygame.display.get_surface()
		self.bg = pygame.image.load('./graphics/other/map.png').convert()
	
	def customize_draw(self, player):
		self.offset.x = player.rect.centerx - WINDOW_WIDTH / 2
		self.offset.y = player.rect.centery - WINDOW_HEIGHT / 2


		self.display_surface.blit(self.bg, -self.offset)
		for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
			offset_rect = sprite.image.get_rect(center = sprite.rect.center)
			offset_rect.center -= self.offset
			self.display_surface.blit(sprite.image, offset_rect)

class Game: 
	def __init__(self):
		pygame.init()
		self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption('Western shooter')
		self.clock = pygame.time.Clock()
		self.bullet_surf = pygame.image.load('graphics/other/particle.png').convert_alpha()

		# Groups
		self.all_sprites = Allsprites()
		self.obstacles = pygame.sprite.Group()
		self.bullets = pygame.sprite.Group()
		self.monsters = pygame.sprite.Group()


		self.setup()
		self.font = pygame.font.Font('./font/subatomic.ttf', 50)
		self.music = pygame.mixer.Sound('./sound/music.mp3')
		self.music.set_volume(MUSIC_VOLUME)
		self.music.play(loops = -1)

	def create_bullet(self, pos, direction):
		Bullet(pos, direction, self.bullet_surf, [self.all_sprites, self.bullets])

	def bullet_collision(self):

		for obstacle in self. obstacles.sprites():
			pygame.sprite.spritecollide(obstacle, self.bullets, True, pygame.sprite.collide_mask)

		for bullet in self.bullets.sprites():
			sprites = pygame.sprite.spritecollide(bullet, self.monsters, False, pygame.sprite.collide_mask)

			if sprites:
				bullet.kill()
				for sprite in sprites:
					sprite.damage()

		if pygame.sprite.spritecollide(self.player, self.bullets, True, pygame.sprite.collide_mask):
			self.player.damage()

	def setup(self):
		tmx_map = load_pygame('./data/map.tmx')
		for x, y, surf in tmx_map.get_layer_by_name('fence').tiles():
			Sprite((x * 64,y * 64), surf, [self.all_sprites, self.obstacles])
		for x, y, surf in tmx_map.get_layer_by_name('fence2').tiles():
			Sprite((x * 64,y * 64), surf, [self.all_sprites, self.obstacles])

		for obj in tmx_map.get_layer_by_name('Object'):
			Sprite((obj.x, obj.y), obj.image, [self.all_sprites, self.obstacles])

		for obj in tmx_map.get_layer_by_name('Entities'):
			if obj.name == 'Player':
				self.player = Player(
					pos = (obj.x,obj.y),
					groups =  self.all_sprites,
					path =  PATHS['player'],
					collision_sprites =  self.obstacles,
					create_bullet =  self.create_bullet)
			if obj.name == 'Coffin':
				Coffin((obj.x,obj.y), [self.all_sprites, self.monsters], PATHS['coffin'], self.obstacles, self.player)
			if obj.name == 'Cactus':
				Cactus((obj.x, obj.y), [self.all_sprites, self.monsters], PATHS['cactus'], self.obstacles, self.player, self.create_bullet)

		self.heart_surf = pygame.image.load('./graphics/other/heart.png').convert_alpha()

	def display_win(self):
		Highscore_text = 'You Win!'
		text_surf = self.font.render(Highscore_text, True, (255, 255, 255))
		text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
		self.display_surface.blit(text_surf, text_rect)
		pygame.draw.rect(self.display_surface, (255, 0, 0), text_rect.inflate(30, 30), width = 8, border_radius = 5)
		time.sleep(5)

	def run(self):
		while True:
			# event loop 
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
			dt = self.clock.tick() / 1000

			# Update
			self.all_sprites.update(dt)
			self.bullet_collision()
			# Draw
			self.display_surface.fill('black')
			
			self.all_sprites.customize_draw(self.player)

			
			if self.player.health >= 1:	
				self.display_surface.blit(self.heart_surf, ((WINDOW_WIDTH / 60) + 200, WINDOW_HEIGHT / 90))
			if self.player.health >= 2:
				self.display_surface.blit(self.heart_surf, ((WINDOW_WIDTH / 60) + 100, WINDOW_HEIGHT / 90))
			if self.player.health >= 3:
				self.display_surface.blit(self.heart_surf, (WINDOW_WIDTH / 60, WINDOW_HEIGHT / 90))

			if self.player.score == 25:
				self.display_win()
			pygame.display.update()


if __name__ == '__main__':
	print('Please edit the settings file before playing.')

	if AGREE:
		game = Game()
		game.run()
	else:
		print("You have not agreed to the t's and c's, find them in the settings file")
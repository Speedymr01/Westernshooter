import pygame
from pygame.math import Vector2 as vector
from os import walk
from entity import Entity
import sys
import time

class Player(Entity):
    def __init__(self, pos, groups, path, collision_sprites, create_bullet):
        super().__init__(pos, groups, path, collision_sprites)
        self.create_bullet = create_bullet
        self.bullet_shot = False
        self.health = 3
        self.reloading = False
        self.reload_start_time = 0
        self.reload_duration = 4500  # 4.5 seconds
        self.ammo = 6
        self.reload_sound = pygame.mixer.Sound('sound/reload.wav')
        self.score = 0

    def get_status(self):
        # idle
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = self.status.split('_')[0] + '_idle'
        # attack
        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def input(self):
        keys = pygame.key.get_pressed()
        if not self.attacking:
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
            if keys[pygame.K_r]:
                self.reload()
            if keys[pygame.K_SPACE]:
                if self.ammo > 0:
                    self.attacking = True
                    self.direction = vector()
                    self.frame_index = 0
                    self.bullet_shot = False
                    self.ammo -= 1
                    match self.status.split('_')[0]:
                        case 'left': self.bullet_direction = vector(-1,0)
                        case 'right': self.bullet_direction = vector(1,0)
                        case 'up': self.bullet_direction = vector(0,-1)
                        case 'down': self.bullet_direction = vector(0,1)

    def animate(self, dt):
        current_animation = self.animations[self.status]
        self.frame_index += 7 * dt
        if int(self.frame_index) == 2 and self.attacking and not self.bullet_shot:
            bullet_start_pos = self.rect.center + self.bullet_direction * 80
            self.create_bullet(bullet_start_pos, self.bullet_direction)
            self.bullet_shot = True
            self.shoot_sound.play()
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)


    def reload(self):
        if self.ammo == 0 and not self.reloading:
            self.reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            self.reload_sound.play()

    def check_death(self):
        if self.health <= 0:
            
            pygame.quit()
            sys.exit()


    def update(self, dt):
        if self.reloading:
            elapsed_time = pygame.time.get_ticks() - self.reload_start_time
            if elapsed_time >= self.reload_duration:
                self.reloading = False
                self.ammo = 6
        
        self.get_status()
        self.input()
        self.move(dt)
        self.animate(dt)
        self.blink()
        self.vulnerability_timer()
        self.check_death()
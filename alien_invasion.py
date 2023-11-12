import pygame
from pygame.sprite import Group
from alien import Alien
from settings import Settings
from ship import Ship
from game_stats import GameStats
from button import Button
import game_functions as gf

def run_game():
    #Initialise game and create a screen object
    pygame.init()
    ai_settings=Settings()
    screen=pygame.display.set_mode((ai_settings.screen_width,ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")

    #Create an instance to store game statistics.
    stats=GameStats(ai_settings)

    #Make a ship.
    ship=Ship(ai_settings,screen)

    #Make a group for bullets and aliens.
    bullets=Group()
    aliens=Group()

    #Create a fleet of aliens
    gf.create_fleet(ai_settings,screen,ship,aliens)

    #Make the Play Button
    play_button=Button(ai_settings,screen,"Play")
    
    #Set the background color
    bg_color=(230,230,230)

    #Make an alien
    alien=Alien(ai_settings,screen)

    #Start the main loop for the game
    while True:
        #Watch for keyboard and mouse events
        gf.check_events(ai_settings,screen,stats,play_button,ship,aliens,bullets)

        if stats.game_active:
            ship.update()
            bullets.update()
            gf.update_bullets(ai_settings,screen,ship,aliens,bullets)
            gf.update_aliens(ai_settings,stats,screen,ship,aliens,bullets)
        gf.update_screen(ai_settings,screen,stats,ship,aliens,bullets,play_button)        
#Call the function.
run_game()

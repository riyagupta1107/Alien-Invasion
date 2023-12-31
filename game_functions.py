import sys
from time import sleep
import pygame
import ship
from bullet import Bullet
from alien import Alien

def ship_hit(ai_settings,stats,screen,ship,aliens,bullets):
    """Respond to ship being hit by alien."""
    if stats.ship_left>0:
        #Decrement ships_left
        stats.ship_left-=1

        #Empty the list of aliens and bullets
        aliens.empty()
        bullets.empty()

        #Create a new fleet and center the ship
        create_fleet(ai_settings,screen,ship,aliens)
        #Pause
        sleep(0.5)
    else:
        stats.game_active=False
        pygame.mouse.set_visible(True)

def get_number_rows(ai_settings,ship_height,alien_height):
    """Determine the number of rows of aliens that fit on the screen."""
    available_space_y=(ai_settings.screen_height-(3*alien_height)-ship_height)
    number_rows=int(available_space_y/(2*alien_height))
    return number_rows

def get_number_aliens_x(ai_settings,alien_width):
    """Determine the number of aliens that fit in a row."""
    available_space_x=ai_settings.screen_width-(2*alien_width)
    number_aliens_x=int(available_space_x/(2*alien_width))
    return number_aliens_x

def create_alien(ai_settings,screen,aliens,alien_number,row_number):
    """Create an alien and place it in a row"""
    alien=Alien(ai_settings,screen)
    alien_width=alien.rect.width
    alien.x=alien_width+2*alien_width*alien_number
    alien.rect.x=alien.x
    alien.rect.y=alien.rect.height+2*alien.rect.height*row_number
    aliens.add(alien)

def create_fleet(ai_settings,screen,ship,aliens):
    """Create a full fleet of aliens."""
    alien=Alien(ai_settings,screen)
    #Create an alien and find the number of aliens in a row.
    #Spacing between each alien is equal to one alien width.
    number_aliens_x=get_number_aliens_x(ai_settings,alien.rect.width)
    number_rows=get_number_rows(ai_settings,ship.rect.height,alien.rect.height)

    #Create a fleet of aliens.
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings,screen,aliens,alien_number,row_number)

def check_fleet_edges(ai_settings,aliens):
    """Respond appropriately if aliens have reached an edge."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings,aliens)
            break

def change_fleet_direction(ai_settings,aliens):
    """Drop the entire fleet and change alien's direction."""
    for alien in aliens.sprites():
        alien.rect.y+=ai_settings.fleet_drop_speed
    ai_settings.fleet_direction*=-1

def check_keydown_events(event,ai_settings,screen,ship,bullets):
    """Respond to keypresses"""
    if event.key==pygame.K_RIGHT:
        ship.moving_right=True
    elif event.key==pygame.K_LEFT:
        ship.moving_left=True
    elif event.key==pygame.K_SPACE:
        fire_bullets(ai_settings,screen,ship,bullets)
    elif event.key==pygame.K_q:
        sys.exit()
        
def fire_bullets(ai_settings,screen,ship,bullets):
    """Fire a bullet if limit has not reached yet."""
    #Create a new bullet and add it to bullets group
    if len(bullets)<ai_settings.bullets_allowed:
        new_bullet=Bullet(ai_settings,screen,ship)
        bullets.add(new_bullet)

def check_keyup_events(event,ship):
    """Respond to key release"""
    if event.key==pygame.K_RIGHT:
        ship.moving_right=False
    elif event.key==pygame.K_LEFT:
        ship.moving_left=False

def check_events(ai_settings,screen,stats,play_button,ship,aliens,bullets):
    """Respond to key presses and mouse events"""
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            sys.exit
        elif event.type==pygame.KEYDOWN:
            check_keydown_events(event,ai_settings,screen,ship,bullets)
        elif event.type==pygame.KEYUP:
            check_keyup_events(event,ship)
        elif event.type==pygame.MOUSEBUTTONDOWN:
            mouse_x,mouse_y=pygame.mouse.get_pos()
            check_play_button(ai_settings,screen,stats,play_button,ship,aliens,bullets,mouse_x,mouse_y)

def check_play_button(ai_settings,screen,stats,play_button,ship,aliens,bullets,mouse_x,mouse_y):
    """Start a new game when the player clicks Play!"""
    button_clicked=play_button.rect.collidepoint(mouse_x,mouse_y)
    if button_clicked and not stats.game_active:
        #Reset the game settings
        ai_settings.initialize_dynamic_settings()
        #Hide the mouse cursor
        pygame.mouse.set_visible(False)
        #Reset game statistics
        stats.reset_stats()
        stats.game_active=True

        #Empty the list of aliens and bullets
        aliens.empty()
        bullets.empty()

        #Create a new fleet and center the ship
        create_fleet(ai_settings,screen,ship,aliens)
        ship.center_ship()

def update_screen(ai_settings,screen,stats,ship,aliens,bullets,play_button):

    """Update images on screen and flip to new screen"""
    #Redraw the screen during each pass of the loop.
    screen.fill(ai_settings.bg_color)
    #Redraw all bullets behind ship and aliens.
    for i in bullets.sprites():
        i.draw_bullet()
    ship.blitme()
    aliens.draw(screen)

    #Draw the play button if the game is inactive
    if not stats.game_active:
        play_button.draw_button()

    #Make the most recently drawn screen visible
    pygame.display.flip()

def update_bullets(ai_settings,screen,ship,aliens,bullets):
    bullets.update()

    #Get rid of bullets that have disappeared
    for i in bullets.copy():
            if i.rect.bottom<=0:
                bullets.remove(i) 

    check_bullet_alien_collisions(ai_settings,screen,ship,aliens,bullets)
    
def check_bullet_alien_collisions(ai_settings,screen,ship,aliens,bullets):
    """Respond to bullet-alien collisions"""
    #Check for any bullets that hit aliens.
    #If so, get rid of the bullet and alien.
    collisions=pygame.sprite.groupcollide(bullets,aliens,False,True)

    if len(aliens)==0:
        #Destroy existing aliens and create new fleet.
        bullets.empty()
        ai_settings.increase_speed()
        create_fleet(ai_settings,screen,ship,aliens)

def update_aliens(ai_settings,stats,screen,ship,aliens,bullets):

    """Update positions of all aliens in the fleet."""
    check_fleet_edges(ai_settings,aliens)
    aliens.update()

    """Look for alien ship collisions."""
    if pygame.sprite.spritecollideany(ship,aliens):
        ship_hit(ai_settings,stats,screen,ship,aliens,bullets)

    #Look for alien ship that hit the bottom
    check_aliens_bottom(ai_settings,stats,screen,ship,aliens,bullets)

def check_aliens_bottom(ai_settings,stats,screen,ship,aliens,bullets):
    """Check if any aliens have reached the bottom of the screen"""
    screen_rect=screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom>=screen_rect.bottom:
            #Treat this same as if the ship got hit
            ship_hit(ai_settings,stats,screen,ship,aliens,bullets)
            break
    

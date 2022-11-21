from typing import List

import pygame

from ave import Bandada, AveRule, SimpleSeparationRule, AlignmentRule, CohesionRule, NoiseRule
from settings import GameSettings


pygame.init()

def main():
    game_settings = GameSettings()

    pygame.display.set_caption("Aves")
    win = pygame.display.set_mode((game_settings.window_width, game_settings.window_height))
    fill_colour = (255, 255, 255)

    n_aves = 50
    ave_fear = 10
    ave_radius = 100
    ave_max_speed = 200

    bandada = Bandada(game_settings)
    bandada_rules: List[AveRule] = [
        CohesionRule(weighting=0.5, game_settings=game_settings),
        AlignmentRule(weighting=1, game_settings=game_settings),
        NoiseRule(weighting=1, game_settings=game_settings),
        SimpleSeparationRule(weighting=1, game_settings=game_settings, push_force=ave_fear)
    ]
    bandada.generate_aves(n_aves, rules=bandada_rules, local_radius=ave_radius, max_velocity=ave_max_speed)

    entities = bandada.aves
    tick_length = int(1000/game_settings.ticks_per_second)

    last_tick = pygame.time.get_ticks()
    while game_settings.is_running:
        win.fill(fill_colour)
        time_since_last_tick = pygame.time.get_ticks() - last_tick
        if time_since_last_tick < tick_length:
            pygame.time.delay(tick_length - time_since_last_tick)

        time_since_last_tick = pygame.time.get_ticks() - last_tick

        last_tick = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_settings.is_running = False

        for entity in entities:
            entity.update(win, time_since_last_tick/1000)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()

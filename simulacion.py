from typing import List

import pygame

import config

from ave import Bandada, AveRule, SimpleSeparationRule, AlignmentRule, CohesionRule, NoiseRule

pygame.init()

def main():

    pygame.display.set_caption("Aves")
    win = pygame.display.set_mode((config.window_width, config.window_height))
    fill_colour = (255, 255, 255)

    bandada = Bandada()
    bandada_rules: List[AveRule] = [
        CohesionRule(weighting=0.5),
        AlignmentRule(weighting=1),
        NoiseRule(weighting=1),
        SimpleSeparationRule(weighting=1, push_force=config.areaAlejamiento)
    ]
    bandada.generate_aves(config.numAves, rules=bandada_rules, local_radius=config.areaDeteccion, max_velocity=config.aveVelMax)

    entities = bandada.aves
    tick_length = int(1000/config.ticks_per_second)

    last_tick = pygame.time.get_ticks()
    while config.is_running:
        win.fill(fill_colour)
        time_since_last_tick = pygame.time.get_ticks() - last_tick
        if time_since_last_tick < tick_length:
            pygame.time.delay(tick_length - time_since_last_tick)

        time_since_last_tick = pygame.time.get_ticks() - last_tick

        last_tick = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                config.is_running = False

        # Cada vez que se hace esto, se calculan las distancias entre todas las aves (O(n**2)), para determinar cuales estan cerca:
        for entity in entities:
            entity.update(win, time_since_last_tick/1000) 

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()

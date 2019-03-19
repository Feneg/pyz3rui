'''
Common executive functions.
'''


import logging as log

import pyz3r


__all__ = 'load', 'generate'


def load(hash: str, settings: dict) -> None:
    '''
    Load and patch an already generated game.

    Args:
        hash: hash code for game to load
        settings: patching settings for game
    '''

    log.debug('Loading game with hash: %s', str(hash))

    # Load game.
    game = pyz3r.alttpr(hash=hash)

    # Patch game.
    patch(game, settings)


def generate(settings: dict):
    '''
    Generate new game.

    Args:
        settings: settings for new game
    '''

    # Generate game.
    game = pyz3r.alttpr(
        randomizer=settings['randomiser'],
        settings={
            'difficulty': settings['difficulty'],
            'enemizer': settings['enemiser'],
            'logic': settings['logic'],
            'mode': settings['state'],
            'goal': settings['goal'],
            'variation': settings['variation'],
            'weapons': settings['swords'],
            'spoilers': settings['spoiler'],
            'tournament': settings['race'],
            'lang': 'en'})

    # Patch game.
    patch(game, settings)


def patch(game, settings: dict) -> None:
    '''
    Patch and write newly randomised game.

    Args:
        game: pyz3r.alttpr.alttprClass object
        settings: dictionary patch settings for game
    '''

    # Load ROM.
    origin = pyz3r.romfile.read(settings['input'])

    # Patch game.
    newgame = game.create_patched_game(
        origin, heartspeed=settings['heartspeed'],
        heartcolor=settings['heartcolour'], spritename=settings['sprite'],
        music=not settings['no-music'])

    # Write new game.
    pyz3r.romfile.write(newgame, settings['output'])

    # Print game info.
    log.info('Permalink: %s', game.url)
    # not working
    # log.info('Code: %s', ' | '.join(game.code()))

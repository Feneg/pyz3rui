'''
Common executive functions.
'''


import logging as log
import os.path
import pprint

import pyz3r


__all__ = 'versions', 'load', 'generate'


def versions() -> None:
    '''
    Print version numbers.
    '''
    
    log.info('pyz3rui: rolling')
    log.info('pyz3r: %s', pyz3r.__version__)


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


def generate(settings: dict) -> None:
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
            'shuffle': settings['entranceshuffle'],
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

    # Build output file location.
    meta = game.data['spoiler']['meta']
    if settings['output']:
        outfile = settings['output']
    else:
        if 'name' in meta:
            outfile = meta['name']
        else:
            outfile = (
                'ALttP - VT_{0:s}_{1:s}-{2:s}{3:s}-{4:s}{5:s}_{6:s}'.format(
                    meta['logic'], meta['difficulty'], meta['mode'],
                    ('_{0:s}'.format(meta['weapons'])
                     if 'weapons' in meta else ''),
                    meta['goal'],
                    ('_{0:s}'.format(meta['variation'])
                     if meta['variation'] != 'none' else ''),
                    game.hash))
        infofile = '{0:s}.txt'.format(outfile)
        outfile = '{0:s}.sfc'.format(outfile)
        outfile = os.path.join(settings['output-dir'], outfile)

    # Write game info.
    if not settings['output']:
        infofile = os.path.join(settings['output-dir'], infofile)
        with open(infofile, 'w') as fid:
            pprint.pprint(game.data['spoiler'], stream=fid)

    # Write new game.
    log.debug('New file: {0:s}'.format(outfile))
    pyz3r.romfile.write(newgame, outfile)

    # Print game info.
    log.info('File: %s', outfile)
    log.info('Permalink: %s', game.url)
    log.info('Code: %s', ' | '.join(game.code()))

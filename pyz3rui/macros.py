'''
Common executive functions.
'''

import http.client
import json
import logging as log
import os.path
import pprint
import random

import pyz3r

VERSION = (1, 1, 0)

__all__ = 'versions', 'load', 'generate'


def versions() -> None:
    '''
    Print version numbers.
    '''

    log.info('pyz3rui: %s', '.'.join(str(n) for n in VERSION))
    log.info('pyz3r: %s', pyz3r.__version__)


async def load(hash: str, settings: dict) -> None:
    '''
    Load and patch an already generated game.

    Args:
        hash: hash code for game to load
        settings: patching settings for game
    '''

    log.debug('Loading game with hash: %s', str(hash))

    # Load game.
    game = await pyz3r.alttpr(hash=hash)

    # Patch game.
    await patch(game, settings)


async def generate(settings: dict) -> None:
    '''
    Generate new game.

    Args:
        settings: settings for new game
    '''

    # Generate game.
    game = await pyz3r.alttpr(settings=settings)

    # Patch game.
    await patch(game, settings)


async def patch(game, settings: dict) -> None:
    '''
    Patch and write newly randomised game.

    Args:
        game: pyz3r.alttpr.alttprClass object
        settings: dictionary patch settings for game
    '''

    # Random sprite?
    if settings['sprite'].lower() == 'random':
        sprite = random_sprite()
        randomsprite = True
    else:
        sprite = settings['sprite']
        randomsprite = False

    # Load ROM.
    origin = await pyz3r.romfile.read(settings['input'])

    # Patch game.
    newgame = await game.create_patched_game(
        origin, heartspeed=settings['heartspeed'],
        heartcolor=settings['heartcolour'], spritename=sprite,
        music=not settings['no_music'])

    # Build output file location.
    meta = game.data['spoiler']['meta']
    if settings['output']:
        outfile = settings['output']
    else:
        if 'name' in meta:
            outfile = meta['name']
        else:
            outfile = (
                'ALttP - VT_{0:s}-{1:s}{2:s}-{3:s}_{4:s}'.format(
                    meta['logic'], meta['mode'],
                    ('_{0:s}'.format(meta['weapons'])
                     if 'weapons' in meta else ''),
                    meta['goal'], game.hash))
        infofile = '{0:s}.txt'.format(outfile)
        outfile = '{0:s}.sfc'.format(outfile)
        outfile = os.path.join(settings['output_dir'], outfile)

    # Write game info.
    if not settings['output']:
        infofile = os.path.join(settings['output_dir'], infofile)
        with open(infofile, 'w') as fid:
            pprint.pprint(game.data['spoiler'], stream=fid)

    # Write new game.
    log.debug('New file: {0:s}'.format(outfile))
    await pyz3r.romfile.write(newgame, outfile)

    # Print game info.
    log.info('File: %s', outfile)
    log.info('Permalink: %s', game.url)
    log.info('Code: %s', ' | '.join(await game.code()))
    if randomsprite:
        log.info('Sprite: %s', sprite)


def random_sprite() -> str:
    '''
    Randomly choose a sprite.

    Args:
        str: random sprite name
    '''

    # Get sprite list.
    alttpr = http.client.HTTPSConnection('alttpr.com')
    alttpr.request('GET', '/sprites')
    sprite_json = alttpr.getresponse().read()
    alttpr.close()
    spritelist = json.loads(sprite_json)

    # RNG
    sprite = spritelist[random.randrange(0, len(spritelist))]['name']
    log.debug('Randomly chosen sprite: %s', sprite)

    return sprite

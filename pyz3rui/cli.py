'''
Command-line interface
'''

import argparse
import configparser
import logging as log
import operator

from . import macros

CONFIGFILE = 'pyz3rui.conf'

__all__ = ('parser',)


def loadconfig(configset: str = 'defaults', nolog: bool = False) -> dict:
    '''
    Load configuration.

    Args:
        configset: name of configuration
        nolog: suppress logging output
    Return:
        dict: selected configuration, None if not found
        list: list of available configurations
    '''

    config = configparser.ConfigParser()
    if not nolog:
        log.debug("Reading configuration '%s'.", configset)
    try:
        config.read(CONFIGFILE)
    except configparser.ParsingError:
        if not nolog:
            log.debug("Could not read config file '%s'.", 'pyz3rui.conf')
        return None, None
    sections=config.sections()
    if not config.has_section(configset):
        if not nolog:
            log.debug("No configuration set '%s' found.", configset)
        return None, None
    return dict(config[configset]), sections


def writeconfig(config: dict) -> None:
    '''
    Write configuration to file.

    This will always write to 'defaults'.

    Args:
        config: configuration to write
    '''

    outconf = configparser.ConfigParser()
    outconf['defaults'] = config
    with open(CONFIGFILE, 'w') as fid:
        outconf.write(fid)


def parser() -> None:
    '''
    Command-line interface parser
    '''

    # Get default values.
    _, available = loadconfig('defaults', nolog=True)
    if not available:
        available = ('defaults',)

    # Build CLI parser.
    args = argparse.ArgumentParser(
        prog='python3 -m pyz3rui',
        description='Generate and download Zelda 3 randomiser games.',
        epilog=(
            "Note: This program reads and writes a file 'pyz3rui.conf' in the "
            'current working directory.'))
    args.add_argument(
        '--config', action='store', choices=available,
        help='Choose custom configuration.')
    args.add_argument(
        '--debug', action='store_true', help='Print debug output.')
    args.add_argument(
        '--input', action='store', help='Input ROM file',
        metavar='<input file path>')
    args.add_argument(
        '--output', action='store', help='Output ROM file',
        metavar='<output file path>')
    args.add_argument(
        '--heartspeed', action='store',
        choices=('double', 'normal', 'half', 'quarter'),
        help='Select low-health alert sound frequency.')
    args.add_argument(
        '--heartcolour', action='store',
        choices=('red', 'green', 'blue', 'yellow'),
        help='Select heart colour.')
    args.add_argument(
        '--sprite', action='store', help='Select Link sprite.',
        metavar='<sprite name>')
    args.add_argument(
        '--no-music', action='store_true', help='Disable game music.')
        
    args.add_argument(
        '--randomiser', action='store', choices=('item', 'entrance'),
        help='Randomisation type')

    commands = args.add_subparsers(
        title='commands', metavar='<command>',
        description="(use '<command> -h' for further help)")
    commands.required = True

    genargs = commands.add_parser(
        'generate', aliases=('gen', 'g'),
        description='Generate new randomised game.',
        help='Generate new randomised game.')
    genargs.add_argument(
        '--difficulty', action='store',
        choices=('easy', 'normal', 'hard', 'expert', 'insane', 'crowdControl'),
        help='Game difficulty')
    genargs.add_argument(
        '--logic', action='store',
        choices=('NoGlitches', 'OverworldGlitches', 'MajorGlitches', 'None'),
        help='Item placement ruleset')
    genargs.add_argument(
        '--state', action='store',
        choices=('standard', 'open', 'inverted'), help='Game state')
    genargs.add_argument(
        '--goal', action='store',
        choices=('ganon', 'crystals', 'dungeons', 'pedestal', 'triforce-hunt'),
        help='Game goal.')
    genargs.add_argument(
        '--variation', action='store',
        choices=(
            'none', 'key-sanity', 'retro', 'timed-race', 'timed-ohko', 'ohko'),
        help='Game variation.')
    genargs.add_argument(
        '--swords', action='store',
        choices=('randomized', 'uncle', 'swordless'), help='Sword placement')
    genargs.add_argument(
        '--entranceshuffle', action='store',
        choices=('simple', 'restricted', 'full', 'crossed', 'insanity'),
        help='Entrance shuffle mode.')
    genargs.add_argument(
        '--spoiler', action='store_true', help='Generate spoiler game.')
    genargs.add_argument(
        '--race', action='store_true', help='Generate race game.')
    genargs.add_argument(
        '--enemiser', action='store_true', help='Acitvate enemiser.')
    genargs.set_defaults(func=macros.generate)

    loadargs = commands.add_parser(
        'load', aliases=('l',), description='Load existing game.',
        help='Load existing game.')
    loadargs.add_argument(
        '--hash', action='store', required=True, help='Game hash.',
        metavar='<hash>')
    loadargs.set_defaults(func=macros.load)

    comm = args.parse_args()

    # Initialise logging.
    log.basicConfig(
        level=log.DEBUG if comm.debug else log.INFO,
        format='%(message)s')

    # Load new default values.
    config, _ = loadconfig(
        comm.config if comm.config is not None else 'defaults')
    if not config:
        log.debug('Applying default configuration.')
        config = {
            'input': 'Zelda no Densetsu - Kamigami no Triforce.sfc',
            'output': 'Z3R.sfc',
            'heartspeed': 'half', 'heartcolour': 'red', 'sprite': 'Link',
            'no-music': False, 'randomiser': 'item',
            'difficulty': 'normal', 'logic': 'NoGlitches', 'state': 'standard',
            'goal': 'ganon', 'variation': 'none', 'swords': 'randomized',
            'entranceshuffle': 'full', 'spoiler': False, 'race': False,
            'enemiser': False}

    # Apply default values as needed.
    for conf in config:
        getter = operator.attrgetter(conf.replace('-', '_'))
        try:
            stored = getter(comm)
        except AttributeError:
            pass
        else:
            if stored is not None:
                config[conf] = stored
    log.debug('Applying game settings:')
    for conf in config:
        log.debug('   %s: %s', conf, str(config[conf]))

    # Run command.
    if comm.func is macros.load:
        macros.load(comm.hash, config)
    else:
        assert comm.func is macros.generate
        macros.generate(config)

    # Store arguments.
    writeconfig(config)

'''
Command-line interface
'''

import argparse
import asyncio
import configparser
import http.client
import json
import logging as log
import operator

import pyz3r

from . import macros

CONFIGFILE = 'pyz3rui.conf'

__all__ = ('parser',)


def listconfigs() -> list:
    '''
    List available configurations.

    Returns:
        list: list of available configurations
    '''

    config = configparser.ConfigParser()
    try:
        config.read(CONFIGFILE)
    except configparser.ParsingError:
        return None
    if not config.has_section('version'):
        log.debug('Found old configuration file.')
        with open(CONFIGFILE, 'w') as fid:
            fid.write('')
        return None
    else:
        fileversion = tuple(
            int(n) for n in config['version']['version'].split('.'))
        def vercalc(v): return 1000**2 * v[0] + 1000 * v[1] + v[2]
        if vercalc(fileversion) < vercalc(macros.VERSION):
            log.debug('Found outdated configuration file.')
            with open(CONFIGFILE, 'w') as fid:
                fid.write('')
            return None
    del config['version']
    return config.sections()


def loadconfig(configset: str = 'defaults') -> dict:
    '''
    Load configuration.

    Args:
        configset: name of configuration
    Return:
        dict: selected configuration, None if not found
    '''

    config = configparser.ConfigParser()
    log.debug("Reading configuration '%s'.", configset)
    try:
        config.read(CONFIGFILE)
    except configparser.ParsingError:
        log.debug("Could not read config file '%s'.", CONFIGFILE)
        return None
    if not config.has_section('version'):
        log.debug('Found old configuration file.')
        with open(CONFIGFILE, 'w') as fid:
            fid.write('')
        return None
    else:
        fileversion = tuple(
            int(n) for n in config['version']['version'].split('.'))
        def vercalc(v): return 1000**2 * v[0] + 1000 * v[1] + v[2]
        if vercalc(fileversion) < vercalc(macros.VERSION):
            log.debug('Found outdated configuration file.')
            with open(CONFIGFILE, 'w') as fid:
                fid.write('')
            return None
    if not config.has_section(configset):
        log.debug("No configuration set '%s' found.", configset)
        return None
    return dict(config[configset])


def writeconfig(config: dict) -> None:
    '''
    Write configuration to file.

    This will always write to 'defaults'.

    Args:
        config: configuration to write
    '''

    outconf = configparser.ConfigParser()
    try:
        outconf.read(CONFIGFILE)
    except configparser.ParsingError:
        pass
    outconf['defaults'] = config
    outconf['version'] = {'version': '.'.join(str(n) for n in macros.VERSION)}
    with open(CONFIGFILE, 'w') as fid:
        outconf.write(fid)


def loadoptions() -> dict:
    '''
    Load available randomiser options.

    Returns:
        dict: {'configuration': {'option': 'description'}}
    '''

    alttpr = http.client.HTTPSConnection('alttpr.com')
    alttpr.request('GET', '/randomizer/settings')
    options = json.loads(alttpr.getresponse().read())
    alttpr.close()
    del options['presets']['custom']
    return options


def parser() -> None:
    '''
    Command-line interface parser
    '''

    # Get configuration sets.
    available = listconfigs()
    if not available:
        available = ('defaults',)

    # Get available settings.
    options = loadoptions()

    # Build CLI parser.
    args = argparse.ArgumentParser(
        prog='python3 -m pyz3rui',
        description='Generate and download Zelda 3 randomiser games.',
        epilog=(
            "Note: This program reads and writes a file 'pyz3rui.conf' in the "
            'current working directory. WARNING: Do not use for races!'))
    args.add_argument(
        '--config', action='store', choices=available,
        help='Choose custom configuration.')
    args.add_argument(
        '--debug', action='store_true', help='Print debug output.')
    args.add_argument(
        '--input', action='store', help='Input ROM file',
        metavar='<input file path>')
    outpargs = args.add_mutually_exclusive_group()
    outpargs.add_argument(
        '--output', action='store', help='Output ROM file', default=None,
        metavar='<output file path>')
    outpargs.add_argument(
        '--output-dir', action='store',
        help='Output ROM location (file name will be generated automatically)')
    args.add_argument(
        '--heartspeed', action='store',
        choices=('double', 'normal', 'half', 'quarter', 'off'),
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
        '--palette-shuffle', action='store_true',
        help='Activate palette shuffle.')

    commands = args.add_subparsers(
        title='commands', metavar='<command>',
        description="(use '<command> -h' for further help)")
    commands.required = True

    genargs = commands.add_parser(
        'generate', aliases=('gen', 'g'),
        description='Generate new randomised game.',
        help='Generate new randomised game.')
    for config in options:
        genargs.add_argument(
            '--{0:s}'.format(config.replace('_', '-')), action='store',
            choices=tuple(options[config].keys()))
    spoilargs = genargs.add_mutually_exclusive_group()
    spoilargs.add_argument(
        '--race', action='store_true', help='Generate race game.')
    genargs.set_defaults(func=macros.generate)

    loadargs = commands.add_parser(
        'load', aliases=('l',), description='Load existing game.',
        help='Load existing game.')
    loadargs.add_argument(
        'hash', action='store', help='Game hash', metavar='<hash>')
    loadargs.set_defaults(func=macros.load)

    versargs = commands.add_parser(
        'version', aliases=('ver', 'v'), description='Print version numbers.',
        help='Print version numbers.')
    versargs.set_defaults(func=macros.versions)

    comm = args.parse_args()

    # Initialise logging.
    log.basicConfig(
        level=log.DEBUG if comm.debug else log.INFO,
        format='%(message)s')

    # Version numbers.
    if comm.func is macros.versions:
        return macros.versions()

    # Load default values.
    default_config = {
        'input': 'Zelda no Densetsu - Kamigami no Triforce.sfc',
        'output': 'Z3R.sfc', 'output_dir': '',
        'heartspeed': 'half', 'heartcolour': 'red', 'sprite': 'Link',
        'no_music': False,
        'presets': 'default', 'race': False}
    default_config.update(options['presets'][default_config['presets']])
    config = loadconfig(comm.config if comm.config is not None else 'defaults')
    if not config:
        log.debug('Applying default configuration.')
        config = default_config

    # Apply default values as needed.
    for conf in default_config:
        getter = operator.attrgetter(conf)
        try:
            stored = getter(comm)
        except AttributeError:
            if conf not in config:
                config[conf] = default_config[conf]
        else:
            if stored is not None:
                config[conf] = stored
    if config['output_dir'] and not comm.output:
        config['output'] = ''
    log.debug('Applying game settings:')
    for conf in config:
        log.debug('   %s: %s', conf, config[conf])

    # Run command.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if comm.func is macros.load:
        loop.run_until_complete(macros.load(comm.hash, config))
    else:
        assert comm.func is macros.generate
        loop.run_until_complete(macros.generate(config))

    # Store arguments.
    writeconfig(config)

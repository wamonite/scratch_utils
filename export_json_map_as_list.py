#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Export Tiled JSON exported map as text list

* map file is Tiled app exported JSON map
* tileset CSV file is a lookup from export JSON map tile id to PNG/costume id e.g. <int id>,<costume name>
* exported file is <prefix>_<map layer id>.csv
* unless provided, file prefix is map JSON file name without extension
"""

from __future__ import print_function, absolute_import
import argparse
import sys
import json


class ScriptException(Exception):
    pass


def get_args():
    parser = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--tileset', help = 'tileset lookup CSV')
    parser.add_argument('--prefix', help = 'output file prefix')
    parser.add_argument('map', nargs = 1, help = 'Tiled map JSON file')

    return parser.parse_args()


def load_tileset(file_name):
    tileset_lookup = {}
    with open(file_name) as file_object:
        for line in file_object:
            line = line.strip()
            key, name = line.split(',')
            tileset_lookup[key] = name

    return tileset_lookup


def load_level(file_name):
    try:
        with open(file_name) as file_object:
            return json.load(file_object)

    except Exception as ex:
        raise ScriptException("failed to load file={} error='{}:{}'".format(
            file_name,
            ex.__class__.__name__,
            ex,
        ))


def write_level(level_data, tileset_lookup, prefix):
    for layer_idx, layer in enumerate(level_data['layers']):
        file_name = '{}_{}.csv'.format(prefix, layer_idx)
        row_list = []
        row_width = layer['width']
        tile_count = 0
        row_buffer = []
        for tile in layer['data']:
            tile_name = tileset_lookup[str(tile)] if tileset_lookup else tile
            row_buffer.append(tile_name)

            tile_count += 1

            if tile_count == row_width:
                row_list.append(row_buffer)
                row_buffer = []
                tile_count = 0

        if row_buffer:
            row_list.append(row_buffer)

        print('writing {}'.format(file_name))

        with open(file_name, 'w') as file_object:
            for row in reversed(row_list):
                for tile in row:
                    file_object.write('{}\n'.format(tile))


def main():
    args = get_args()

    level_file_name = args.level[0]
    tileset_file_name = args.tileset

    level_data = load_level(level_file_name)
    tileset_lookup = load_tileset(tileset_file_name) if tileset_file_name else {}

    file_prefix = args.prefix
    if not file_prefix:
        file_prefix = level_file_name.split('.')[0]

    write_level(level_data, tileset_lookup, file_prefix)


def run():
    try:
        main()

    except ScriptException as e:
        print('Error: {}'.format(e), file = sys.stderr)
        sys.exit(1)

    except Exception as e:
        print('Error: ({}) {}'.format(e.__class__.__name__, e), file = sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    run()

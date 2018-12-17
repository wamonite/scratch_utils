#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Export JSON map exported from https://www.mapeditor.org/ as text list

* tileset use has only been tested with embedded collections of images
"""

from __future__ import print_function, absolute_import
import argparse
import sys
import pytmx
import os


TILE_EMPTY_NAME = 'empty'


class ScriptException(Exception):
    pass


def get_args():
    parser = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--prefix', help = 'output file prefix')
    parser.add_argument('--empty', default = TILE_EMPTY_NAME, help = 'name to use for empty tile')
    parser.add_argument('map', nargs = 1, help = 'exported JSON map file')

    return parser.parse_args()


def write_map(map_data, prefix, empty_tile_name):
    try:
        screen_width = int(map_data.properties.get('screen_width'))
        screen_height = int(map_data.properties.get('screen_height'))
    except Exception:
        raise ScriptException('screen_width and screen_height need to be set as custom map properties')

    print('screen size {} x {}'.format(screen_width, screen_height))

    for layer_id in map_data.visible_tile_layers:
        layer = map_data.layers[layer_id]
        layer_name = layer.name
        print("processing layer '{}'".format(layer_name))

        map_width = layer.width
        map_height = layer.height
        print('map size in tiles {} x {}'.format(map_width, map_height))

        screen_x_max = map_height / screen_height
        screen_y_max = map_width / screen_width
        print('map size in screens {} x {}'.format(screen_x_max, screen_y_max))

        tile_output_list = []
        try:
            for screen_y in range(screen_y_max):
                screen_y_offset = screen_y * screen_height
                for screen_x in range(screen_x_max):
                    print('screen {}, {}'.format(screen_x, screen_y))

                    screen_x_offset = screen_x * screen_width
                    for y in range(screen_height):
                        for x in range(screen_width):
                            # print('screen offset {} x {}'.format(
                            #     x + screen_x_offset,
                            #     y + screen_y_offset,
                            # ))
                            tile_info = map_data.get_tile_properties(
                                x + screen_x_offset,
                                y + screen_y_offset,
                                layer_id,
                            )

                            if tile_info:
                                tile_path = tile_info['source']
                                tile_name = os.path.basename(tile_path)
                                tile_key = os.path.splitext(tile_name)[0]

                            else:
                                tile_key = empty_tile_name

                            tile_output_list.append(tile_key)

        except Exception as ex:
            print("failed to parse layer '{}' error '{}:{}'".format(
                layer_name,
                ex.__class__.__name__,
                ex,
            ))

        else:
            file_name = '{}_{}.csv'.format(prefix, layer_name)

            print('writing {}'.format(file_name))

            with open(file_name, 'w') as file_object:
                for tile in tile_output_list:
                    file_object.write('{}\n'.format(tile))


def main():
    args = get_args()

    map_file_name = args.map[0]
    map_data = pytmx.TiledMap(map_file_name)

    file_prefix = args.prefix
    if not file_prefix:
        file_prefix = map_file_name.split('.')[0]

    write_map(map_data, file_prefix, args.empty)


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

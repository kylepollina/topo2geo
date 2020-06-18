"""
topo2geo/core.py
"""

import os
import json
from itertools import chain

import click
from shapely.geometry import asShape

from . import version as VERSION

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help']
}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('input_file')
@click.argument('output_file')
def main(input_file, output_file):
    """
    CLI tool to convert TopoJSON to GeoJSON

    Example:
        topo2geo input.topojson output.geojson
    """
    try:
        topo2geo(input_file, output_file)
    except Exception:
        import traceback
        tb = traceback.format_exc()
        print(tb)
        print(f'topo2geo version: {VERSION}')
        print('There was an error. If you want to make this tool better, please create an issue at https://github.com/kylepollina/topo2geo')
        print('thanks =]')


def topo2geo(input_file: str, output_file: str) -> None:
    """Converts the TopoJSON in input_file to GeoJSON and writes to output_file"""
    if os.path.exists(input_file) is False:
        print(f'Error: Input file {input_file} does not exist.')
        return
    with open(input_file, 'r') as f:
        topology = json.loads(f.read())

    geojson_layers = build_geojson_layers(topology)

    output_filename, output_extension = os.path.splitext(output_file)

    for layer, geojson in geojson_layers.items():
        if len(geojson_layers.keys()) > 1:
            geojson_fn = f'{output_filename}_{layer}{output_extension}'
        else:
            geojson_fn = output_file

        try:
            with open(geojson_fn, 'w+') as dest:
                dest.write(json.dumps(geojson, indent=4))

        # These should be raised in the build_geojson_layers() function
        # if that function fails to produce valid geojson
        except AssertionError:
            print('Error: Invalid TopoJSON')
        except ValueError as e:
            print('Error: Invalid TopoJSON')
            print(f'{e}')
        except IOError:
            print('Error: Issue reading file')


def build_geojson_layers(topology: dict) -> dict:
    """Convert the data in the topology dict to GeoJSON"""
    layers = list(topology['objects'].keys())
    scale = topology['transform']['scale']
    translate = topology['transform']['translate']

    geojson_layers = {}
    for layer in layers:
        features = topology['objects'][layer]['geometries']

        fc = {'type': "FeatureCollection", 'features': []}

        for index, feature in enumerate(features):
            if feature.get('id'):
                index = feature.get('id')

            f = {'id': index, 'type': "Feature"}
            f['properties'] = feature['properties'].copy()

            geommap = geometry(feature, topology['arcs'], scale, translate)
            geom = asShape(geommap).buffer(0)
            assert geom.is_valid
            f['geometry'] = geom.__geo_interface__

            fc['features'].append(f)

        geojson_layers[layer] = fc

    return geojson_layers


def geometry(obj, topology_arcs, scale=None, translate=None) -> dict:
    """Converts a topology object to a geometry object.

    The topology object is a dict with 'type' and 'arcs' items, such as
    {'type': "LineString", 'arcs': [0, 1, 2]}.
    See the coordinates() function for a description of the other three
    parameters.
    """
    return {
        "type": obj['type'],
        "coordinates": coordinates(
            obj['arcs'], topology_arcs, scale, translate
        )
    }


def coordinates(arcs, topology_arcs, scale=None, translate=None) -> list:
    """Return GeoJSON coordinates for the sequence(s) of arcs.

    The arcs parameter may be a sequence of ints, each the index of a
    coordinate sequence within topology_arcs
    within the entire topology -- describing a line string, a sequence of
    such sequences -- describing a polygon, or a sequence of polygon arcs.

    The topology_arcs parameter is a list of the shared, absolute or
    delta-encoded arcs in the dataset.
    The scale and translate parameters are used to convert from delta-encoded
    to absolute coordinates. They are 2-tuples and are usually provided by
    a TopoJSON dataset.
    """
    if isinstance(arcs[0], int):
        coords = [
            list(
                rel2abs(
                    topology_arcs[arc if arc >= 0 else ~arc],
                    scale,
                    translate
                )
            )[::arc >= 0 or -1][i > 0:] for i, arc in enumerate(arcs)]
        return list(chain.from_iterable(coords))
    elif isinstance(arcs[0], (list, tuple)):
        return list(
            coordinates(arc, topology_arcs, scale, translate) for arc in arcs)
    else:
        raise ValueError("Invalid input %s", arcs)


def rel2abs(arc, scale=None, translate=None):
    """Yields absolute coordinate tuples from a delta-encoded arc.
    If either the scale or translate parameter evaluate to False, yield the
    arc coordinates with no transformation."""
    if scale and translate:
        a, b = 0, 0
        for ax, bx in arc:
            a += ax
            b += bx
            yield scale[0] * a + translate[0], scale[1] * b + translate[1]
    else:
        for x, y in arc:
            yield x, y

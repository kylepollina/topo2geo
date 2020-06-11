"""
topo2geo/core.py

Authors:
    Sean Gillies
    Matthew Perry
    Kyle Pollina

Sources:
    https://gist.github.com/perrygeo/1e767e42e8bc54ad7262
    https://github.com/sgillies/topojson/blob/master/topojson.py
"""

import os
import json
from itertools import chain

import click
from shapely.geometry import asShape

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help']
}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('input_file')
@click.argument('output_file')
def main(input_file, output_file):
    """
    CLI tool to convert TopoJSON to GeoJSON
    """
    if os.path.exists(input_file) is False:
        print(f'Error: Input file {input_file} does not exist.')
        return

    geojson_layers = to_geojson(input_file)

    for layer, geojson in geojson_layers.items():
        try:
            with open(f'{layer}_{output_file}', 'w+') as dest:
                dest.write(json.dumps(geojson))
        except AssertionError:
            print('Error: Invalid TopoJSON')
        except ValueError as e:
            print('Error: Invalid TopoJSON')
            print(f'{e}')
        except IOError:
            print('Error: Issue reading file')


def geometry(obj, topology_arcs, scale=None, translate=None):
    """Converts a topology object to a geometry object.

    The topology object is a dict with 'type' and 'arcs' items, such as
    {'type': "LineString", 'arcs': [0, 1, 2]}.
    See the coordinates() function for a description of the other three
    parameters.
    """
    return {
        "type": obj['type'],
        "coordinates": coordinates(
            obj['arcs'], topology_arcs, scale, translate)}


def coordinates(arcs, topology_arcs, scale=None, translate=None):
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


def to_geojson(topojson_path):
    """Convert the data in topojson_path to GeoJSON"""
    with open(topojson_path, 'r') as fh:
        f = fh.read()
        topology = json.loads(f)

    layers = list(topology['objects'].keys())
    scale = topology['transform']['scale']
    translate = topology['transform']['translate']

    seperate_layers = {}
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

        seperate_layers[layer] = fc

    return seperate_layers


# topo2geo

CLI for converting [TopoJSON](https://en.wikipedia.org/wiki/GeoJSON#TopoJSON) files to [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON)

### Installation

```
pip install topo2geo
```

Depends on [shapely](https://pypi.org/project/Shapely/) and [click](https://pypi.org/project/click/)

### Usage

```
$ topo2geo input.topojson output.geojson
```

### Multilayered Topojsons
If the topojson contains mulitple layers (i.e. there are multiple values in the "objects" key). Then seperate geojson files will be output with the layer name. 

For example a topojson containing states and counties:
```
{
    "type": "Topology",
    "objects": {
        "county": {
            "type": "GeometryCollection",
            "geometries": [...]
        },
        "state": {
            "type": "GeometryCollection",
            "geometries": [...]
        }
    }
}
```
would produce two geojson files, `output_geo_county.json` and `output_geo_state.json`

### Troubleshooting
If you experience a "segmentation fault" one thing to try is explained [here](https://github.com/Toblerity/Shapely#source-distributions):
```
pip install shapely --no-binary shapely
```

### Credits
Originally written by [sgillies](https://github.com/sgillies) and [perrygeo](https://github.com/perrygeo). Converted to Python3 and packaged into a CLI by [kylepollina](https://github.com/kylepollina).

Sources:
* https://gist.github.com/perrygeo/1e767e42e8bc54ad7262
* https://github.com/sgillies/topojson/blob/master/topojson.py

-------

License - https://github.com/topojson/topojson/blob/master/LICENSE.md

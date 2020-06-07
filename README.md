
# topo2geo

CLI for converting TopoJSON files to GeoJSON

### Installation

```
pip install topo2geo
```

Depends on [shapely](https://pypi.org/project/Shapely/) and [click](https://pypi.org/project/click/)

### Usage

```
[~]$ topo2geo input.topojson output.geojson
```

### Troubleshooting
If you experience a "segmentation fault" one thing to try is explained [here](https://pypi.org/project/Shapely/):
```
pip install shapely --no-binary shapely
```
### Credits
Originally written by [sgillies](https://github.com/sgillies) and [perrygeo](https://github.com/perrygeo). Converted to Python3 and packaged into a CLI by [kylepollina](https://github.com/kylepollina).

Sources:
* https://gist.github.com/perrygeo/1e767e42e8bc54ad7262
* https://github.com/sgillies/topojson/blob/master/topojson.py

-------

[License](https://github.com/topojson/topojson/blob/master/LICENSE.md)

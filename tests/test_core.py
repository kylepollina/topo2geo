
import json
import pytest
import filecmp
import os

from topo2geo import core

def test_end_to_end():
    core.topo2geo('tests/data/hawaii.topojson', '/tmp/test.geojson')
    assert filecmp.cmp('tests/data/hawaii.geojson', '/tmp/test.geojson')
    os.remove('/tmp/test.geojson')


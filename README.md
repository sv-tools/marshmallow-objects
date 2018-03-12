marshmallow-objects
===================
[![Build Status](https://travis-ci.org/SVilgelm/marshmallow-objects.svg?branch=master)](https://travis-ci.org/SVilgelm/marshmallow-objects)
[![codecov](https://codecov.io/gh/SVilgelm/marshmallow-objects/branch/master/graph/badge.svg)](https://codecov.io/gh/SVilgelm/marshmallow-objects)
[![PyPI version](https://badge.fury.io/py/marshmallow-objects.svg)](https://badge.fury.io/py/marshmallow-objects)

**Marshmallow Objects and Models**

Serializing/Deserializing Python objects using [Marshmallow](https://github.com/marshmallow-code/marshmallow) library.

```python
import marshmallow_objects as marshmallow


class Artist(marshmallow.Model):
    name = marshmallow.fields.Str()


class Album(marshmallow.Model):
    title = marshmallow.fields.Str()
    release_date = marshmallow.fields.Date()
    artist = marshmallow.NestedModel(Artist)


bowie_raw = dict(name='David Bowie')
album_raw = dict(artist=bowie_raw, title='Hunky Dory',
                 release_date='1971-12-17')

album = Album(**album_raw)
print(album.title)
print(album.release_date)
print(album.artist.name)

# Hunky Dory
# 1971-12-17
# David Bowie
```

Get It Now
----------

```bash
$ pip install -U marshmallow-objects
```

Project Links
-------------

* [Marshmallow](https://github.com/marshmallow-code/marshmallow)
* [PyPi](https://pypi.python.org/pypi/marshmallow-objects)
* [Cookbook](https://github.com/SVilgelm/marshmallow-objects/wiki)

License
-------
MIT licensed. See the bundled [LICENSE](LICENSE) file for more details.

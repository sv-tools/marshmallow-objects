# marshmallow-objects

[![Test](https://img.shields.io/github/workflow/status/sv-tools/marshmallow-objects/Test%20Master%20Branch)](https://github.com/sv-tools/marshmallow-objects/actions?query=workflow%3A%22Test+Master+Branch%22)
[![Codecov](https://img.shields.io/codecov/c/github/sv-tools/marshmallow-objects)](https://codecov.io/gh/sv-tools/marshmallow-objects)
[![Version](https://img.shields.io/pypi/v/marshmallow-objects?label=version)](https://pypi.org/project/marshmallow-objects/)
[![Black](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

[Looking for Maintainer](https://github.com/sv-tools/marshmallow-objects/issues/125)

## Marshmallow Objects and Models

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

## Get It Now

```bash
$ pip install -U marshmallow-objects
```

## Project Links

* [Marshmallow](https://github.com/marshmallow-code/marshmallow)
* [PyPi](https://pypi.python.org/pypi/marshmallow-objects)
* [Cookbook](https://github.com/sv-tools/marshmallow-objects/wiki)

## License

MIT licensed. See the bundled [LICENSE](LICENSE) file for more details.

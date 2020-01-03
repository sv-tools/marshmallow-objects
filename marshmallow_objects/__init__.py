from marshmallow import *  # noqa

from marshmallow_objects.models import (  # noqa
    Model,
    NestedModel,
    dump_many,
    dump_many_json,
    dump_many_yaml,
)

fields.Boolean.truthy.update(["y", "Y", "yes", "Yes", "YES", "on", "On", "ON"])  # noqa
fields.Boolean.falsy.update(["n", "N", "no", "No", "NO", "off", "Off", "OFF"])  # noqa

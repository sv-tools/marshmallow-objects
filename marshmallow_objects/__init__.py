from marshmallow import *  # noqa

from marshmallow_objects.models import (  # noqa
    Model, NestedModel, dump_many, dump_many_json, dump_many_yaml, compat)

fields.Boolean.truthy.update(  # noqa
    ['y', 'Y', 'yes', 'Yes', 'YES', 'on', 'On', 'ON'])
fields.Boolean.falsy.update(  # noqa
    ['n', 'N', 'no', 'No', 'NO', 'off', 'Off', 'OFF'])

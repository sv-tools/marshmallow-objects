import collections
import copy
import json
import unittest

try:
    import yaml

    skip_yaml = False
except ImportError:
    skip_yaml = True

import marshmallow_objects as marshmallow


class A(marshmallow.Model):
    test_field = marshmallow.fields.Str(missing='test_value', allow_none=False)
    tag_field = marshmallow.fields.Str(load_only=True)

    @marshmallow.post_load
    def set_tag_field(self, data):
        data.tag_field = data.test_field
        return data

    class Meta:
        ordered = True

    def on_bind_field(self, field_name, field_obj):
        pass

    def handle_error(self, error, data):
        pass


class AMethod(marshmallow.Model):
    yes_no = marshmallow.fields.Method(
        serialize='serialize_yes_no',
        deserialize='deserialize_yes_no',
    )

    def serialize_yes_no(self, obj):
        return 'Yes' if obj else 'No'

    def deserialize_yes_no(self, obj):
        return obj.lower() in ['y', 'yes']


class B(marshmallow.Model):
    test_field = marshmallow.fields.Str(allow_none=True)
    a = marshmallow.NestedModel(A, allow_none=False, required=True)


class C(marshmallow.Model):
    a = marshmallow.NestedModel(A, many=True)


def serialize_context_field(obj, context=None):
    return obj.test_field == context['value']


def deserialize_context_field(obj, context=None):
    return obj == context['value']


class AContext(marshmallow.Model):
    test_field = marshmallow.fields.Str()
    test_context_field = marshmallow.fields.Function(
        serialize=serialize_context_field,
        deserialize=deserialize_context_field)


class BContext(marshmallow.Model):
    test_field = marshmallow.fields.Str()
    a = marshmallow.NestedModel(AContext)


class TestModelMeta(unittest.TestCase):
    def test_schema_name(self):
        self.assertEqual('ASchema', A.__schema_class__.__name__)

    def test_schema_class(self):
        assert issubclass(A.__schema_class__, marshmallow.Schema)

    def test_model_class(self):
        assert issubclass(A.__schema_class__.__model_class__,
                          marshmallow.Model)

    def test_tag_processor(self):
        assert hasattr(A.__schema_class__, 'set_tag_field')

    def test_meta(self):
        assert hasattr(A.__schema_class__, 'Meta')
        self.assertEqual(id(A.Meta), id(A.__schema_class__.Meta))
        assert not hasattr(B, 'Meta')
        assert hasattr(B.__schema_class__, 'Meta')

    def test_on_bind_filed(self):
        self.assertEqual(
            id(A.on_bind_field), id(A.__schema_class__.on_bind_field))

    def test_handle_error(self):
        self.assertEqual(
            id(A.handle_error), id(A.__schema_class__.handle_error))


class TestModel(unittest.TestCase):
    def test_tag_field(self):
        a = A(test_field='tag_value', tag_field='fake')
        self.assertEqual('tag_value', a.tag_field)

    def test_default_value(self):
        a = A()
        self.assertEqual('test_value', a.test_field)

    def test_value(self):
        a = A(test_field='foo')
        self.assertEqual('foo', a.test_field)

    def test_prohibited_none_value(self):
        self.assertRaises(marshmallow.ValidationError, B)

    def test_nested_object(self):
        b = B(a=A(test_field='123'))
        self.assertEqual('123', b.a.test_field)

    def test_nested_dict(self):
        b = B(a=dict(test_field='123'))
        self.assertIsInstance(b.a, A)
        self.assertEqual('123', b.a.test_field)

    def test_nested_dict_many(self):
        c = C(a=[dict(test_field='1'), dict(test_field='2')])
        self.assertEqual(2, len(c.a))

    def test_partial(self):
        self.assertRaises(marshmallow.ValidationError, B)
        b = B(partial=True)
        self.assertIsNone(b.a)

    def test_validate(self):
        b = B.validate({})
        self.assertIn('a', b)

    def test_validate_partial(self):
        class APartial(marshmallow.Model):
            test_field = marshmallow.fields.Str(required=True)
            email = marshmallow.fields.Email()

        a = APartial.validate(dict(email='foo'), partial=True)
        self.assertNotIn('test_field', a)
        self.assertIn('email', a)

    def test_eq(self):
        a1 = A(test_field='1')
        a2 = A(test_field='1')
        self.assertNotEqual(id(a1), id(a2))
        self.assertEqual(a1, a2)

    def test_not_eq(self):
        a1 = A(test_field='1')
        a2 = A(test_field='2')
        self.assertNotEqual(a1, a2)

    def test_not_eq_classes(self):
        class A1(marshmallow.Model):
            pass

        class A2(marshmallow.Model):
            pass

        a1 = A1()
        a2 = A2()
        self.assertNotEqual(a1, a2)

    def test_copy(self):
        a1 = A(test_field='1')
        a2 = copy.copy(a1)
        self.assertNotEqual(id(a1), id(a2))
        self.assertEqual(a1, a2)

    def test_repr(self):
        a = A()
        self.assertIn('test_value', repr(a))

    def test_str(self):
        a = A()
        self.assertIn('test_value', str(a))

    def test_yes_no(self):
        a = AMethod(yes_no='Y')
        self.assertTrue(a.yes_no)
        self.assertEqual({'yes_no': 'Yes'}, a.dump())

        a = AMethod(yes_no='NOOOO')
        self.assertFalse(a.yes_no)

    def test_dump_mode_on(self):
        a = A()
        self.assertFalse(a.__dump_mode__)
        with a.__dump_mode_on__():
            self.assertTrue(a.__dump_mode__)
            with a.__dump_mode_on__():
                self.assertTrue(a.__dump_mode__)
            self.assertTrue(a.__dump_mode__)
        self.assertFalse(a.__dump_mode__)


class TestModelLoadDump(unittest.TestCase):
    def setUp(self):
        self.data = dict(test_field='foo')

    def test_load_dict(self):
        a = A.load(self.data)
        self.assertEqual('foo', a.test_field)

    def test_load_dict_partial(self):
        self.assertRaises(marshmallow.ValidationError, B)
        b = B.load({}, partial=True)
        self.assertIsNone(b.a)

    def test_load_dict_nested(self):
        ddata = dict(test_field='foo', a=dict(test_field='bar'))
        b = B.load(ddata)
        self.assertEqual('foo', b.test_field)
        self.assertEqual('bar', b.a.test_field)

    def test_dump_dict(self):
        a = A(test_field='foo')
        self.assertEqual(self.data, a.dump())

    def test_load_json(self):
        jdata = json.dumps(self.data)
        a = A.load_json(jdata)
        self.assertEqual('foo', a.test_field)

    def test_load_json_partial(self):
        self.assertRaises(marshmallow.ValidationError, B)
        b = B.load_json('{}', partial=True)
        self.assertIsNone(b.a)

    def test_dump_json(self):
        a = A(test_field='foo')
        jdata = json.loads(a.dump_json())
        self.assertEqual(self.data, jdata)

    @unittest.skipIf(skip_yaml, 'PyYaml is not installed')
    def test_load_yaml(self):
        ydata = yaml.dump(self.data)
        a = A.load_yaml(ydata)
        self.assertEqual('foo', a.test_field)

    @unittest.skipIf(skip_yaml, 'PyYaml is not installed')
    def test_load_yaml_partial(self):
        self.assertRaises(marshmallow.ValidationError, B)
        b = B.load_yaml('{}', partial=True)
        self.assertIsNone(b.a)

    @unittest.skipIf(skip_yaml, 'PyYaml is not installed')
    def test_dump_yaml(self):
        a = A(test_field='foo')
        ydata = yaml.load(a.dump_yaml())
        self.assertEqual(self.data, ydata)

    def test_dump_ordered(self):
        a = A(test_field='foo').dump()
        b = B(test_field='foo', a=dict(test_field='bar')).dump()
        self.assertIsInstance(a, collections.OrderedDict)
        self.assertIsInstance(b, dict)


class TestContext(unittest.TestCase):
    def setUp(self):
        self.context = {'value': 'foo'}
        self.data = dict(test_field='foo')
        self.nested_data = dict(a=self.data)

    def test_load_context(self):
        a = AContext.load(self.data, self.context)
        ddata = a.dump()
        self.assertTrue(ddata['test_context_field'])

    def test_context(self):
        a = AContext(context=self.context, **self.data)
        ddata = a.dump()
        self.assertTrue(ddata['test_context_field'])

    def test_no_context(self):
        a = AContext(**self.data)
        self.assertRaises(KeyError, a.dump)

    def test_nested_context(self):
        b = BContext(context=self.context, **self.nested_data)
        self.assertEqual(b.context, b.a.context)
        ddata = b.dump()
        self.assertTrue(ddata['a']['test_context_field'])

    def test_update_context(self):
        b = BContext(context=self.context, **self.nested_data)
        b.context['value'] = 'bar'
        self.assertEqual(b.context, b.a.context)
        ddata = b.dump()
        self.assertFalse(ddata['a']['test_context_field'])

    def test_override_context(self):
        b = BContext(context=self.context, **self.nested_data)
        b.context = {'value': 'bar'}
        self.assertEqual(b.context, b.a.context)
        ddata = b.dump()
        self.assertFalse(ddata['a']['test_context_field'])

    def test_validate_partial(self):
        class APartial(marshmallow.Model):
            test_field = marshmallow.fields.Str(required=True)
            email = marshmallow.fields.Email()

        aa = APartial.validate(
            [dict(email='foo'), dict(email='bar')], many=True, partial=True)
        self.assertEqual(2, len(aa))
        for a in aa.values():
            self.assertNotIn('test_field', a)
            self.assertIn('email', a)


class TestMany(unittest.TestCase):
    def setUp(self):
        self.data = [
            dict(test_field='foo', a=dict(test_field='bar')),
            dict(test_field='foo', a=dict(test_field='bar'))
        ]

    def assert_objects(self, bb):
        self.assertEqual(2, len(bb))
        ids = set()
        for b in bb:
            self.assertEqual('foo', b.test_field)
            self.assertEqual('bar', b.a.test_field)
            b_id = id(b)
            a_id = id(b.a)
            self.assertNotIn(b_id, ids)
            self.assertNotIn(a_id, ids)
            ids.add(b_id)
            ids.add(a_id)

    def test_load_many(self):
        bb = B.load(self.data, many=True)
        self.assert_objects(bb)

    def test_load_many_as_one(self):
        self.assertRaises(marshmallow.ValidationError, B.load, self.data)

    def test_load_many_partial(self):
        self.assertRaises(
            marshmallow.ValidationError,
            B.load,
            data=[{}, {}],
            many=True,
            partial=False)
        bb = B.load([{}, {}], many=True, partial=True)
        self.assertEqual(2, len(bb))
        for b in bb:
            self.assertIsNone(b.test_field)
            self.assertIsNone(b.a)

    def test_load_json(self):
        jdata = json.dumps(self.data)
        bb = B.load_json(jdata, many=True)
        self.assert_objects(bb)

    @unittest.skipIf(skip_yaml, 'PyYaml is not installed')
    def test_load_yaml(self):
        ydata = yaml.dump(self.data, default_flow_style=False)
        bb = B.load_yaml(ydata, many=True)
        self.assert_objects(bb)

    def test_dump_same_classes(self):
        bb = B.load(self.data, many=True)
        ddata = marshmallow.dump_many(bb)
        self.assertEqual(self.data, ddata)

    def test_dump_different_classes(self):
        adata = dict(test_field='foo')
        odata = [B.load(self.data, many=True), A(**adata)]
        ddata = marshmallow.dump_many(odata)
        self.assertEqual([self.data, adata], ddata)

    def test_dump_fake(self):
        self.assertRaises(
            marshmallow.ValidationError, marshmallow.dump_many, data='fake')

    def test_dump_context(self):
        context = {'value': 'bar'}
        bb = BContext.load(self.data, context=context, many=True)
        ddata = marshmallow.dump_many(bb, context={'value': 'foo'})
        context_id = id(context)
        for b in bb:
            self.assertEqual(context_id, id(b.context))
            self.assertEqual(context_id, id(b.a.context))
        for b in ddata:
            self.assertFalse(b['a']['test_context_field'])

    def test_dump_json(self):
        bb = B.load(self.data, many=True)
        jdata = marshmallow.dump_many_json(bb)
        ddata = json.loads(jdata)
        self.assertEqual(self.data, ddata)

    @unittest.skipIf(skip_yaml, 'PyYaml is not installed')
    def test_dump_yaml(self):
        bb = B.load(self.data, many=True)
        ydata = marshmallow.dump_many_yaml(bb)
        ddata = yaml.load(ydata)
        self.assertEqual(self.data, ddata)


class TestIni(unittest.TestCase):
    def setUp(self):
        self.data = """
[DEFAULT]
test_field = foo

[a]
test_field = bar
""".strip()

    def test_load(self):
        b = B.load_ini(self.data)
        self.assertEqual('foo', b.test_field)
        self.assertEqual('bar', b.a.test_field)

    def test_dump(self):
        b = B(test_field='foo', a=dict(test_field='bar'))
        self.assertEqual(self.data, b.dump_ini())


class InitModel(marshmallow.Model):
    count = 0

    def __init__(self):
        super(InitModel, self).__init__()
        self.count = self.count + 1


class TestInit(unittest.TestCase):
    def test_init(self):
        obj = InitModel()
        self.assertEqual(1, obj.count)


class OptionalModel(marshmallow.Model):
    str_field = marshmallow.fields.Str(missing='foo')
    int_field = marshmallow.fields.Int(default=-1)


class TestOptionalModel(unittest.TestCase):
    def test_partial_model(self):
        model = OptionalModel(partial=True)
        self.assertIsNone(model.str_field)
        self.assertIsNone(model.int_field)

    def test_model_default_and_missing_fields(self):
        model = OptionalModel()
        self.assertEqual('foo', model.str_field)
        self.assertIsNone(model.int_field)

    def test_model_present_fields(self):
        model = OptionalModel(str_field='bar', int_field=1)
        self.assertEqual('bar', model.str_field)
        self.assertEqual(1, model.int_field)

    def test_dump(self):
        ddata = OptionalModel().dump()
        self.assertEqual({'int_field': -1, 'str_field': 'foo'}, ddata)

    def test_dump_partial(self):
        ddata = OptionalModel(partial=True).dump()
        self.assertEqual({'int_field': -1}, ddata)

    def test_dump_changed_missing_field(self):
        obj = OptionalModel(partial=True)
        obj.int_field = 1
        ddata = obj.dump()
        self.assertEqual({'int_field': 1}, ddata)

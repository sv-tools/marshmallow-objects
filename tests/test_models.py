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


class B(marshmallow.Model):
    test_field = marshmallow.fields.Str(allow_none=True)
    a = marshmallow.NestedModel(A, allow_none=False, required=True)


class C(marshmallow.Model):
    a = marshmallow.NestedModel(A, many=True)


class TestModelMeta(unittest.TestCase):
    def test_schema_name(self):
        self.assertEqual('ASchema', A.__schema_class__.__name__)

    def test_schema_class(self):
        assert issubclass(A.__schema_class__, marshmallow.Schema)

    def test_model_class(self):
        assert issubclass(A.__schema_class__.__model_class__,
                          marshmallow.Model)


class TestModel(unittest.TestCase):
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


class TestModelLoadDump(unittest.TestCase):
    def setUp(self):
        self.data = dict(test_field='foo')

    def test_load_dict(self):
        a = A.load(self.data)
        self.assertEqual('foo', a.test_field)

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
    def test_dump_yaml(self):
        a = A(test_field='foo')
        ydata = yaml.load(a.dump_yaml())
        self.assertEqual(self.data, ydata)


class AContext(marshmallow.Model):
    test_field = marshmallow.fields.Str()
    test_context_field = marshmallow.fields.Function(
        lambda obj, context: obj.test_field == context['value'])


class BContext(marshmallow.Model):
    a = marshmallow.NestedModel(AContext)


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

import json


class Filter(object):
    def __init__(self, name, op='eq', **kwargs):
        val = kwargs.pop('val', None)
        field = kwargs.pop('field', None)

        if val is not None and field is not None:
            raise Exception('`val` and `field` can not be specified together')

        if val is None and field is None:
            raise Exception('either `val` or `field` needs to be specified')

        if '__' in name:
            self.name = name.split('__', 1)[0]
            self.op = 'has'
            self.val = json.loads(
                json.dumps(
                    Filter(
                        name=name.split('__', 1)[1],
                        op=op,
                        val=val,
                        field=field
                    ),
                    cls=FilterEncoder
                )
            )
        else:
            self.name = name
            self.op = op
            self.val = val
            self.field = field


class FilterEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Filter):
            x = dict(name=obj.name, op=obj.op)

            if obj.val:
                x['val'] = obj.val
            else:
                x['field'] = obj.field

            return x

        return json.JSONEncoder.default(self, obj)

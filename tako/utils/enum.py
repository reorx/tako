KV = type('KV', (object, ), {})


class SimpleEnumMeta(type):
    def __new__(mcs, name, bases, attrs):
        keys = []
        values = []
        value_key_map = {}
        for k, v in attrs.items():
            if k.startswith('_'):
                continue
            if v is KV:
                v = k
                attrs[k] = v
            keys.append(k)
            values.append(v)
            value_key_map[v] = k
        attrs['_keys'] = keys
        attrs['_values'] = values
        attrs['_value_key_map'] = value_key_map
        return type.__new__(mcs, name, bases, attrs)


class SimpleEnum(object, metaclass=SimpleEnumMeta):
    @classmethod
    def keys(cls):
        return cls._keys

    @classmethod
    def values(cls):
        return cls._values

    @classmethod
    def items(cls):
        return list(zip(cls._keys, cls._values))

    @classmethod
    def value_to_key(cls, value):
        return cls._value_key_map[value]

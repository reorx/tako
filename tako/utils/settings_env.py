import environ


class DefaultOptions:
    env_file = None
    prefix = None


class EnvMeta(type):
    def __new__(mcs, name, bases, attrs):
        kwargs = {}
        opts = DefaultOptions
        for k, v in attrs.items():
            if k.startswith('_'):
                continue
            if k == 'Meta':
                opts = v
                continue
            # class methods
            if k in ['pretty_format']:
                continue
            kwargs[k] = v
        # create Env instance
        env = environ.Env(**kwargs)
        # read env file
        if opts.env_file:
            print(f'read env file: {opts.env_file}')
            env.read_env(opts.env_file)
        attrs['_env'] = env
        envs = {}
        for k in kwargs:
            # get env value
            v = env(k)
            attrs[k] = v
            envs[k] = v
        attrs['_envs'] = envs
        return type.__new__(mcs, name, bases, attrs)


class EnvBase(object, metaclass=EnvMeta):
    @classmethod
    def pretty_format(cls):
        kvs = [f'{k}={v}' for k, v in cls._envs.items()]
        return f'{cls.__name__}<{", ".join(kvs)}>'

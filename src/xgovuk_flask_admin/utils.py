def widget_for_sqlalchemy_type(*args):
    def _inner(func):
        func._widget_converter_for = frozenset(args)
        return func

    return _inner

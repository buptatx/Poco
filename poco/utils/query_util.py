# coding=utf-8
from __future__ import unicode_literals
__author__ = 'lxn3032'


__all__ = ['query_expr']


TranslatePred = {
    'attr=': '=',
    'attr.*=': ' matches ',
}


TranslateOp = {
    'and': '&',
    'or': '|',
    '/': '/',
    '>': '>',
    '-': '-',
}


def query_expr(query):
    op = query[0]
    if op in ('/', '>', '-'):
        return TranslateOp[op].join([query_expr(q) for q in query[1]])
    elif op == 'index':
        return '{}[{}]'.format(query_expr(query[1][0]), query[1][1])
    elif op in ('and', 'or'):
        exprs = []
        for subquery in query[1]:
            pred, (k, v) = subquery
            if k == 'name':
                exprs.append(v)
            else:
                exprs.append('{}{}{}'.format(k, TranslatePred[pred], v))
        return TranslateOp[op].join(exprs)
    else:
        raise RuntimeError('Bad query format. "{}"'.format(repr(query)))


def ensure_unicode(value):
    # py3 to be supported
    if isinstance(value, str):
        return value.decode("utf-8")
    else:
        return value


def build_query(name, **attrs):
    query = []
    if name is not None:
        name = ensure_unicode(name)
        attrs['name'] = name
    for attr_name, attr_val in attrs.items():
        attr_val = ensure_unicode(attr_val)
        if attr_name.startswith('_'):
            raise NameError("Cannot use private attribute '{}' in your Query Expression as private attributes do not "
                            "have stable values.".format(attr_name))
        elif attr_name.endswith('Matches'):
            attr_name = attr_name[:-7]  # textMatches -> (attr.*=, text)
            op = 'attr.*='
        else:
            op = 'attr='
        query.append((op, (attr_name, attr_val)))
    return 'and', tuple(query)

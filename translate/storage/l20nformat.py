import sys
print(sys.path);

from translate.storage import base
from l20n.format.parser import L20nParser
import l20n.format.ast as ast
from l20n.format.serializer import Serializer


class l20nunit(base.TranslationUnit):
    """Single L20n Entity"""

    def __init__(self, source=''):
        super(l20nunit, self).__init__(source)
        self.id = ''
        self.value = ''
        self.attrs = []
        self.value_index = None
        self.source = source
        pass

    def getsource(self):
        return self.id

    def setsource(self, source):
        self.id = source

    source = property(getsource, setsource)

    def gettarget(self):
        return self.value

    def settarget(self, target):
        self.value = target

    target = property(gettarget, settarget)

    def getid(self):
        return self.id

    def setid(self, new_id):
        self.id = new_id

    def get_index(self, index):
        if index is None:
            return None

        l20n_index = []
        for i in index:
            if i['name'] == '@cldr.plural':
                glob = ast.Global(ast.Identifier('cldr'))
                prop = ast.PropertyExpression(glob, ast.Identifier('plural'))
                args = []
                for a in i['args']:
                    if a['type'] == 'variable':
                        args.append(ast.Variable(ast.Identifier(a['name'])))
                call = ast.CallExpression(prop, args)
                l20n_index.append(call)
        return l20n_index



    def get_value(self, value):
        if isinstance(value, dict):
            ret = ast.Hash()
            for k, v in value.items():
                id = ast.Identifier(k)
                value = self.get_value(v)
                hashItem = ast.HashItem(id, value, False)
                ret.items.append(hashItem)
            return ret
        elif isinstance(value, str) or isinstance(value, unicode):
            return ast.String(value)

    def getoutput(self):
        id = ast.Identifier(self.id)
        value = self.get_value(self.value)
        index = self.get_index(self.value_index)
        entity = ast.Entity(id, value, index)

        serializer = Serializer()

        return serializer.dumpEntity(entity)

class l20nfile(base.TranslationStore):
    UnitClass = l20nunit

    def __init__(self, inputfile=None):
        super(l20nfile, self).__init__(unitclass=self.UnitClass)
        self.filename = getattr(inputfile, 'name', '')
        if inputfile is not None:
            l20nsrc = inputfile.read()
            self.parse(l20nsrc)
            self.makeindex()

    def parse_index(self, l20n_indexes):
        if l20n_indexes is None:
            return None

        indexes = []

        for index in l20n_indexes:
            if index.type == 'CallExpression' and \
               index.callee.type == 'PropertyExpression' and \
               index.callee.exp.type == 'Identifier' and \
               index.callee.exp.name == 'plural' and \
               index.callee.idref.type == 'Global' and \
               index.callee.idref.name.name == 'cldr':
                indexes.append({'name': '@cldr.plural',
                                'args': [{
                                    'type': 'variable',
                                    'name': index.args[0].name.name
                                }]})
            else:
                indexes.append(None)
        return indexes

    def parse_value(self, value):
        if isinstance(value, ast.String):
            return value.source
        elif isinstance(value, ast.Hash):
            ret = {}
            for hashItem in value.items:
                ret[hashItem.id.name] = self.parse_value(hashItem.value)
            return ret

    def parse(self, l20nsrc):
        parser = L20nParser()
        ast = parser.parse(l20nsrc)

        for entry in ast.body:
            newl20n = l20nunit()
            newl20n.id = entry.id.name
            newl20n.value = self.parse_value(entry.value)
            newl20n.value_index = self.parse_index(entry.index)

            for attr in entry.attrs:
                newl20n.attrs.append({
                    'id': attr.id.name,
                    'value': self.parse_value(attr.value),
                    'index': self.parse_index(attr.index)
                })

            self.units.append(newl20n)

    def __str__(self):
        lines = []
        for unit in self.units:
            lines.append(unit.getoutput())
        uret = u"\n".join(lines)
        return uret

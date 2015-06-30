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

    def getoutput(self):
        id = ast.Identifier(self.id)
        value = self.value
        entity = ast.Entity(id, value)

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

    def parse(self, l20nsrc):
        parser = L20nParser()
        ast = parser.parse(l20nsrc)

        for entry in ast.body:
            newl20n = l20nunit()
            newl20n.id = entry.id.name
            newl20n.value = entry.value
            newl20n.value_index = entry.index

            self.units.append(newl20n)

    def __str__(self):
        lines = []
        for unit in self.units:
            lines.append(unit.getoutput())
        uret = u"\n".join(lines)
        return uret

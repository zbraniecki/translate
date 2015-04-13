from translate.storage import base
from l20nparser import L20nParser

class l20nunit(base.TranslationUnit):
    """Single L20n Entity"""

    def __init__(self, source=''):
        super(l20nunit, self).__init__(source)
        self.name = ''
        self.value = ''
        self.source = source
        pass

    def getsource(self):
        return self.value

    def setsource(self, source):
        self.value = source

    source = property(getsource, setsource)

    def gettarget(self):
        return self.translation

    def settarget(self, target):
        self.translation = target

    target = property(gettarget, settarget)

    def getid(self):
        pass

    def setid(self):
        pass

    def getoutput(self):
        return "%(key)s = %(value)s" % {
            'value': self.value,
            'key': self.name
        }

    def addlocation(self, location):
        pass

    def getlocations(self):
        return [self.name]

    def addnote(self, text):
        pass

    def getnotes(self):
        pass

    def removenotes(self):
        pass

    def isblank(self):
        pass

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

        for entry in ast:
            newl20n = l20nunit()
            newl20n.name = entry['$i']
            newl20n.value = entry['$v']
            self.units.append(newl20n)

    def __str__(self):
        lines = []
        for unit in self.units:
            lines.append(unit.getoutput())
        uret = u"".join(lines)
        return uret

from translate.storage import base

class l20nunit(base.TranslationUnit):
    def __init__(self, source=""):
        pass

    def getsource(self):
        pass

    def setsource(self, source):
        pass

    source = property(getsource, setsource)

    def gettarget(self):
        pass

    def settarget(self, target):
        pass

    target = property(gettarget, settarget)

    def getid(self):
        pass

    def setid(self):
        pass

    def getoutput(self):
        pass

    def addlocation(self, location):
        pass

    def getlocations(self):
        return

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
        pass

    def parse(self, l20nsrc):
        pass

    def __str__(self):
        pass

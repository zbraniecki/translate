import string
import re
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
        self.filename = getattr(inputfile, 'name', '')
        if inputfile is not None:
            l20nsrc = inputfile.read()
            self.parse(l20nsrc)
            self.makeindex()

    def parse(self, l20nsrc):
        parser = L20nParser()
        ast = parser.parse(l20nsrc)
        print(ast)
        pass

    def __str__(self):
        pass

class ParserError(Exception):
    def __init__(self, message, pos, context):
        self.name = 'ParserError'
        self.message = message
        self.pos = pos
        self.context = context

class L20nParser():
    def __init__(self):
        self._patterns = {
            'identifier': re.compile('[A-Za-z_]\w*')
        }

    def parse(self, string):
        self._source = string
        self._index = 0
        self._length = len(string)

        return self.getL20n()

    def getAttributes(self):
        attrs = {}

        while True:
            attr = self.getKVPWithIndex()
            attrs[attr[0]] = attr[1]
            ws1 = self.getRequiredWS()
            ch = self._source[self._index]
            if ch == '>':
                break
            elif not ws1:
                raise self.error('Expected ">"')
        return attrs

    def getKVP(self, type):
        key = self.getIdentifier()
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()
        return {
            'type': type,
            'key': key,
            'value': self.getValue()
        }

    def getKVPWithIndex(self, type=None):
        key = self.getIdentifier()
        index = []

        if self._source[self._index] == '[':
            self._index += 1
            self.getWS()
            index = self.getItemList(self.getExpression, ']')
        self.getWS()
        if self._source[self._index] != ':':
            raise self.error('Expected ":"')
        self._index += 1
        self.getWS()
        return {
            'type': type,
            'key': key,
            'value': self.getValue(),
            'index': index
        }

    def getHash(self):
        self._index += 1
        self.getWS()
        hasDefItem = False
        hash = []
        while True:
            defItem = False
            if self._source[self._index] == '*':
                self._index += 1
                if hasDefItem:
                    raise self.error('Default item redefinition forbidden')
                defItem = True
                hasDefItem = True
            hi = self.getKVP('HashItem')
            hi['default'] = defItem
            hash.append(hi)
            self.getWS()

            comma = self._source[self._index] == ','
            if comma:
                self._index += 1
                self.getWS()
            if self._source[self._index] == '}':
                self._index += 1
                break
            if not comma:
                raise self.error('Expected "}"')
        return {
            'type': 'Hash',
            'content': hash
        }

    def unescapeString(self, str):
        return str

    def getString(self, opchar):
        buf = ""
        body = []
        oplen = len(opchar)

        self._index += oplen

        while True:
            ch = self._source[self._index]
            # unescape
            if ch == '\\':
                self._index += 1
                ch2 = self._source[self._index]
                if ch2 == 'u':
                    # unescape unicode \uXXXX chars
                    buf += unichr(int(self._source[self._index+1:self._index+5], 16))
                    self._index += 5
                else:
                    #otherwise just take the next char
                    buf += ch2
                    self._index += 1
                ch = self._source[self._index]
            # expression
            if ch == '{':
                if self._source[self._index+1] == '{':
                    if len(buf):
                        body.append({
                            'type': 'String',
                            'content': buf
                        })
                        buf = ""
                    self._index += 2
                    self.getWS()
                    body.append(self.getExpression())
                    self.getWS()
                    self._index += 2
                    ch = self._source[self._index]
            # close string, depending on if oplen is 1 or 3
            if oplen == 1:
                if ch == opchar:
                    self._index += oplen
                    break
            else:
                if self._source[self._index:self._index+3] == opchar:
                    self._index += oplen
                    break
            # or just add a char to a buffer
            buf += ch
            self._index += 1
            if self._index >= self._length:
                raise self.error('Unclosed string literal')
                break

        if len(buf):
            if len(body):
                # if there's body and a leftover, add the leftover
                body.append({
                    'type': 'String',
                    'content': buf
                })
            else:
                # otherwise return it as a simple string
                return {
                    'type': 'String',
                    'content': buf
                }
        # if not returned as a simple string, return ComplexString
        return {
            'type': 'ComplexString',
            'content': body
        }

    def getValue(self, optional, ch=None, index=None):
        if ch is None:
            if self._length > self._index:
                ch = self._source[self._index]
            else:
                ch = None
        if ch == "'" or ch == '"':
            val = self.getString(ch)
        if ch == '{':
            val = self.getHash()

        if val is None:
            if not optional:
                raise self.error('Unknown value type')
            return None

        if index:
            return {
                '$v': val,
                '$x': index
            }
        return val

    def getRequiredWS(self):
        pos = self._index
        cc = ord(self._source[self._index])

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            self._index += 1
            if self._length <= self._index:
                break
            cc = ord(self._source[self._index])
        return pos != self._index

    def getWS(self):
        cc = ord(self._source[self._index])

        while cc == 32 or cc == 10 or cc == 9 or cc == 13:
            self._index += 1
            if self._length <= self._index:
                break
            cc = ord(self._source[self._index])

    def getIdentifier(self):
        reId = self._patterns['identifier']

        match = reId.match(self._source[self._index:])

        self._index += match.end()
        return match.group(0)


    def getEntity(self, id, index):
        entity = {'$i': id}

        if index:
            entity['$x'] = index

        if not self.getRequiredWS():
            raise self.error('Expected white space')

        ch = self._source[self._index]
        value = self.getValue(index is None, ch)
        attrs = None

        if value is None:
            if ch == '>':
                raise self.error('Expected ">"')
            attrs = self.getAttributes()
        else:
            entity['$v'] = value
            ws1 = self.getRequiredWS()
            if not self._source[self._index] == '>':
                if not ws1:
                    raise self.error('Expected ">"')
                attrs = self.getAttributes()

        self._index += 1
        if attrs:
            for key in attrs:
                entity[key] = attrs[key]

        return entity

    def getEntry(self):
        # 66 === '<'
        if ord(self._source[self._index]) == 60:
            self._index += 1
            id = self.getIdentifier()
            # 91 === '['
            if ord(self._source[self._index]) == 91:
                self._index += 1
                return self.getEntity(id, self.getIndex())
            return self.getEntity(id, None)
        raise self.error('Invalid entry')

    def getL20n(self):
        ast = []

        self.getWS()

        while self._index < self._length:
            ast.append(self.getEntry())
            if self._index < self._length:
                self.getWS()
        return ast

    def getIndex(self):
        pass

    def parseString(self, str):
        return str

    def error(self, message, pos=None):
        if pos is None:
            pos = self._index
        start = self._source.rfind('<', pos - 1)
        lastClose = self._source.rfind('>', pos - 1)
        start = lastClose + 1 if lastClose > start else start
        context = self._source[start:pos + 10]

        msg = '%s at pos %s: "%s"' % (message, pos, context)
        return ParserError(msg, pos, context)

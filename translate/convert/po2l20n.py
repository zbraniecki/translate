#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2002-2015 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Convert Gettext PO localization files to .l20n files.
"""

import logging
import re
import warnings

from translate.convert import accesskey, convert
from translate.lang import data
from translate.misc import quote
from translate.storage import po, l20nformat

import l20n.format.ast as ast

L20N_PLURAL_RE = re.compile("<l20n:plural>@cldr.plural\(\$([^\s]+)\)</l20n>")


logger = logging.getLogger(__name__)


class po2l20n:

    def __init__(self, templatefile, inputstore, includefuzzy=False):
        self.templatestore = l20nformat.l20nfile(templatefile)
        self.inputstore = inputstore
        self.includefuzzy = includefuzzy
        self.lang = self.inputstore.gettargetlanguage()

    def mergeunit(self, unit):
        pass

    def create_plural(self, variable):
        glob = ast.Global(ast.Identifier('cldr'))
        prop = ast.PropertyExpression(glob, 'plural')
        call = ast.CallExpression(prop, [ast.Variable(ast.Identifier(variable))])
        return call

    def convertunit(self, unit):
        l20n_unit = l20nformat.l20nunit()
        if not unit.istranslated() and not self.includefuzzy:
            return None
        l20n_unit.setid(unit.getlocations()[0])
        if unit.hasplural():
            l20n_unit.value_index = [self.create_plural(
                L20N_PLURAL_RE.findall(unit.getnotes("developer"))[0])]

            l20n_unit.value = ast.Hash()
            if self.lang in data.cldr_plural_languages:
                categories = data.cldr_plural_languages[self.lang]
            else:
                logger.error("'Language:' is unset in header or language ('%s') "
                             "is not defined for CLDR plural forms defaulting "
                             "to ['one', 'other']" % self.lang)
                categories = ['one', 'other']
            if len(categories) != len(unit.target.strings):
                logger.warning("Warning: PO plurals does not match expected "
                               "CLDR plurals")
            for category, text in zip(categories, unit.target.strings):
                id = ast.Identifier(category)
                value = ast.String(str(text))
                defItem = False
                hashItem = ast.HashItem(id, value, defItem)
                l20n_unit.value.items.append(hashItem)
        else:
            l20n_unit.value = ast.String(unit.target)
        return l20n_unit

    def mergestore(self):
        pass

    def convertstore(self):
        outputstore = l20nformat.l20nfile()
        for unit in self.inputstore.units:
            newunit = self.convertunit(unit)
            if newunit is not None:
                outputstore.addunit(newunit)
        return outputstore


def convertl20n(inputfile, outputfile, templatefile, includefuzzy=False,
                outputthreshold=None):
    inputstore = po.pofile(inputfile)

    if templatefile is None:
        convertor = po2l20n(templatefile, inputstore, includefuzzy)
        outputl20n = convertor.convertstore()
    else:
        convertor = po2l20n(templatefile, inputstore, includefuzzy)
        outputl20n = convertor.mergestore()
    outputfile.write(str(outputl20n))
    return 1

formats = {
    ("po", "l20n"): ("l20n", convertl20n),
    ("po"): ("l20n", convertl20n),
}


def main(argv=None):
    # handle command line options
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_fuzzy_option()
    parser.run(argv)

if __name__ == '__main__':
    main()

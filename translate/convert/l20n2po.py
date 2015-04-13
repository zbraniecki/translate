#!/usr/bin/env python

"""Convert Mozilla .l20n files to Gettext PO localization files.

See: http://docs.translatehouse.org/projects/translate-toolkit/en/latest/commands/l20n2po.html
for examples and usage instructions.
"""

from translate.storage import po, l20n

class l20n2po:
    """convert a .l20n file to a .po file for handling the
    translation."""

    def __init__(self, blankmsgstr=False, duplicatestyle="msgctxt"):
        pass

    def convertl20nunit(self, store, unit):
        po_unit = po.pounit(encoding="UTF-8")
        po_unit.source = unit.source
        po_unit.setid(unit.getid())
        return po_unit

    def convertstore(self, l20n_store):
        """converts a .l20n file to a .po file..."""
        target_store = po.pofile()
        targetheader = target_store.header()
        targetheader.addnote("extracted from %s" % l20n_store.filename,
                             "developer")
        l20n_store.makeindex()
        for l20nunit in l20n_store.units:
            pounit = self.convertl20nunit(l20n_store, l20nunit)
            target_store.addunit(pounit)
        return target_store
        

def convertl20n(inputfile, outputfile, templatefile,
                pot=False, duplicatestyle="msgctxt"):
    inputstore = l20n.l20nfile(inputfile)
    convertor = l20n2po(blankmsgstr=pot,
                        duplicatestyle=duplicatestyle)
    if templatefile is None:
        outputstore = convertor.convertstore(inputstore)
    else:
        templatestore = l20n.l20nfile(templatefile)
        outputstore = convertor.mergestore(templatestore, inputstore)
    if outputstore.isempty():
        return 0
    outputfile.write(str(outputstore))
    return 1

formats = {
    "l20n": ("po", convertl20n),
    ("l20n", "l20n"): ("po", convertl20n),
}

def main(argv=None):
    from translate.convert import convert

    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         usepots=True, description=__doc__)
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)


if __name__ == '__main__':
    main()

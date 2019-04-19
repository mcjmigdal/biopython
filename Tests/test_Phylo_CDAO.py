# Copyright (C) 2013 by Ben Morris (ben@bendmorris.com)
# based on code by Eric Talevich (eric.talevich@gmail.com)
# This code is part of the Biopython distribution and governed by its
# license. Please see the LICENSE file that should have been included
# as part of this package.

"""Unit tests for the CDAO and CDAOIO modules."""

import os
import tempfile
import unittest
from Bio import MissingExternalDependencyError

import Bio.Phylo as bp
from Bio.Phylo import CDAO
try:
    from Bio.Phylo import CDAOIO
except ImportError:
    raise MissingExternalDependencyError('Install RDFlib if you want to use the CDAO tree format.')

# Example CDAO files
cdao_files = (
              'test.cdao',
              )

# Temporary file name for Writer tests below
DUMMY = tempfile.mktemp()


# ---------------------------------------------------------
# Parser tests

def _test_parse_factory(source):
    """Generate a test method for parse()ing the given source.

    The generated function extracts each phylogenetic tree using the parse()
    function.
    """
    filename = os.path.join('CDAO/', source)

    def test_parse(self):
        trees = list(bp._io.parse(filename, 'cdao'))

    test_parse.__doc__ = "Parse the phylogenies in %s." % source
    return test_parse


def _test_write_factory(source):
    """Test for serialization of objects to CDAO format.

    Modifies the globally defined filenames in order to run the other parser
    tests on files (re)generated by CDAOIO's own writer.
    """
    filename = os.path.join('CDAO/', source)

    def test_write(self):
        """Parse, rewrite and retest an example file."""
        with open(filename) as infile:
            t1 = next(CDAOIO.Parser(infile).parse())

        with open(DUMMY, 'w') as outfile:
            CDAOIO.write([t1], outfile)
        with open(DUMMY) as infile:
            t2 = next(CDAOIO.Parser(infile).parse())

        for prop_name in ('name', 'branch_length', 'confidence'):
            p1 = [getattr(n, prop_name) for n in t1.get_terminals()]
            p2 = [getattr(n, prop_name) for n in t2.get_terminals()]
            if p1 == p2:
                pass
            else:
                # Can't sort lists with None on Python 3 ...
                self.assertFalse(None in p1, "Bad input values for %s: %r" % (prop_name, p1))
                self.assertFalse(None in p2, "Bad output values for %s: %r" % (prop_name, p2))
                self.assertEqual(sorted(p1), sorted(p2))

    test_write.__doc__ = "Write and re-parse the phylogenies in %s." % source
    return test_write


class ParseTests(unittest.TestCase):
    """Tests for proper parsing of example CDAO files."""


for n, ex in enumerate(cdao_files):
    parse_test = _test_parse_factory(ex)
    parse_test.__name__ = 'test_parse_%s' % n
    setattr(ParseTests, parse_test.__name__, parse_test)


class WriterTests(unittest.TestCase):
    pass


for n, ex in enumerate(cdao_files):
    write_test = _test_write_factory(ex)
    write_test.__name__ = 'test_write_%s' % n
    setattr(WriterTests, write_test.__name__, write_test)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
    # Clean up the temporary file
    if os.path.exists(DUMMY):
        os.remove(DUMMY)

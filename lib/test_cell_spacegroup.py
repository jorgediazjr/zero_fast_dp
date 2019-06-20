#!/usr/local/crys-local/ccp4-7.0/bin/cctbx.python
'''
This is a test script for cell_spacegroup
and all of its functions.

- J Diaz Jr
'''

from cell_spacegroup import ersatz_pointgroup

def test_ersatz_pointgroup():
    assert ersatz_pointgroup('hello') == 'hello', 'Should be hello'


if __name__ == '__main__':
    test_ersatz_pointgroup()

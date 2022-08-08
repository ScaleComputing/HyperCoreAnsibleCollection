from __future__ import absolute_import, division, print_function
__metaclass__ = type

import sys

import pytest

pytestmark = pytest.mark.skipif(
    sys.version_info < (2, 7), reason="requires python2.7 or higher"
)


def test_ok_always():
    pass


#def test_error_always():
#    1234/0

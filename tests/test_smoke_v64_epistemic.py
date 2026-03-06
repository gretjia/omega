import os
import sys

TESTS_ROOT = os.path.abspath(os.path.dirname(__file__))
if TESTS_ROOT not in sys.path:
    sys.path.insert(0, TESTS_ROOT)

from smoke_v64_epistemic import smoke_test_v64_kernel


def test_smoke_v64_kernel_script():
    smoke_test_v64_kernel()

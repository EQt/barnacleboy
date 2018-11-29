"""
Find data (for test instances, etc.)
"""
from os import path


_pwd = path.dirname(__file__)


def _test_file_name() -> str:
    """File name to the test file (on my computer)"""
    return path.join(_pwd, "..", "..", "raw", "rep2",
                     "assigned_blist.bin")


def moffit_example() -> str:
    "../data/"
    return path.join(_pwd, "..", "data", "moffit", "example.csv.gz")

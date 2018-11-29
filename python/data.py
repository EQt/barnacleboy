"""
Find data (for test instances, etc.)
"""
from os import path


def _test_file_name() -> str:
    """File name to the test file (on my computer)"""
    return path.join(path.dirname(__file__),
                     "..", "..", "raw", "rep2", "assigned_blist.bin")

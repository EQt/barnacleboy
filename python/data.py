"""
Find data (for test instances, etc.)
"""
import sys
from os import path


_pwd = path.dirname(__file__)


def _test_file_name() -> str:
    """File name to the test file (on my computer)"""
    return path.join(_pwd, "..", "..", "raw", "rep2",
                     "assigned_blist.bin")


def moffit_example(generate=True) -> str:
    fn = path.join(_pwd, "..", "data", "moffit", "example.csv.gz")
    if generate and not path.exists(fn):
        import subprocess as sp

        cmd = ['make', '-C', path.dirname(fn), path.basename(fn)]
        print(*cmd, file=sys.stderr)
        sp.check_call(cmd)
    return fn

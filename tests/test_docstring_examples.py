"""各API直下の入力例と期待結果を、通常のテストと一緒に検証する。"""

import doctest
import importlib
from pathlib import Path


def load_tests(loader, tests, pattern):
    library = Path(__file__).resolve().parents[1] / 'mogura'
    for path in sorted(library.glob('*.py')):
        if path.stem != '__init__':
            module = importlib.import_module('mogura.' + path.stem)
            tests.addTests(doctest.DocTestSuite(module))
    return tests

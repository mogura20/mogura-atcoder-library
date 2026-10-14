"""各API直下の入力例と期待結果を、通常のテストと一緒に検証する。"""

import importlib
import ast
import contextlib
import inspect
import io
import textwrap
import unittest
from unittest.mock import patch
from pathlib import Path


class MoguraStandardInputExamples(unittest.TestCase):
    def test_sample_inputs_match_sample_outputs(self):
        """API直下の読込みコードへ入力例を渡し、表示の出力例と比較する。"""
        library = Path(__file__).resolve().parents[1] / 'mogura'
        count = 0
        for path in sorted(library.glob('*.py')):
            if path.stem == '__init__':
                continue
            module = importlib.import_module('mogura.' + path.stem)
            targets = []
            for node in ast.parse(path.read_text(encoding='utf-8')).body:
                if isinstance(node, ast.FunctionDef):
                    targets.append((node.name, getattr(module, node.name)))
                elif isinstance(node, ast.ClassDef):
                    cls = getattr(module, node.name)
                    targets.append((node.name, cls))
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef) and (not method.name.startswith('_') or method.name == '__init__'):
                            targets.append((node.name + '.' + method.name, getattr(cls, method.name)))
            for name, target in targets:
                with self.subTest(module=path.stem, api=name):
                    doc = inspect.getdoc(target)
                    sample_input = textwrap.dedent(doc.split('入力例:\n', 1)[1].split('\n\n出力例:', 1)[0])
                    expected = textwrap.dedent(doc.split('出力例:\n', 1)[1].split('\n\n読み込み・呼び出し例:', 1)[0])
                    code_lines = []
                    for line in doc.split('読み込み・呼び出し例:\n', 1)[1].splitlines():
                        if not line.startswith('    '):
                            break
                        code_lines.append(line)
                    code = textwrap.dedent('\n'.join(code_lines))
                    output = io.StringIO()
                    with patch('sys.stdin', io.StringIO(sample_input + '\n')), contextlib.redirect_stdout(output):
                        exec(compile(code, str(path) + ':' + name, 'exec'), dict(vars(module)))
                    self.assertEqual(output.getvalue(), expected + '\n')
                    count += 1
        self.assertEqual(count, 119)

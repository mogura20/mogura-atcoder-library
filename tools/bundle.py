# Source: https://github.com/mogura20/mogura-atcoder-library/blob/0722a9a6b352a27e43e3ee2aa287ebf1e04f43ba/tools/bundle.py
"""mogura: 指定モジュールを提出用コードへ展開する非AIのツール。

例: python3 tools/bundle.py dsu graph --main examples/shortest_path.py
公開後は--source-refで実際に公開済みのコミットSHAを指定する。
"""

import argparse
import ast
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULES = ("basic", "dsu", "fenwick", "segtree", "lazy_segtree", "graph", "lca", "number_theory", "string",
           "weighted_dsu", "graph_extra", "mst", "matching", "dp", "range_utils", "math_extra",
           "geometry", "trie", "rolling_hash", "enumeration", "heuristic", "interactive")
DEPENDENCIES = {"mst": ("dsu",)}


def mogura_bundle(modules, main_text="", repository="mogura20/mogura-atcoder-library", source_ref=None):
    """文字列として返す。指定順を保持して重複排除。出典は各モジュール別。

    main_text中のfrom mogura.xxx import ...だけを除去する。
    選択されていないモジュールや別形式のmogura importは拒否する。
    出力に入力コードのmain処理を足すだけで、問題固有のコードは生成しない。
    """
    modules = list(dict.fromkeys(modules))
    if any(module not in MODULES for module in modules):
        raise ValueError("未対応のモジュール名です")
    # 指定したモジュールの依存だけを先に展開。現在はmst→dsu。
    ordered = []

    def include(module):
        if module in ordered:
            return
        for dependency in DEPENDENCIES.get(module, ()):
            include(dependency)
        ordered.append(module)

    for module in modules:
        include(module)
    modules = ordered
    tree = ast.parse(main_text)
    lines = main_text.splitlines(keepends=True)
    removed = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(alias.name == "mogura" or alias.name.startswith("mogura.") for alias in node.names):
                raise ValueError("from mogura.xxx import 名前 の形式を使ってください")
        if isinstance(node, ast.ImportFrom) and node.module and (node.module == "mogura" or node.module.startswith("mogura.")):
            if node not in tree.body or node.col_offset != 0:
                raise ValueError("mogura importはファイルのトップレベルに置いてください")
            if node.module != "mogura." + node.module.split(".")[-1] or node.module.split(".")[-1] not in modules:
                raise ValueError("mainで使うmoguraモジュールを引数にも指定してください")
            if any(alias.asname or alias.name == "*" for alias in node.names):
                raise ValueError("別名や*でのmogura importには対応していません")
            # 同じ行に別の文がある場合、行単位の除去では失われるため拒否。
            if any(other is not node and getattr(other, "lineno", 0) <= node.end_lineno
                   and getattr(other, "end_lineno", 0) >= node.lineno for other in tree.body):
                raise ValueError("mogura importは独立した行に置いてください")
            removed.update(range(node.lineno - 1, node.end_lineno))
    if any(isinstance(node, ast.ImportFrom) and node.module == "__future__" for node in ast.walk(tree)):
        raise ValueError("mainの__future__ importには対応していません")
    output = ["# mogura library bundle\n"]
    output.extend("# " + line + "\n" for line in (ROOT / "LICENSE").read_text(encoding="utf-8").splitlines())
    if source_ref is None:
        output.append("# 未公開の開発版: コンテスト利用前に公開と参照URLの指定が必要です。\n")
    for module in modules:
        output.append("\n# === mogura: " + module + " ===\n")
        if source_ref:
            output.append("# Source: https://github.com/" + repository + "/blob/" + source_ref + "/mogura/" + module + ".py\n")
        module_text = (ROOT / "mogura" / (module + ".py")).read_text(encoding="utf-8")
        module_lines = module_text.splitlines(keepends=True)
        import_lines = set()
        for node in ast.parse(module_text).body:
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('mogura.'):
                dependency = node.module.split('.')[-1]
                if dependency not in modules:
                    raise ValueError('DEPENDENCIESに内部依存を登録してください: ' + dependency)
                import_lines.update(range(node.lineno-1, node.end_lineno))
        output.extend(line for index,line in enumerate(module_lines) if index not in import_lines)
    output.append("\n# === 自分で書く問題固有の処理 ===\n")
    output.extend(line for index, line in enumerate(lines) if index not in removed)
    result = "".join(output)
    ast.parse(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("modules", nargs="+", choices=MODULES)
    parser.add_argument("--main", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repository", default="mogura20/mogura-atcoder-library")
    parser.add_argument("--source-ref", help="コンテスト開始前にWeb公開済みのコミットSHA")
    args = parser.parse_args()
    if args.source_ref and (len(args.source_ref) != 40 or any(c not in "0123456789abcdefABCDEF" for c in args.source_ref)):
        parser.error("--source-refは40桁のコミットSHAで指定してください")
    if args.source_ref:
        # 未コミットの修正版を古い公開URLで引用することを防ぐ。
        required = set(args.modules)
        for module in list(required):
            required.update(DEPENDENCIES.get(module, ()))
        paths = ['mogura/' + module + '.py' for module in sorted(required)] + ['LICENSE']
        if args.main:
            try:
                example = args.main.resolve().relative_to(ROOT / 'examples')
            except ValueError:
                pass
            else:
                paths.append('examples/' + example.as_posix())
        for path in paths:
            result = subprocess.run(['git', 'show', args.source_ref + ':' + path],
                                    cwd=ROOT, capture_output=True)
            if result.returncode:
                parser.error('指定SHAのソースがローカルにありません。git fetchで取得してください: ' + path)
            if result.stdout != (ROOT / path).read_bytes():
                parser.error('手元のコードと指定SHAが一致しません。公開済みの同じ版を使ってください: ' + path)
    main_text = args.main.read_text(encoding="utf-8") if args.main else ""
    if args.main and args.source_ref:
        try:
            relative = args.main.resolve().relative_to(ROOT / "examples")
        except ValueError:
            pass
        else:
            main_text = "# Source: https://github.com/" + args.repository + "/blob/" + args.source_ref + "/examples/" + relative.as_posix() + "\n" + main_text
    try:
        code = mogura_bundle(args.modules, main_text, args.repository, args.source_ref)
    except (ValueError, SyntaxError) as error:
        parser.error(str(error))
    if args.output:
        args.output.write_text(code, encoding="utf-8")
    else:
        print(code, end="")


if __name__ == "__main__":
    main()

# 元ファイルと移行先の対応表

確認日: 2026年10月14日。元フォルダ直下の55ファイルを確認しました。比較先は初版コミット`5d47aeaf46e9bbbe3ecafcc0ddb855e8cfdefe21`です。

- 追加: 未収録の機能を汎用APIへ再実装。
- 既存: 同等機能がすでにあるため重複コードは追加しない。
- 説明へ整理: 標準機能や学習用の例を用途別メモへ。
- 対象外: 問題専用の解答。

元ファイルのコードをそのまま転載せず、機能を読み取って整理・再実装しています。外部出典が不明なスニペットも転載していません。`.vscode`と`.DS_Store`は対象外です。ファイルのサイズ・SHA256は[JSON一覧](desktop_inventory.json)に保存しました。

| 元ファイル | 分類 | 移行先・扱い |
|---|---|---|
| `*コンテスト用 copy.py` | 対象外 | 問題専用の入出力・BMI判定。汎用ライブラリではない |
| `*コンテスト用.py` | 既存＋追加 | DSUは既存。Kruskalはmogura/mst.pyへ |
| `*迷った時に01` | 説明へ整理 | docs/python_notes.mdの選択表。名前だけの高度手法は未実装と明記 |
| `*迷った時に02` | 説明へ整理 | docs/python_notes.md。問題番号・秒数による固定的な目安は転載しない |
| `DP_グリッドDP(2次元DP).py` | 追加 | mogura/dp.py: mogura_grid_path_count |
| `DP_ビットDP.py` | 追加 | mogura/dp.py: mogura_hamiltonian_cost（任意始点） |
| `DP_区間DP.py` | 追加 | mogura/dp.py: mogura_interval_dp（追加コスト関数を指定） |
| `DP_巡回セールスマン問題(TSP).py` | 追加 | mogura/dp.py: mogura_hamiltonian_cost（cycle=True） |
| `DP_最長共通部分列(LCS).py` | 追加 | mogura/dp.py: mogura_lcs（復元、デバッグ出力除去） |
| `DP_最長増加部分列(LIS).py` | 追加 | mogura/dp.py: mogura_lis（復元、非減少も対応） |
| `DP_木DP.py` | 追加 | mogura/dp.py: mogura_tree_independent_set（反復処理・復元） |
| `DP_確率DP.py` | 追加 | mogura/dp.py: mogura_expected_steps（移動量・確率を指定） |
| `インタラクティブ問題_デバッグ用コードなど.py` | 追加＋説明 | mogura/interactive.pyとdocs/python_notes.md。問題固有の解答は移行しない |
| `グラフ理論_BFS.py` | 既存＋追加 | BFSは既存graph.py。0–1 BFSはgraph_extra.pyへ |
| `グラフ理論_DFS.py` | 追加＋説明 | graph_extra.pyのmogura_dfs_orders。経路は親配列で復元。問題専用/第三者スニペットは転載しない |
| `グラフ理論_トポロジカルソート.py` | 既存 | mogura/graph.py: mogura_toposort |
| `グラフ理論_最大2部マッチング.py` | 追加 | mogura/matching.py: MoguraHopcroftKarp、読みやすいBFS増加路法も用意 |
| `グラフ理論_最小全域木_クラスカル法.py` | 追加 | mogura/mst.py: mogura_kruskal（入力を変更しない、非連結も明示） |
| `グラフ理論_最小全域木_プリム法.py` | 追加 | mogura/mst.py: mogura_prim（全成分を処理） |
| `グラフ理論_最短経路_ダイクストラ.py` | 既存 | mogura/graph.py: mogura_dijkstra |
| `グラフ理論_最短経路_ベルマンフォード.py` | 追加 | mogura/graph_extra.py: mogura_bellman_ford |
| `グラフ理論_最短経路_ワーシャルフロイド.py` | 追加 | mogura/graph_extra.py: mogura_floyd_warshall |
| `データ構造_UnionFind.py` | 既存＋追加 | 通常DSUは既存。weighted_dsu.pyへ重み付き版を追加（差の符号を変更） |
| `データ構造_heapq_SortedSet copy.py` | 説明へ整理 | docs/python_notes.md。外部SortedContainersは依存として取り込まない |
| `データ構造_セグメントツリー.py` | 既存 | mogura/segtree.py、lazy_segtree.py。誤った呼出しや問題別入出力は転載しない |
| `データ構造_セグメントツリー2.py` | 既存＋説明 | 汎用演算は既存MoguraSegTreeへ統一。XOR/AND/OR設定例を追加 |
| `データ構造_フェンウィックツリー.py` | 既存 | mogura/fenwick.py（0始まり・半開区間へ統一） |
| `ヒューリスティック_ビームサーチ_chatgpt.py` | 追加 | mogura/heuristic.pyとexamples/heuristic_recipes.py |
| `ヒューリスティック_焼きなまし.py` | 追加 | mogura/heuristic.pyへ汎用化。例の点巡回の専用入出力は取り込まない |
| `ヒューリスティック_焼きなまし_chatgpt.py` | 追加 | mogura/heuristic.pyとexamples/heuristic_recipes.py |
| `基本型_ビット全探索.py` | 追加＋説明 | mogura/enumeration.pyとdocs/python_notes.md |
| `基本型_メモ化再帰.py` | 説明へ整理 | docs/python_notes.md: cacheの使い方と終了条件 |
| `基本型_二分探索_*基本.py` | 既存 | mogura/basic.py: mogura_bisect_int。問題固有判定は呼び出し側で記述 |
| `基本型_二分探索_しゃくとり法.py` | 追加＋説明 | range_utils.py: 非負和のしゃくとり/連続区間。第三者の問題専用例は転載しない |
| `基本型_再帰関数.py` | 説明へ整理 | docs/python_notes.mdの再帰・反復の使い分けとFibonacci例 |
| `基本型_累積和_二次元累積和.py` | 追加 | range_utils.py: MoguraPrefixSum2D |
| `数学_ビットシフト演算_進数.py` | 追加＋説明 | math_extra.py: mogura_base_digits、docs/python_notes.md |
| `数学_冪乗(pow).py` | 説明へ整理 | docs/python_notes.md: 標準pow |
| `数学_切り上げ_切り捨て.py` | 追加＋説明 | math_extra.py: mogura_ceil_div、docs/python_notes.md |
| `数学_座標回転.py` | 追加 | geometry.py: mogura_rotate_point（中心指定可） |
| `数学_最大公約数_最小公倍数.py` | 説明へ整理 | docs/python_notes.md: 標準gcd/lcm |
| `数学_直線の交差判定.py` | 追加 | geometry.py: 閉線分交差、外積/内積/距離二乗。無限直線とは区別 |
| `数学_約数列挙.py` | 追加 | math_extra.py: mogura_divisors |
| `数学_素因数分解(Osa_k法).py` | 追加 | math_extra.py: MoguraOsaK |
| `数学_素因数分解.py` | 既存 | number_theory.py: mogura_factorize。リスト形式ならMoguraOsaK.factor_list |
| `数学_素数列挙.py` | 既存 | number_theory.py: mogura_sieve |
| `数学_組合せ(N人をTチームに分ける) チームを区別しない.py` | 追加 | math_extra.py: mogura_team_sizes（整数分割） |
| `数学_組合せ(N人をTチームに分ける)チームを区別する.py` | 追加 | math_extra.py: mogura_team_sizes（labeled=True、整数組成） |
| `数学_転置行列.py` | 追加 | geometry.py: mogura_transpose/mogura_rotate_grid、NumPy不要 |
| `数学_集合演算.py` | 説明へ整理 | docs/python_notes.md: set |
| `数学_順列_組合せ(itertools_math).py` | 追加＋説明 | enumeration.py: 重複なし順列、docs/python_notes.mdのitertools/math |
| `文字列処理_ランレングス圧縮.py` | 追加 | string.py: mogura_run_length |
| `文字列検索_Trie木.py` | 追加 | trie.py: MoguraTrie（空文字/重複/前方一致/LCP総和） |
| `文字列検索_Zアルゴリズム.py` | 既存＋追加 | Z本体は既存。string.pyへmogura_z_searchを追加 |
| `文字列検索_ローリングハッシュ.py` | 追加 | rolling_hash.py: MoguraRollingHash（二重化、区間取得O(1)） |

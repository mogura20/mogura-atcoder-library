# Source: https://github.com/mogura20/mogura-atcoder-library/blob/3c3652ff152a79f54e88806b9a261df05b2aa4bc/mogura/trie.py
"""mogura: 重複を数えられる文字列Trie。再帰なし。"""


class MoguraTrie:
    """insert/count/count_prefixはO(文字列長)、領域O(総挿入文字数)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    全ペアの共通接頭辞長の総和を出力。

    入力形式:
        N
        S_1
        ...
        S_N

    入力例:
        3
        ab
        ac
        ab

    出力例:
        4

    読み込み・呼び出し例:
        n = int(input())
        trie = MoguraTrie()
        for _ in range(n):
            trie.insert(input().strip())
        print(trie.pair_lcp_sum())

    ノードを整数添字で管理。空文字・重複も数える。削除は未対応。
    pair_lcp_sumは全ての異なる挿入番号の組についてLCP長の総和を返す。
    例: 'ab','ac','ab'を入れるとLCP総和は1+2+1=4。
    """

    def __init__(self):
        """空のTrieを初期化する。"""
        self.children = [{}]
        self.prefix_count = [0]
        self.terminal_count = [0]

    def insert(self, text):
        """文字列textを1件挿入する。同じ文字列も別の1件として数える。"""
        node = 0
        self.prefix_count[node] += 1
        for char in text:
            if char not in self.children[node]:
                self.children[node][char] = len(self.children)
                self.children.append({})
                self.prefix_count.append(0)
                self.terminal_count.append(0)
            node = self.children[node][char]
            self.prefix_count[node] += 1
        self.terminal_count[node] += 1

    def _find(self, text):
        node = 0
        for char in text:
            node = self.children[node].get(char, -1)
            if node == -1:
                return -1
        return node

    def count(self, text):
        """文字列textと完全一致する挿入件数を返す。"""
        node = self._find(text)
        return 0 if node == -1 else self.terminal_count[node]

    def count_prefix(self, prefix):
        """prefixから始まる挿入文字列の件数を返す。"""
        node = self._find(prefix)
        return 0 if node == -1 else self.prefix_count[node]

    def pair_lcp_sum(self):
        """根以外の各ノードでcount choose 2を加算。O(ノード数)。"""
        return sum(count*(count-1)//2 for count in self.prefix_count[1:])

"""mogura: 対話問題の問合せを実通信とローカル模擬で切り替える。"""

import sys


class MoguraInteractiveIO:
    """ask(*values)は応答文字列を返し、answer(*values)は最終回答を送る。

    入力例・結果:
    >>> io = MoguraInteractiveIO(mock_query=lambda i: '0111'[i])
    >>> io.ask(1)
    '1'

    通常は'? ...'/'! ...'形式でflush。問題が違う形式ならprefixを変更。
    mock_queryを指定すると標準出力を汚さず模擬応答を返す。
    デバッグ情報を出す場合はstderrへ。問合せ上限・失敗応答は問題ごとに扱う。
    askの応答をintへ変換するかも呼び出し側で決める。
    """

    def __init__(self, mock_query=None, query_prefix='?', answer_prefix='!', input_stream=None, output_stream=None):
        """実通信の入出力、またはmock_queryによる模擬応答を設定する。

        入力例・結果:
        >>> io = MoguraInteractiveIO(mock_query=lambda i: '0111'[i])
        >>> io.ask(1)
        '1'
        """
        self.mock_query = mock_query
        self.query_prefix, self.answer_prefix = query_prefix, answer_prefix
        self.input_stream = sys.stdin if input_stream is None else input_stream
        self.output_stream = sys.stdout if output_stream is None else output_stream
        self.query_count = 0
        self.last_answer = None

    def ask(self, *values):
        """問合せを送って応答文字列を返す。模擬モードでは通信しない。

        入力例・結果:
        >>> io = MoguraInteractiveIO(mock_query=lambda i: '0111'[i])
        >>> io.ask(0), io.ask(2), io.query_count
        ('0', '1', 2)
        """
        self.query_count += 1
        if self.mock_query is not None:
            return str(self.mock_query(*values))
        print(self.query_prefix, *values, file=self.output_stream, flush=True)
        response = self.input_stream.readline()
        if response == '':
            raise EOFError('ジャッジからの応答がありません')
        return response.strip()

    def answer(self, *values):
        """最終回答を送る。模擬モードではlast_answerへ保存する。

        入力例・結果:
        >>> io = MoguraInteractiveIO(mock_query=lambda i: 0)
        >>> io.answer(3)  # 模擬モードでは標準出力に書かない
        >>> io.last_answer
        (3,)
        """
        self.last_answer = values
        if self.mock_query is None:
            print(self.answer_prefix, *values, file=self.output_stream, flush=True)

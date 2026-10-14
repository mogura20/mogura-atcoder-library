"""mogura: 対話問題の問合せを実通信とローカル模擬で切り替える。"""

import sys


class MoguraInteractiveIO:
    """ask(*values)は応答文字列を返し、answer(*values)は最終回答を送る。

    通常は'? ...'/'! ...'形式でflush。問題が違う形式ならprefixを変更。
    mock_queryを指定すると標準出力を汚さず模擬応答を返す。
    デバッグ情報を出す場合はstderrへ。問合せ上限・失敗応答は問題ごとに扱う。
    askの応答をintへ変換するかも呼び出し側で決める。
    """

    def __init__(self, mock_query=None, query_prefix='?', answer_prefix='!', input_stream=None, output_stream=None):
        self.mock_query = mock_query
        self.query_prefix, self.answer_prefix = query_prefix, answer_prefix
        self.input_stream = sys.stdin if input_stream is None else input_stream
        self.output_stream = sys.stdout if output_stream is None else output_stream
        self.query_count = 0
        self.last_answer = None

    def ask(self, *values):
        self.query_count += 1
        if self.mock_query is not None:
            return str(self.mock_query(*values))
        print(self.query_prefix, *values, file=self.output_stream, flush=True)
        response = self.input_stream.readline()
        if response == '':
            raise EOFError('ジャッジからの応答がありません')
        return response.strip()

    def answer(self, *values):
        self.last_answer = values
        if self.mock_query is None:
            print(self.answer_prefix, *values, file=self.output_stream, flush=True)

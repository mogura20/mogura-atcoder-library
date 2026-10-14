# Source: https://github.com/mogura20/mogura-atcoder-library/blob/92672adf53b8e2d9409cc822a203867ca24ae4bc/mogura/interactive.py
"""mogura: 対話問題の問合せを実通信とローカル模擬で切り替える。"""

import sys


class MoguraInteractiveIO:
    """ask(*values)は応答文字列を返し、answer(*values)は最終回答を送る。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    ローカル模擬用の入力。Iは0始まり。本番の対話形式は問題ごとに異なる。

    入力形式:
        S
        I

    入力例:
        0111
        1

    出力例:
        1

    読み込み・呼び出し例:
        hidden = input().strip()
        index = int(input())
        io = MoguraInteractiveIO(mock_query=lambda i: hidden[i])
        print(io.ask(index))

    通常は'? ...'/'! ...'形式でflush。問題が違う形式ならprefixを変更。
    mock_queryを指定すると標準出力を汚さず模擬応答を返す。
    デバッグ情報を出す場合はstderrへ。問合せ上限・失敗応答は問題ごとに扱う。
    askの応答をintへ変換するかも呼び出し側で決める。
    """

    def __init__(self, mock_query=None, query_prefix='?', answer_prefix='!', input_stream=None, output_stream=None):
        """実通信の入出力、またはmock_queryによる模擬応答を設定する。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        ローカル模擬用の入力。Iは0始まり。本番の対話形式は問題ごとに異なる。

        入力形式:
            S
            I

        入力例:
            0111
            1

        出力例:
            1

        読み込み・呼び出し例:
            hidden = input().strip()
            index = int(input())
            io = MoguraInteractiveIO(mock_query=lambda i: hidden[i])
            print(io.ask(index))
        """
        self.mock_query = mock_query
        self.query_prefix, self.answer_prefix = query_prefix, answer_prefix
        self.input_stream = sys.stdin if input_stream is None else input_stream
        self.output_stream = sys.stdout if output_stream is None else output_stream
        self.query_count = 0
        self.last_answer = None

    def ask(self, *values):
        """問合せを送って応答文字列を返す。模擬モードでは通信しない。

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        ローカル模擬用。Iは0始まり。本番は問合せを送り、ジャッジの応答を読む。

        入力形式:
            S
            I

        入力例:
            0111
            1

        出力例:
            1

        読み込み・呼び出し例:
            hidden = input().strip()
            index = int(input())
            io = MoguraInteractiveIO(mock_query=lambda i: hidden[i])
            print(io.ask(index))
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

        この入出力は使用方法を示す例。関数自体は標準入力を読みません。
        ローカル模擬用。保存された回答を確認する。本番は! Xをflush付きで送信。

        入力形式:
            X

        入力例:
            3

        出力例:
            3

        読み込み・呼び出し例:
            answer = int(input())
            io = MoguraInteractiveIO(mock_query=lambda i: 0)
            io.answer(answer)
            print(*io.last_answer)
        """
        self.last_answer = values
        if self.mock_query is None:
            print(self.answer_prefix, *values, file=self.output_stream, flush=True)

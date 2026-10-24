# Source: https://github.com/mogura20/mogura-atcoder-library/blob/9bfcc0557ab1f6feec0911de8c6cf5bd26c11a41/mogura/heuristic.py
"""mogura: 評価・状態遷移を差し替える焼きなましとビームサーチ。"""

from heapq import nlargest
from math import exp, isfinite
from random import Random
from time import perf_counter


def mogura_anneal(initial, score, propose, copy_state, iterations=10000,
                  time_limit=None, start_temp=100.0, end_temp=0.1, seed=0):
    """(best_state,best_score,stats)を返す。評価は大きいほど良い。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    動作説明用に、値を1増やす近傍・値そのものを評価とする。実問題では変更する。

    入力形式:
        X K

    入力例:
        0 3

    出力例:
        3 3

    読み込み・呼び出し例:
        initial, iterations = map(int, input().split())
        best, value, stats = mogura_anneal(initial, lambda x: x, lambda x, rng: x + 1,
                                          copy_state=lambda x: x, iterations=iterations)
        print(best, value)

    score(state): 有限数の評価値。
    propose(state,rng): 元を変更せず候補を返す。候補の合法性は呼び出し側。
    copy_state(state): 最良解を保存できる独立コピー（不変値ならlambda x:x）。
    固定iterationsなら再現可能。time_limitも指定すると早い方で打ち切る。
    iterations=Noneは時間のみの制限。両方Noneは不可。温度は指数冷却。
    時間はループ境界で確認するため、1回の評価/候補生成の時間だけ超過し得る。
    差分評価を使う場合、state自身にscoreを持たせscore=lambda s:s.scoreとする。
    """
    if iterations is None and time_limit is None:
        raise ValueError('反復回数か時間制限が必要です')
    if iterations is not None and iterations < 0:
        raise ValueError('iterationsは非負')
    if time_limit is not None and time_limit < 0:
        raise ValueError('time_limitは非負')
    if not (isfinite(start_temp) and isfinite(end_temp) and start_temp > 0 and end_temp > 0):
        raise ValueError('温度は有限の正数')
    rng = Random(seed)
    current = copy_state(initial)
    current_score = score(current)
    if not isfinite(current_score):
        raise ValueError('scoreは有限数')
    best, best_score = copy_state(current), current_score
    start = perf_counter()
    count = accepted = 0
    while iterations is None or count < iterations:
        elapsed = perf_counter() - start
        if time_limit is not None and elapsed >= time_limit:
            break
        progress = count / max(1, iterations-1) if iterations is not None else elapsed / time_limit
        if time_limit is not None and time_limit > 0:
            progress = max(progress, elapsed / time_limit)
        temperature = start_temp * (end_temp / start_temp) ** min(progress, 1.0)
        candidate = propose(current, rng)
        value = score(candidate)
        if not isfinite(value):
            raise ValueError('scoreは有限数')
        delta = value-current_score
        if delta >= 0 or rng.random() < exp(delta / temperature):
            current, current_score = candidate, value
            accepted += 1
            if value > best_score:
                best, best_score = copy_state(candidate), value
        count += 1
    return best, best_score, {'iterations': count, 'accepted': accepted}


def mogura_beam_search(initial, expand, evaluate, is_complete, final_score=None,
                       key=None, width=100, max_depth=100, time_limit=None):
    """(best_complete,score,stats)を返す。完成解なしは(None,None,stats)。

    この入出力は使用方法を示す例。関数自体は標準入力を読みません。
    動作説明用に、1または2を加算してG以上で完成とする。評価は大きいほど良い。

    入力形式:
        G

    入力例:
        3

    出力例:
        4 4

    読み込み・呼び出し例:
        goal = int(input())
        best, value, stats = mogura_beam_search(0, lambda x: [x + 1, x + 2],
                                               lambda x: x, lambda x: x >= goal,
                                               width=2, max_depth=goal)
        print(best, value)

    expand(state)は新しい子状態のiterable。元の状態を変更しないこと。
    evaluateは途中順位、final_scoreは完成解の評価（省略時evaluate）。
    key指定時は同じキーの途中状態でevaluate最大だけを残す。
    キーでまとめてよいかは問題依存。例えば訪問maskだけでは末尾を失う。
    完成状態は延長しないが、別の枝の深い完成解を探すため即終了しない。
    幅上位だけ残すので最適解保証なし。同点でも状態自体を比較しない。
    時間確認は子の生成後。expand/evaluateの1回が長いと超過し得る。
    1段でC候補なら選別O(C log(width+1))、保存領域O(C+width)。
    """
    if width <= 0 or max_depth < 0 or (time_limit is not None and time_limit < 0):
        raise ValueError('width>0、max_depth/time_limitは非負')
    final_score = final_score or evaluate
    start = perf_counter()
    best, best_value = None, None
    beam = [initial]
    generated = depth = 0
    serial = 0

    def timed_out():
        return time_limit is not None and perf_counter()-start >= time_limit

    def consider(state):
        nonlocal best, best_value
        if is_complete(state):
            value = final_score(state)
            if best is None or value > best_value:
                best, best_value = state, value
            return True
        return False

    if consider(initial):
        beam = []
    for depth_index in range(max_depth):
        if not beam or timed_out():
            break
        candidates = []
        deduplicated = {}
        for state in beam:
            for child in expand(state):
                generated += 1
                if not consider(child):
                    item = (evaluate(child), serial, child)
                    serial += 1
                    if key is None:
                        candidates.append(item)
                    else:
                        hash_key = key(child)
                        previous = deduplicated.get(hash_key)
                        if previous is None or item[0] > previous[0]:
                            deduplicated[hash_key] = item
                if timed_out():
                    break
            if timed_out():
                break
        if key is not None:
            candidates = list(deduplicated.values())
        beam = [item[2] for item in nlargest(width, candidates, key=lambda item: (item[0], -item[1]))]
        depth = depth_index+1
    return best, best_value, {'depth': depth, 'generated': generated, 'beam_size': len(beam)}

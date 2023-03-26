from typing import Iterator, Iterable
import functools
import re
# sys.setrecursionlimit(30)       # デバッグ用


def __cstream(istr: Iterator[str]) -> Iterator[str]:
    ''' ストリーム（イテレータ）から１文字ずつ取得するイテレータ。
        ストリームから取得した文字がバックスラッシュなら、
        次の１文字を無条件にくっつけて返す。
        注）内部で StopIteration が発生する場合あり。
    '''
    for chr in istr:
        if chr == '\\':
            yield chr + next(istr)
        else:
            yield chr


def __get_quoted(istr: Iterator[str]) -> str:
    ''' ダブルクォートで囲まれた文字列を取得する。
        （末尾のダブルクォートを含む）
        ldata = 'abc"XYZ\\"QQQ"nnn'
        get_quoted(iter(ldata[4:]))='XYZ\\"QQQ"'
    '''
    item: list[str] = []
    for chr in __cstream(istr):
        item.append(chr)
        if chr == '"':
            break
    return "".join(item)


def __get_bracketed(istr: Iterator[str]) -> str:
    ''' ブラケットで囲まれた文字列を取得する。
        （先頭に'{'は含まれない。末尾に'}'は含まれる）
    '''
    item: list[str] = []
    for chr in __cstream(istr):
        if chr == '{':      # ネストされた{}処理
            item.append('{' + __get_bracketed(istr))
        elif chr == '"':    # ダブルクォート範囲処理
            tt = __get_quoted(istr)
            item.append('"' + tt)
        else:
            item.append(chr)

        if chr == '}':
            break
    return "".join(item)


def __is_onebracketed(sdata: str) -> bool:
    ''' 文字列が全て {} に内包されているか？
        ex) "{A,B,C{1,2,3}}: True
            "{A,B,C}{X,Y,Z}: False
    '''
    return sdata[0] == '{'\
        and sdata[-1] == '}'\
        and len(sdata) == len(__get_bracketed(iter(sdata[1:]))) + 1


def __expand_range(moto: str) -> list[str]:
    ''' 連続数字、文字の範囲展開を行う。
        "{1..5}" -> ['1', '2', '3', '4', '5']
        "{-1..005..1}" -> ['-01', '000', '001', '002', '003', '004', '005']
        "{A..D}" -> ['A', 'B', 'C', 'D']
        展開できない場合は空のリストを返す。
    '''
    def altanative_range(start: int, end: int, step: int) -> Iterable[int]:
        ''' {1..5}、{5..3..1} などと、Pythonの range() と仕様調整
            altanative_range(1, 5, 0) -> range(1, 6, 1)
            altanative_range(5, 3, 1) -> range(5, 2, -1)
        '''
        end = end + 1 if start <= end else end - 1
        step = max(1, abs(step)) if start <= end else - max(1, abs(step))
        return range(start, end, step)

    ''' ここから本文 '''
    try:
        ps = [s for s in moto.split('..', 2)] + ["1"]
        if ps[0].isalpha() and ps[1].isalpha() and len(ps[0]) == 1 and len(ps[1]) == 1:
            if len(ps) in [3, 4]:       # 文字(start)..文字(end)
                return [chr(i) for i in altanative_range(ord(ps[0]), ord(ps[1]), int(ps[2]))]
        else:                           # 数字(start)..数字(end)
            pa = [int(s) for s in ps]
            if len(pa) in [3, 4]:
                # '001' とか、'-05' とかのゼロフィル長さを取得
                length = 0
                if re.match('^0|^-0', ps[0]) or re.match('^0|^-0', ps[1]):
                    length = max(len(ps[0]), len(ps[1]))
                return [str(i).zfill(length) for i in altanative_range(pa[0], pa[1], pa[2])]
    except ValueError:
        pass
    return []


def __expand_or(sdata: str) -> list[str]:
    ''' {} で囲われた文字列のカンマ展開を行う。
        展開できない場合は空のリストを返す。
    '''
    istr = iter(sdata)

    ''' カンマ分割を行う
        '{A,B,{Q,W}{1,2}}' --> ['A','B','{Q,W}{1,2}']
    '''
    items: list[str] = []       # 分割された文字列リスト
    part: list[str] = []        # 分割用work
    for chr in __cstream(istr):
        if chr == ',':
            items.append("".join(part))
            part = []
            continue
        elif chr == '"':
            part.append('"' + __get_quoted(istr))
        elif chr == '{':
            part.append('{' + __get_bracketed(istr))
        else:
            part.append(chr)

    items.append("".join(part))
    if len(items) <= 1:         # 分割（展開）されなかった
        return []

    ''' 分割された文字列をさらに展開する
        ['A','B','{Q,W}{1,2}'] --> ['A','B','Q1','Q2','W1','W2']
    '''
    newitems: list[str] = []
    for it in items:
        newitems.extend(__b_expansion(it))

    return newitems


def __expand_mul(sdata: str) -> list[str]:
    ''' 文字列の {} による分割と乗算展開を行う '''

    def array_multiply(m1: list[str], m2: list[str]) -> list[str]:
        ''' 文字列配列同士の乗算を行う
            dim_mul(['A','B','C'], ['x','y']) ->
                        ['Ax', 'Ay', 'Bx', 'By', 'Cx', 'Cy']
        '''
        return [s1 + s2 for s1 in m1 for s2 in m2]

    def __expand_mul2(sdata: str) -> list[str]:
        ''' 文字列の {} による分割を行う '''

        def _btype(bdata: str) -> str:
            ''' 分割ブロックのタイプを返す
                -> 'L': "{xxx", 'R': "xxx}", 'B': "{xxx}, 'F': "xxx"
            '''
            if bdata[0] == '{':
                if bdata[-1] == '}':
                    return 'B'
                else:
                    return 'L'
            elif bdata[-1] == '}':
                return 'R'
            return 'F'

        istr = iter(sdata)

        ''' 分割処理
            "{P,Q}A,{1..{5,6}}" -->
            ['{P,Q}', 'A,', '{1..', '{5,6}', '}']
        '''
        items: list[str] = []   # 結果のリスト
        witems: list[str] = []   # 分割作業用リスト
        for chr in __cstream(istr):
            if chr == '{':          # '{' で分割開始
                if witems:
                    items.append("".join(witems))
                    witems = []
                witems.append(chr)
            elif chr == '}':        # '}' で分割終了、次の開始
                witems.append(chr)
                items.append("".join(witems))
                witems = []
            elif chr == '"':        # "" で囲まれた文字列処理
                tt = __get_quoted(istr)
                witems.append('"' + tt)
            else:
                witems.append(chr)
        if witems:
            items.append("".join(witems))

        ''' {} の要素毎の連結処理
            ['{P,Q}', 'A,', '{1..', '{5,6}', '}'] -->
            ['{P,Q}', 'A,', '{1..{5,6}}']
        '''
        newitems: list[str] = []    # 連結後の格納用リスト
        witems = items[::-1]        # 頭からpopするために反転リスト
        while witems:
            ww = witems.pop()
            if _btype(ww) == 'R':   # 右カッコのブロック、キタ
                wlist = [ww]            # ワークに積む
                while newitems:
                    w2 = newitems.pop()     # 左カッコのブロックを掘り出すまで、
                    wlist.append(w2)        # ワークに積む

                    # 始まりの左カッコのブロック、あり
                    if _btype(w2) == 'L':
                        newitems.append("".join(wlist[::-1]))
                        break

                # 始まりの左カッコのブロック、なし
                # （右カッコブロックは単なるデータだった）
                else:
                    newitems.extend(wlist[::-1])

                continue
            else:
                newitems.append(ww)     # 右カッコのブロックが来るまで詰め込む

        return newitems

    ''' ここから本文 '''

    # 文字列の {} による分割を行う
    '''
        "{P,Q}A,{1..{5,6}}" -->
        ['{P,Q}', 'A,', '{1..{5,6}}']
    '''
    if __is_onebracketed(sdata):
        ''' 全体が一つの {}内にあるときは、外側の {} を外してから分割を行う
            '{{P,Q}{x,y}}' --> '{' + '{P,Q}{x,y}' + '}'
                           --> ['{', '{P,Q}', '{x,y}', '}']
        '''
        newitems = ['{'] + __expand_mul2(sdata[1:-1]) + ['}']
    else:
        newitems = __expand_mul2(sdata)

    # 分割した個々のパーツをさらに展開する
    '''
        ['{', '{P,Q}', '{x,y}', '}'] --> [['{'], ['P', 'Q'], ['x', 'y'], ['}']]
    '''
    retitems = [__b_expansion(it) if __is_onebracketed(it) else [it] for it in newitems]

    # 分割した個々のパーツの乗算処理を行う
    '''
        A{x,y}{1,2}Z --> [['A'], ['x', 'y'], ['1', '2'], ['Z']]

        ['A'], ['x', 'y'] --> ['Ax', 'Ay']
        ['Ax', 'Ay'], ['1', '2'] --> ['Ax1', 'Ax2', 'Ay1', 'Ay2']
        ['Ax1', 'Ax2', 'Ay1', 'Ay2'], ['Z'] --> ['Ax1Z', 'Ax2Z', 'Ay1Z', 'Ay2Z']
    '''
    return functools.reduce(array_multiply, retitems)


def __b_expansion(sdata: str) -> list[str]:
    ''' ブレース展開を行う '''

    if '{' not in sdata:    # { が一つもない
        return [sdata]          # 展開不要で終了

    ''' 全体が {} で囲われた文字列を展開する '''
    if __is_onebracketed(sdata):      # 全体が {} 囲われている場合
        items = __expand_or(sdata[1:-1])      # カンマ展開をしてみる
        if items:                           # カンマ展開成功
            return items

        items = __expand_range(sdata[1:-1])   # 範囲展開してみる
        if items:                           # 範囲展開成功
            return items

    ''' 全体が {} 囲われているが、カンマ分割も範囲展開もできない '''
    ''' または、全体が {} 囲われていない '''
    items = __expand_mul(sdata)               # 乗算展開してみる
    return items


def b_expansion(sdata: str) -> list[str]:
    ''' ブレース展開を行い、結果を文字列の配列で返す '''

    def __clean(sdata: str) -> str:
        ''' 文字列中の、単独の " は削除、\" は単体の " に置き換える '''
        if '"' in sdata:
            return "".join(['' if c == '"'
                            else '"' if c == '\\"'
                            else '' if c == '\\'
                            # else c for c in sdata])
                            else c for c in __cstream(iter(sdata)) ])
        return sdata

    # ブレース展開を行う
    ret = __b_expansion(sdata)

    # 文字列中の、単独の " は削除、\" は単体の " に置き換え、
    # 空アイテムを削除する
    return [i for i in (map(__clean, ret)) if i]


if __name__ == '__main__':
    import sys

    sdata = "{XY..{P.Q}}"
    sdata = "X,Y{P,Q}A,{1..3}"
    # sdata = "{P,{Q,R}X}A"
    # sdata = "{P,Q}A,{1..{56}}"
    # sdata = "{P,Q}A,{1..{5,6}}"
    # sdata = "abc,{P,Q}A,{1..{5,6}}"
    # sdata = "{XY..{P.Q}}"
    # sdata = "{a,b{1..3{X,Y{A}QZ"
    # sdata = "{AB{C,D{Q,X}Z}EF"
    # sdata = '{AB"{C,D"{Q,X}Z}EF'
    # sdata = "AB{C,D{Q,X}Z}EF}"
    sdata = "{{P,Q}{x,y}}"
    sdata = "A{x,y}{1,2}Z"
    # sdata = "{{P,Q},{x,y}}"

    # sdata = "{ab,x,y,{35}{A,B}}"
    # sdata = "ab,x,y,{35}{A,B}"
    # sdata = "7月{01日,02日,03日}"
    sdata = '{わかめ,"月見,たぬき"}\\"うどん\\"{01..5}'
    # sdata = "{2021..2022}-{01..12}-file.txt"
    # sdata = "{1..{4,8,10}}"
    # sdata = "test{08..-04..+2}"
    # sdata = '{AB\\"{C,D\\"{Q,X}Z}EF'
    # sdata = "{a,}"
    # sdata = "{{A,B}{X,Z}}"
    # sdata = "file.txt{,.backup}"
    # sdata = "/usr/local/src/bash/{old,new,dist,bugs}"
    # sdata = "a{,,,}"

    print(sys.argv)
    if len(sys.argv) > 1:
        sdata = sys.argv[1]

    items = b_expansion(sdata)

    print(f'{sdata}')
    print()
    for it in items:
        print(it)

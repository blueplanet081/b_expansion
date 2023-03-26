# 各引数を、一行ずつ echo する。
# . echoln.sh でfunction登録して使う。

echoln() {
    for I; do
        echo $I
    done
}
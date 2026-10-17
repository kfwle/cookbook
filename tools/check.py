#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сравнивает вывод всех собранных реализаций «Книги рецептов».

Эталон — ассемблерная версия (build/cookbook). Остальные запускаются,
если нашлись бинарники/интерпретаторы, и их вывод должен совпасть
с эталоном побайтово на каждом сценарии ввода.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = sys.argv[1] if len(sys.argv) > 1 else "build"

# (имя, команда) — порядок не важен
CANDIDATES = [
    ("python3",   ["python3", "cookbook.py"]),
    ("go",        [os.path.join(BUILD, "cb-go")]),
    ("c",         [os.path.join(BUILD, "cb-c")]),
    ("c++",       [os.path.join(BUILD, "cb-cpp")]),
    ("rust",      [os.path.join(BUILD, "cb-rs")]),
    ("zig",       [os.path.join(BUILD, "cb-zig")]),
    ("typescript", ["node", os.path.join(BUILD, "ts", "cookbook.js")]),
    ("node",      ["node", "cookbook.js"]),
    ("lua",       ["lua", "cookbook.lua"]),
    ("perl",      ["perl", "cookbook.pl"]),
    ("ruby",      ["ruby", "cookbook.rb"]),
    ("php",       ["php", "cookbook.php"]),
    ("julia",     ["julia", "cookbook.jl"]),
    ("haskell",   [os.path.join(BUILD, "cb-hs")]),
    ("swift",     [os.path.join(BUILD, "cb-swift")]),
    ("elixir",    ["elixir", "cookbook.ex"]),
    ("java",      ["java", "-Dfile.encoding=UTF-8", "-cp", ".", "Cookbook"]),
    ("kotlin",    ["java", "-jar", os.path.join(BUILD, "cb.kt.jar")]),
    ("csharp",   ["dotnet", os.path.join(BUILD, "cs", "Cookbook.dll")]),
    ("erlang",   ["erl", "-noshell", "-pa", BUILD, "-eval",
                  "cookbook:main(), init:stop()."]),
    ("fsharp",   ["dotnet", "fsi", "cookbook.fsx"]),
    ("scheme",   ["guile", "--no-auto-compile", "cookbook.scm"]),
    ("tcl",      ["tclsh", "cookbook.tcl"]),
    ("crystal",  ["crystal", "cookbook.cr"]),
    ("fortran",  [os.path.join(BUILD, "cb-f90")]),
    ("nim",      [os.path.join(BUILD, "cb-nim")]),
    ("lisp",     ["sbcl", "--script", "cookbook.lisp"]),
    ("clojure",  ["clojure", "cookbook.clj"]),
    ("ocaml",    ["ocaml", "cookbook.ml"]),
    ("groovy",   ["groovy", "cookbook.groovy"]),
    ("ada",      [os.path.join(BUILD, "cb-ada")]),
    ("dlang",    [os.path.join(BUILD, "cb-d")]),
    ("pascal",   [os.path.join(BUILD, "cb-pas")]),
    ("dart",     ["dart", "cookbook.dart"]),
]

SCENARIOS = [
    (b"42\n\n7\n101\nabc\n100\n\n0\n", "рецепт, пауза, ошибка, рецепт 100, выход"),
    (b"0\n",                             "сразу выход"),
    (b"",                                "только EOF"),
    (b"\n\n0\n",                         "пустые строки"),
    (b"-5\n0\n",                         "отрицательное число"),
    (b"101\n0\n",                        "вне диапазона"),
]


def run(cmd, data):
    """Возвращает только stdout: предупреждения инструментов в stderr
    не должны влиять на сравнение с эталоном."""
    p = subprocess.run(cmd, input=data, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, cwd=ROOT)
    return p.stdout


def main():
    ref_bin = os.path.join(BUILD, "cookbook")
    if not os.path.exists(os.path.join(ROOT, ref_bin)):
        print("эталон %s не собран — запустите make" % ref_bin)
        return 1

    found = [(n, c) for n, c in CANDIDATES
             if c[0].endswith(("cookbook.py", "cookbook.js", "cookbook.lua",
                               "cookbook.pl", "cookbook.rb", "cookbook.php",
                               "cookbook.jl"))
             or os.path.exists(os.path.join(ROOT, c[0]))
             or __import__("shutil").which(c[0])]

    if not found:
        print("не найдено ни одной реализации")
        return 1

    print("реализаций к проверке: %d\n" % len(found))
    ok = True
    for data, title in SCENARIOS:
        ref = run([ref_bin], data)
        print("сценарий: %s" % title)
        for name, cmd in found:
            got = run(cmd, data)
            if got == ref:
                print("   %-11s ок" % name)
            else:
                ok = False
                print("   %-11s РАСХОЖДЕНИЕ (%d против %d байт)"
                      % (name, len(got), len(ref)))
        print()

    print("ИТОГ:", "все совпали с эталоном" if ok else "есть расхождения")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
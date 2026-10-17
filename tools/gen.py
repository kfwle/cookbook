#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор всех реализаций «Книги рецептов».

Источник истины — tools/recipes_data.py. Отсюда собираются:
  cookbook.s    ассемблер x86-64 (рецепты вшиты в .rodata)
  recipes.txt   тот же набор данных в читаемом текстовом виде
  cookbook.*    19 реализаций на других языках

Все файлы генерируются, поэтому править руками их не нужно:
достаточно поправить recipes_data.py и запустить make regen.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recipes_data import R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAST = len(R)

# ---------------------------------------------------------------- общие тексты

RULE = "=" * 52
HEAD = [
    "",
    RULE,
    "             КНИГА РЕЦЕПТОВ — 100 блюд",
    RULE,
    "Введи номер от 1 до 100, затем Enter.  0 — выход.",
]

NAMES = [r[0] for r in R]


def full_text(i):
    """Текст рецепта в том виде, в котором он печатается."""
    _, title, serv, ing, st = R[i]
    lines = ["### %d. %s (%s)" % (i + 1, title, serv), "Ингредиенты:"]
    lines += ["  " + x for x in ing]
    lines.append("Приготовление:")
    lines += ["  %d. %s" % (n + 1, x) for n, x in enumerate(st)]
    return "\n" + "\n".join(lines) + "\n"


TEXTS = [full_text(i) for i in range(LAST)]

COLS = 4
PER = (LAST + COLS - 1) // COLS
MENU_ROWS = []
for row in range(PER):
    cells = []
    for c in range(COLS):
        k = c * PER + row
        cells.append("%3d. %-15s" % (k + 1, NAMES[k]) if k < LAST else " " * 19)
    MENU_ROWS.append(("  " + " ".join(cells)).rstrip())

MENU = "\n".join(HEAD + MENU_ROWS) + "\n> "

MSG_BAD = ("\n[!] Нет такого рецепта. "
           "Введи число от 1 до 100 или 0 для выхода.\n")
MSG_PAUSE = "\n--- Нажми Enter, чтобы вернуться в меню ---\n"
MSG_BYE = "\nПриятного аппетита!\n"


# ---------------------------------------------------------------- экранирование

def lit(s, quote='"'):
    """Строковый литерал: реальные переводы строк -> \\n, кавычки экранируются.

    Нужен именно escape-вариант: в отличие от Go (raw string) почти все языки
    требуют, чтобы перевод строки был записан как два символа \\ и n.
    """
    out = s.replace("\\", "\\\\")
    out = out.replace(quote, "\\" + quote)
    out = out.replace("\r", "\\r").replace("\n", "\\n")
    return quote + out + quote


def lit_perl(s):
    return lit(s).replace("$", "\\$").replace("@", "\\@")


def lit_ruby(s):
    return lit(s).replace("#{", "\\#{")


def raw_go(s):
    """Go raw string: настоящие переводы строк, кавычки не нужны."""
    assert "`" not in s
    return "`" + s + "`"


# ---------------------------------------------------------------- хелперы

def w(path, text):
    p = os.path.join(ROOT, path)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    print("  %-16s %6d байт" % (path, len(text.encode("utf-8"))))


def qlist(items, indent, open_, close, sep=", ", escf=lit):
    """Список строковых литералов через запятую."""
    pad = "\n" + " " * indent
    return open_ + pad + (sep + pad).join(escf(i) for i in items) + close


def py_lit(s):
    """Литерал для тройных кавычек Python: реальные \\n остаются как есть."""
    return s.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')


def plist(items, escf=py_lit):
    return "[" + ", ".join('"""' + escf(i) + '"""' for i in items) + "]"


# ================================================================ templates

def gen_txt():
    out = ["# Книга рецептов — 100 блюд",
           "# Формат: строки вида '### <N> | <короткое имя> | <заголовок>'",
           "# открывают рецепт, остальные строки печатаются как есть.",
           "# Файл используется как эталон данных для всех реализаций.",
           ""]
    for i in range(LAST):
        _, title, serv, _, _ = R[i]
        out.append("### %d | %s | %s (%s)" % (i + 1, NAMES[i], title, serv))
        out += ["  " + x for x in R[i][3]]
        out.append("Приготовление:")
        out += ["  %d. %s" % (n + 1, x) for n, x in enumerate(R[i][4])]
        out.append("")
    w("recipes.txt", "\n".join(out) + "\n")


def gen_py():
    t = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py, не править руками."""

import sys

NAMES = {plist(NAMES)}

RECIPES = {plist(TEXTS)}

MENU = """{MENU}"""
MSG_BAD = {lit(MSG_BAD)}
MSG_PAUSE = {lit(MSG_PAUSE)}
MSG_BYE = {lit(MSG_BYE)}


def out(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def read_line():
    """Строка без перевода строки, либо None на конце потока."""
    line = sys.stdin.readline()
    if line == "":
        return None
    return line.strip()


def parse(line):
    """Номер рецепта: 1..{LAST}. Возвращает int или None. 0 — выход."""
    if not 1 <= len(line) <= 3 or not all("0" <= ch <= "9" for ch in line):
        return None
    return int(line)


def main():
    while True:
        out(MENU)
        line = read_line()
        if line is None:
            break
        n = parse(line)
        if n == 0:
            break
        if n is None or not 1 <= n <= {LAST}:
            out(MSG_BAD)
            continue
        out(RECIPES[n - 1])
        out(MSG_PAUSE)
        if read_line() is None:
            break
    out(MSG_BYE)


if __name__ == "__main__":
    main()
'''
    w("cookbook.py", t)


def gen_go():
    names = qlist(NAMES, 1, "[]string{", "}")
    recs = qlist(TEXTS, 1, "[]string{", "}", escf=raw_go)
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
package main

import (
	"bufio"
	"os"
)

var names = {names}

var recipes = {recs}

const menu = `{MENU}`
const msgBad = `{MSG_BAD}`
const msgPause = `{MSG_PAUSE}`
const msgBye = `{MSG_BYE}`

// parse возвращает номер рецепта, 0 при ошибке ввода.
// Выход из программы обозначается отдельным флагом.
func parse(s string) (int, bool) {{
	if len(s) < 1 || len(s) > 3 {{
		return 0, false
	}}
	n := 0
	for i := 0; i < len(s); i++ {{
		if s[i] < '0' || s[i] > '9' {{
			return 0, false
		}}
		n = n*10 + int(s[i]-'0')
	}}
	return n, true
}}

func main() {{
	in := bufio.NewReaderSize(os.Stdin, 1<<16)
	out := bufio.NewWriter(os.Stdout)
	defer out.Flush()

	for {{
		out.WriteString(menu)
		out.Flush()

		raw, err := in.ReadString('\\n')
		if raw == "" && err != nil {{
			break
		}}
		line := ""
		for i := 0; i < len(raw); i++ {{
			if raw[i] == '\\n' || raw[i] == '\\r' {{
				break
			}}
			line += string(raw[i])
		}}

		n, ok := parse(line)
		if !ok {{
			out.WriteString(msgBad)
			continue
		}}
		if n == 0 {{
			break
		}}
		if n > {LAST} {{
			out.WriteString(msgBad)
			continue
		}}

		out.WriteString(recipes[n-1])
		out.WriteString(msgPause)
		out.Flush()
		if _, err := in.ReadString('\\n'); err != nil && len(line) == 0 {{
			break
		}}
	}}

	out.WriteString(msgBye)
	out.Flush()
	_ = names
}}
'''
    w("cookbook.go", t)


def gen_c():
    names = qlist(NAMES, 1, "static const char *const names[] = {", "};", escf=lit)
    recs = qlist(TEXTS, 1, "static const char *const recipes[] = {", "};", escf=lit)
    t = f'''/* Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LAST {LAST}

{names}

{recs}

static const char menu[] =
{lit(MENU)};
static const char msg_bad[] =
{lit(MSG_BAD)};
static const char msg_pause[] =
{lit(MSG_PAUSE)};
static const char msg_bye[] =
{lit(MSG_BYE)};

/* Читает строку, убирая перевод строки.
   Возвращает 0 на конце потока или ошибке. */
static int read_line(char *buf, size_t cap)
{{
    size_t len;

    if (fgets(buf, (int)cap, stdin) == NULL)
        return 0;
    len = strlen(buf);
    while (len > 0 && (buf[len - 1] == '\\n' || buf[len - 1] == '\\r'))
        buf[--len] = '\\0';
    return 1;
}}

/* 1..LAST — номер рецепта, 0 — выход, -1 — ошибка ввода */
static int parse(const char *s)
{{
    size_t len = strlen(s), i;
    int n = 0;

    if (len < 1 || len > 3)
        return -1;
    for (i = 0; i < len; i++) {{
        if (s[i] < '0' || s[i] > '9')
            return -1;
        n = n * 10 + (s[i] - '0');
    }}
    return n;
}}

int main(void)
{{
    char line[256];
    int n;

    for (;;) {{
        fputs(menu, stdout);
        if (!read_line(line, sizeof line))
            break;

        n = parse(line);
        if (n == 0)
            break;
        if (n < 1 || n > LAST) {{
            fputs(msg_bad, stdout);
            continue;
        }}

        fputs(recipes[n - 1], stdout);
        fputs(msg_pause, stdout);
        fflush(stdout);
        if (!read_line(line, sizeof line))
            break;
    }}

    fputs(msg_bye, stdout);
    return 0;
}}
'''
    w("cookbook.c", t)


def gen_cpp():
    recs = qlist(TEXTS, 2, "static const std::vector<std::string> recipes = {", "};")
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
#include <iostream>
#include <string>
#include <vector>

static const int LAST = {LAST};

{recs}

static const std::string MENU = {lit(MENU)};
static const std::string MSG_BAD = {lit(MSG_BAD)};
static const std::string MSG_PAUSE = {lit(MSG_PAUSE)};
static const std::string MSG_BYE = {lit(MSG_BYE)};

// 1..LAST — номер рецепта, 0 — выход, -1 — ошибка ввода
static int parse(const std::string& s)
{{
    if (s.empty() || s.size() > 3)
        return -1;
    int n = 0;
    for (char c : s) {{
        if (c < '0' || c > '9')
            return -1;
        n = n * 10 + (c - '0');
    }}
    return n;
}}

static bool read_line(std::string& out)
{{
    if (!std::getline(std::cin, out))
        return false;
    while (!out.empty() && (out.back() == '\\r' || out.back() == '\\n'))
        out.pop_back();
    return true;
}}

int main()
{{
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::string line;
    for (;;) {{
        std::cout << MENU << std::flush;
        if (!read_line(line))
            break;

        int n = parse(line);
        if (n == 0)
            break;
        if (n < 1 || n > LAST) {{
            std::cout << MSG_BAD;
            continue;
        }}

        std::cout << recipes[n - 1] << MSG_PAUSE << std::flush;
        if (!read_line(line))
            break;
    }}

    std::cout << MSG_BYE;
    return 0;
}}
'''
    w("cookbook.cpp", t)


def gen_cs():
    recs = qlist(TEXTS, 2, "static readonly string[] Recipes = {", "};")
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
using System;

internal static class Program
{{
    private const int Last = {LAST};

{recs}

    private const string Menu = {lit(MENU)};
    private const string MsgBad = {lit(MSG_BAD)};
    private const string MsgPause = {lit(MSG_PAUSE)};
    private const string MsgBye = {lit(MSG_BYE)};

    // 1..Last — номер рецепта, 0 — выход, -1 — ошибка ввода
    private static int Parse(string? s)
    {{
        if (string.IsNullOrEmpty(s) || s.Length > 3)
            return -1;
        int n = 0;
        foreach (char c in s)
        {{
            if (c < '0' || c > '9')
                return -1;
            n = n * 10 + (c - '0');
        }}
        return n;
    }}

    private static void Main()
    {{
        while (true)
        {{
            Console.Write(Menu);
            var line = Console.ReadLine();
            if (line is null)
                break;

            int n = Parse(line);
            if (n == 0)
                break;
            if (n < 1 || n > Last)
            {{
                Console.Write(MsgBad);
                continue;
            }}

            Console.Write(Recipes[n - 1]);
            Console.Write(MsgPause);
            if (Console.ReadLine() is null)
                break;
        }}

        Console.Write(MsgBye);
    }}
}}
'''
    w("cookbook.cs", t)


def gen_rs():
    recs = qlist(TEXTS, 4, "const RECIPES: [&str; %d] = [" % LAST, "];")
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
use std::io::{{self, BufRead, Write}};

const LAST: usize = {LAST};

{recs}

const MENU: &str = {lit(MENU)};
const MSG_BAD: &str = {lit(MSG_BAD)};
const MSG_PAUSE: &str = {lit(MSG_PAUSE)};
const MSG_BYE: &str = {lit(MSG_BYE)};

/// 1..=LAST — номер рецепта, `None` — ошибка ввода.
fn parse(s: &str) -> Option<u32> {{
    if s.is_empty() || s.len() > 3 {{
        return None;
    }}
    let mut n: u32 = 0;
    for c in s.bytes() {{
        if !c.is_ascii_digit() {{
            return None;
        }}
        n = n * 10 + u32::from(c - b'0');
    }}
    Some(n)
}}

fn main() {{
    let stdin = io::stdin();
    let mut stdout = io::stdout();
    for line in stdin.lock().lines() {{
        write!(stdout, "{{MENU}}").unwrap();
        stdout.flush().unwrap();

        let Ok(line) = line else {{ break }};
        let line = line.trim();

        let Some(n) = parse(line) else {{
            write!(stdout, "{{MSG_BAD}}").unwrap();
            continue;
        }};
        if n == 0 {{
            break;
        }}
        if n as usize > LAST {{
            write!(stdout, "{{MSG_BAD}}").unwrap();
            continue;
        }}

        write!(stdout, "{{}}{{}}{{}}", RECIPES[n as usize - 1], MSG_PAUSE).unwrap();
        stdout.flush().unwrap();
        let _ = stdin.lock().lines().next();
    }}
    write!(stdout, "{{MSG_BYE}}").unwrap();
}}
'''
    w("cookbook.rs", t)


def gen_zig():
    recs = qlist(TEXTS, 4, "const recipes = [_][]const u8{", "};")
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
const std = @import("std");

const last: usize = {LAST};

{recs}

const menu = {lit(MENU)};
const msg_bad = {lit(MSG_BAD)};
const msg_pause = {lit(MSG_PAUSE)};
const msg_bye = {lit(MSG_BYE)};

/// Номер рецепта, 0 — выход, null — ошибка ввода.
fn parse(s: []const u8) ?usize {{
    if (s.len == 0 or s.len > 3) return null;
    var n: usize = 0;
    for (s) |c| {{
        if (c < '0' or c > '9') return null;
        n = n * 10 + @as(usize, c - '0');
    }}
    return n;
}}

fn trim(s: []const u8) []const u8 {{
    var t = s;
    while (t.len > 0 and (t[t.len - 1] == '\\n' or t[t.len - 1] == '\\r'))
        t = t[0 .. t.len - 1];
    return t;
}}

pub fn main() !void {{
    var gpa = std.heap.GeneralPurposeAllocator(.{{}}){{}};
    defer _ = gpa.deinit();

    const stdin = std.io.getStdIn();
    const stdout = std.io.getStdOut();
    const reader = stdin.reader();
    var buf: [256]u8 = undefined;

    while (true) {{
        try stdout.writeAll(menu);

        const raw = (try reader.readUntilDelimiterOrEof(&buf, '\\n')) orelse break;
        const n = parse(trim(raw)) orelse {{
            try stdout.writeAll(msg_bad);
            continue;
        }};
        if (n == 0) break;
        if (n > last) {{
            try stdout.writeAll(msg_bad);
            continue;
        }}

        try stdout.writeAll(recipes[n - 1]);
        try stdout.writeAll(msg_pause);

        _ = (try reader.readUntilDelimiterOrEof(&buf, '\\n')) orelse break;
    }}

    try stdout.writeAll(msg_bye);
}}
'''
    w("cookbook.zig", t)


def gen_java():
    recs = qlist(TEXTS, 8, "    private static final String[] RECIPES = {", "    };")
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;

public final class Cookbook {{
    private static final int LAST = {LAST};

{recs}

    private static final String MENU = {lit(MENU)};
    private static final String MSG_BAD = {lit(MSG_BAD)};
    private static final String MSG_PAUSE = {lit(MSG_PAUSE)};
    private static final String MSG_BYE = {lit(MSG_BYE)};

    /** 1..LAST — номер рецепта, -1 — ошибка ввода. */
    private static int parse(String s) {{
        if (s.isEmpty() || s.length() > 3) return -1;
        int n = 0;
        for (int i = 0; i < s.length(); i++) {{
            char c = s.charAt(i);
            if (c < '0' || c > '9') return -1;
            n = n * 10 + (c - '0');
        }}
        return n;
    }}

    public static void main(String[] args) throws IOException {{
        BufferedReader in = new BufferedReader(
                new InputStreamReader(System.in, StandardCharsets.UTF_8));

        while (true) {{
            System.out.print(MENU);
            System.out.flush();

            String line = in.readLine();
            if (line == null) break;

            int n = parse(line);
            if (n == 0) break;
            if (n < 1 || n > LAST) {{
                System.out.print(MSG_BAD);
                continue;
            }}

            System.out.print(RECIPES[n - 1]);
            System.out.print(MSG_PAUSE);
            System.out.flush();
            if (in.readLine() == null) break;
        }}

        System.out.print(MSG_BYE);
    }}
}}
'''
    w("cookbook.java", t)


def gen_kt():
    recs = qlist(TEXTS, 4, "val recipes = listOf(", ")")
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
private const val LAST = {LAST}

{recs}

private val menu = {lit(MENU)}
private val msgBad = {lit(MSG_BAD)}
private val msgPause = {lit(MSG_PAUSE)}
private val msgBye = {lit(MSG_BYE)}

/** 1..LAST — номер рецепта, null — ошибка ввода. */
fun parse(s: String): Int? {{
    if (s.isEmpty() || s.length > 3) return null
    var n = 0
    for (c in s) {{
        if (c < '0' || c > '9') return null
        n = n * 10 + (c - '0')
    }}
    return n
}}

fun main() {{
    while (true) {{
        print(menu)
        val line = readlnOrNull() ?: break

        val n = parse(line)
        if (n == 0) break
        if (n == null || n < 1 || n > LAST) {{
            print(msgBad)
            continue
        }}

        print(recipes[n - 1])
        print(msgPause)
        if (readlnOrNull() == null) break
    }}

    print(msgBye)
}}
'''
    w("cookbook.kt", t)


def gen_js():
    recs = qlist(TEXTS, 2, "const recipes = [", "];", escf=lit)
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
'use strict';

const readline = require('node:readline');

const LAST = {LAST};

{recs}

const MENU = {lit(MENU)};
const MSG_BAD = {lit(MSG_BAD)};
const MSG_PAUSE = {lit(MSG_PAUSE)};
const MSG_BYE = {lit(MSG_BYE)};

/** 1..LAST — номер рецепта, 0 — выход, -1 — ошибка ввода. */
function parse(s) {{
  const t = s.trim();
  if (t.length < 1 || t.length > 3) return -1;
  let n = 0;
  for (const c of t) {{
    if (c < '0' || c > '9') return -1;
    n = n * 10 + Number(c - '0');
  }}
  return n;
}}

const rl = readline.createInterface({{ input: process.stdin, terminal: false }});

let done = false;

function bye() {{
  if (!done) {{
    done = true;
    process.stdout.write(MSG_BYE);
  }}
}}

let awaitingEnter = false;

rl.on('line', (raw) => {{
  // строка после рецепта — просто подтверждение, дальше снова меню
  if (awaitingEnter) {{
    awaitingEnter = false;
    process.stdout.write(MENU);
    return;
  }}

  const n = parse(raw);
  if (n === 0) {{
    bye();
    rl.close();
    return;
  }}
  if (n < 1 || n > LAST) {{
    process.stdout.write(MSG_BAD + MENU);
    return;
  }}

  awaitingEnter = true;
  process.stdout.write(recipes[n - 1] + MSG_PAUSE);
}});

// Ctrl+D в любой момент — корректный выход
rl.on('close', bye);

process.stdout.write(MENU);
'''
    w("cookbook.js", t)


def gen_ts():
    recs = qlist(TEXTS, 2, "const recipes: readonly string[] = [", "];", escf=lit)
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
import * as readline from 'node:readline';

const LAST = {LAST};

{recs}

const MENU = {lit(MENU)};
const MSG_BAD = {lit(MSG_BAD)};
const MSG_PAUSE = {lit(MSG_PAUSE)};
const MSG_BYE = {lit(MSG_BYE)};

/** 1..LAST — номер рецепта, 0 — выход, -1 — ошибка ввода. */
function parse(raw: string): number {{
  const t = raw.trim();
  if (t.length < 1 || t.length > 3) return -1;
  let n = 0;
  for (const c of t) {{
    if (c < '0' || c > '9') return -1;
    n = n * 10 + Number(c.charCodeAt(0) - 48);
  }}
  return n;
}}

const rl = readline.createInterface({{ input: process.stdin, terminal: false }});

let done = false;

function bye(): void {{
  if (!done) {{
    done = true;
    process.stdout.write(MSG_BYE);
  }}
}}

let awaitingEnter = false;

rl.on('line', (raw: string) => {{
  // строка после рецепта — просто подтверждение, дальше снова меню
  if (awaitingEnter) {{
    awaitingEnter = false;
    process.stdout.write(MENU);
    return;
  }}

  const n = parse(raw);
  if (n === 0) {{
    bye();
    rl.close();
    return;
  }}
  if (n < 1 || n > LAST) {{
    process.stdout.write(MSG_BAD + MENU);
    return;
  }}

  awaitingEnter = true;
  process.stdout.write(recipes[n - 1] + MSG_PAUSE);
}});

rl.on('close', bye);

process.stdout.write(MENU);
'''
    w("cookbook.ts", t)


def gen_rb():
    recs = qlist(TEXTS, 2, "RECIPES = [", "]")
    t = f'''# Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
# frozen_string_literal: true

LAST = {LAST}

{recs}

MENU = {lit_ruby(MENU)}
MSG_BAD = {lit_ruby(MSG_BAD)}
MSG_PAUSE = {lit_ruby(MSG_PAUSE)}
MSG_BYE = {lit_ruby(MSG_BYE)}

# 1..LAST — номер рецепта, 0 — ошибка ввода
def parse(s)
  return 0 if s.nil? || s.empty? || s.length > 3 || !s.match?(/\\A\\d+\\z/)

  s.to_i
end

loop do
  print MENU
  line = $stdin.gets
  break if line.nil?

  n = parse(line.strip)
  break if n.zero?
  (print MSG_BAD; next) if n.negative? || n > LAST

  print RECIPES[n - 1]
  print MSG_PAUSE
  break if $stdin.gets.nil?
end

print MSG_BYE
'''
    w("cookbook.rb", t)


def gen_php():
    recs = qlist(TEXTS, 1, "$recipes = [", "];", escf=lit)
    t = f'''<?php
// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
declare(strict_types=1);

const LAST = {LAST};

{recs}

const MENU = {lit(MENU)};
const MSG_BAD = {lit(MSG_BAD)};
const MSG_PAUSE = {lit(MSG_PAUSE)};
const MSG_BYE = {lit(MSG_BYE)};

/** 1..LAST — номер рецепта, 0 — ошибка ввода. */
function parse(string $s): int
{{
    $t = trim($s);
    if ($t === '' || strlen($t) > 3 || preg_match('/^\\\\d+$/', $t) !== 1) {{
        return 0;
    }}
    return (int) $t;
}}

function readLine(): ?string
{{
    $line = fgets(STDIN);
    if ($line === false) {{
        return null;
    }}
    return rtrim($line, "\\r\\n");
}}

while (true) {{
    echo MENU;
    $line = readLine();
    if ($line === null) {{
        break;
    }}

    $n = parse($line);
    if ($n === 0) {{
        break;
    }}
    if ($n < 1 || $n > LAST) {{
        echo MSG_BAD;
        continue;
    }}

    echo $recipes[$n - 1];
    echo MSG_PAUSE;
    if (readLine() === null) {{
        break;
    }}
}}

echo MSG_BYE;
'''
    w("cookbook.php", t)


def gen_lua():
    recs = qlist(TEXTS, 1, "local recipes = {", "}", escf=lit)
    t = f'''-- Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
local LAST = {LAST}

{recs}

local menu = {lit(MENU)}
local msg_bad = {lit(MSG_BAD)}
local msg_pause = {lit(MSG_PAUSE)}
local msg_bye = {lit(MSG_BYE)}

-- Номер рецепта, 0 — выход, -1 — ошибка ввода
local function parse(s)
  if #s < 1 or #s > 3 then return -1 end
  local n = 0
  for i = 1, #s do
    local b = s:byte(i)
    if b < 48 or b > 57 then return -1 end
    n = n * 10 + (b - 48)
  end
  return n
end

local function trim(s)
  return (s:gsub("^[\\r\\n]+", ""):gsub("[\\r\\n]+$", ""))
end

while true do
  io.write(menu)
  local line = io.read("*l")
  if line == nil then break end

  local n = parse(trim(line))
  if n == 0 then break end
  if n < 1 or n > LAST then
    io.write(msg_bad)
  else
    io.write(recipes[n])
    io.write(msg_pause)
    if io.read("*l") == nil then break end
  end
end

io.write(msg_bye)
'''
    w("cookbook.lua", t)


def gen_pl():
    recs = qlist(TEXTS, 1, "my @recipes = (", ");", escf=lit_perl)
    t = f'''#!/usr/bin/perl
# Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
use strict;
use warnings;
use utf8;
binmode(STDOUT, ':encoding(UTF-8)');
binmode(STDIN,  ':encoding(UTF-8)');

use constant LAST => {LAST};

{recs}

my $menu      = {lit_perl(MENU)};
my $msg_bad   = {lit_perl(MSG_BAD)};
my $msg_pause = {lit_perl(MSG_PAUSE)};
my $msg_bye   = {lit_perl(MSG_BYE)};

# 1..LAST — номер рецепта, 0 — выход, undef — ошибка ввода или конец потока
sub parse {{
    my ($s) = @_;
    return undef if !defined $s;
    $s =~ s/^[\\r\\n]+//;
    $s =~ s/[\\r\\n]+$//;
    return undef if $s !~ /\\A\\d{{1,3}}\\z/;
    return 0 + $s;
}}

while (1) {{
    print $menu;
    my $line = <STDIN>;
    last if !defined $line;

    my $n = parse($line);
    if (!defined $n) {{ print $msg_bad; next }}
    if ($n == 0)   {{ last }}
    if ($n < 1 || $n > LAST) {{ print $msg_bad; next }}

    print $recipes[$n - 1];
    print $msg_pause;

    my $ack = <STDIN>;
    last if !defined $ack;
}}

print $msg_bye;
'''
    w("cookbook.pl", t)


def gen_hs():
    recs = qlist(TEXTS, 1, "recipes :: [String]", "", escf=lit)
    t = f'''-- Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
module Main (main) where

import System.IO
import Control.Monad (unless)
import Data.Char (isDigit)

lastIndex :: Int
lastIndex = {LAST}

recipes :: [String]
recipes =
{recs}

menu :: String
menu = {lit(MENU)}

msgBad, msgPause, msgBye :: String
msgBad = {lit(MSG_BAD)}
msgPause = {lit(MSG_PAUSE)}
msgBye = {lit(MSG_BYE)}

-- Just 1..lastIndex, Nothing при ошибке ввода.
parse :: String -> Maybe Int
parse s
  | null s || length s > 3 = Nothing
  | not (all isDigit s) = Nothing
  | otherwise = Just (read s :: Int)

main :: IO ()
main = loop
  where
    loop = do
      putStr menu
      hFlush stdout
      eof <- isEOF
      if eof
        then putStr msgBye
        else do
          line <- getLine
          case parse line of
            Just 0 -> putStr msgBye
            Just n | n >= 1 && n <= lastIndex -> do
              putStr (recipes !! (n - 1))
              putStr msgPause
              hFlush stdout
              _ <- getLine
              loop
            _ -> putStr msgBad >> loop
'''
    w("cookbook.hs", t)


def gen_swift():
    recs = qlist(TEXTS, 1, "let recipes: [String] = [", "]")
    t = f'''// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
import Foundation

let lastIndex = {LAST}

{recs}

let menu = {lit(MENU)}
let msgBad = {lit(MSG_BAD)}
let msgPause = {lit(MSG_PAUSE)}
let msgBye = {lit(MSG_BYE)}

/// 1...lastIndex — номер рецепта, nil при ошибке ввода.
func parse(_ s: String) -> Int? {{
    let bytes = Array(s.utf8)
    if bytes.isEmpty || bytes.count > 3 {{ return nil }}
    var n = 0
    for b in bytes {{
        if b < 48 || b > 57 {{ return nil }}
        n = n * 10 + Int(b - 48)
    }}
    return n
}}

func out(_ s: String) {{
    FileHandle.standardOutput.write(s.data(using: .utf8)!)
}}

while true {{
    out(menu)
    guard let line = readLine(strippingNewline: true) else {{
        out(msgBye)
        break
    }}

    guard let n = parse(line) else {{
        out(msgBad)
        continue
    }}
    if n == 0 {{
        out(msgBye)
        break
    }}
    if n < 1 || n > lastIndex {{
        out(msgBad)
        continue
    }}

    out(recipes[n - 1])
    out(msgPause)
    if readLine(strippingNewline: true) == nil {{
        out(msgBye)
        break
    }}
}}
'''
    w("cookbook.swift", t)


def gen_ex():
    recs = qlist(TEXTS, 1, "@recipes [", "]", escf=lit)
    t = r'''# Книга рецептов — %%LAST%% блюд. Сгенерировано tools/gen.py.
defmodule Cookbook do
  @last %%LAST%%

%%RECS%%

  @menu "%%MENU%%"
  @msg_bad "%%BAD%%"
  @msg_pause "%%PAUSE%%"
  @msg_bye "%%BYE%%"

  # 1..@last — номер рецепта, nil — ошибка ввода
  defp parse(line) do
    case Regex.run(~r/\A\d{1,3}\z/, line) do
      [_] -> String.to_integer(line)
      _ -> nil
    end
  end

  defp read_line do
    case IO.gets(:stdio, "") do
      :eof -> nil
      {:error, _} -> nil
      line -> line
    end
  end

  def loop do
    IO.write(@menu)

    case read_line() do
      nil ->
        IO.write(@msg_bye)

      line ->
        line = String.trim(line)

        case parse(line) do
          0 ->
            IO.write(@msg_bye)

          nil ->
            IO.write(@msg_bad)
            loop()

          n when n > @last ->
            IO.write(@msg_bad)
            loop()

          n ->
            IO.write(Enum.at(@recipes, n - 1))
            IO.write(@msg_pause)

            case read_line() do
              nil -> IO.write(@msg_bye)
              _ -> loop()
            end
        end
    end
  end
end

Cookbook.loop()
'''
    t = (t.replace("%%RECS%%", recs)
          .replace("%%MENU%%", lit(MENU))
          .replace("%%BAD%%", lit(MSG_BAD))
          .replace("%%PAUSE%%", lit(MSG_PAUSE))
          .replace("%%BYE%%", lit(MSG_BYE))
          .replace("%%LAST%%", str(LAST)))
    w("cookbook.ex", t)


def gen_jl():
    recs = qlist(TEXTS, 1, "const RECIPES = [", "]", escf=lit)
    t = f'''# Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
const LAST = {LAST}

{recs}

const MENU = {lit(MENU)}
const MSG_BAD = {lit(MSG_BAD)}
const MSG_PAUSE = {lit(MSG_PAUSE)}
const MSG_BYE = {lit(MSG_BYE)}

# 1..LAST — номер рецепта, nothing — ошибка ввода
function parse(s::String)
    isempty(s) && return nothing
    length(s) > 3 && return nothing
    all(isdigit, s) || return nothing
    return parse(Int, s)
end

function main()
    while true
        print(MENU)
        line = readline()
        if line === nothing
            print(MSG_BYE)
            break
        end

        n = parse(strip(line))
        if n === nothing
            print(MSG_BAD)
            continue
        elseif n == 0
            print(MSG_BYE)
            break
        elseif n > LAST
            print(MSG_BAD)
            continue
        end

        print(RECIPES[n])
        print(MSG_PAUSE)
        readline() === nothing && (print(MSG_BYE); break)
    end
end

main()
'''
    w("cookbook.jl", t)


def gen_asm():
    """Ассемблерная версия — рецепты вшиты в .rodata (см. tools/gen.py)."""
    import subprocess
    src = open(os.path.join(ROOT, "cookbook.s"), encoding="utf-8").read()
    # рецепты в .rodata генерируются отдельным шагом; здесь только проверка
    for i in range(1, LAST + 1):
        if "rec%d:" % i not in src:
            raise SystemExit("cookbook.s: нет rec%d" % i)
    w("cookbook.s", src)


def main():
    print("генерация (%d рецептов):" % LAST)
    gen_txt()
    gen_py()
    gen_go()
    gen_c()
    gen_cpp()
    gen_cs()
    gen_rs()
    gen_zig()
    gen_java()
    gen_kt()
    gen_js()
    gen_ts()
    gen_rb()
    gen_php()
    gen_lua()
    gen_pl()
    gen_hs()
    gen_swift()
    gen_ex()
    gen_jl()
    gen_asm()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Вторая партия реализаций «Книги рецептов» (15 языков).

Хелперы и данные берутся из gen.py — импорт безопасен, потому что
main() в нём вызывается только под __main__.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen as G  # noqa: E402

lit = G.lit
qlist = G.qlist
w = G.w
LAST = G.LAST
TEXTS = G.TEXTS
MENU = G.MENU
MSG_BAD = G.MSG_BAD
MSG_PAUSE = G.MSG_PAUSE
MSG_BYE = G.MSG_BYE

NAMES = ["erl", "fsx", "scm", "tcl", "cr", "f90", "nim", "lisp",
         "clj", "ml", "groovy", "adb", "d", "pas", "dart"]


def gen_erl():
    recs = qlist(TEXTS, 4, "recipes() ->\n    [", "].", escf=lit)
    recs = "\n".join('    ' + lit(TEXTS[i]) + ("," if i + 1 < LAST else "")
                     for i in range(LAST))
    w("cookbook.erl", f"""%% Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
-module(cookbook).
-export([main/0]).

-define(LAST, {LAST}).

recipes() ->
    [
{recs}
    ].

menu() -> {lit(MENU)}.

msg_bad() -> {lit(MSG_BAD)}.

msg_pause() -> {lit(MSG_PAUSE)}.

msg_bye() -> {lit(MSG_BYE)}.

%% nil — конец потока или ошибка ввода
read_line() ->
    case io:get_line("") of
        eof -> nil;
        {{error, _}} -> nil;
        L -> string:trim(L)
    end.

all_digits([]) -> true;
all_digits([C | T]) when C >= $0, C =< $9 -> all_digits(T);
all_digits(_) -> false.

%% 1..?LAST — номер рецепта, nil — ошибка ввода
parse(S) when S == [] -> nil;
parse(S) ->
    case all_digits(S) andalso length(S) =< 3 of
        true -> list_to_integer(S);
        false -> nil
    end.

main() -> loop().

loop() ->
    io:put_chars(menu()),
    case read_line() of
        nil -> io:put_chars(msg_bye());
        S -> handle(S)
    end.

handle(S) ->
    case parse(S) of
        nil -> io:put_chars(msg_bad()), loop();
        0 -> io:put_chars(msg_bye());
        N when N > ?LAST -> io:put_chars(msg_bad()), loop();
        N -> show(N)
    end.

show(N) ->
    io:put_chars(lists:nth(N, recipes())),
    io:put_chars(msg_pause()),
    case read_line() of
        nil -> io:put_chars(msg_bye());
        _ -> loop()
    end.
""")


def gen_fsx():
    recs = qlist(TEXTS, 2, "let recipes : string[] = [|", "|]", sep="; ", escf=lit)
    w("cookbook.fsx", f"""// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
open System
open System.IO

let last = {LAST}

{recs}

let menu = {lit(MENU)}
let msgBad = {lit(MSG_BAD)}
let msgPause = {lit(MSG_PAUSE)}
let msgBye = {lit(MSG_BYE)}

/// Some n для 1..last, None при ошибке ввода.
let parse (s : string) : int option =
    let t = s.Trim()
    if t = "" || t.Length > 3 then None
    elif not (Seq.forall Char.IsDigit t) then None
    else Some (Int32.Parse t)

let rec loop () =
    Console.Write(menu)
    match Console.ReadLine() with
    | null -> Console.Write(msgBye)
    | line ->
        match parse line with
        | Some 0 -> Console.Write(msgBye)
        | Some n when n > last ->
            Console.Write(msgBad)
            loop ()
        | Some n ->
            Console.Write(recipes.[n - 1])
            Console.Write(msgPause)
            match Console.ReadLine() with
            | null -> Console.Write(msgBye)
            | _ -> loop ()
        | None ->
            Console.Write(msgBad)
            loop ()

loop ()
""")


def gen_scm():
    recs = "\n".join('   ' + lit(TEXTS[i]) + ("" if i + 1 == LAST else "")
                     for i in range(LAST))
    w("cookbook.scm", f""";; Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
(use-modules (ice-9 rdelim))

(define last {LAST})

(define recipes
  (list
{recs}))

(define menu {lit(MENU)})
(define msg-bad {lit(MSG_BAD)})
(define msg-pause {lit(MSG_PAUSE)})
(define msg-bye {lit(MSG_BYE)})

;; #f на конце потока
(define (read-stdin-line)
  (let ((l (read-line (current-input-port))))
    (if (eof-object? l) #f (string-trim l))))

(define (all-digits? cs)
  (cond ((null? cs) #t)
        ((let ((k (char->integer (car cs))))
           (and (>= k 48) (<= k 57)))
         (all-digits? (cdr cs)))
        (else #f)))

(define (parse s)
  (if (and (> (string-length s) 0)
           (<= (string-length s) 3)
           (all-digits? (string->list s)))
      (string->number s)
      #f))


(define (loop)
  (display menu)
  (let ((s (read-stdin-line)))
    (cond
     ((not s) (display msg-bye))
     (else
      (let ((n (parse s)))
        (cond
         ((not n) (display msg-bad) (loop))
         ((= n 0) (display msg-bye))
         ((> n last) (display msg-bad) (loop))
         (else (display (list-ref recipes (1- n)))
               (display msg-pause)
               (if (read-stdin-line) (loop) (display msg-bye)))))))))

(loop)
""")


def gen_tcl():
    recs = "\n".join('    ' + lit(TEXTS[i]) + ("" if i + 1 == LAST else "")
                     for i in range(LAST))
    w("cookbook.tcl", f"""# Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
set LAST {LAST}

set recipes [list \\
{recs}]

set menu {lit(MENU)}
set msg_bad {lit(MSG_BAD)}
set msg_pause {lit(MSG_PAUSE)}
set msg_bye {lit(MSG_BYE)}

# -1 на конце потока
proc read_line {{}} {{
    if {{[gets stdin line] < 0}} {{ return -1 }}
    return [string trim $line]
}}

proc parse {{s}} {{
    if {{$s eq "" || [string length $s] > 3}} {{ return -1 }}
    foreach c [split $s ""] {{
        if {{![string is digit -strict $c]}} {{ return -1 }}
    }}
    return [expr {{$s + 0}}]
}}

proc loop {{}} {{
    puts -nonewline $menu
    set s [read_line]
    if {{$s == -1}} {{
        puts -nonewline $msg_bye
        return
    }}
    set n [parse $s]
    if {{$n == 0}} {{
        puts -nonewline $msg_bye
        return
    }}
    if {{$n < 1 || $n > $LAST}} {{
        puts -nonewline $msg_bad
        loop
        return
    }}
    puts -nonewline [lindex $recipes [expr {{$n - 1}}]]
    puts -nonewline $msg_pause
    if {{[read_line] == -1}} {{
        puts -nonewline $msg_bye
        return
    }}
    loop
}}

loop
""")


def gen_cr():
    recs = qlist(TEXTS, 2, "RECIPES = [", "]", escf=lit)
    w("cookbook.cr", f"""# Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
LAST = {LAST}

{recs}

MENU = {lit(MENU)}
MSG_BAD = {lit(MSG_BAD)}
MSG_PAUSE = {lit(MSG_PAUSE)}
MSG_BYE = {lit(MSG_BYE)}

def parse(line : String) : Int32?
  s = line.strip
  return nil if s.empty? || s.size > 3
  return nil unless s.each_char.all?(&.ascii_number? >= 0)
  s.to_i32
end

loop do
  print MENU
  line = STDIN.gets(chomp: true)
  if line.nil?
    print MSG_BYE
    break
  end

  n = parse(line)
  if n.nil?
    print MSG_BAD
    next
  end
  break if n == 0
  if n < 1 || n > LAST
    print MSG_BAD
    next
  end

  print RECIPES[n - 1]
  print MSG_PAUSE
  if STDIN.gets(chomp: true).nil?
    print MSG_BYE
    break
  end
end
""")


def gen_f90():
    recs = "\n".join("  recipes(%d) = %s" % (i + 1, lit(TEXTS[i])) for i in range(LAST))
    w("cookbook.f90", f"""! Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
program cookbook
  implicit none
  integer, parameter :: LAST = {LAST}
  character(len=2048) :: recipes({LAST})
  character(len=4096) :: menu
  character(len=256) :: msg_bad, msg_pause, msg_bye, line
  integer :: n, ios, i, k, c, val

  recipes = (/ {lit(TEXTS[0])}, &
{recs[recs.index(chr(10)) + 1:]} /)
  menu = {lit(MENU)}
  msg_bad = {lit(MSG_BAD)}
  msg_pause = {lit(MSG_PAUSE)}
  msg_bye = {lit(MSG_BYE)}

  do
    write(*, '(A)', advance='no') trim(menu)
    flush(6)
    read(*, '(A)', iostat=ios) line
    if (ios /= 0) then
      write(*, '(A)') trim(msg_bye)
      stop
    end if

    n = -1
    k = len_trim(line)
    val = 0
    if (k >= 1 .and. k <= 3) then
      n = 0
      do i = 1, k
        c = iachar(line(i:i))
        if (c < 48 .or. c > 57) then
          n = -1
          exit
        end if
        val = val * 10 + (c - 48)
      end do
      if (n == 0) n = val
    end if

    if (n == -1) then
      write(*, '(A)') trim(msg_bad)
    else if (n == 0) then
      write(*, '(A)') trim(msg_bye)
      stop
    else if (n > LAST) then
      write(*, '(A)') trim(msg_bad)
    else
      write(*, '(A)') trim(recipes(n))
      write(*, '(A)') trim(msg_pause)
      flush(6)
      read(*, '(A)', iostat=ios) line
      if (ios /= 0) then
        write(*, '(A)') trim(msg_bye)
        stop
      end if
    end if
  end do

end program cookbook
""")


def gen_nim():
    recs = qlist(TEXTS, 2, "const recipes = [", "]", escf=lit)
    w("cookbook.nim", f"""# Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
const LAST = {LAST}

{recs}

const menu = {lit(MENU)}
const msgBad = {lit(MSG_BAD)}
const msgPause = {lit(MSG_PAUSE)}
const msgBye = {lit(MSG_BYE)}

const EOF_SENTINEL = "\\x01eof"

proc readLine(): string =
  let l = stdin.readLine()
  if l.len == 0: EOF_SENTINEL else: l

proc parse(line: string): int =
  let s = line.strip()
  if s.len == 0 or s.len > 3: return -1
  for c in s:
    if c < '0' or c > '9': return -1
  return parseInt(s)

while true:
  stdout.write(menu)
  stdout.flushFile()
  let line = readLine()
  if line == EOF_SENTINEL:
    stdout.write(msgBye)
    break
  let n = parse(line)
  if n == 0:
    stdout.write(msgBye)
    break
  if n < 1 or n > LAST:
    stdout.write(msgBad)
    continue
  stdout.write(recipes[n - 1])
  stdout.write(msgPause)
  stdout.flushFile()
  if readLine() == EOF_SENTINEL:
    stdout.write(msgBye)
    break
""")


def gen_lisp():
    recs = "\n".join('   ' + lit(TEXTS[i]) + ("" if i + 1 == LAST else "")
                     for i in range(LAST))
    w("cookbook.lisp", f""";;; Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
(defparameter *last* {LAST})

(defparameter *recipes*
  (list
{recs}))

(defparameter *menu* {lit(MENU)})
(defparameter *msg-bad* {lit(MSG_BAD)})
(defparameter *msg-pause* {lit(MSG_PAUSE)})
(defparameter *msg-bye* {lit(MSG_BYE)})

(defun read-line ()
  (let ((l (read-line *standard-input* nil nil)))
    (when (stringp l) (string-trim l))))

(defun parse (s)
  (when (and (stringp s)
             (> (length s) 0)
             (<= (length s) 3)
             (every #'(char<= #\9 (char>= #\0)) (coerce s 'list)))
    (parse-integer s)))

(defun loop ()
  (princ *menu*)
  (finish-output)
  (let ((s (read-stdin-line)))
    (if (null s)
        (progn (princ *msg-bye*) (finish-output))
        (let ((n (parse s)))
          (cond
            ((null n) (princ *msg-bad*) (finish-output) (loop))
            ((= n 0) (princ *msg-bye*) (finish-output))
            ((> n *last*) (princ *msg-bad*) (finish-output) (loop))
            (t (princ (nth (1- n) *recipes*))
               (princ *msg-pause*)
               (finish-output)
               (if (read-line) (loop) (progn (princ *msg-bye*) (finish-output)))))))))
(loop)
""")


def gen_clj():
    recs = "\n".join('   ' + lit(TEXTS[i]) + ("" if i + 1 == LAST else "")
                     for i in range(LAST))
    w("cookbook.clj", f""";; Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
(def last-idx {LAST})

(def recipes
  [{recs}])

(def menu {lit(MENU)})
(def msg-bad {lit(MSG_BAD)})
(def msg-pause {lit(MSG_PAUSE)})
(def msg-bye {lit(MSG_BYE)})

(def stdin-reader (java.io.BufferedReader. (java.io.InputStreamReader. System/in "UTF-8")))

(defn read-line []
  (let [l (.readLine stdin-reader)]
    (when (some? l) (.trim l))))

(defn parse [s]
  (when (and s (pos? (count s)) (<= (count s) 3) (re-matches #"[0-9]+" s))
    (Integer/parseInt s)))

(defn loop []
  (print menu)
  (flush)
  (let [s (read-line)]
    (cond
      (nil? s) (print msg-bye)
      :else
      (let [n (parse s)]
        (cond
          (nil? n) (do (print msg-bad) (flush) (recur))
          (zero? n) (do (print msg-bye) (flush))
          (> n last-idx) (do (print msg-bad) (flush) (recur))
          :else (do (print (nth recipes (dec n)))
                    (print msg-pause)
                    (flush)
                    (if (read-line) (recur) (do (print msg-bye) (flush)))))))))

(loop)
""")


def gen_ml():
    recs = qlist(TEXTS, 2, "let recipes = [|", "|]", escf=lit)
    w("cookbook.ml", f"""(* Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py. *)
let last = {LAST}

{recs}

let menu = {lit(MENU)}
let msg_bad = {lit(MSG_BAD)}
let msg_pause = {lit(MSG_PAUSE)}
let msg_bye = {lit(MSG_BYE)}

let read_line () =
  try Some (String.trim (input_line stdin)) with End_of_file -> None

let parse s =
  let n = String.length s in
  if n < 1 || n > 3 then None
  else if not (String.for_all (fun c -> c >= '0' && c <= '9') s) then None
  else Some (int_of_string s)

let rec loop () =
  print_string menu;
  flush stdout;
  match read_line () with
  | None -> print_string msg_bye
  | Some s -> (
      match parse s with
      | Some 0 -> print_string msg_bye
      | Some n when n > last ->
          print_string msg_bad;
          loop ()
      | Some n ->
          print_string recipes.(n - 1);
          print_string msg_pause;
          (match read_line () with
           | None -> print_string msg_bye
           | Some _ -> loop ())
      | None ->
          print_string msg_bad;
          loop ())

let () = loop ()
""")


def gen_groovy():
    recs = qlist(TEXTS, 2, "def recipes = [", "]", escf=lit)
    w("cookbook.groovy", f"""// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
def LAST = {LAST}

{recs}

def MENU = {lit(MENU)}
def MSG_BAD = {lit(MSG_BAD)}
def MSG_PAUSE = {lit(MSG_PAUSE)}
def MSG_BYE = {lit(MSG_BYE)}

def reader = new BufferedReader(new InputStreamReader(System.in, "UTF-8"))

Integer parse(String line) {{
    def t = line?.trim()
    if (!t || t.length() == 0 || t.length() > 3) return -1
    if (!(t ==~ /[0-9]+/)) return -1
    return t as Integer
}}

def loop() {{
    System.out.print(MENU)
    System.out.flush()
    def line = reader.readLine()
    if (line == null) {{
        System.out.print(MSG_BYE)
        return
    }}
    def n = parse(line)
    if (n == 0) {{
        System.out.print(MSG_BYE)
        return
    }}
    if (n < 1 || n > LAST) {{
        System.out.print(MSG_BAD)
        loop()
        return
    }}
    System.out.print(recipes[n - 1])
    System.out.print(MSG_PAUSE)
    System.out.flush()
    def ack = reader.readLine()
    if (ack == null) {{
        System.out.print(MSG_BYE)
        return
    }}
    loop()
}}

loop()
""")


def gen_adb():
    recs = "\n".join("   R (%d) := To_Unbounded_String (%s);" % (i + 1, lit(TEXTS[i]))
                     for i in range(LAST))
    w("cookbook.adb", f"""-- Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
with Ada.Text_IO;
with Ada.Strings.Unbounded;
use Ada.Text_IO;
use Ada.Strings.Unbounded;

procedure Cookbook is
   Last : constant := {LAST};

   type Recipe_Array is array (1 .. Last) of Unbounded_String;
   R : Recipe_Array;

   Menu      : Unbounded_String;
   Msg_Bad   : Unbounded_String;
   Msg_Pause : Unbounded_String;
   Msg_Bye   : Unbounded_String;
   Line      : Unbounded_String;
   N         : Integer;

   function Read_Line return Boolean is
   begin
      if End_Of_Line then
         return False;
      end if;
      Get_Line (Line);
      return True;
   end Read_Line;

   function Parse return Integer is
      S : constant String := To_String (Trim (Line, Both));
      Acc : Integer := 0;
   begin
      if S'Length < 1 or else S'Length > 3 then
         return -1;
      end if;
      for C of S loop
         if C not in '0' .. '9' then
            return -1;
         end if;
         Acc := Acc * 10 + (Character'Pos (C) - Character'Pos ('0'));
      end loop;
      return Acc;
   end Parse;

begin
{recs}

   Menu      := To_Unbounded_String ({lit(MENU)});
   Msg_Bad   := To_Unbounded_String ({lit(MSG_BAD)});
   Msg_Pause := To_Unbounded_String ({lit(MSG_PAUSE)});
   Msg_Bye   := To_Unbounded_String ({lit(MSG_BYE)});

   loop : loop
      Put (Menu);
      if not Read_Line then
         Put (Msg_Bye);
         exit;
      end if;
      N := Parse;
      if N = -1 then
         Put (Msg_Bad);
      elsif N = 0 then
         Put (Msg_Bye);
         exit;
      elsif N > Last then
         Put (Msg_Bad);
      else
         Put (R (N));
         Put (Msg_Pause);
         if not Read_Line then
            Put (Msg_Bye);
            exit;
         end if;
      end if;
   end loop loop;
end Cookbook;
""")


def gen_d():
    recs = qlist(TEXTS, 2, "string[] recipes = [", "];", escf=lit)
    w("cookbook.d", f"""// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
import std.stdio, std.conv, std.string;

enum LAST = {LAST};

{recs}

immutable string MENU = {lit(MENU)};
immutable string MSG_BAD = {lit(MSG_BAD)};
immutable string MSG_PAUSE = {lit(MSG_PAUSE)};
immutable string MSG_BYE = {lit(MSG_BYE)};

bool eofReached;

string readLine() {{
    auto s = readln();
    if (s is null) {{
        eofReached = true;
        return "";
    }}
    return s.strip().idup;
}}

int parse(string s) {{
    if (s.length < 1 || s.length > 3) return -1;
    foreach (c; s) {{
        if (c < '0' || c > '9') return -1;
    }}
    return s.to!int;
}}

void main() {{
    while (true) {{
        write(MENU);
        auto line = readLine();
        if (eofReached) {{
            write(MSG_BYE);
            return;
        }}
        auto n = parse(line);
        if (n == 0) {{
            write(MSG_BYE);
            return;
        }}
        if (n < 1 || n > cast(int) LAST) {{
            write(MSG_BAD);
            continue;
        }}
        write(recipes[n - 1]);
        write(MSG_PAUSE);
        readLine();
        if (eofReached) {{
            write(MSG_BYE);
            return;
        }}
    }}
}}
""")


def gen_pas():
    recs = ",\n".join("  " + lit(TEXTS[i]) for i in range(LAST))
    w("cookbook.pas", f"""{{$mode delphi$}}
{{$H+}}
{{ Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py. }}
program Cookbook;
const
  LAST = {LAST};
  RECIPES: array[1..LAST] of AnsiString = (
{recs}
);
  MENU = {lit(MENU)};
  MSG_BAD = {lit(MSG_BAD)};
  MSG_PAUSE = {lit(MSG_PAUSE)};
  MSG_BYE = {lit(MSG_BYE)};

var
  Line: AnsiString;
  N: Integer;
  Got: Boolean;

function ReadLine: Boolean;
begin
  Result := False;
  if not Eof(Input) then
  begin
    ReadLn(Line);
    Line := Trim(Line);
    Result := True;
  end;
end;

function Parse(const S: AnsiString): Integer;
var
  I, K, Acc: Integer;
begin
  K := Length(S);
  if (K < 1) or (K > 3) then begin Parse := -1; Exit; end;
  Acc := 0;
  for I := 1 to K do
  begin
    if (S[I] < '0') or (S[I] > '9') then begin Parse := -1; Exit; end;
    Acc := Acc * 10 + (Ord(S[I]) - Ord('0'));
  end;
  Parse := Acc;
end;

begin
  repeat
    Write(MENU);
    Got := ReadLine;
    if not Got then
    begin
      Write(MSG_BYE);
      Break;
    end;
    N := Parse(Line);
    if N = -1 then Write(MSG_BAD)
    else if N = 0 then
    begin
      Write(MSG_BYE);
      Break;
    end
    else if N > LAST then Write(MSG_BAD)
    else
    begin
      Write(RECIPES[N]);
      Write(MSG_PAUSE);
      if not ReadLine then
      begin
        Write(MSG_BYE);
        Break;
      end;
    end;
  until False;
end.
""")


def gen_dart():
    recs = qlist(TEXTS, 2, "const recipes = [", "];", escf=lit)
    w("cookbook.dart", f"""// Книга рецептов — {LAST} блюд. Сгенерировано tools/gen.py.
import 'dart:io';

const int last = {LAST};

{recs}

const menu = {lit(MENU)};
const msgBad = {lit(MSG_BAD)};
const msgPause = {lit(MSG_PAUSE)};
const msgBye = {lit(MSG_BYE)};

int? parse(String line) {{
  final s = line.trim();
  if (s.isEmpty || s.length > 3) return null;
  for (final c in s.codeUnits) {{
    if (c < 0x30 || c > 0x39) return null;
  }}
  return int.parse(s);
}}

void main() {{
  while (true) {{
    stdout.write(menu);
    final line = stdin.readLineSync();
    if (line == null) {{
      stdout.write(msgBye);
      return;
    }}

    final n = parse(line);
    if (n == null) {{
      stdout.write(msgBad);
      continue;
    }}
    if (n == 0) {{
      stdout.write(msgBye);
      return;
    }}
    if (n < 1 || n > last) {{
      stdout.write(msgBad);
      continue;
    }}

    stdout.write(recipes[n - 1]);
    stdout.write(msgPause);
    if (stdin.readLineSync() == null) {{
      stdout.write(msgBye);
      return;
    }}
  }}
}}
""")


def main():
    print("генерация, партия 2:")
    for n in NAMES:
        globals()["gen_" + n]()


if __name__ == "__main__":
    main()
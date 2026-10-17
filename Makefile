# ============================================================
#  Книга рецептов — 100 блюд на 20 языках
#
#  make            собрать ассемблерную версию (эталон)
#  make run        запустить эталон
#  make check      собрать всё, что есть в системе, и сравнить вывод
#  make regen      пересобрать исходники из tools/recipes_data.py
#  make clean      убрать сборочные артефакты
#
#  Языки: asm python3 go c c++ csharp rust zig java kotlin js ts
#         ruby php lua perl haskell swift elixir julia
#
#  Тулчейны, которых нет в системе, просто пропускаются.
#  Указать путь можно переменной, например:
#      make check ZIG=/opt/zig/zig TS=./node_modules/.bin/tsc
# ============================================================

PYTHON   ?= python3
GO       ?= go
CC       ?= gcc
CXX      ?= g++
NODE     ?= node
TSC      ?= tsc
LUA      ?= lua
PERL     ?= perl
ZIG      ?= zig
DOTNET   ?= dotnet
RUSTC    ?= rustc
JAVAC    ?= javac
KOTLINC  ?= kotlinc
RUBY     ?= ruby
PHP      ?= php
GHC      ?= ghc
SWIFT    ?= swift
SWIFTC   ?= swiftc
ELIXIR   ?= elixir
JULIA    ?= julia
ERLC     ?= erlc
ERL      ?= erl
FSI      ?= dotnet-fsi
GUILE    ?= guile
TCLSH    ?= tclsh
CRYSTAL  ?= crystal
GFORTRAN ?= gfortran
NIM      ?= nim
SBCL     ?= sbcl
CLJ      ?= clojure
OCAML    ?= ocaml
GROOVY   ?= groovy
GNATM    ?= gnatmake
GDC      ?= gdc
FPC      ?= fpc
DART     ?= dart

BUILD    := build

# первый запуск dotnet интерактивен, а нам нужен неинтерактивный
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE := 1
export DOTNET_CLI_TELEMETRY_OPTOUT := 1
export DOTNET_NOLOGO := 1

# --- эталон: ассемблер ------------------------------------------------
$(BUILD)/cookbook: cookbook.s
	@mkdir -p $(BUILD)
	as --64 -o $(BUILD)/cookbook.o cookbook.s
	ld -o $@ $(BUILD)/cookbook.o

asm: $(BUILD)/cookbook

run: $(BUILD)/cookbook
	@$(BUILD)/cookbook

# --- остальные языки --------------------------------------------------
py:      ; @$(PYTHON)  cookbook.py
go:      ; @$(GO) build -o $(BUILD)/cookbook-go  cookbook.go
c:       ; @$(CC)  -std=c11   -O2 -o $(BUILD)/cookbook-c  cookbook.c
cpp:     ; @$(CXX) -std=c++17 -O2 -o $(BUILD)/cookbook-cpp cookbook.cpp
ts:      ; @npm i --silent --no-fund --no-audit && $(TSC) -p tsconfig.json
js:      ; @$(NODE) cookbook.js
lua:     ; @$(LUA)  cookbook.lua
perl:    ; @$(PERL) cookbook.pl
zig:     ; @$(ZIG) build-exe cookbook.zig -O ReleaseSafe -femit-bin=$(BUILD)/cookbook-zig
cs:      ; @$(DOTNET) run --project cookbook.csproj
rs:      ; @$(RUSTC) -O cookbook.rs -o $(BUILD)/cookbook-rs
java:    ; @$(JAVAC) -encoding UTF-8 cookbook.java && java Cookbook
kt:      ; @$(KOTLINC) cookbook.kt -include-runtime -d $(BUILD)/cb.kt.jar
rb:      ; @$(RUBY) cookbook.rb
php:     ; @$(PHP)  cookbook.php
hs:      ; @$(GHC)  -O cookbook.hs -o $(BUILD)/cookbook-hs
swift:   ; @$(SWIFTC) cookbook.swift -O -o $(BUILD)/cookbook-swift
ex:      ; @$(ELIXIR) cookbook.ex
jl:      ; @$(JULIA) cookbook.jl
erl:     ; @$(ERLC) -o $(BUILD) cookbook.erl
fsx:     ; @$(FSI) cookbook.fsx
scm:     ; @$(GUILE) cookbook.scm
tcl:     ; @$(TCLSH) cookbook.tcl
cr:      ; @$(CRYSTAL) cookbook.cr
f90:     ; @$(GFORTRAN) -ffree-line-length-none -O2 -o $(BUILD)/cb-f90 cookbook.f90
nim:     ; @$(NIM) c -d:release --hints:off --out:$(BUILD)/cb-nim cookbook.nim
lisp:    ; @$(SBCL) --script cookbook.lisp
clj:     ; @$(CLJ) cookbook.clj
ml:      ; @$(OCAML) cookbook.ml
groovy:  ; @$(GROOVY) cookbook.groovy
adb:     ; @$(GNATM) -o $(BUILD)/cb-ada cookbook.adb
d:       ; @$(GDC) -O2 -o $(BUILD)/cb-d cookbook.d
pas:     ; @$(FPC) -O2 -o$(BUILD)/cb-pas cookbook.pas
dart:    ; @$(DART) cookbook.dart

# --- проверка: вывод всех реализаций должен совпасть побайтово ------
INPUTS := '42\n\n7\n101\nabc\n100\n\n0\n' '0\n' '' '\n\n0\n' '-5\n0\n' '101\n0\n'

check: $(BUILD)/cookbook
	@mkdir -p $(BUILD)
	@command -v $(CC)      >/dev/null && $(CC)  -std=c11   -O2 -o $(BUILD)/cb-c   cookbook.c   || true
	@command -v $(CXX)     >/dev/null && $(CXX) -std=c++17 -O2 -o $(BUILD)/cb-cpp cookbook.cpp || true
	@command -v $(GO)      >/dev/null && $(GO) build -o $(BUILD)/cb-go  cookbook.go || true
	@command -v $(ZIG)     >/dev/null && $(ZIG) build-exe cookbook.zig -O ReleaseSafe -femit-bin=$(BUILD)/cb-zig || true
	@command -v $(TSC)     >/dev/null && $(TSC) -p tsconfig.json || true
	@command -v $(DOTNET)  >/dev/null && $(DOTNET) build cookbook.csproj -o $(BUILD)/cs >/dev/null || true
	@command -v $(RUSTC)   >/dev/null && $(RUSTC) -O cookbook.rs -o $(BUILD)/cb-rs || true
	@command -v $(JAVAC)   >/dev/null && $(JAVAC) -encoding UTF-8 cookbook.java || true
	@command -v $(KOTLINC) >/dev/null && $(KOTLINC) cookbook.kt -include-runtime -d $(BUILD)/cb.kt.jar || true
	@command -v $(GHC)     >/dev/null && $(GHC) -O cookbook.hs -o $(BUILD)/cb-hs || true
	@command -v $(SWIFTC)  >/dev/null && $(SWIFTC) cookbook.swift -O -o $(BUILD)/cb-swift || true
	@command -v $(GFORTRAN) >/dev/null && $(GFORTRAN) -ffree-line-length-none -O2 -o $(BUILD)/cb-f90 cookbook.f90 || true
	@command -v $(NIM)      >/dev/null && $(NIM) c -d:release --hints:off --out:$(BUILD)/cb-nim cookbook.nim || true
	@command -v $(GNATM)   >/dev/null && $(GNATM) -o $(BUILD)/cb-ada cookbook.adb || true
	@command -v $(GDC)     >/dev/null && $(GDC) -O2 -o $(BUILD)/cb-d cookbook.d || true
	@command -v $(FPC)     >/dev/null && $(FPC) -O2 -o$(BUILD)/cb-pas cookbook.pas || true
	@command -v $(ERLC)    >/dev/null && $(ERLC) -o $(BUILD) cookbook.erl || true
	@python3 tools/check.py $(BUILD)

# --- генерация -------------------------------------------------------
regen:
	@$(PYTHON) tools/gen.py

clean:
	rm -rf $(BUILD) cookbook cookbook.o

.PHONY: all run check regen clean py go c cpp cs rs zig java kt js ts rb php \
        lua perl hs swift ex jl asm erl fsx scm tcl cr f90 nim lisp clj ml \
        groovy adb d pas dart
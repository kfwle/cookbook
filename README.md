# cookbook

Консольная «Книга рецептов» — 100 блюд на 20 языках. Одна и та же
программа, одинаковый вывод, разные средства.

```
Введи номер от 1 до 100, затем Enter.  0 — выход.
> 42

### 42. ГОЛУБЦЫ с мясом и рисом (6 порции)
...

--- Нажми Enter, чтобы вернуться в меню ---
```

## Запуск

```
make run          # ассемблерная версия (эталон)
python3 cookbook.py
```

## Реализации

| Язык | Файл | Собрано и проверено |
|---|---|---|
| Ассемблер x86-64 | `cookbook.s` | да (эталон) |
| Python | `cookbook.py` | да |
| Go | `cookbook.go` | да |
| C | `cookbook.c` | да |
| C++ | `cookbook.cpp` | да |
| JavaScript | `cookbook.js` | да |
| TypeScript | `cookbook.ts` | да |
| Lua | `cookbook.lua` | да |
| Perl | `cookbook.pl` | да |
| Zig | `cookbook.zig` | да |
| C# | `cookbook.cs` | да |
| Rust | `cookbook.rs` | да |
| Java | `cookbook.java` | да |
| Kotlin | `cookbook.kt` | да |
| Ruby | `cookbook.rb` | да |
| PHP | `cookbook.php` | да |
| Haskell | `cookbook.hs` | нет — см. ниже |
| Swift | `cookbook.swift` | да |
| Elixir | `cookbook.ex` | да |
| Julia | `cookbook.jl` | да |

Ассемблерная версия идёт без libc — только системные вызовы
`write`, `read`, `exit`.

Проверенные версии дают **побайтово одинаковый** вывод: `make check`
собирает всё найденное и сравнивает с эталоном на шести сценариях
ввода (рецепт, пауза, ошибка, выход, пустые строки, число вне
диапазона).

Проверено **19 из 20** — все, кроме Haskell. Причина не в коде:
GHC 9.6.7 в системе доустановлен криво, каталога с интерфейсами
пакета `base` просто нет, поэтому не компилируется вообще ничего.
Сам `cookbook.hs` синтаксически разбирается без ошибок. Лечится
переустановкой пакета `ghc`.

TypeScript требует `npm i` (ставит typescript и @types/node) —
`make ts` делает это сам.

## Вторая партия

| Язык | Файл | Компилятор | Проверено |
|---|---|---|---|
| Erlang | `cookbook.erl` | `erlc` | да |
| F# | `cookbook.fsx` | `dotnet fsi` | да |
| Scheme | `cookbook.scm` | `guile` | да |
| Tcl | `cookbook.tcl` | `tclsh` | нет |
| Crystal | `cookbook.cr` | `crystal` | нет |
| Fortran | `cookbook.f90` | `gfortran` | нет |
| Nim | `cookbook.nim` | `nim` | нет |
| Common Lisp | `cookbook.lisp` | `sbcl` | нет |
| Clojure | `cookbook.clj` | `clojure` | нет |
| OCaml | `cookbook.ml` | `ocaml` | нет |
| Groovy | `cookbook.groovy` | `groovy` | нет |
| Ada | `cookbook.adb` | `gnatmake` | нет |
| D | `cookbook.d` | `gdc` | нет |
| Pascal | `cookbook.pas` | `fpc` | нет |
| Dart | `cookbook.dart` | `dart` | нет |

Тулчейны для непроверенных ставятся одним списком — см. README в
разделе «Сборка».

## Как это устроено

```
tools/recipes_data.py   единственный источник рецептов
tools/gen.py            генератор всех файлов
tools/check.py          сравнение вывода реализаций
recipes.txt             те же данные в читаемом виде
```

Рецепты описаны один раз в `tools/recipes_data.py`. `tools/gen.py`
по нему собирает все 20 исходников, `recipes.txt` и `cookbook.s`.
Править руками сгенерированные файлы бессмысленно — они перезапишутся.

```
make regen              пересобрать всё из recipes_data.py
```

Состав рецептов сверен с the-challenger.ru, gastronom.ru, kulina.ru,
ria.ru, barilla.ru, vkusvill.ru, delo-vcusa.ru, supercook.ru.

## Сборка отдельной версии

```
make c && ./build/cookbook-c
make go && ./build/cookbook-go
make java
```

Тулчейны, которых нет в системе, пропускаются. Путь можно задать
переменной: `make check ZIG=/opt/zig/zig`.
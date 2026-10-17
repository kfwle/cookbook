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
| C# | `cookbook.cs` | нет |
| Rust | `cookbook.rs` | нет |
| Java | `cookbook.java` | нет |
| Kotlin | `cookbook.kt` | нет |
| Ruby | `cookbook.rb` | нет |
| PHP | `cookbook.php` | нет |
| Haskell | `cookbook.hs` | нет |
| Swift | `cookbook.swift` | нет |
| Elixir | `cookbook.ex` | нет |
| Julia | `cookbook.jl` | нет |

Ассемблерная версия идёт без libc — только системные вызовы
`write`, `read`, `exit`.

Проверенные версии дают **побайтово одинаковый** вывод: `make check`
собирает всё найденное и сравнивает с эталоном на шести сценариях
ввода (рецепт, пауза, ошибка, выход, пустые строки, число вне
диапазона).

Непроверенные версии написаны по тем же правилам, но собрать их
здесь нечем — тулчейна нет в системе, а ставить без root нельзя.
Их код стоит прогнать через `make check` на машине, где нужный
компилятор есть.

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
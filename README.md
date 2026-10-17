# cookbook

Консольная «Книга рецептов» на ассемблере x86-64. Только системные
вызовы Linux (`write`, `read`, `exit`), без libc.

```
./cookbook
```

Меню с 10 рецептами, ввести номер и Enter. `0` — выход.
Готовый бинарник: [Releases](https://github.com/kfwle/cookbook/releases).

## Сборка

Нужны только `as` и `ld`:

```
make
```
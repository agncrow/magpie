# magpie

The log as a directory of batch files, written in Crow. Each commit is
one file, written once: its rows take the log's next positions, sorted
by the log's keys, with the statistics a reader prunes by. Over the
files are the reads a program asks of a log — the rows since a position,
the newest version of each key, a lookup, a window scanned, a search
ranked as Lucene ranks it, the nearest vectors, an aggregate pushed
below the reader and an as-of join. A sequencer orders every write of a
process and refuses a stale commit; a merge folds the files into sorted
segments; a second node follows the log by its files. Two doors let
other products' clients in: Kafka's protocol and Redis's. Every answer
is the same in `crow run -i` and `crow run`.

```
deps = map[magpie = 'github.com/agncrow/magpie/packages/magpie@v0.1.1']
```

`crow install` checks the package out into `crow_modules/magpie`, and
`crow.lock` pins the commit it took and the hash of the files it
installed. A program imports it and calls it qualified; the doors are
the package's parts:

```
use magpie, frame
use magpie.kafka
```

Magpie stands on the standard library's own layer — `use sys` for bytes,
files and sockets, `use memory` for the sequencer's state, which the
process holds — as any package that needs it may. Its file format is its
own.

[The Magpie book](https://agncrow.github.io/magpie/book/) is the tour:
every write and read as a program with what it prints, the doors, the
packages built on Magpie and the design. [REFERENCE.md](REFERENCE.md) has
every function and part, and the design notes that decided them;
[PARTS.md](PARTS.md) shows each part at work alone; `example.co` runs the
book's tour and every part's block in both modes.

## License

Business Source License 1.1: the `LICENSE` beside this file, in plain
words in the repository's `LICENSING.md`. Free for development, testing
and non-commercial use, and for commercial production on one machine per
application; clusters and hosted services need a commercial license
(vkotinaga@gmail.com). Each version becomes Apache-2.0 four years after
it is published.

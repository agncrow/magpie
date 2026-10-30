<p align="center"><img src="assets/magpie.svg" width="128" alt="Magpie"></p>

# Magpie

The log as a directory of batch files, written in Crow: each commit one
file written once, its rows given positions and sorted by the log's keys,
with the statistics a reader prunes by; the reads a program asks of a log
over those files — since a position, the newest version of each key, a
lookup, a window, a search ranked as Lucene ranks it, the nearest vectors,
an aggregate pushed below the reader, an as-of join; a sequencer that
orders every write and refuses a stale commit; a merge into sorted
segments; a second node that follows the log by its files; and doors that
let Kafka's and Redis's clients in. Every answer is the same in
`crow run -i` and `crow run`.

**Introducing Magpie**, with diagrams of how it works and its first
measurements: [agncrow.github.io/magpie](https://agncrow.github.io/magpie/).

| Package | What it is |
|---|---|
| [`packages/magpie`](packages/magpie/README.md) | the log, its parts and its two doors — the tour in its README, every function in [REFERENCE.md](packages/magpie/REFERENCE.md), each part at work in [PARTS.md](packages/magpie/PARTS.md) |
| [`packages/kg`](packages/kg/README.md) | a knowledge graph whose nodes and edges are Magpie logs |
| [`packages/features`](packages/features/README.md) | a feature store over Magpie, held to pandas's `merge_asof` |

A program installs a package as any dependency and calls it qualified:

```
deps = map[magpie = 'github.com/agncrow/magpie/packages/magpie@v0.1.1']
```

```
use magpie, frame

made = mkdir['orders']
first = magpie.batch['orders', frame.new[id = [1, 2], qty = [10, 20]], by = ['id']]
log[magpie.latest['orders'].qty]
```

kg and features name magpie in their crowfiles, so `crow install` puts it
beside them. Magpie needs a crow newer than its latest release (0.7.0):
until the next release, build crow from a checkout of its main branch
with `./install.sh --source`.

## What else is here

- `examples/magpie`: a page over a log — orders land as batches, the page
  reads the table the log holds, a search over the notes and the log's
  figures, each a derivation that follows the writes; `crow run main.co`
  from its folder serves it on port 3600.
- `tests/parity`: programs held to give the same output interpreted and
  compiled; `tests/doors.py`: the HTTP, Kafka and RESP doors, a shared log
  and its followers, and a merge or a put cut short, driven from outside
  in both modes; `tests/measure`: the programs behind Magpie's measured
  numbers, run by hand (their README says how); `tests/reference.py`: the
  BM25 scores a search is held to.
- `docs`: the design ([magpie-design.md](docs/magpie-design.md)) and the
  port of its Rust kernels to Crow ([magpie-in-crow.md](docs/magpie-in-crow.md)).

## Testing

```
./test.sh [path to crow]
```

runs `crow test --packages` (each package's test blocks, and its
`example.co` in both modes), `crow test --parity`, `crow test --served`
(the example app, its pages compared across the modes) and
`tests/doors.py` — the crow on the PATH unless a binary is named. The
Kafka door's run needs the pure-Python client (kafka-python 3.0.11),
looked for as `CROW_KAFKA_PYTHON` or in the Python running the script,
and is skipped without it.

Magpie needs a crow from 2026-10-30 or later: one in which a package may
import `sys` and `memory`, a package linked into `crow_modules` keeps its
name in every file it brings, `crow install` installs a package without
its own `crow_modules/` (kg and features keep links to magpie there), and
the served harness serves an app with its linked packages. Crow's own gate runs this suite before a change to
the compiler lands, so a change that breaks Magpie is seen there.

## History and license

Magpie was built inside the crow repository — as standard modules under
`src/modules/` until 2026-10-29, then as `packages/magpie` — and its
history up to the move is crow's.

Magpie is source-available under the [Business Source License 1.1](LICENSE)
(in plain words: [LICENSING.md](LICENSING.md)). It is free for development
and testing, for non-commercial use, and for commercial production on one
machine per application. Clusters, standbys, shards and hosted services
need a commercial license (vkotinaga@gmail.com). Each version becomes
Apache-2.0 four years after it is published.

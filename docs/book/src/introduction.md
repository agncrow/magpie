# Introduction

Magpie is a storage engine written in Crow. Every write enters an ordered
log, kept as a directory of files written once, and a program reads that
one history in the ways an application needs: the newest row of each key,
the rows since a position, a window, a search ranked as Lucene ranks it,
the nearest vectors, an aggregate pushed below the reader and an as-of
join. A sequencer orders every write of a process and refuses a stale
commit; a merge folds the files into sorted segments; a second node
follows the log by its files; and doors let other programs' clients in,
over HTTP and in Kafka's and Redis's protocols. Every answer is the same
in `crow run -i` and `crow run`.

[Introducing Magpie](../index.html) tells the idea and the design with
diagrams, and the first measurements. This book is the manual:

- **Part I, the log**: installing Magpie, then a tour of its writes and
  reads, each a program with what it prints.
- **Part II, other clients**: the HTTP door, and the Kafka and Redis
  protocols Magpie speaks.
- **Part III, built on Magpie**: a knowledge graph and a feature store,
  two packages whose data are Magpie logs.
- **Part IV, reference**: every function and part, and each part at work
  alone.
- **Appendices**: the design and the decisions behind it, the port of
  Magpie's Rust kernels to Crow, how its numbers were measured, and its
  license.

Every program in Parts I and II runs as it is written. `crow test --book`,
run from the repository's root, runs each one interpreted and compiled
and holds both to the output printed under it; the parts' programs in
Part IV run the same way in the package's `example.co`.

# Magpie's measures, on small sets

The programs behind the measured results of Magpie's article and of
docs/magpie-in-crow.md (4.2). Each prints its own numbers. Magpie is
Crow code, so the compiled program is the measure: build each with
`crow build` and run the binary, one at a time, on a quiet machine
(`crow run -i` runs the same program interpreted, and slower). Every
number is end to end in the program, from the call to the value in
hand, with no result serialization: the first run cold where a program
says so, then the median of the warm runs where it says `REPS`.

| Program | What it measures | Needs |
|---|---|---|
| `vectors.co` | `nearest` over `N` vectors of width `W` from the files, against crow's vectors package's flat index (`packages/vectors` in the crow repository) over the same matrix in memory; the positions and the cosines must agree | nothing |
| `graph.co` | a hop over `N` nodes with `D` out-edges each: `neighbors`, `walk` of one to three hops (`packages/kg`) | nothing |
| `words.co` | a common word's top 10 over `N` texts: the batches scanned, then the merged segment's index | nothing |
| `wide.co` | a log of `N` rows by `C` float columns: the write, the merge, a scan of two columns, a lookup, a summary | nothing |
| `seq.co` | `put`, `latest` of one key and a durable `batch`, 2,000 each, beside Postgres's `INSERT` and `SELECT` by primary key (`PG`, a scratch database); Redis is asked by `redis-benchmark -p 6399 -t set,get -n 2000 -c 1 -q` beside it | Postgres; `redis-server --port 6399 --save '' --appendonly no` |
| `copy_month.co` | finch's September 2026 copied out of ClickHouse and Postgres into a Magpie log under `ROOT`, a batch a day, each log merged | finch's ClickHouse (native port 9000) and Postgres |
| `finch.co` | finch's five questions against ClickHouse as finch runs it (`clickhouse://localhost:8123/finch_trading`) and against the log `ROOT`, from the files and over rows held, five times each; the answers checked against ClickHouse's | `copy_month.co` first |

Run from this directory, so `use magpie`, `use kg` and `use vectors.flat`
resolve through `crow_modules/`. Magpie and kg are linked there from this
repository's packages; `vectors` is crow's package, which `crow install`
fetches into `crow_modules/` once (the crowfile names it), before
`vectors.co` runs:

```
crow install
for p in vectors graph words wide seq copy_month finch; do crow build $p.co; done
./copy_month
N=20000 W=64 ./vectors
N=100000 W=64 ./vectors
N=5000 D=10 ./graph
N=100000 ./words
N=200000 C=100 ./wide
redis-server --port 6399 --save '' --appendonly no &
N=2000 ./seq
redis-benchmark -p 6399 -t set,get -n 2000 -c 1 -q
./finch
```

The recorded runs: 2026-10-27 interpreted, while Magpie's byte-level
work ran in Rust kernels inside crow's runtime, since rewritten in Crow
(docs/magpie-design.md, "Measured 2026-10-27"); 2026-10-29 and
2026-10-30 compiled (docs/magpie-in-crow.md 4.2; the article). An Apple
M4 Max with 64 GB, Postgres 14.20 and Redis 8.2 from Homebrew,
ClickHouse 25.7 as finch runs it (143,000 active parts). Small sets
teach mechanisms, not rankings: the sizes are a few hundred thousand
rows, where every structure fits in memory, and no number here says
what a billion rows would.

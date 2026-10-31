# Vectors in the log: the nearest rows

```crow
use magpie
use frame

gone = rm['ex_nearest']
made = mkdir['ex_nearest']
a = magpie.batch['ex_nearest', frame.new[id = [1, 2, 3], e = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]], by = ['id']]
hits = magpie.nearest['ex_nearest', 'e', [1.0, 0.1], 2]
log[hits.id]
log[fmt[hits.score[0], decimals = 3]]
log[magpie.latest['ex_nearest', equal = ['3']].e[0]]
gone = rm['ex_nearest']
```

```text
[1, 3]
0.995
[1, 1]
```

A column of vectors (an embedding per row) is held as any column —
written as a float chunk of rows × width, `narrow` keeping 32 bits,
carried through `latest`, `since` and the merge — and `nearest` finds
the `k` rows nearest a query vector by the cosine, the best first,
exact over every row of the log. An entity is found by meaning first,
and the edges expand it (packages/kg's `embed` and `similar`).

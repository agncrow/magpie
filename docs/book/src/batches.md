# Batches, reads, a commit and a merge

```crow
use magpie
use frame

gone = rm['ex_magpie']
made = mkdir['ex_magpie']
first = magpie.batch['ex_magpie', frame.new[id = [1, 2], qty = [10, 20]], by = ['id']]
log[first]
second = magpie.batch['ex_magpie', frame.new[id = [2, 3], qty = [25, 30]], by = ['id']]
log[second]
log[magpie.head['ex_magpie']]
log[magpie.latest['ex_magpie'].qty]
log[magpie.lookup['ex_magpie', ['id'], ['2']].qty]
stale = magpie.commit['ex_magpie', frame.new[id = [2], qty = [26]], seen = 1, columns = ['id'], equal = ['2']]
log[stale.reason]
log[magpie.since['ex_magpie', 3].qty]
log[magpie.scan['ex_magpie', 0, 1].id]
log[len[magpie.batches['ex_magpie']]]
log[magpie.merge['ex_magpie']]
log[magpie.batches['ex_magpie'].form]
log[magpie.latest['ex_magpie'].qty]
log[magpie.batch['ex_magpie', frame.new[id = [4], qty = [40]], by = ['qty']].reason]
log[magpie.batch['ex_magpie', frame.new[id = [4], qty = [40]]]]
gone = rm['ex_magpie']
```

```text
0
2
3
[10, 25, 30]
[20, 25]
conflict: id = 2 was written at position 2, after snapshot 1
[30]
[1, 2]
2
ex_magpie/S000000000001.segment
['segment']
[10, 25, 30]
the log at 'ex_magpie' is keyed by id, not by qty
4
```

Each `batch` is one file in the directory, written once: the rows take
the next positions, sorted by the log's keys, with the statistics a
reader prunes by in the file's index. The first batch fixes the keys
(`by`), and the manifest beside the files records them: a later batch
names the same keys or none, and another set is refused naming both.
`latest` is the table the log holds, one row per key; `lookup` reads
only the files whose filters admit the value; `commit` is the sequencer,
refusing a write whose reads are stale; `merge` folds the files into one
segment holding the latest version of each key, then switches the
manifest to name it, which the same readers read.

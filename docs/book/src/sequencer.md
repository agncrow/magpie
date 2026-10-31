# The sequencer: put, a key's newest row, and a commit decided in memory

```crow
use magpie
use frame
use math

gone = rm['ex_tail']
made = mkdir['ex_tail']
first = magpie.put['ex_tail', frame.new[id = [1, 2], qty = [10, 20]], by = ['id']]
log[first]
log[int[sum[magpie.batches['ex_tail'].rows]]]
log[magpie.since['ex_tail', 0].qty]
second = magpie.put['ex_tail', frame.new[id = [2, 3], qty = [25, 30]]]
log[magpie.latest['ex_tail', equal = ['2']].qty]
log[len[magpie.latest['ex_tail', equal = ['9']]]]
log[magpie.sync['ex_tail'] gte 1]
log[int[sum[magpie.batches['ex_tail'].rows]]]
stale = magpie.commit['ex_tail', frame.new[id = [2], qty = [26]], seen = 1, columns = ['id'], equal = ['2']]
log[stale.reason]
fine = magpie.commit['ex_tail', frame.new[id = [2], qty = [26]], seen = 3, columns = ['id'], equal = ['2']]
log[fine]
log[magpie.latest['ex_tail', equal = ['2']].qty]
gone = rm['ex_tail']
```

```text
0
2
[10, 20]
[25]
0
true
4
conflict: id = 2 was written at position 2, after snapshot 1
4
[26]
```

Every write of a process goes through the log's sequencer: `put` gives
the rows their positions as they arrive and the process reads them at
once, as the catalog's `pending` row; the flush the put asks for writes
them as a batch file (`later`: at once under `crow run -i`, on a thread
compiled), or `sync` does now, and `batch` is a put
and a flush, durable before it answers. `latest` of one key (`equal`) reads the newest row of a
key from the image the sequencer keeps in memory, and a `commit` whose
reads are the log's keys is decided against the sequencer's index in
memory.

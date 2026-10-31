# A batch without the flush, and a sync

```crow
use magpie
use frame

gone = rm['ex_flush']
made = mkdir['ex_flush']
a = magpie.batch['ex_flush', frame.new[id = [1, 2], qty = [10, 20]], by = ['id'], flush = false]
b = magpie.batch['ex_flush', frame.new[id = [3], qty = [30]], by = ['id'], flush = false]
log[magpie.latest['ex_flush'].qty]
log[magpie.sync['ex_flush'] gt 0]
gone = rm['ex_flush']
```

```text
[10, 20, 30]
true
```

With `flush = false` a batch is written but not flushed to the disk, so
a crash may lose the batches since the last `sync`: Redis's default
durability, for a log that chooses it; `sync` flushes every file of the
log and its directory, and a program calls it on a timer.

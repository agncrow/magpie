# Operations: the figures, a backup, a restore

```crow
use magpie
use frame

gone = rm['ex_ops']
gone = rm['ex_ops_copy']
made = mkdir['ex_ops']
a = magpie.batch['ex_ops', frame.new[id = [1, 2], qty = [10, 20]], by = ['id']]
b = magpie.batch['ex_ops', frame.new[id = [2, 3], qty = [25, 30]], by = ['id']]
figures = magpie.metrics['ex_ops']
log[figures.files]
log[figures.rows]
log[figures.head]
log[figures.bytes[0] gt 0]
log[magpie.backup['ex_ops', 'ex_ops_copy']]
gone = rm['ex_ops']
log[magpie.restore['ex_ops_copy', 'ex_ops']]
log[magpie.latest['ex_ops'].qty]
gone = rm['ex_ops']
gone = rm['ex_ops_copy']
```

```text
[2]
[4]
[3]
true
3
3
[10, 25, 30]
```

`metrics` is the log's figures as a frame of one row, a table a program
keeps by writing it to a log of its own. `backup` copies the live files
and the manifest under a directory or an `s3://` prefix and writes a
`listing` last, so a backup is whole only when its listing is; `restore` copies them back,
and the batches written since are the rest of the log.

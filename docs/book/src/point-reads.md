# A point read by two keys, and only the columns asked

```crow
use magpie
use frame

gone = rm['ex_keys']
made = mkdir['ex_keys']
a = magpie.batch['ex_keys', frame.new[day = [1, 1, 2, 2], sym = ['A', 'B', 'A', 'B'], px = [10, 11, 12, 13], qty = [1, 2, 3, 4]], by = ['day', 'sym']]
log[magpie.lookup['ex_keys', ['day', 'sym'], ['2', 'A']].px]
log[magpie.lookup['ex_keys', ['day'], ['1'], ['sym', 'px']].columns]
log[magpie.scan['ex_keys', 0, -1, ['qty']].qty]
log[magpie.since['ex_keys', 2, -1, ['sym', '_pos']].sym]
gone = rm['ex_keys']
```

```text
[12]
['sym', 'px']
[1, 2, 3, 4]
['A', 'B']
```

`lookup` takes every key at once, so a segment sorted by day then
symbol reads one row group for one symbol's day instead of the symbol's
whole month; `columns` on `lookup`, `scan`, `since` and `latest` names
the columns to read, and a segment decodes only those, which is what a
month's scan pays for two columns and not ten. A lookup by a column the
log is not sorted by scans the files its filters admit: where that
recurs, keep a second log of the same rows sorted by that column, fed
from the first with `tail` (a sorted projection: one more write per row,
and the point read reads one group again).

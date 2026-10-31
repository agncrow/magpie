# Windows: a read is bounded, the log is walked

```crow
use magpie
use frame
use math

gone = rm['ex_windows']
made = mkdir['ex_windows']
a = magpie.batch['ex_windows', frame.new[day = ['d1', 'd1', 'd2', 'd2'], sym = ['A', 'B', 'A', 'B'], px = [1, 2, 3, 4]], by = ['day', 'sym']]
b = magpie.batch['ex_windows', frame.new[day = ['d2', 'd3'], sym = ['A', 'A'], px = [5, 6]]]
log[magpie.since['ex_windows', 2, 4].px]
log[magpie.scan['ex_windows', 1, 2, ['px']].px]
log[magpie.latest['ex_windows', lo = 'd2', hi = 'd2'].px]
log[magpie.latest['ex_windows', hi = 'd1'].sym]
total = 0
at = 0
last = magpie.head['ex_windows']
while at lte last
    piece = magpie.since['ex_windows', at, at + 1, ['px']]
    total = total + int[sum[piece.px]]
    at = at + 2
log[total]
gone = rm['ex_windows']
```

```text
[3, 4, 5]
[2, 3]
[4, 5]
['A', 'B']
21
```

A read answers a frame, so every read is bounded: `since` and `scan`
take a position window, `latest` a range of the log's first key, read
through the groups the range covers. A read over the whole log is a
loop over windows, as the sum above walks the positions two at a time;
an aggregate over a billion rows is that loop, each window reading its
segments and its columns and nothing else.

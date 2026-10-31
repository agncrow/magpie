# A view that follows the log

```crow
use magpie
use frame
use math

gone = rm['ex_tail']
made = mkdir['ex_tail']
first = magpie.batch['ex_tail', frame.new[sym = ['A', 'B'], qty = [10, 20]]]
seen = -1
total = 0
rows = magpie.tail['ex_tail', seen, 0.2]
total = total + sum[rows.qty]
seen = max[rows._pos]
second = magpie.batch['ex_tail', frame.new[sym = ['A'], qty = [5]]]
rows = magpie.tail['ex_tail', seen, 0.2]
total = total + sum[rows.qty]
seen = max[rows._pos]
log[total]
log[seen]
none = magpie.tail['ex_tail', seen, 0.05]
log[len[none]]
gone = rm['ex_tail']
```

```text
35
2
0
```

`tail` answers the rows past a position, waiting up to the seconds for
some to arrive: a view is a loop over it, each round a batch of new rows
folded into the state the view keeps, the position of the last row read
kept with it, and its results written back to a log with `batch` for
other views and other nodes to read.

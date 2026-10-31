# Aggregates below the reader, and the as-of join

```crow
use magpie
use frame

gone = rm['ex_summary']
made = mkdir['ex_summary']
a = magpie.batch['ex_summary', frame.new[day = [1, 1, 2, 2], sym = ['A', 'B', 'A', 'B'], px = [10.0, 20.0, 12.0, 22.0], vol = [1, 2, 3, 4]], by = ['day', 'sym']]
sums = magpie.summary['ex_summary', ['sym'], ['px', 'vol'], ['mean', 'sum']]
log[sums.columns]
log[sums.px_mean]
log[sums.vol_sum]
log[magpie.summary['ex_summary', ['day'], ['vol'], ['count'], on = ['sym'], ops = ['eq'], equal = ['A']].vol_count]
log[magpie.summary['ex_summary', [], ['px'], ['max'], lo = '2'].px_max]
gone = rm['ex_summary']
gone = rm['ex_asof']
made = mkdir['ex_asof']
b = magpie.batch['ex_asof', frame.new[sym = ['A', 'A', 'B'], t = [10, 20, 15], px = [1.0, 2.0, 5.0]], by = ['sym'], time = 't']
labels = frame.new[sym = ['A', 'B', 'A'], t = [25, 12, 5]]
j = magpie.prior['ex_asof', labels]
log[j.columns]
log[j.px[0]]
log[j.px[1].ok]
log[magpie.prior['ex_asof', labels, [], 0].px[0]]
gone = rm['ex_asof']
```

```text
['sym', 'px_mean', 'vol_sum']
[11, 21]
[4, 6]
[1, 1]
[22]
['sym', 't', 'px']
2
false
1
```

`summary` is the aggregate pushed below the reader: each row group is
pruned by its statistics, decoded for the columns named alone, filtered
by the predicates, grouped and reduced one group at a time, and the
partials are combined, so the rows are never held as one frame. It answers what
`group` answers over `scan` of the same rows. `prior` is the as-of join
over the log: for each label's keys and moment, the newest row at or
before it, from the key's run; with `upto`, as of that position, so a
training set a position names comes out the same at every run.

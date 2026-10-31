# Search over the log

```crow
use magpie
use frame

gone = rm['ex_search']
made = mkdir['ex_search']
a = magpie.batch['ex_search', frame.new[id = [1, 2, 3], text = ['the quick brown fox', 'a lazy dog', 'the fox and the dog']]]
b = magpie.batch['ex_search', frame.new[id = [4], text = ['brown bread']]]
hits = magpie.search['ex_search', 'text', ['brown', 'dog'], 3]
log[hits.id]
log[fmt[hits.score[0], decimals = 3]]
log[len[magpie.search['ex_search', 'text', ['zebra']]]]
gone = rm['ex_search']
```

```text
[4, 2, 1]
0.382
0
```

A batch is read whole when it is searched; the merge indexes every text
column of the segments it writes (per row group, a filter over its
words, a sorted dictionary and each word's postings), and a search reads
a merged group through them. Either way the rows are scored as Lucene
scores them (BM25), over the whole log as one corpus, and the ranking is
the same.

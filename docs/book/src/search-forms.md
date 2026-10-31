# Search's forms: a phrase, a prefix, a fuzzy word, a snippet

```crow
use magpie
use frame

gone = rm['ex_forms']
made = mkdir['ex_forms']
a = magpie.batch['ex_forms', frame.new[id = [1, 2, 3, 4, 5], text = ['the kitchen table is set', 'a table in the garden', 'kitchens of the world', 'running the kitchen', 'tables and chairs']]]
log[magpie.search['ex_forms', 'text', ['kitchen table']].id]
log[magpie.search['ex_forms', 'text', ['kit*']].id]
log[magpie.search['ex_forms', 'text', ['kitchn~']].id]
log[magpie.search['ex_forms', 'text', ['table'], 2, snippet = 6].snippet]
m = magpie.merge['ex_forms']
log[magpie.search['ex_forms', 'text', ['kitchen table']].id]
log[magpie.search['ex_forms', 'text', ['tabel~', 'kitchen']].id]
s = magpie.batch['ex_stems', frame.new[id = [1, 2, 3], text = ['the tables', 'a table', 'no chairs']], stem = true]
log[magpie.search['ex_stems', 'text', ['tabling']].id]
gone = rm['ex_stems']
gone = rm['ex_forms']
```

```text
[1]
[1, 3, 4]
[1, 3, 4]
['…tchen table is se…', 'a table in th…']
[1]
[1, 2, 5, 4]
[1, 2]
```

A word with a space is a phrase (the tokens in order), `kit*` a prefix,
`kitchn~` a fuzzy word within two edits (`~1` within one), and
`snippet` asks for that many characters each side of the first hit. A
log declared with `stem = true` stems its words with the Porter
stemmer at the index and at the query, so `tabling` finds `tables` and
`table`. A batch is read whole and a merged segment through the
postings the merge built, and the ranking is the same.

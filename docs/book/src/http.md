# HTTP: the verbs from another process

```crow
use magpie
use frame

gone = rm['ex_door']
made = mkdir['ex_door']
a = magpie.batch['ex_door/orders', frame.new[id = [1, 2], qty = [10, 20]], by = ['id']]
served = magpie.door['ex_door', 0, rounds = 3]
log[served]
gone = rm['ex_door']
```

```text
0
```

`door[root, port]` serves every log under the root over HTTP: a
request's path names the log and the verb (`/orders/latest`,
`/orders/lookup`, `/orders/search`, `/orders/summary`, …), the query its
arguments, the body the rows of a `/orders/put` or `/orders/batch` as
JSON records, and the answer a frame as JSON records. A program in
another process reaches a log through the same verbs given its URL —
`latest['http://host:9000/orders']`, `batch['http://host:9000/orders',
rows]` — and so does any HTTP client
(`curl 'http://host:9000/orders/lookup?on=id&equal=2'`). The block above runs
the door's loop three rounds with nobody connecting; a client's session
in both modes is tests/doors.py.

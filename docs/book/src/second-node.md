# A second node

A second node follows the log: it holds the same files and reads them
with the same verbs. A table too large for one node is split into logs
by a key, one on each node, and a query runs the same verbs on each and
stacks the answers.

```crow,norun
use magpie

--- the leader: its log served to followers, forever
served = magpie.share['orders', 3700]
```

```crow,norun
use magpie

--- a follower, on another machine: the files it lacks, fetched; then
--- the log read by position as any log is, and the pass run again
seen = -1
came = magpie.follow['orders', 'leader.local', 3700]
rows = magpie.since['orders', seen + 1]
```

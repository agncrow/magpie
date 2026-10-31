# The Kafka protocol: `use magpie.kafka`

```crow
use magpie.kafka
use frame

gone = rm['ex_kafka']
served = kafka.serve['ex_kafka', 0, rounds = 3]
log[served]
log[exists['ex_kafka']]
gone = rm['ex_kafka']
```

```text
0
true
```

`kafka.serve[root, port]` is the door: a Kafka client that connects to the port
is spoken to in the protocol a 0.10.1 broker speaks, its records landing
in the magpie's logs under the root, one log per topic. The block above
runs the door's loop three rounds with nobody connecting; a producer and a
consumer group driven against a running door are tests/doors.py's, with
the pure-Python client.

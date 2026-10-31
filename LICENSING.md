# Licensing

Magpie is source-available under the [Business Source License 1.1](https://github.com/agncrow/magpie/blob/main/LICENSE)
(BSL), with an additional use grant. This page says what that means in
plain words; where the two differ, the license decides.

## Free, for everyone

- Reading, changing and sharing the code.
- Development, testing, evaluation, continuous integration, staging and
  demos, on any number of machines.
- **Non-commercial use in production, without limit** — an individual's
  study, research and hobby projects, and charities, schools, public
  research and government, clusters included.
- **Commercial use in production on one machine per application.**

## Needs a commercial license

- A company's production use of one application on **more than one
  machine**: a follower or read replica (`follow`), a standby that keeps
  up with the log, shards on several machines, or a log opened by several
  machines over shared or network storage.
- Offering Magpie — or a product whose main value is Magpie — to others
  as a **hosted or managed service**.

## Counting machines

A machine is one physical computer or one virtual machine, with every
process and container on it.

| A second machine (needs a license) | Not a second machine (free) |
|---|---|
| A follower or read replica (`follow`) | Clients reaching the machine through Magpie's HTTP, Kafka or Redis doors, or the application's own API |
| A standby that keeps up with the log | Backups at rest (`backup` to a directory or S3) |
| One application's logs split across machines | Restoring onto a replacement machine after a failure |
| One log opened by several machines over shared storage | Several processes or containers on the one machine |

## Forks

A modified copy stays under the same license, whoever modified it and
whatever was added: it may not be used in production beyond these terms,
nor offered as a hosted service, and it may not use the name Magpie.

## Four years on

Each version of Magpie becomes available under the Apache License 2.0 four
years after it is published — the BSL's change date.

## Contributions

Outside contributions are not accepted yet: a contributor license
agreement will come first (see [CONTRIBUTING.md](https://github.com/agncrow/magpie/blob/main/CONTRIBUTING.md)).

## Commercial licenses

Write to vkotinaga@gmail.com.

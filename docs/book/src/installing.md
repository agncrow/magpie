# Installing Magpie

Magpie is a Crow package. A program names it among its dependencies, in
its crowfile:

```
deps = map[magpie = 'github.com/agncrow/magpie/packages/magpie@v0.1.1']
```

`crow install` checks the package out into `crow_modules/magpie`, and
`crow.lock` pins the commit it took and the hash of the files it
installed. A program imports it and calls it qualified; the doors are the
package's parts:

```
use magpie, frame
use magpie.kafka
```

Magpie needs Crow 0.8.0 or later ([installing
Crow](https://agncrow.github.io/crow/ch01-01-toolchain.html)). It stands
on the standard library's own layer — `use sys` for bytes, files and
sockets, `use memory` for the sequencer's state, which the process holds
— as any package that needs it may. Its file format is its own ([the
design](design.md)).

The knowledge graph and the feature store are packages of the same
repository, installed the same way (`packages/kg`, `packages/features`);
each names magpie in its own crowfile, so `crow install` puts it beside
them.

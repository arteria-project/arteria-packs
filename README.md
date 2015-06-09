arteria-packs
-------------

NOTE: This is very much a work in progress, mostly containing dummy workflows so far.

StackStorm pack to setup automation workflow taking data from the sequencer to delivery on the remote host...

If you are using the `arteria-provisioning` this directory should be mounted under the `/opt/stackstorm/packs/arteria-packs` (make sure to set the path in the Vagrant file). To load all actions, rules, etc, run `st2 run packs.load register=all`.


arteria-packs
-------------

NOTE: This is very much a work in progress, mostly containing dummy workflows so far.

StackStorm pack to setup automation workflow taking data from the sequencer to delivery on the remote host...

If you are using the `arteria-provisioning` this directory should be mounted under the `/opt/stackstorm/packs/arteria-packs` (make sure to set the path in the Vagrant file). To load all actions, rules, etc, run `st2 run packs.load register=all`.

Registering the auth token in the key store
-------------------------------------------

Get your auth token setup (substitute for correct user and password as nessacary) :

    export ST2_AUTH_TOKEN=$(st2 auth --only-token testu -p testp)
    st2 key set st2_auth_token $ST2_AUTH_TOKEN

Right now this token needs to be setup in the keystore to allow workflows to trigger other workflows.


arteria-packs
-------------

NOTE: This is very much a work in progress, mostly containing dummy workflows so far.

StackStorm pack to setup automation workflow taking data from the sequencer to delivery on the remote host...

Development and testing
-----------------------
To make development and testing of arteria-packs simpler, we provide a Vagrant environment (this requires that VirtualBox is installed on your system).

```
# Get it up and running
vagrant up

# SSH into the vagrant environment
vagrant ssh

# Then go to the vagrant synced folder which contains this code
cd /vagrant

# Now you can start developing on the packs

# Note that all the scripts run below this point assume that your current
# working directory is the packs directory i.e. /arteria-packs in
# the vagrant environment

# Prepare the test environment environment (this only needs to be
# done when setting up for the first time), run this:
./utils/prepare_test_env.sh

# Note that this will checkout the st2 repo and create a virtual env called
# venv in the working directory

# Run the tests
./utils/run_tests.sh

# To test registering all pack components run
./utils/st2-check-register-pack-resources utils/st2.tests.conf
```

Getting an authentication token
-------------------------------

Get your auth token setup (substitute for correct user and password as necessary) :

    export ST2_AUTH_TOKEN=$(st2 auth --only-token testu -p testp)
    
Example of starting a workflow
------------------------------

Now you should be good to go. Here's an example of how to run a action:

     st2 run arteria-packs.ngi_uu_workflow runfolder=/data/testarteria1/150605_M00485_0183_000000000-ABGT6_testbio14 host=testarteria1
     
To see the result of a run - you can first list the executions:

    st2 execution list
    
Pick the one you're interested in and:

    st2 execution get --detail --json <your execution id>
    
Examples of using traces to track a runfolder
---------------------------------------------

Each execution will get it's own unique id when run by StackStorm. However it can be convenient to be able to tag executions
in other ways. Such as being able to see all executions for a particular runfolder for example. You can achieve this by
 using  the `--trace-tag` argument when staring a job, e.g:
 
    st2 run arteria-packs.ngi_uu_workflow \
        runfolder=/data/testarteria1/150605_M00485_0183_000000000-ABGT6_testbio14 \
        host=testarteria1 \
        --trace-tag 150605_M00485_0183_000000000-ABGT6_testbio14
    
Now you can search for the trace-tag using:

    st2 trace list --trace-tag 150605_M00485_0183_000000000-ABGT6_testbio14
    
To find more information about a particular trace, use:

    st2 trace get <trace id>
    
From there you can go to getting more information on the executions using:

    st2 execution get <execution id>
       
This will list all executions and triggers associated with the tag.

All of this has been wrapped by `scripts/trace_runfolder.py`, which allows you to get all excutions of a workflow
associated with a tag, e.g.:

    python scripts/trace_runfolder.py --tag 150605_M00485_0183_000000000-ABGT6_testbio14 | xargs -n1 st2 execution get
    
For automatic triggering the trace tag can be injected via the sensor. For more info on traces, see: http://docs.stackstorm.com/traces.html

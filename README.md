Arteria Pack
============

This is the new and improved version of the Arteria StackStorm pack.

The aim of this pack is to provide re-usable units for automating tasks at a
sequencing core facility. However, the type of things presented here can be of use to any
group which does enough sequencing that a high degree of automation is necessary.

This pack is intended as a starting point, not a turn-key solution. Most sequencing cores
will have a sufficiently unique environment that a specialized solution has to be developed,
however, the components provided here can make that work easier.

For more information on Arteria in general, look at our pre-print here:
https://www.biorxiv.org/content/early/2017/11/06/214858

tl;dr
=====
Just want to get going and already have Docker and Docker Compose installed?
Here is how you can get going:

```
git clone https://github.com/johandahlberg/arteria-incubation.git
cd arteria-incubation
make prepare
make up

# Place a runfolder in `/docker-mountpoints/monitored-folder`

docker exec stackstorm st2 run packs.setup_virtualenv packs=arteria
docker exec stackstorm st2 run arteria.workflow_bcl2fastq_and_checkqc \
  runfolder_path='/opt/monitored-folder/<name of the runfolder>' \
  bcl2fastq_body='{"additional_args": "--ignore-missing-bcls --ignore-missing-filter --ignore-missing-positions --tiles s_1", "use_base_mask": "--use-bases-mask y1n*,n*"}'
```

What does Arteria pack do?
==========================
Arteria is a pack for the [StackStorm](http://stackstorm.com/) event-driven automation platform. It provides re-usable components for StackStorm in the 
  form of actions, workflows, sensors, and rules. For more information about these concepts, see the [StackStorm docs](https://docs.stackstorm.com). 
A very quick summary of the different concepts:

- Actions encapsulate things that the system can do, e.g. calling a web-service or running a shell script
 - Workflows tie actions together
 - Sensors pick up events from the environment, e.g. looks for a file to appear on a file system, or polls a web-service for new information
 - Rules parse events from sensors and decide if an action or a workflow should be fired or not based on the information they recive 

The components provided by Arteria pack have two purposes:

- To be a point of collaboration for the Arteria community where StackStorm components which have a re-use potential can be 
deposited
- To provide a starting point for people interested in implementing an Arteria system to get started quickly.

To make it easier to get started, this repo therefore also contains the code and setup necessary to start a container based Arteria system, which 
in addition to running a StackStorm instance, also runs a set of Arteria micro-services, which make it possible to run bcl2fastq on an Illumina 
runfolder, and then check that is passes a set of quality criteria using [checkQC](https://github.com/Molmed/checkQC)

General outline of this repository 
==================================

```
.
├── actions = directory with all StackStorm actions
│   └── workflows = contains StackStorm workflows
├── aliases = contains StackStorm aliaes (used e.g. for ChatOps)
├── docker-conf = contains files specifying the environment for the different docker images in the system
├── docker-mountpoints
│   ├── bcl2fastq-output = when running the included sample workflow, bcl2fastq will place it's output here
│   └── monitored-folder = this is where you need to place any runfolder that you want the system to be able to access
├── docker-runtime = placing scripts here which will run when launching the containers, see: https://github.com/StackStorm/st2-docker#running-custom-shell-scripts-on-boot
│   ├── entrypoint.d
│   └── st2.d
├── docker-images = this is where all docker files used to create the Arteria containers will exist.
│   ├── bcl2fastq-service
│   ├── checkqc-service
│   └── runfolder-service
├── policies = place for StackStorm policies (can e.g. be used to limit concurrency of actions)
├── rules = place for StackStorm rules 
├── sensors = place for StackStorm sensors
└── tests = this directory contains all test code, both for action unit tests, but also integration testing code
```

Getting started / Installation
------------------------------
In order to have an development environment in which to get started quickly, we provide a
Docker based environment with the repository.

To get started with it follow the installation guides for you platform for [Docker](https://docs.docker.com/engine/installation/)
 and [Docker Compose](https://docs.docker.com/compose/install/).

Once you have that installed, ensure that you have Make installed (should be available from
your favorite package manager). Then you can get the system up and running by executing the
following set of commands:

```
git clone https://github.com/johandahlberg/arteria-incubation.git
cd arteria-incubation
make prepare
make up
```

Congratulations, you're now ready to get started trying out the Arteria pack.

To get into the StackStorm master node, run:

```
make interact
```

Running a workflow
------------------
Once you are inside the StackStorm container, it's time to install and configure the
Arteria pack. You only need to do this the first time you bring up the environment
(or if you re-build it later).

```
# Copy the default config into the StackStorm config directory
cp /opt/stackstorm/packs/arteria/default.config.yaml /opt/stackstorm/configs/arteria.yaml

# Register packs and configuration values
st2ctl reload --register-all

# Ensure that the Arteria virtual env is installed
st2 run packs.setup_virtualenv packs=arteria
```

Now the environment should be ready to run a workflow.

All you need to do is place a runfolder under `docker-mountpoints/monitored-directory`,
then give its path as a parameter when initiating the workflow:

```
st2 run arteria.workflow_bcl2fastq_and_checkqc runfolder_path="/opt/monitored-folder/<runfolder name>"
```

Eventually you should see something like this:

```
id: 5a2516ea10895200eb467b63
action.ref: arteria.workflow_bcl2fastq_and_checkqc
parameters:
  runfolder_path: /opt/monitored-folder/my_runfolder
status: succeeded (286s elapsed)
result_task: mark_as_done
result:
  exit_code: 0
  result: true
  stderr: ''
  stdout: ''
start_timestamp: 2017-12-04T09:35:38.361039Z
end_timestamp: 2017-12-04T09:40:24.743737Z
+--------------------------+--------------------------+--------------------+---------------------------+-------------------------------+
| id                       | status                   | task               | action                    | start_timestamp               |
+--------------------------+--------------------------+--------------------+---------------------------+-------------------------------+
| 5a2516eb10895200eb467b66 | succeeded (1s elapsed)   | get_runfolder_name | core.local                | Mon, 04 Dec 2017 09:35:38 UTC |
| 5a2516eb10895200eb467b68 | succeeded (1s elapsed)   | mark_as_started    | arteria.runfolder-service | Mon, 04 Dec 2017 09:35:39 UTC |
| 5a2516ed10895200eb467b6a | succeeded (1s elapsed)   | start_bcl2fastq    | arteria.bcl2fastq-service | Mon, 04 Dec 2017 09:35:41 UTC |
| 5a2516ef10895200eb467b6c | succeeded (267s elapsed) | poll_bcl2fastq     | arteria.bcl2fastq-service | Mon, 04 Dec 2017 09:35:42 UTC |
| 5a2517fd10895200eb467b6e | succeeded (1s elapsed)   | checkqc            | core.http                 | Mon, 04 Dec 2017 09:40:13 UTC |
| 5a2517fe10895200eb467b70 | succeeded (1s elapsed)   | mark_as_done       | arteria.runfolder-service | Mon, 04 Dec 2017 09:40:14 UTC |
+--------------------------+--------------------------+--------------------+---------------------------+-------------------------------+
```

Indicating that you have successfully executed a workflow which has demultiplexed the runfolder
 using bcl2fastq and and checked its quality control statistics using [CheckQC](https://github.com/Molmed/checkQC).

Starting a workflow through a sensor
------------------------------------
The way that Stackstorm will detect changes in the surrounding environment is through sensors.
In this pack there is a sensor called the `RunfolderSensor`, which will query the the runfolder
service for information about the state of runfolders.

To activate the rule, i.e. the part that glues the sensor and a workflow/action together,
run:

```
st2 rule enable arteria.when_runfolder_is_ready_start_bcl2fastq
```

Then to start processing the runfolder, set its state to `ready` using:

```
st2 run arteria.runfolder_service cmd="set_state" state="ready" runfolder="/opt/monitored-folder/<name of your runfolder>" url="http://runfolder-service"
```

Within 15s you should if you execute `st2 execution list` see that a workflow processing that runfolder
has started. This is the way that Arteria can be used to automatically start processes as needed.

Running tests
-------------

To run the pack tests, run the following command in the StackStorm container:

```
st2-run-pack-tests -c -v -p /opt/stackstorm/packs/arteria
```

Acknowledgements
================
The docker environment provided here has been heavily inspired by the ones provided by
[StackStorm](https://github.com/StackStorm/st2-docker) and [UMCCR](https://github.com/umccr/st2-arteria-docker).


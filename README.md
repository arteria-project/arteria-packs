Arteria Stackstorm Pack
=======================

[![Build Status](https://travis-ci.org/arteria-project/arteria-packs.svg?branch=master)](https://travis-ci.org/arteria-project/arteria-packs)
[![Join the chat at https://gitter.im/arteria-project/arteria-project](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/arteria-project/arteria-project)

This pack provides re-usable units for automating tasks at a
sequencing core facility using the [StackStorm](http://stackstorm.com/)
event-driven automation platform.

It forms the core of the Arteria automation system,
which you can read about on our [website](https://arteria-project.github.io/)
or [preprint](https://www.biorxiv.org/content/early/2017/11/06/214858).
This pack integrates with a series of bioinformatic micro-services,
which can be found at https://github.com/arteria-project.

This repository includes a Docker environment allowing you to install
Arteria and its dependencies within a containerized environment.

This pack is intended as a starting point, not a turn-key solution. Most sequencing cores
will have a sufficiently unique environment that a specialized solution must be developed,
but our goal is to provide components to facilitate this development.

Mission
=======
The components provided by Arteria pack have a two-fold purpose:

- To be a point of collaboration for the Arteria community where potentially reusable StackStorm components can be deposited
- To provide a quick-start launchpad for organizations interested in implementing an Arteria system

Demo
=====

Here we demonstrate using Docker to bootstrap an Arteria system
comprised of arteria-packs and several Arteria microservices.
We then use the system to run a simple workflow on a runfolder.

[![asciicast](https://asciinema.org/a/YSz20Jfo7U1hCYzWP5K05mT1S.png)](https://asciinema.org/a/YSz20Jfo7U1hCYzWP5K05mT1S)


Getting Started
===============

System requirements
-------------------
You will need to have the following installed:
- [docker](https://docs.docker.com/)
- [docker-compose](https://docs.docker.com/compose/)
- make

bcl2fastq
---------
You also need to download Illumina software bcl2fastq manually since Illumina requires that you register before donwloading.
- Download the [zip file](https://support.illumina.com/softwaredownload.html?assetId=e8ed3335-5201-48ff-a2bc-db4bfb792c85&assetDetails=bcl2fastq2-v2-20-0-linux-x86-64.zip) containing the rpm. Save in at docker-images/bcl2fastq-service/local_files

Installation
------------
```
git clone https://github.com/arteria-project/arteria-packs
cd arteria-packs
make up
```

To register the Arteria pack with Stackstorm, run:
```
docker exec stackstorm st2ctl reload --register-all
docker exec stackstorm st2 run packs.setup_virtualenv packs=arteria
```

Congratulations, you're now ready to run workflows.


Running the sample workflow
---------------------------

Put a runfolder in the `docker-mountpoints/monitored-folder` directory.

You can find a suitably small test data set here: https://doi.org/10.5281/zenodo.1204292

Then run:

```
docker exec stackstorm st2 run arteria.workflow_bcl2fastq_and_checkqc \
  runfolder_path='/opt/monitored-folder/<name of the runfolder>' \
  bcl2fastq_body='{"additional_args": "--ignore-missing-bcls --ignore-missing-filter --ignore-missing-positions --tiles s_1", "use_base_mask": "--use-bases-mask y1n*,n*"}'
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

You can find bcl2fastq output in `docker-mountpoints/bcl2fastq-output`.

Architecture
============

This project provides re-usable components for StackStorm in the
form of actions, workflows, sensors, and rules.

The [StackStorm docs](https://docs.stackstorm.com) are a
comprehensive guide to these concept, but here we provide a summary:

- **Actions** encapsulate system tasks such as calling a web service or running a shell script
- **Workflows** tie actions together
- **Sensors** pick up events from the environment, e.g. listening for new files to appear in a directory, or polling a web service for new events
- **Rules** parse events from sensors and determine if an action or a workflow should be initiated

In order to facilitate quick setup, this repo also provides a Docker environment.
In addition to running a StackStorm instance, it also runs a set of Arteria micro-services,
which make it possible to run bcl2fastq on an Illumina runfolder,
and then check that is passes a set of quality criteria using [checkQC](https://github.com/Molmed/checkQC)

The code is structured as follows:

```
.
├── actions = StackStorm actions
│   └── workflows = StackStorm workflows
├── docker-conf = config files for the docker images
├── docker-images = Dockerfiles for Arteria containers
│   ├── bcl2fastq-service
│   ├── checkqc-service
│   └── runfolder-service
├── docker-mountpoints = directories mounted to Docker containers
│   ├── bcl2fastq-output = will contain bcl2fastq output from the sample workflow
│   └── monitored-folder = deposit your runfolders here for processing
├── docker-runtime = startup container scripts, see: https://github.com/StackStorm/st2-docker#running-custom-shell-scripts-on-boot
├── rules = StackStorm rules
├── sensors = StackStorm sensors
└── tests = unit and integration tests
```

Advanced Usage
==============

Container access
----------------

To get into the StackStorm master node, run:

```
make interact
```

From there you can issue st2 commands directly, without the ```docker exec stackstorm``` prefix.

Running as sudo
---------------
If you are running make and docker with `sudo` you need to do so with the `-E` flag to
ensure that the environment variables get passed correctly. For example:

```
sudo -E make up
```

Troubleshooting
---------------

You may encounter failures during one or more steps in the workflow:

```
+--------------------------+------------------------+--------------------+--------------------------+--------------------------+
| id                       | status                 | task               | action                   | start_timestamp          |
+--------------------------+------------------------+--------------------+--------------------------+--------------------------+
| 5c78e3ba8123e6012739119c | succeeded (0s elapsed) | get_runfolder_name | core.local               | Fri, 01 Mar 2019         |
|                          |                        |                    |                          | 07:48:10 UTC             |
| 5c78e3ba8123e6012739119e | succeeded (1s elapsed) | mark_as_started    | arteria.runfolder_servic | Fri, 01 Mar 2019         |
|                          |                        |                    | e                        | 07:48:10 UTC             |
| 5c78e3bb8123e601273911a0 | failed (0s elapsed)    | start_bcl2fastq    | arteria.bcl2fastq_servic | Fri, 01 Mar 2019         |
|                          |                        |                    | e                        | 07:48:11 UTC             |
+--------------------------+------------------------+--------------------+--------------------------+--------------------------+
```

You can troubleshoot the failed step further by getting the execution id, in this case:

```
docker exec arteria-packs_st2client_1 st2 execution get 5c78e3bb8123e601273911a0
```

Activating sensors
------------------
Stackstorm can detect changes in the surrounding environment through sensors.
This pack provides a `RunfolderSensor`, which queries the the runfolder
service for state information.

By activating this sensor, we can automatically trigger
a workflow once a runfolder is marked "ready" in the runfolder service.

You can confirm that the sensor is activated by running:

```
st2 sensor list
```

To connect the sensor and workflow, activate the rule:

```
docker exec stackstorm st2 rule enable arteria.when_runfolder_is_ready_start_bcl2fastq
```

Put a runfolder in `docker-mountpoints/monitored-folder`, and
set its state to `ready` using:

```
docker exec stackstorm st2 run arteria.runfolder_service cmd="set_state" state="ready" runfolder="/opt/monitored-folder/<name of your runfolder>" url="http://runfolder-service"
```

Within 15s you should if you execute `docker exec stackstorm st2 execution list` see that a workflow processing that runfolder
has started. This is the way that Arteria can be used to automatically start processes as needed.

You can see details of the sensor's inner workings with:

```
docker exec stackstorm /opt/stackstorm/st2/bin/st2sensorcontainer --config-file=/etc/st2/st2.conf --debug --sensor-ref=arteria.RunfolderSensor
```

Re-building the environment
---------------------------

You can remove the existing environment with:

```
make remove-all
```

Then, re-run the Installation instructions.

Running tests
-------------

```
docker exec stackstorm st2-run-pack-tests -c -v -p /opt/stackstorm/packs/arteria
```

Acknowledgements
================
The docker environment provided here has been heavily inspired by the ones provided by
[StackStorm](https://github.com/StackStorm/st2-docker) and [UMCCR](https://github.com/umccr/st2-arteria-docker).

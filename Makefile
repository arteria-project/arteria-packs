# This file has been modified from the https://github.com/StackStorm/st2-docker repo
# It is therefore subject to Apache Licence 2.0.
# It has been modified to work with the specific Arteria services and workflow.

# If ARTERIA_MONITORED_FOLDER is not defined in the environment set it to the
# default of using a monitored folder in the arteria repo
export ARTERIA_MONITORED_FOLDER ?= ${PWD}/docker-mountpoints/monitored-folder/
export ST2_VERSION=3.7

prepare:
	mkdir -p -m 2770 docker-mountpoints/bcl2fastq-output
	mkdir -p -m 2770 docker-mountpoints/monitored-folder
	mkdir -p -m 2770 docker-runtime/entrypoint.d
	mkdir -p -m 2770 docker-runtime/st2.d
	docker volume create --opt "device=${ARTERIA_MONITORED_FOLDER}" --opt "type=local" --opt "o=bind" monitored-dir-volume

up: prepare
	docker-compose up -d
	sleep 20

down:
	docker-compose down

interact: up
	docker exec -it stackstorm /bin/bash

test-pack: up
	docker exec arteria-packs_st2actionrunner_1 st2-run-pack-tests -c -v -p /opt/stackstorm/packs/arteria

test-integration: up
	docker exec arteria-packs_st2actionrunner_1 /opt/stackstorm/packs/arteria/tests/integration_tests_setup
	docker exec arteria-packs_st2client_1 /opt/stackstorm/packs/arteria/tests/integration_tests_run

exec:
	docker exec -it stackstorm $(cmd)

remove-all: down
	docker rmi $$(docker images -a -q)

remove-st2: down
	docker images -a  | grep stackstorm | awk '{print($$1)}' | xargs docker rmi

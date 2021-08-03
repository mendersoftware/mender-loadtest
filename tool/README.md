# Load testing scripts

This directory contains Python scripts to run the Mender Load Testing.

The goal of these scripts is to run a load test (also known as stress or scale
test) against a working Mender installation.

## Init the Python virtual environment

To run them, you need to install a list of required Python packages,
preferably in a virtualenv:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

## Export the environment variables

Export the Shell environment variables read by the scripts:

```bash
$ export USERNAME=...
$ export PASSWORD=...
$ export URL=https://testing.hosted.mender.io
```

It is your responsibility to install and operate the Mender environment
publishing it under the URL specified above. Similarly, it is your
responsibility to create the user and password pair needed by the different
scripts to call the API end-points.

## Interactive utility

This utility allows you to interact with different APIs of the Mender server

```bash
$ python testenv_control.py
```

Currently it supports:

* List, create predefined, and delete filters (dynamic groups)
* List, create and abort deployments

## Unattended scripts

### Get the number of devices

You can obtain the number of pending or accepted devices running:

```bash
$ python3 get_number_of_devices.py pending
1000
$ python3 get_number_of_devices.py accepted
0
```

### Accept the pending devices

You can accept all the pending devices:

```bash
$ python3 accept_all_devices.py
```

### Static groups

You can create static groups with a given number of devices:

```bash
$ python3 create_group_of_devices.py --devices-qty 100 --group group1
```

### Deploy an artifact to the whole fleet

You can deploy an artifact to the whole fleet running:

```bash
$ ARTIFACT_NAME=artifact-1 python3 do_deployment_to_all_devices.py
```

The artifact referenced by the `ARTIFACT_NAME` environment variable must
already exist in Mender and be compatible with the target devices.

### Deploy an artifact to a group of devices

You can deploy an artifact to a group of devices running:

```bash
$ ARTIFACT_NAME=artifact-1 GROUP_NAME=name-of-group python3 do_deployment_to_group.py
```

The artifact referenced by the `ARTIFACT_NAME` environment variable must
already exist in Mender and be compatible with the target devices. The
group referenced by `GROUP_NAME` can be static or dynamic, but must already
exist in Mender.

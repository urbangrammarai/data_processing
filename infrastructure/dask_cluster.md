# Set up ad-hoc Dask cluster

This guide documents how to set up an ad-hoc cluster of machines that can run [Dask](https://dask.org/) processes. 

## Requirements

For this guide, we will assume you have access to the following:

- At least two machines connected to a network that allows them to talk to each other over ssh
- Ability to run on each machine [`gds_env`](https://github.com/darribas/gds_env) containers (for this example, we will use `gds_dev` but the same should work with `gds_py` and `gds`)

## Intuition

Dask has several ways of setting up a cluster, including over ssh or with orchestration tools such as Kubernetes. For a more thorough coverage, please visit the [official docs](https://docs.dask.org/en/latest/setup.html). In this guide, we will connect a few machines that can talk to each other over ssh. This is handy, for example, if you have a few computers running on the same local network.

The structure a Dask cluster relies on a single "entry point", the *"scheduler"*, that recruits resources from a series of additional machines, the *"workers"* (including itself potentially).

The sequence of actions will be as follows:

1. Start the scheduler
1. Start workers on different machines, attaching them to the scheduler
1. Use the cluster on a Python session with a Dask `Client`

## Scheduler

We will run the scheduler inside a Jupyter Lab session that will then [use the cluster](#Use-the-cluster), although this need not be the case. For illustration, we will refer to the IP on which this machine can be reached at with `<scheduler-ip>`.

1. Fire up a terminal and type:

```shell
docker run --rm -ti -p 8888:8888 -p 8787:8787 -p 8786:8786 darribas/gds_dev:latest start.sh
```

This will spin up a `gds_dev` container with a JupyterLab instance, opening ports 8888 (JupyterLab), 8787 (Dask dashboard) and 8786 (scheduler).

2. Inside JupyterLab, open a terminal window and launch the scheduler with:

```shell
dask-scheduler
```

## Workers

Now go to each of the machines in the network you want to recruit as workers. Open a terminal and run:

```shell
docker run --network="host"  --rm -ti -p 8786:8786 darribas/gds_dev:latest start.sh dask-worker <scheduler-ip>:8786
```

This will launch a container that starts a worker process and attaches to the scheduler (through the `<scheduler-ip>` link). 

It's important to include the `--network="host"` parameter so that the worker container can be reached from outside the machine through ssh.

## Use the cluster

Once the cluster is available, we can use it on a Python session. 

1. Open a notebook or Python console in the same JupyterLab instance as the scheduler
2. Import Dask's `Client`

```python
from dask.distributed import Client
```

3. Set up a client for the session

```python
client = Client("tcp://172.17.0.2:8786")
```

Replace `tcp://172.17.0.2:8786` by the URL where the scheduler is running at (you can see this on the scheduler log feed).

4. You can check the status of the cluster at `<scheduler-ip>:8787`

---

Now the cluster is set up and linked to the session, when you run a Dask operation, its computation will be distributed across the cluster.
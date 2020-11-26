# Manage Kubernetes cluster

## Cluster setup

This guide documents the process of setting up a Kubernetes cluster between an arbitrary number of machines to run Dask loads in a distributed way.

Here is our preliminary set up:

- All machines are connected to the same network and hence "available to each other"
- Each machine is running Ubuntu and we have admin rights on them all

This guide will use the following jargon:

- `cluster`: a Kubernetes deployment that connects different machines and allows to run distributed jobs through containers
- `node`: each of the physical machines that are part of the cluster
- `scheduler`: the JupyterLab session that controls the cluster, creates and distributes jobs across the cluster
- `pod`: a single containerised task distributed from the Dask scheduler

### Install Kubernetes (via `microk8s`)

To simplify the set up of Kubernetes, we rely on [`microk8s`](https://microk8s.io), by Canonical. This is a pre-packaged version of Kubernetes set up with "sensible defaults" so deployment is simplified. Installation happens through `snap`.

On each machine that will be part of the cluster, run:

```
sudo snap install microk8s --classic --channel=1.19
```

This will create a `microk8s` Kubernetes instance on each machine. You can check the machine is properly setup with:

```
sudo microk8s status --wait-ready
```

For the overall status of the single machine cluster. Or:

```
sudo microk8s kubectl get nodes
```

To confirm the cluster has a single node.

### Link up machines to the cluster

So far we have independent, one-machine clusters running, now we will link them up into a single cluster that can "orchestrate" tasks across machines.

Pick one machine to act as the main "entry point". It is not very important which one you pick as, as soon as you have more than two, the cluster will automatically become "high availability", meaning each node can act as the entry point. But, to get there, pick one. We will call this node the *entry point*, and the other ones the *followers*.

On the entry point, run:

```
sudo microk8s add-node
```

This will print a command starting by `microk8s join ...` that you can copy on a given follower, preceded by `sudo`. Once both machines shake hands and complete the process, you can check your cluster entry point has two nodes:

```
sudo microk8s kubectl get nodes
```

Repeat this process for as many nodes as you want to join to the cluster.

### Remove machines from the cluster

Once a node is joined to the cluster, the add computing resources to the pool that Kubernetes manages. Kubernetes is also very good at letting you dynamically adjust a cluster, adding more resources as you acquire them (e.g. get a new machine), and dropping them as you need them somewhere else. 

Removing a node from the cluster is a two-stage process:

1. First, remove the node. For that, from the node you want to remove:

```
sudo microk8s leave
```
1.  Once that process has completed, update the cluster information. From the entry point (or any node on a high availability cluster):

```
sudo microk8s remove-node <node-id>
```

where `<node-id>` is the name you'd find for the node if you run `sudo microk8s kubectl get nodes` when the node is part of the cluster.

## Connecting to a cluster via Dask

To use Kubernetes cluster as a Dask cluster, you need to connect to it using `config` file and specify how each worker should look like. 

Note that you should ideally run the same docker container as a scheduler and pods (workers).

### Kubernetes config

To connect to Kubernetes cluster, you need its configuration saved in `/home/jovyan/.kube/config` file. You can generate config using 

```shell
microk8s config > config
```

It is likely that this will be generated outside of the container on the host machine, so make sure it is available from the container. Once your Jupyter instance is up and running, you create `.kube` folder and copy the file there.

```shell
mkdir /home/jovyan/.kube
cp config /home/jovyan/.kube/config
```

That way Kubernetes knows to which cluster it should connect and how.

### dask.Client on Kubernetes cluster

To connect Dask to Kuberenetes cluster, you need `dask-kubernetes` installed in the docker container. Then you can use `KubeCluster` within Dask `Client`.

```python
from dask_kubernetes import KubeCluster
from dask.distributed import Client
```

Kubernetes requires specification of pods, i.e. which docker image it should use, CPU and memory limits and other information. That should be stored in`.yml`, which you load during the creation of `KubeCluster`. See below the example specification.

```python
cluster = KubeCluster.from_yaml('worker-spec.yml')
```

Once we have `KubeCluster` set up, we can hook it into dask client.

```python
client = Client(cluster)
```

### Scaling

By default the cluster will not give you any worker, so you have to specify them. You can either do that manually and specify the number of workers or set up adaptive scaling. 

Using `cluster.scale(20)`, Kubernetes will try to start 20 pods (workers) for you. However, if your nodes are not able to accomodate all of them due to memory and CPU limitations, you may get less than that.  

Using `cluster.adapt(minimum=1, maximum=100)` Kubernetes will try to adapt number of pods based on the actual workload.

Once you are finished, use `cluster.close()` to shut down all pods (that will also happen automatically if you shut down Jupyter kernel).

### Example worker specification

This is the example of `worker-spec.yml` which will start each pod using `darribas/gds_py:6.0alpha1` docker container and limits each of them to two CPUs and 8GB of RAM.


```yaml
kind: Pod
metadata:
  labels:
    foo: bar
spec:
  restartPolicy: Never
  containers:
  - image: darribas/gds_py:6.0alpha1
    imagePullPolicy: IfNotPresent
    args: [start.sh, dask-worker, --nthreads, '2', --no-dashboard, --memory-limit, 6GB, --death-timeout, '60']
    name: dask
    resources:
      limits:
        cpu: "2"
        memory: 8G
      requests:
        cpu: "2"
        memory: 8G
```

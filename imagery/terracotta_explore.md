# Explore Imagery with `terracotta`

For quick exploration of imagery in the browser, we can use
[`terracotta`](https://terracotta-python.readthedocs.io/en/latest/index.html).
This document captures how to serve a folder of images and explore it
interactively.

## Build `terracotta`

A containerised version of `terracotta` can be built using the
[`Dockerfile`](Dockerfile.terracotta):

```shell
docker built -t terracotta -f ./Dockerfile.terracotta .
```

This is a relatively lightweight image based off the [Alpine version of
miniconda3](https://hub.docker.com/r/continuumio/miniconda3/tags) (v.`4.8.2-alpine`).

## Serving

The approach follows a client/server model so, first, we need to spin up a
server that makes the imagery available. For that, we first launch the server
container:

```shell
docker run --rm \
           -ti \
           -p 5000:5000 \
           -v /media/dani/DataStore/GHS-composite-S2/:/data \
           terracotta sh
```

This needs to be run off the same machine where the imagery is stored.

Once inside the container, launch the server with:

```shell
/opt/conda/bin/terracotta serve \
                          --allow-all-ips \
                          -r /path/to/data/folder/S2_percentile_UTM_{tile}-{scene1}-{scene2}_osgb.tif
```

This should open a Flask server that will listen to port 5000 for requests.

## Exploring

Once the imagery is being served, we can launch a web app through a separate
(local or remote) container:

```shell
docker run --rm \
           -ti \
           -p 5005:5005 \
           -v /path/to/data/folder/:/data \
           --network host 
           terracotta sh
```

Note that although the command is similar to that we use for the server, here
we set `--network host` so the client can be reached from the guest's browser.

## Optimising

The above process "works", but if the imagery is too heavy, it'll choke and
will struggle to be responsive enough for exploration. If that is the case,
consider pre-optimising the images. Following the [`terracotta` tutorial](https://terracotta-python.readthedocs.io/en/latest/get-started.html), we can generate optimised versions by:

```shell
/opt/conda/bin/terracotta optimize-rasters -o /target/folder \
                                           --reproject \
                                           /path/to/data/*.tif
```

Once this finishes, you can serve as [above](#Serving), with the modification
of the data path.

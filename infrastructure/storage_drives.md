# Mount samba drives on linux from the command line

This document covers how to (un)mount and access data on a samba drive from Ubuntu, using the command line and have it
accessible for read/write access within docker jupyter lab instance.

## Using `cifs`

### Requirements

For this route, you will need:

- The `cifs` tools. If you do not have them, you can install them:

```shell
sudo apt-get install cifs-utils
```

- The address of the samba server you'd like to mount. For this example we will use `<server-url>` for the address, `<drive>` for the folder you want to mount and `<username>` 
- sudo rights

### Mount the drive

First create an empty folder where you will mount the drive:

```shell
mkdir <mount-point>
```

To mount the drive, you can:

```shell
sudo mount -t cifs <server-url>/<drive> <mount-point> -o domain=<domain>,sec=ntlm,vers=1.0,username=<samba_username>,password=<samba_password>
```

Note that `sec=ntlm,vers=1.0` may not be needed for your server or it may use different settings.

The drive is now mounted under the `<mount-point>` path and you can read from there. To have it accessible within docker,
the `<mount-point>` should be within your current working dierectory which you pass as a volume to a container:

```shell
docker run --rm -ti --user root -e GRANT_SUDO=yes -e NB_UID=$UID -e NB_GID=100 -p 8888:8888 -v ${PWD}:/home/jovyan/work darribas/gds_dev:5.0 start.sh
```

Container will open shell, from which you have to start Jupyter lab with sudo access:

```shell
sudo jupyter lab --allow-root
```


### Unmount the drive

Simply run:

```shell
sudo umount <mount-point>
```

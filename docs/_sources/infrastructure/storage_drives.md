# Mount samba drives on linux from the command line

This document covers how to (un)mount and access data on a samba drive from Ubuntu, using the command line.

## Using `cifs`

### Requirements

For this route, you will need:

- The `cifs` tools
- The address of the samba server you'd like to mount. For this example we will use `<server-url>` for the address, `<drive>` for the folder you want to mount and `<username>` 

### Mount the drive

First create an empty folder where you will mount the drive:

```shell
mkdir <mount-point>
```

To mount the drive, you can:

```shell
sudo mount -t cifs -o user=<username>,domain=<domain> <server-url>/<drive> <mount-point>
```

The drive is mounted now under the `<mount-point>` path and you can read from there, as well as pass it as a volume to a container:

```shell
docker run --rm -ti -v <mount-point>:/home/jovyan/data darribas/gds:5.0
```

### Unmount the drive

Simply run:

```shell
sudo umount <mount-point>
```

### To do

Currently, because the mount relies on `sudo`, the user cannot write to the drive. It'd be nice to allow write capabilities as well.

## Using `gvfs` (deprecated)

### Requirements

You will need to have the following:

- The `gio`/`gvfs` tools
- The address of the samba server you'd like to mount. For this example we will use `<server-url>` for the address, `<drive>` for the folder you want to mount and `<username>` 

### Mount the drive

To mount a samba drive,  you can run:

```shell
gio mount smb://<username>@<server-url>/<drive>
```

This will ask for your password and, once entered, will mount the drive.

To check the drive is effectively mounted, you can run:

```shell
gio mount -l
```

and that should display at least the drive you just mounted.

To get more info on the mount, you can do:

```shell
gio info smb://<username>@<server-url>/<drive>
```

### Access the drive

The command above will mount the drive at the mount point:

```shell
/run/user/$UID/gvfs/
```

You can run `ls` on the folder above to see under what mount point it's been attached.

### Unmount the drive

To unmount the drive:

```shell
gio mount -u smb://<username>@<server-url>/<drive>
```


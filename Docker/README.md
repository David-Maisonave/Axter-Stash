# Create Docker Stash Container (By David Maisonave)

CreateContainer.cmd is a Windows script that is used to create a Stash container on Docker.

To use it, first copy the file to the following path:
`C:\Users\MyUserName\AppData\Local\Docker\wsl\CreateContainer.cmd`

Note: Replace **MyUserName** with the actual user name.

Then use a DOS window to change to the **ws1** directory before calling the script.
### The script requires at minumum 3 arguments.
- New Container Name
- Image Name
- Stash Port Number

### Example Commands:
- Example usage with minumum arguments:
  - `CreateContainer.cmd MyContainerName "stashapp/stash:latest" 9998`
- Example with shared mount paths: 
  - `CreateContainer.cmd ContainerName1 "stashapp/stash:latest" 9991 C:\MySharedMountPath C:\Another\Shared\Folder`
- Example with shared mount paths with write access: 
  - `CreateContainer.cmd ContainerName1 "stashapp/stash:latest" 9991 C:\MyShared  WRITE`
- Example adding Stash **Image** and container:
  - `CreateContainer.cmd v0.27.2 "stashapp/stash:v0.27.2" 9997 PULL`
- Example with DLNA:
  - `CreateContainer.cmd v272 "stashapp/stash:v0.27.2" 9996 C:\downloads DLNA`
- Example skipping docker-compose:
  - `CreateContainer.cmd ContainerName "stashapp/stash:v0.26.2" 9992 C:\Videos SKIP`

### Shared Mount Paths
- CreateContainer.cmd can create 1-5 shared mount paths on the container. A shared mount path is a path that is a HOST path that is mounted on the container, which allows the container to access files.
- By default the shared mount is READ-ONLY, but by appending **WRITE** to the command line, the script will make all the shared mounts with read-write access.
  - Example:  `CreateContainer.cmd ContainerName1 "stashapp/stash:latest" 9999 C:\MySharedMountPath WRITE`

### DLNA Functionality
- The script can create a Stash container with DLNA Functionality. To add DLNA Functionality, append **DLNA** to the command line.
  - Example:`CreateContainer.cmd v272 "stashapp/stash:v0.27.2" 9996 DLNA`

### Skip docker-compose
- By default, `docker-compose up -d` is called after the script creates the **docker-compose.yml** file. To skip this call, append SKIP to the command line.
  - Example:  `CreateContainer.cmd ContainerName "stashapp/stash:v0.26.2" 9992 SKIP`
- When SKIP is used, the script only creates the container directory and creates the **docker-compose.yml** file in the newly created directory.
- This option is mainly used for debugging purposes.

### Downloads
- Docker
  - Use the following link to download Docker
  - [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
- Stash Image
  - The CreateContainer.cmd script can download the Image before creating the container by adding **PULL** at the end of the command line.
  - Example: `CreateContainer.cmd ver0272 "stashapp/stash:v0.27.2" 9999 PULL`
  - To see what Stash images are available, see the following link: [https://hub.docker.com/r/stashapp/stash/tags](https://hub.docker.com/r/stashapp/stash/tags).

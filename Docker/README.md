# Create Docker Stash Container (By David Maisonave)

CreateContainer.cmd is a Windows script that is used to create a Stash container on Docker.

To use it, first copy the file to the following path:
**C:\Users\MyUserName\AppData\Local\Docker\wsl\CreateContainer.cmd**

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
- Example adding Stash **Image** and container:
  - `CreateContainer.cmd v0.27.2 "stashapp/stash:v0.27.2" 9997 PULL`
- Example with DLNA:
  - `CreateContainer.cmd v272 "stashapp/stash:v0.27.2" 9996 C:\downloads DLNA`
- Example skipping docker-compose:
  - `CreateContainer.cmd ContainerName "stashapp/stash:v0.26.2" 9992 C:\Videos SKIP`

### Downloads
- Docker
  - Use the following link to download Docker
  - (https://www.docker.com/products/docker-desktop/)[https://www.docker.com/products/docker-desktop/]
- Stash Image
  - The CreateContainer.cmd script can download the Image before creating the container by adding **PULL** at the end of the command line.
  - Example: `CreateContainer.cmd ver0272 "stashapp/stash:v0.27.2" 9999 PULL`

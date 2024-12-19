@ECHO OFF
:: This file is to create Stash Docker containers, and should be copied and called from the following path:
:: C:\Users\MyUserName\AppData\Local\Docker\wsl\CreateContainer.cmd
:: Example usage: 
::				CreateContainer.cmd MyContainerName "stashapp/stash:latest" 9998
:: Example with shared mount paths: 
::				CreateContainer.cmd ContainerName1 "stashapp/stash:latest" 9991 C:\MySharedMountPath C:\Another\Shared\Folder
:: Example adding Stash IMAGE and container:
::				CreateContainer.cmd v0.27.2 "stashapp/stash:v0.27.2" 9997 PULL
:: Example with DLNA:
::				CreateContainer.cmd v272 "stashapp/stash:v0.27.2" 9996 C:\downloads DLNA
:: Example skipping docker-compose:
::					CreateContainer.cmd ContainerName "stashapp/stash:v0.26.2" 9992 C:\Videos SKIP
set NewContainerName=%1
:: Example image arguments:stashapp/stash:latest, stashapp/stash:v0.27.2, stashapp/stash:v0.26.2
set Image=%2
:: Example Port Numbers: 9999, 9990, 9991, 9995, 9998
set STASH_PORT=%3
:: The SharedMountPath's variables are optional arguments, and can be empty.
:: Use SharedMountPath's to specify shared paths that are mounted as READ-ONLY.
:: Example SharedMountPath: C:\Videos, E:\MyMedia, Z:\MyVideoCollections, C:\Users\MyUserName\Videos, C:\Users\MyUserName\download
set SharedMountPath=%4
set SharedMountPath2=%5
set SharedMountPath3=%6
set SharedMountPath4=%7
set SharedMountPath5=%8
set VariableArg=%9
set SkipDockerCompose=
set DLNAFunctionality="no"
set PullDockerStashImage=
set MountAccess=":ro"
if [%SharedMountPath%]==[DLNA] 		(set DLNAFunctionality=yes) & (set SharedMountPath=)
if [%SharedMountPath%]==[SKIP] 		(set SkipDockerCompose=yes) & (set SharedMountPath=)
if [%SharedMountPath%]==[PULL] 		(set PullDockerStashImage=yes) & (set SharedMountPath=)
if [%SharedMountPath2%]==[DLNA] 	(set DLNAFunctionality=yes) & (set SharedMountPath2=)
if [%SharedMountPath2%]==[SKIP] 	(set SkipDockerCompose=yes) & (set SharedMountPath2=)
if [%SharedMountPath2%]==[PULL] 	(set PullDockerStashImage=yes) & (set SharedMountPath2=)
if [%SharedMountPath2%]==[WRITE]	(set MountAccess=) & (set SharedMountPath2=)
if [%SharedMountPath3%]==[DLNA] 	(set DLNAFunctionality=yes) & (set SharedMountPath3=)
if [%SharedMountPath3%]==[SKIP] 	(set SkipDockerCompose=yes) & (set SharedMountPath3=)
if [%SharedMountPath3%]==[PULL] 	(set PullDockerStashImage=yes) & (set SharedMountPath3=)
if [%SharedMountPath3%]==[WRITE]	(set MountAccess=) & (set SharedMountPath3=)
if [%SharedMountPath4%]==[DLNA] 	(set DLNAFunctionality=yes) & (set SharedMountPath4=)
if [%SharedMountPath4%]==[SKIP] 	(set SkipDockerCompose=yes) & (set SharedMountPath4=)
if [%SharedMountPath4%]==[PULL] 	(set PullDockerStashImage=yes) & (set SharedMountPath4=)
if [%SharedMountPath4%]==[WRITE]	(set MountAccess=) & (set SharedMountPath4=)
if [%SharedMountPath5%]==[DLNA] 	(set DLNAFunctionality=yes) & (set SharedMountPath5=)
if [%SharedMountPath5%]==[SKIP] 	(set SkipDockerCompose=yes) & (set SharedMountPath5=)
if [%SharedMountPath5%]==[PULL] 	(set PullDockerStashImage=yes) & (set SharedMountPath5=)
if [%SharedMountPath5%]==[WRITE]	(set MountAccess=) & (set SharedMountPath5=)
if [%VariableArg%]==[DLNA] 			(set DLNAFunctionality=yes)
if [%VariableArg%]==[SKIP] 			(set SkipDockerCompose=yes)
if [%VariableArg%]==[PULL] 			(set PullDockerStashImage=yes)
if [%VariableArg%]==[WRITE] 		(set MountAccess=)
echo SkipDockerCompose = %SkipDockerCompose% ; DLNAFunctionality = %DLNAFunctionality%
set DockerComposeFile="docker-compose.yml"

if [%NewContainerName%]==[] goto :MissingArgumentNewContainerName
goto :HaveVariableNewContainerName
:MissingArgumentNewContainerName
set /p NewContainerName="Enter the new container name: "
:HaveVariableNewContainerName

if [%Image%]==[] goto :MissingArgumentImage
goto :HaveVariableImage
:MissingArgumentImage
set /p Image="Enter the image name: "
:HaveVariableImage

if [%STASH_PORT%]==[] goto :MissingArgumentSTASH_PORT
goto :HaveVariableSTASH_PORT
:MissingArgumentSTASH_PORT
set /p STASH_PORT="Enter the Stash port number: "
:HaveVariableSTASH_PORT

if exist %NewContainerName%\ (
  echo %NewContainerName% already exists. 
) else (
  echo creating folder %NewContainerName%
  mkdir %NewContainerName%
)
cd %NewContainerName%
echo DockerComposeFile=%DockerComposeFile%; NewContainerName=%NewContainerName%; Image=%Image%; STASH_PORT=%STASH_PORT%; DLNAFunctionality=%DLNAFunctionality%; SharedMountPath=%SharedMountPath%; SharedMountPath1=%SharedMountPath1%; SharedMountPath2=%SharedMountPath2%
echo services:> %DockerComposeFile%
echo   stash:>> %DockerComposeFile%
echo     image: %Image%>> %DockerComposeFile%
echo     container_name: %NewContainerName%>> %DockerComposeFile%
echo     restart: unless-stopped>> %DockerComposeFile%
if [%DLNAFunctionality%]==[yes] goto :DoDLNA_Functionality
echo     ports:>> %DockerComposeFile%
echo       - "%STASH_PORT%:9999">> %DockerComposeFile%
goto :SkipDLNA_Functionality
:DoDLNA_Functionality
echo     network_mode: host>> %DockerComposeFile%
:SkipDLNA_Functionality
echo     logging:>> %DockerComposeFile%
echo       driver: "json-file">> %DockerComposeFile%
echo       options:>> %DockerComposeFile%
echo         max-file: "10">> %DockerComposeFile%
echo         max-size: "2m">> %DockerComposeFile%
echo     environment:>> %DockerComposeFile%
echo       - STASH_STASH=/data/>> %DockerComposeFile%
echo       - STASH_GENERATED=/generated/>> %DockerComposeFile%
echo       - STASH_METADATA=/metadata/>> %DockerComposeFile%
echo       - STASH_CACHE=/cache/>> %DockerComposeFile%
if [%DLNAFunctionality%]==[yes] goto :DoDLNA_Functionality_pt2
echo       - STASH_PORT=9999>> %DockerComposeFile%
goto :SkipDLNA_Functionality_pt2
:DoDLNA_Functionality_pt2
echo       - STASH_PORT=%STASH_PORT%>> %DockerComposeFile%
:SkipDLNA_Functionality_pt2
echo     volumes:>> %DockerComposeFile%
echo       - /etc/localtime:/etc/localtime:ro>> %DockerComposeFile%
echo       - ./config:/root/.stash>> %DockerComposeFile%
echo       - ./data:/data>> %DockerComposeFile%
echo       - ./metadata:/metadata>> %DockerComposeFile%
echo       - ./cache:/cache>> %DockerComposeFile%
echo       - ./blobs:/blobs>> %DockerComposeFile%
echo       - ./generated:/generated>> %DockerComposeFile%
if [%SharedMountPath%]==[] goto :SkipSharedMountPaths
echo       - %SharedMountPath%:/external%MountAccess%>> %DockerComposeFile%
if [%SharedMountPath2%]==[] goto :SkipSharedMountPaths
echo       - %SharedMountPath2%:/external2%MountAccess%>> %DockerComposeFile%
if [%SharedMountPath3%]==[] goto :SkipSharedMountPaths
echo       - %SharedMountPath3%:/external3%MountAccess%>> %DockerComposeFile%
if [%SharedMountPath4%]==[] goto :SkipSharedMountPaths
echo       - %SharedMountPath4%:/external4%MountAccess%>> %DockerComposeFile%
if [%SharedMountPath5%]==[] goto :SkipSharedMountPaths
echo       - %SharedMountPath5%:/external5%MountAccess%>> %DockerComposeFile%
:SkipSharedMountPaths

if [%SkipDockerCompose%] NEQ [] goto :DoNot_DockerCompose
if [%PullDockerStashImage%] NEQ [yes] goto :SkipPullDockerStashImage
docker pull %Image%
:SkipPullDockerStashImage
docker-compose up -d
:DoNot_DockerCompose
cd ..


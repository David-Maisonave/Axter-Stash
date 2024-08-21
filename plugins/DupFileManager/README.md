# This Plugin is under construction!!!

# DupFileManager: Ver 0.1.0 (By David Maisonave)
DupFileManager is a [Stash](https://github.com/stashapp/stash) plugin which manages duplicate file in the Stash system.
### Features
- Can merge potential source in the duplicate file names for tag names, performers, and studios.
  - Normally when Stash searches the file name for tag names, performers, and studios, it only does so using the primary file. This plugin scans the duplicate files to see if additional fields are available.
- Delete duplicate file task with the following options:
  - Options in plugin UI (Settings->Plugins->Plugins->[DupFileManager])
    - Ignore reparse-points. By default, reparse-points are not deleted.
    - Ignore symbolic links. By default, symbolic links are not deleted.
    - Before deletion, merge potential source in the duplicate file names for tag names, performers, and studios.
    - Optionally permanently duplicates or moved them to **trash can** / alternate folder.
  - Options available via DupFileManager_config.py
    - Use a white list of preferential directories to determine which duplicate should be the primary.
    - Use a black list to determine which duplicates should be deleted first.
    - Use an ignore list to avoid specific directories. No action is taken on any file in the ignore list.
    - Target directories list. If this list is populated, only files under these directories are process. If list is empty, all files are processed (excluding those in ignore list).
	- Alternative path to move duplicate files. Path needs to be in the same drive as the duplicate file. 
	  - Example: "C:\TempDeleteFolder"

### Using DupFileManager
This Plugin is under construction!!!

### Requirements
`pip install stashapp-tools`
`pip install --upgrade stashapp-tools`
`pip install pyYAML`
`pip install Send2Trash`

### Installation
- Follow **Requirements** instructions.
- In the stash plugin directory (C:\Users\MyUserName\.stash\plugins), create a folder named **DupFileManager**.
- Copy all the plugin files to this folder.(**C:\Users\MyUserName\\.stash\plugins\DupFileManager**).
- Click the **[Reload Plugins]** button in Stash->Settings->Plugins->Plugins.

That's it!!!

### Options
- Options are accessible in the GUI via Settings->Plugins->Plugins->[DupFileManager].
- More options available in DupFileManager_config.py.


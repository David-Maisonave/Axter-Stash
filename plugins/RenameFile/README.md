# RenameFile:
RenameFile is a [Stash](https://github.com/stashapp/stash) plugin which performs the following two main task.
- **Rename Scene File Name** (On-The-Fly)
- **Append tag names** to file name

It allows users to rename the video (scene) file name by editing the [Title] field located in the scene [Edit] tab.
In addition, the plugin also appends tags to the file name if the tag does not already exist in the name.

Note: This script is **largely** based on the [Renamer](https://github.com/Serechops/Serechops-Stash/tree/main/plugins/Renamer) script.

### Using RenameFile
- Open a scene (via Stash), and click on the [**Edit**] tab. Populate the [**Title**] field with the desired file name. 
  - Note: Do **NOT** include the file folder name and do **NOT** include file extension. 
- After populating the Title field, click the save button.
- After a few seconds, the file will get renamed and the screen will get updated with the new file name.
- By default tag names are appended to the file name only if the tags do not exist in the original name.
  - The [Tag Append] feature can be disabled by adding "tags" to the **exclude_keys** field in **renamefile_settings.py** file.
- Since this plugin is largely based on the [Renamer](https://github.com/Serechops/Serechops-Stash/tree/main/plugins/Renamer) plugin, it inherited some of its features, like being able to include any of the following fields when auto-renaming is executed:
  - studio, performers, date, height, video_codec, frame_rate
  - To add these fields removed the desired field(s) from **exclude_keys** in renamefile_settings.py.
  - To change the order, modify the **key_order** field.
  - There is a dry_run option in the renamefile_settings.py, and I highly recommend enabling this option before making changes to renamefile_settings.py. The renamefile.log can be reviewed to verify that the rename action will occur as expected.

**Note:** On Windows 10/11, the file can not be renamed while it's playing. It will result in following error:
`
Error: [WinError 32] The process cannot access the file because it is being used by another process
`
To avoid this error, refresh the URL before changing the Title field.

### Requirements
`pip install stashapp-tools`

`pip install pyYAML`

### Installation
- Follow **Requirements** instructions.
- In the stash plugin directory (C:\Users\MyUserName\.stash\plugins), create a folder named **RenameFile**.
- Copy all the plugin files to this folder.(**C:\Users\MyUserName\.stash\plugins\RenameFile**).
- Restart Stash.

That's it!!!

### Options
To change options, see **renamefile_settings.py** file. After making changes, go to http://localhost:9999/settings?tab=plugins, and click [Reload Plugins].

# Under Development!!!

Warning: Items in this folder are under development and have NOT been tested. 
Development on some items listed on this page have not been started.

# DupFileManager: Ver 0.2.0 (By David Maisonave)

DupFileManager is a [Stash](https://github.com/stashapp/stash) plugin which manages duplicate files in the Stash system.
It has both **task** and **tools-UI** components.

### Features

- Creates a report which can be accessed from the settings->tools menu.The report has the following options:
  - Delete: Delete file and remove from Stash library.
  - Remove: Remove from Stash library.
  - Rename: Rename file.
  - Copy: Copy file from left (source) to right (to-keep).
  - Move: Copy file and metadata left to right.
  - Cpy-Name: Copy file name left to right.
  - Add-Exclude: Add exclude tag to scene,so that scene is excluded from deletion.
  - Remove-Tag: Remove duplicate tag from scene.
  - *Flag-Scene: Flag (mark) scene in report as reviewed (or as requiring further review). Optional flags (red, blue, green, black, & hide-item)
  - Merge: Copy Metadata (tags, performers,& studios) from left to right.
- Can merge potential source in the duplicate file names for tag names, performers, and studios.
  - Normally when Stash searches the file name for tag names, performers, and studios, it only does so using the primary file.
- Advance menu (for specially tagged duplicates)
  - Delete only specially tagged duplicates in blacklist path.
  - Delete duplicates with specified file path.
  - Delete duplicates with specific string in File name.
  - Delete duplicates with specified file size range.
  - Delete with specified duration range.
  - Delete with resolution range.
  - Delete duplicates having specified tags.
  - Delete duplicates with specified rating.
  - Delete duplicates with any of the above combinations.
- Delete duplicate file task with the following options:
  - Tasks (Settings->Task->[Plugin Tasks]->DupFileManager)
    - **Tag Duplicates** - Set tag DuplicateMarkForDeletion to the duplicates with lower resolution, duration, file name length, and/or black list path.
    - **Delete Tagged Duplicates** - Delete scenes having DuplicateMarkForDeletion tag.
    - **Delete Duplicates** - Deletes duplicate files. Performs deletion without first tagging.
  - Plugin UI options (Settings->Plugins->Plugins->[DupFileManager])
    - Has a 3 tier path selection to determine which duplicates to keep, and which should be candidates for deletions.
      - **Whitelist** - List of paths NOT to be deleted. 
        - E.g. C:\Favorite\,E:\MustKeep\
      - **Gray-List** - List of preferential paths to determine which duplicate should be the primary. 
        - E.g. C:\2nd_Favorite\,H:\ShouldKeep\
      - **Blacklist** - List of LEAST preferential paths to determine primary candidates for deletion. 
        - E.g. C:\Downloads\,F:\DeleteMeFirst\
    - **Permanent Delete** - Enable to permanently delete files, instead of moving files to trash can.
    - **Max Dup Process** - Use to limit the maximum files to process. Can be used to do a limited test run.
    - **Merge Duplicate Tags** - Before deletion, merge metadata from duplicate. E.g. Tag names, performers, studios, title, galleries, rating, details, etc...
    - **Swap High Resolution** - When enabled, swaps higher resolution files between whitelist and blacklist/graylist files.
    - **Swap Longer Duration** - When enabled, swaps scene with longer duration.
  - Options available via DupFileManager_config.py
    - **dup_path** - Alternate path to move deleted files to. Example: "C:\TempDeleteFolder"
    - **toRecycleBeforeSwap** - When enabled, moves destination file to recycle bin before swapping files.
    - **addPrimaryDupPathToDetails** - If enabled, adds the primary duplicate path to the scene detail.

### Requirements

- `pip install --upgrade stashapp-tools`
- `pip install requests`
- `pip install Send2Trash`

### Installation

- Follow **Requirements** instructions.
- In the stash plugin directory (C:\Users\MyUserName\.stash\plugins), create a folder named **DupFileManager**.
- Copy all the plugin files to this folder.(**C:\Users\MyUserName\\.stash\plugins\DupFileManager**).
- Click the **[Reload Plugins]** button in Stash->Settings->Plugins->Plugins.

That's it!!!

### Options

- Options are accessible in the GUI via Settings->Plugins->Plugins->[DupFileManager].
- More options available in DupFileManager_config.py.


# DupFileManager: Ver 0.1.3 (By David Maisonave)

DupFileManager is a [Stash](https://github.com/stashapp/stash) plugin which manages duplicate file in the Stash system.

<img width="500" alt="DupFileManager_Task_UI" src="https://github.com/user-attachments/assets/d25fd76b-4624-401b-bb12-091a4dadbe0c">

### Features
- Delete duplicate file task with the following options:
  - Tasks (Settings->Task->[Plugin Tasks]->DupFileManager)
    - **Tag Duplicates** - Set tag DuplicateMarkForDeletion to the duplicates with lower resolution, duration, file name length, and/or black list path.
    - **Delete Tagged Duplicates** - Delete scenes having DuplicateMarkForDeletion tag.
    - **Delete Duplicates** - Deletes duplicate files. Performs deletion without first tagging.
  - Plugin UI options (Settings->Plugins->Plugins->[DupFileManager])
    - Has a 3 tier path selection to determine which duplicates to keep, and which should be candidates for deletions.
      - **Whitelist** - List of paths NOT to be deleted. 
        - E.g. C:\Favorite\,E:\MustKeep\
      - **Gray-List** - List of preferential paths to determine which duplicate should be the primary. The list should be in order of most preferable in the beginning of the list.
        - E.g. C:\2nd_Fav,C:\3rd_Fav,C:\4th_Fav,H:\ShouldKeep
      - **Blacklist** - List of LEAST preferential paths to determine primary candidates for deletion. The list should be in order of least preferable at the end.
        - E.g. C:\Downloads,C:\DeleteMe-3rd,C:\DeleteMe-2nd,C:\DeleteMeFirst
    - **Permanent Delete** - Enable to permanently delete files, instead of moving files to trash can.
    - **Max Dup Process** - Use to limit the maximum files to process. Can be used to do a limited test run.
    - **Merge Duplicate Tags** - Before deletion, merge metadata from duplicate. E.g. Tag names, performers, studios, title, galleries, rating, details, etc...
    - **Swap High Resolution** - When enabled, swaps higher resolution files between whitelist and blacklist/graylist files.
    - **Swap Longer Duration** - When enabled, swaps scene with longer duration.
  - Options available via DupFileManager_config.py
    - **dup_path** - Alternate path to move deleted files to. Example: "C:\TempDeleteFolder"
    - **toRecycleBeforeSwap** - When enabled, moves destination file to recycle bin before swapping files.
    - **addPrimaryDupPathToDetails** - If enabled, adds the primary duplicate path to the scene detail.
- Optionally merge metadata between duplicates before file deletion. (tag names, performers, studios, etc...)
  - <img width="500" alt="MergeMetadataOption" src="https://github.com/user-attachments/assets/73ca7775-37e4-4409-8dac-1ddc7f31415d">

### Requirements

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

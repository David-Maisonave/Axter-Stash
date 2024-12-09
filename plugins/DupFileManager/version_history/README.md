##### This page was added starting on version 0.2.0 to keep track of newly added features between versions.
- Note: Sub versions (x.x.x.**x**) are only listed on this page.
### 0.2.0
- For report, added logic to transfer option settings **[Disable Complete Confirmation]** and **[Disable Delete Confirmation]** when paginating.
- Fixed minor bug in advance_options.html for GQL params.
### 0.2.1
- Added logic to have reports and advanced menu to work with Stash settings requiring a password by adding API-Key as param argument for advance menu, and adding API-Key as variable in reports.
- When **[Advance Tag Menu]** is called from reports, it's given both the GQL URL and the apiKey on the URL param, which allows advance menu to work with non-standard URL's and with API-Key.
### 0.2.2
- Added dropdown menu logic to Advance Menu and reports.
- Added Graylist deletion option to Advance Menu.
- Report option to clear all flags from report.
- Report option to clear all (_DuplicateMarkForDeletion_?) tag from all scenes.
- Report option to delete from Stash DB all scenes with missing files in file system.
- Added popup tag list to report which list all tags associated with scene.
- Added popup performer list to report which list all performers associated with scene.
- Added popup gallery list to report which list all galleries associated with scene.
- Added popup group list to report which list all groups associated with scene.
- After merging tags in report, the report gets updated with the merged scene metadata.
- Added graylist deletion option to [**Advance Duplicate File Deletion Menu**].
- Added pinklist option to Settings->Plugins->Plugins and to [**Advance Duplicate File Deletion Menu**]
  - The pinklist is only used with the [**Advance Duplicate File Deletion Menu**], and it's **NOT** used in the primary process to selected candidates for deletion.
- Advance Menu now works with non-tagged scenes that are in the current report.
### 1.0.0
- Consolidated buttons and links on report into dropdown buttons.
- On report, added dropdown menu options for flags.
- Rename Tools-UI advance duplicate tagged menu to [**Advance Duplicate File Deletion Menu**]
- When [**Advance Duplicate File Deletion Menu**] completes report, gives user prompt to open the report in browser.
- Added performance enhancement for removing (clearing) duplicate tags from all scenes by using SQL call.
- Added option to report to delete files that do not exist by duplicate candidates in report, as well as by tagged files.
- Added logic to disable scene in report if deleted by [**Advance Duplicate File Deletion Menu**]. Note: Requires a refresh.
- Added report option to delete by flags set on the report.
### 1.0.0.1
- Fixed bug with report delete scene request.
### 1.0.0.2
- In the report, made icon colors for tags, performers, galleries, and groups with different colors if they don't match. In other words, use different color icons if **candidate to delete** doesn't match **duplicate to keep** associated icon data.
  - If data for associated icon are the same, then both icons are black or blue (the default color).
  - If [**duplicate to keep**] is missing data that is in [**candidate to delete**], than [**candidate to delete**] gets a yellow icon.
  - If [**candidate to delete**] is missing data that is in [**duplicate to keep**], than [**duplicate to keep**] gets a pink icon.
### 1.0.0.3
- Added option on report to merge all metadata missing in [**Duplicate to Keep**] files.
- Added cookies to report so as to remember user options for Disable Complete Confirmation **[Disable Complete Confirmation]** and **[Disable Delete Confirmation]**.
  - This change was needed because sometimes the browser refuse to open local URL's with params on the URL.
  - Using cookies also allows check options status to stay the same after refresh.
- Added code to [**Advance Duplicate File Deletion Menu**] to delete based on flags.
### 1.0.1
- Change [**Advance Duplicate File Deletion Menu**] default input values to placeholder text.
- Change stash toolbar icon for DupFileManager to a file icon with a video camera.
- Removed **plugin/** from the URL for the Tools-UI menu.
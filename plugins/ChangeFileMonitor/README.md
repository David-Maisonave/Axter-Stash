# ChangeFileMonitor: Ver 0.1.0 (By David Maisonave)
ChangeFileMonitor is a [Stash](https://github.com/stashapp/stash) plugin which updates Stash if any changes occurs in the Stash library paths.

### Using ChangeFileMonitor

### Requirements
`pip install stashapp-tools`
`pip install pyYAML`
`pip install watchdog`

### Installation
- Follow **Requirements** instructions.
- In the stash plugin directory (C:\Users\MyUserName\.stash\plugins), create a folder named **ChangeFileMonitor**.
- Copy all the plugin files to this folder.(**C:\Users\MyUserName\\.stash\plugins\ChangeFileMonitor**).
- Restart Stash.

That's it!!!

### Options
- Main options are accessible in the GUI via Settings->Plugins->Plugins->[ChangeFileMonitor].
- Advanced options are avialable in the **changefilemonitor_settings.py** file. After making changes, go to http://localhost:9999/settings?tab=plugins, and click [Reload Plugins].


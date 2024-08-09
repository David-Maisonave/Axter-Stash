# FileMonitor: Ver 0.7.1 (By David Maisonave)
FileMonitor is a [Stash](https://github.com/stashapp/stash) plugin which updates Stash if any changes occurs in the Stash library paths.

### Using FileMonitor as a plugin
- To start monitoring file changes, go to **Stash->Settings->Task->[Plugin Tasks]->FileMonitor**, and click on the [Start Library Monitor] button.
  - ![FileMonitor_Task](https://github.com/user-attachments/assets/f275a70f-8e86-42a4-b2c1-98b3f4935334)
- To stop this task, go to **Stash->Settings->Task->[Task Queue]**, and click on the **[x]**.
  - ![Kill_FileMonitor_Task](https://github.com/user-attachments/assets/a3f4abca-f3a2-49fa-9db5-e0c733e0aeb1)

### Using FileMonitor as a script
**FileMonitor** can be called as a standalone script.
- To start monitoring call the script and pass --url and the Stash URL.
  - python filemonitor.py --url http://localhost:9999
- To stop **FileMonitor**, pass argument **--stop**.
  - python filemonitor.py **--stop**
  - The stop command works to stop the standalone job and the Stash plugin task job.
- To restart **FileMonitor**, pass argument **--restart**.
  - python filemonitor.py **--restart**
  - The restart command restarts FileMonitor as a Task in Stash.

### Requirements
- pip install -r requirements.txt
- Or manually install each requirement:
  - `pip install stashapp-tools --upgrade`
  - `pip install pyYAML`
  - `pip install watchdog`
  - `pip install schedule`

### Installation
- Follow **Requirements** instructions.
- In the stash plugin directory (C:\Users\MyUserName\.stash\plugins), create a folder named **FileMonitor**.
- Copy all the plugin files to this folder.(**C:\Users\MyUserName\\.stash\plugins\FileMonitor**).
- Click the **[Reload Plugins]** button in Stash->Settings->Plugins->Plugins.

That's it!!!

### Options
- All are accessible in the GUI via Settings->Plugins->Plugins->[FileMonitor].
- More options available in filemonitor_config.py.



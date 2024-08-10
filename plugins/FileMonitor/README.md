# FileMonitor: Ver 0.7.2 (By David Maisonave)
FileMonitor is a [Stash](https://github.com/stashapp/stash) plugin which updates Stash if any changes occurs in the Stash library paths.
It also has a scheduler which can be used to schedule reoccurring task.

### Starting FileMonitor from the UI
From the GUI, FileMonitor can be started as a service or as a plugin. The recommended method is to start it as a service. When started as a service, it will jump on the Task Queue momentarily, and then disappear as it starts running in the background.
- To start monitoring file changes, go to **Stash->Settings->Task->[Plugin Tasks]->FileMonitor**, and click on the [Start Library Monitor Service] button.
  - ![FileMonitorService](https://github.com/user-attachments/assets/5c72845e-6c1c-4e06-8e43-5949fe0b91a3)
  - **Important Note**: At first, this will show up as a plugin in the Task Queue momentarily. It will then disappear from the Task Queue and run in the background as a service.
- To stop FileMonitor click on [Stop Library Monitor] button.
- The **[Run as a Plugin]** option is mainaly available for backwards compatibility and for test purposes.
  

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

### Reoccurring Task Scheduler
To enable the scheduler **Stash->Settings->Plugins->Plugins->FileMonitor** and enable the **Scheduler** option.
![ReoccurringTaskScheduler](https://github.com/user-attachments/assets/5a7bf6a4-3bd6-4692-a6c3-e9f8f4664f14)

To configure the schedule or to add new task, edit the **task_reoccurring_scheduler** section in the **filemonitor_config.py** file.
```` python
"task_reoccurring_scheduler": [
	# Frequency can be in minutes, hours, or days.
	# A zero frequency value disables the task.
	{"task" : "Clean",      "days" : 2},  # Maintenance -> [Clean] (every 2 days)
	{"task" : "Generate",   "days" : 7}, # Generated Content-> [Generate] (Weekly)
	{"task" : "Backup",     "days" : 30}, # Backup -> [Backup] (Monthly)
	{"task" : "Scan",       "days" : 7}, # Library -> [Scan] (Weekly)
	{"task" : "Auto Tag",   "hours" : 24},  # Auto Tag -> [Auto Tag] (Daily)
	{"task" : "Optimise Database",   "hours" : 24},  # Maintenance -> [Optimise Database] (Daily)
	{"task" : "Create Tags", "pluginId" : "pathParser", "days" : 1}, # Requires plugin [Path Parser] (Daily)
	{"task" : "PluginButtonName_Here", "pluginId" : "PluginId_Here", "hours" : 0},   # Place holder for custom task.
	# Add additional task here.
],
````
- To add plugins to the task list, both the Plugin-ID and the plugin name is required. The plugin ID is usually the file name of the script without the extension.
- The frequency field can be in minutes, hours, or days.
- The freuency value must be a number greater than zero.
- The scheduler feature requires `pip install schedule`
- If the user leaves the scheduler disabled, **schedule** does NOT have to be installed.
- The scheduler will **NOT** work properly when FileMonitor is run as a plugin.
- The current scheduler code does **NOT** work persistently. That means the schedule always restarts when the program restarts. This may be fixed in future FileMonitor versions.

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
- Main options are accessible in the GUI via Settings->Plugins->Plugins->[FileMonitor].
- Additional options available in filemonitor_config.py.



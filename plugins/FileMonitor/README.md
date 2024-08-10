# FileMonitor: Ver 0.7.2 (By David Maisonave)
FileMonitor is a [Stash](https://github.com/stashapp/stash) plugin which updates Stash if any changes occurs in the Stash library paths.
It also has a scheduler which can be used to schedule reoccurring task.

## Starting FileMonitor from the UI
From the GUI, FileMonitor can be started as a service or as a plugin. The recommended method is to start it as a service. When started as a service, it will jump on the Task Queue momentarily, and then disappear as it starts running in the background.
- To start monitoring file changes, go to **Stash->Settings->Task->[Plugin Tasks]->FileMonitor**, and click on the [Start Library Monitor Service] button.
  - ![FileMonitorService](https://github.com/user-attachments/assets/5c72845e-6c1c-4e06-8e43-5949fe0b91a3)
  - **Important Note**: At first, this will show up as a plugin in the Task Queue momentarily. It will then disappear from the Task Queue and run in the background as a service.
- To stop FileMonitor click on [Stop Library Monitor] button.
- The **[Run as a Plugin]** option is mainaly available for backwards compatibility and for test purposes.
  

## Using FileMonitor as a script
**FileMonitor** can be called as a standalone script.
- To start monitoring call the script and pass --url and the Stash URL.
  - python filemonitor.py --url http://localhost:9999
- To stop **FileMonitor**, pass argument **--stop**.
  - python filemonitor.py **--stop**
  - The stop command works to stop the standalone job and the Stash plugin task job.
- To restart **FileMonitor**, pass argument **--restart**.
  - python filemonitor.py **--restart**
  - The restart command restarts FileMonitor as a Task in Stash.

# Reoccurring Task Scheduler
To enable the scheduler go to **Stash->Settings->Plugins->Plugins->FileMonitor** and enable the **Scheduler** option.
![ReoccurringTaskScheduler](https://github.com/user-attachments/assets/5a7bf6a4-3bd6-4692-a6c3-e9f8f4664f14)

To configure the schedule or to add new task, edit the **task_reoccurring_scheduler** section in the **filemonitor_config.py** file.
```` python
"task_reoccurring_scheduler": [
	{"task" : "Clean",      "hours" : 48},  # Maintenance -> [Clean] (every 2 days)
	{"task" : "Auto Tag",   "hours" : 24},  # Auto Tag -> [Auto Tag] (Daily)
	{"task" : "Optimise Database",   "hours" : 24},  # Maintenance -> [Optimise Database] (Daily)
	
	# The following is the syntax used for plugins. A plugin task requires the plugin name for the [task] field, and the plugin-ID for the [pluginId] field.
	{"task" : "Create Tags", "pluginId" : "pathParser", "hours" : 0}, # This task requires plugin [Path Parser]. To enable this task change the zero to a positive number.
	
	# Note: For a weekly task use the weekday method which is more reliable. The hour section in time MUST be a two digit number, and use military time format. Example: 1PM = "13:00"
	{"task" : "Generate",   "weekday" : "sunday",   "time" : "07:00"}, # Generated Content-> [Generate] (Every Sunday at 7AM)
	{"task" : "Scan",       "weekday" : "sunday",   "time" : "03:00"}, # Library -> [Scan] (Weekly) (Every Sunday at 3AM)
	
	# To perform a task monthly, specify the day of the month as in the weekly schedule format, and add a monthly field.
		# The monthly field value must be 1, 2, 3, or 4.
			# 1 = 1st specified weekday of the month. Example 1st monday.
			# 2 = 2nd specified weekday of the month. Example 2nd monday of the month.
			# 3 = 3rd specified weekday of the month.
			# 4 = 4th specified weekday of the month.
	# Example monthly method.
	{"task" : "Backup",     "weekday" : "saturday",   "time" : "01:00", "monthly" : 2}, # Backup -> [Backup] 2nd saturday of the month at 1AM
	
	# The following is a place holder for a plugin.
	{"task" : "PluginButtonName_Here", "pluginId" : "PluginId_Here", "hours" : 0}, # The zero frequency value makes this task disabled.
	# Add additional plugin task here.
],
````
- To add plugins to the task list, both the Plugin-ID and the plugin name is required. The plugin ID is usually the file name of the script without the extension.
- Task can be scheduled to run monthly, weekly, hourly, and by minutes.
- The scheduler list uses two types of syntax. One is **frequency** based, and the other is **weekday** based.
  - **Frequency Based**
    - The frequency field can be in **minutes** or **hours**.
    - The frequency value must be a number greater than zero, because a frequency value of zero will disable the task on the schedule.
    - **Frequency Based Examples**:
      - Starts a task every 24 hours.
        - `{"task" : "Auto Tag",   "hours" : 24},`
      - Starts a (**plugin**) task every 30 minutes.
        - `{"task" : "Create Tags", "pluginId" : "pathParser", "minutes" : 30},`
  - **weekday Based**
    - Use the weekday based syntax for weekly and monthly schedules.
    - Both weekly and monthly schedules must have a **weekday** field and a **time** field, which specifies the day of the week and the time to start the task.
    - **Weekly**:
      - **Weekly Example**:
        - Starts a task weekly every monday and 9AM.
          - `{"task" : "Generate",   "weekday" : "monday",   "time" : "09:00"},`
    - **Monthly**:
      - The monthly syntax is similar to the weekly format, but it also includes a **"monthly"** field which must be set to 1, 2, 3, or 4.
      - **Monthly Examples**:
        - Starts a task once a month on the 3rd sunday of the month and at 1AM.
          - `{"task" : "Backup",     "weekday" : "sunday",   "time" : "01:00", "monthly" : 3},`
        - Starts a task at 2PM once a month on the 1st saturday of the month.
          - `{"task" : "Optimise Database",     "weekday" : "saturday",   "time" : "14:00", "monthly" : 1},`

- The scheduler feature requires `pip install schedule`
  - If the user leaves the scheduler disabled, **schedule** does NOT have to be installed.
- For best results use the scheduler with FileMonitor running as a service.

## Requirements
- pip install -r requirements.txt
- Or manually install each requirement:
  - `pip install stashapp-tools --upgrade`
  - `pip install pyYAML`
  - `pip install watchdog`
  - `pip install schedule`

## Installation
- Follow **Requirements** instructions.
- In the stash plugin directory (C:\Users\MyUserName\.stash\plugins), create a folder named **FileMonitor**.
- Copy all the plugin files to this folder.(**C:\Users\MyUserName\\.stash\plugins\FileMonitor**).
- Click the **[Reload Plugins]** button in Stash->Settings->Plugins->Plugins.

That's it!!!

## Options
- Main options are accessible in the GUI via Settings->Plugins->Plugins->[FileMonitor].
- Additional options available in filemonitor_config.py.



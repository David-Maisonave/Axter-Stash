# Description: This is a Stash plugin which updates Stash if any changes occurs in the Stash library paths.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/FileMonitor
config = {
    # Enable to run metadata_generate (Generate Content) after metadata scan.
    "runGenerateContent": False,
    # Enable to run scan when triggered by on_any_event.
    "onAnyEvent": False,
    # Enable to monitor changes in file system for modification flag. This option is NOT needed for Windows, because on Windows changes are triggered via CREATE, DELETE, and MOVE flags. Other OS may differ.
    "scanModified": False,
    # Timeout in seconds. This is how often it will check the scheduler and (in-plugin mode) if another job (Task) is in the queue
    "timeOut": 60,
    # Enable to exit FileMonitor by creating special file in plugin folder\working
    "createSpecFileToExit": True,
    # Enable to delete special file imediately after it's created in stop process
    "deleteSpecFileInStop": False,
    # Enable to run metadata clean task after file deletion.
    "runCleanAfterDelete": False,
    
    # The reoccurring scheduler task list.
    # Task can be scheduled to run monthly, weekly, hourly, and by minutes. For best results use the scheduler with FileMonitor running as a service.
    # The frequency field can be in minutes or hours. A zero frequency value disables the task.
    # For weekly and monthly task, use the syntax as done in the **Generate** and **Backup** task below.
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
        {"task" : "Backup",     "weekday" : "sunday",   "time" : "01:00", "monthly" : 2}, # Backup -> [Backup] 2nd sunday of the month at 1AM (01:00)
        
        # The following is a place holder for a plugin.
        {"task" : "PluginButtonName_Here", "pluginId" : "PluginId_Here", "hours" : 0}, # The zero frequency value makes this task disabled.
        # Add additional plugin task here.
    ],
    
    # Maximum backups to keep. When scheduler is enabled, and the Backup runs, delete older backups after reaching maximum backups.
    "BackupsMax" : 12, # Only works if BackupDatabasePath is properly populated.
    # The BACKUP database path. ToDo: Implement code to automate fetching this value
    "BackupDatabasePath" : "C:\\Users\\admin3\\.stash\\DbBackup", # Example populated path
    
    # When enabled, if CREATE flag is triggered, DupFileManager task is called if the plugin is installed.
    "onCreateCallDupFileManager": False, # Not yet implemented!!!!
    
    # The following fields are ONLY used when running FileMonitor in script mode
    "endpoint_Scheme" : "http", # Define endpoint to use when contacting the Stash server
    "endpoint_Host" : "0.0.0.0", # Define endpoint to use when contacting the Stash server
    "endpoint_Port" : 9999, # Define endpoint to use when contacting the Stash server
}

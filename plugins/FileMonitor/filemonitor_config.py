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
    # Timeout in seconds. This is how often it will check if another job (Task) is in the queue.
    "timeOut": 15, # Not needed when running in command line mode.
    # Enable to exit FileMonitor by creating special file in plugin folder\working
    "createSpecFileToExit": True,
    # Enable to delete special file imediately after it's created in stop process
    "deleteSpecFileInStop": False,
    # Enable to run metadata clean task after file deletion.
    "runCleanAfterDelete": False,
    
    # Enable to turn on scheduler_task_list
    "turnOnScheduler": True,
    # Reoccurring scheduler task list. To activate schedule, change number from zero to the number of hours interval
    "task_reoccurring_scheduler": [
        # Example: To perform a 'Clean' task every 48 hours, change zero to 48
        # Hours Conversion: 24=Daily, 168=Weekly, 720=Monthly, 1440=Bi-Monthly, 2160=Quarterly, 8760=Yearly
        {"task" : "Clean",      "hours" : 48},  # Maintenance Clean (every 2 days)
        {"task" : "Generate",   "hours" : 168}, # Generated Content (Weekly)
        {"task" : "Backup",     "hours" : 720}, # Backup Backup (Monthly)
        {"task" : "Scan",       "hours" : 168}, # Library Scan (Weekly)
        # {"task" : "Create Tags",   "hours" : 24},# Requires plugin [Path Parser]
        {"task" : "Create Tags", "pluginId" : "pathParser", "hours" : 24}, # Requires plugin [Path Parser]
        {"task" : "Auto Tag",   "hours" : 0},   # !!! Not yet implemented!!!
        {"task" : "MyTaskHere", "pluginId" : "MyPluginId", "hours" : 0},   # Place holder for custom task.
    ],
    # Maximum backups to keep. When scheduler is enabled, and the Backup runs, delete older backups after reaching maximum backups.
    "BackupsMax" : 6, # Not yet implemented!!!
    
    # When enabled, if CREATE flag is triggered, DupFileManager task is called if the plugin is installed.
    "onCreateCallDupFileManager": False, # Not yet implemented!!!!
    
    # The following fields are ONLY used when running FileMonitor in script mode
    "endpoint_Scheme" : "http", # Define endpoint to use when contacting the Stash server
    "endpoint_Host" : "0.0.0.0", # Define endpoint to use when contacting the Stash server
    "endpoint_Port" : 9999, # Define endpoint to use when contacting the Stash server
}

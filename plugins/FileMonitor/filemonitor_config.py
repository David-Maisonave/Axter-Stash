# Description: This is a Stash plugin which updates Stash if any changes occurs in the Stash library paths.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/FileMonitor
config = {
    # The task scheduler list.
    # Task can be scheduled to run monthly, weekly, daily, hourly, and by minutes. For best results use the scheduler with FileMonitor running as a service.
    # For daily, weekly, and monthly task, use the weekday syntax.
    #   The [Auto Tag] task is an example of a daily scheduled task.
    #   The [Generate] task is an example of a weekly scheduled task.
    #   The [Backup] task is an example of a monthly scheduled task.
    # Note: The hour section in time MUST be a two digit number, and use military time format. Example: 1PM = "13:00" and 1AM = "01:00"
    "task_scheduler": [
         # To create a daily task, include each day of the week for the weekday field.
        {"task" : "Auto Tag",   "weekday" : "monday,tuesday,wednesday,thursday,friday,saturday,sunday",  "time" : "06:00"},  # Auto Tag -> [Auto Tag] (Daily at 6AM)
        {"task" : "Optimise Database",   "weekday" : "monday,tuesday,wednesday,thursday,friday,saturday,sunday",  "time" : "07:00"},  # Maintenance -> [Optimise Database] (Daily at 7AM)
        
        # The following task are scheduled for 3 days out of the week.
        {"task" : "Clean",   "weekday" : "monday,wednesday,friday",  "time" : "08:00"},  # Maintenance -> [Clean] (3 days per week at 8AM)
        {"task" : "Clean Generated Files",   "weekday" : "tuesday,thursday,saturday",  "time" : "08:00"},  # Maintenance -> [Clean Generated Files] (3 days per week at 8AM)
        
        # The following task are scheduled weekly
        {"task" : "Generate",   "weekday" : "sunday",   "time" : "07:00"}, # Generated Content-> [Generate] (Every Sunday at 7AM)
        {"task" : "Scan",       "weekday" : "sunday",   "time" : "03:00"}, # Library -> [Scan] (Weekly) (Every Sunday at 3AM)
        
        # To perform a task monthly, specify the day of the month as in the weekly schedule format, and add a monthly field.
            # The monthly field value must be 1, 2, 3, or 4.
                # 1 = 1st specified weekday of the month. Example 1st monday.
                # 2 = 2nd specified weekday of the month. Example 2nd monday of the month.
                # 3 = 3rd specified weekday of the month.
                # 4 = 4th specified weekday of the month.
        # The following task is scheduled monthly
        {"task" : "Backup",     "weekday" : "sunday",   "time" : "01:00", "monthly" : 2}, # Backup -> [Backup] 2nd sunday of the month at 1AM (01:00)
        
        # The above weekday method is the more reliable method to schedule task, because it doesn't rely on FileMonitor running continuously (non-stop).
        
        # The below examples use frequency field method which can work with minutes and hours. A zero frequency value disables the task.
        #       Note:   Both seconds and days are also supported for the frequency field. 
        #               However, seconds is mainly used for test purposes.
        #               And days usage is discourage, because it only works if FileMonitor is running for X many days non-stop.
        # Note:
        #       The below example tasks are done using hours and minutes because the task is easily disabled (deactivated) by a zero value entry.
        #       Any of these task types can be converted to a daily, weekly, or monthly syntax.
                       
        # The following is the syntax used for plugins. A plugin task requires the plugin name for the [task] field, and the plugin-ID for the [pluginId] field.
        {"task" : "Create Tags", "pluginId" : "pathParser", "hours" : 0}, # This task requires plugin [Path Parser]. To enable this task change the zero to a positive number.
        
        # Example task for calling another Stash plugin, which needs plugin name and plugin ID.
        {"task" : "PluginButtonName_Here", "pluginId" : "PluginId_Here", "hours" : 0}, # The zero frequency value makes this task disabled.
        
        # Example task to call call_GQL API with custom input
        {"task" : "GQL", "input" : "mutation OptimiseDatabase { optimiseDatabase }", "minutes" : 0},
        
        # Example task to call a python script. When this task is executed, the keyword <plugin_path> is replaced by filemonitor.py current directory.
        {"task" : "python", "script" : "<plugin_path>test_script_hello_world.py", "args" : "--MyArguments Hello", "minutes" : 0},
        
        # Example task to execute a command
        {"task" : "execute", "command" : "C:\\MyPath\\HelloWorld.bat", "args" : "", "hours" : 0},
        
        # Commented out test task.
        # {"task" : "Backup",     "seconds" : 30},
    ],
    
    # Timeout in seconds. This is how often FileMonitor will check the scheduler and (in-plugin mode) check if another job (Task) is in the queue.
    "timeOut": 60,
    # Enable to run metadata clean task after file deletion.
    "runCleanAfterDelete": False,
    # Enable to run metadata_generate (Generate Content) after metadata scan.
    "runGenerateContent": False,
    
    # The following fields are ONLY used when running FileMonitor in script mode.
    "endpoint_Scheme" : "http", # Define endpoint to use when contacting the Stash server
    "endpoint_Host" : "0.0.0.0", # Define endpoint to use when contacting the Stash server
    "endpoint_Port" : 9999, # Define endpoint to use when contacting the Stash server
    
    # The following are advanced user options.
    # Enable to run scan when triggered by on_any_event.
    "onAnyEvent": False, # If enabled may cause excessive triggers.
    # Enable to monitor changes in file system for modification flag. This option is NOT needed for Windows, because on Windows changes are triggered via CREATE, DELETE, and MOVE flags. Other OS may differ.
    "scanModified": False, # Warning: Enabling this in Windows OS may cause excessive triggers when user is only viewing directory content.
    # Enable to exit FileMonitor by creating special file in plugin folder\working
    "createSpecFileToExit": True,
    # Enable to delete special file immediately after it's created in stop process.
    "deleteSpecFileInStop": False,
    
    # When enabled, if CREATE flag is triggered, DupFileManager task is called if the plugin is installed.
    "onCreateCallDupFileManager": False, # Not yet implemented!!!!
}

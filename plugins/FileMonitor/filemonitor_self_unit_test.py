# **test** tasks which are disabled by default. To enable test tasks, set selfUnitTest to True.
# To run test, enable all task, and start FileMonitor as a service.
# When executed, these task should be seen in the Task Queue unless otherwise stated in comments.
# These tasks are usually executed before updating major releases on https://github.com/David-Maisonave/Axter-Stash/blob/main/plugins/FileMonitor
# These tasks are ALWAYS executed before updating to https://github.com/stashapp/CommunityScripts
self_unit_test = {
    "task_scheduler_repeat": [        
        {"task" : "TestBadTaskNameError",                       "minutes" : 1}, # Test invalid task name
        {"task" : "execute",                                    "minutes" : 1}, # Test invalid task (missing command)
        {"task" : "python",                                     "minutes" : 1}, # Test invalid task (missing scripts)
        {"task" : "PluginWithOutID",                            "minutes" : 1}, # Test invalid task (missing pluginId)
        {"task" : "execute", "command" : "",                    "minutes" : 1}, # Test invalid task (missing command)
        {"task" : "python", "script" : "",                      "minutes" : 1}, # Test invalid task (missing scripts)
        {"task" : "PluginWithOutID", "pluginId" : "",           "minutes" : 1}, # Test invalid task (missing pluginId)
        {"task" : "Foo","pluginId":"foo","validateDir":"foo",   "minutes" : 1}, # Test invalid task (missing plugin directory)
        {"task" : "Log",  "msg" : "Testing Scheduled Log",      "minutes" : 1}, # Test plugin log file
        {"task" : "Trace",                                      "minutes" : 1}, # Test plugin trace logging
        {"task" : "LogOnce",                                    "seconds" :15}, # Test LogOnce
        {"task" : "TraceOnce",                                  "seconds" : 5}, # Test TraceOnce        
        {"task" : "CheckStashIsRunning", "RunAfter" : [{"task" : "Scan"},{"task" : "Backup", "maxBackup" : 0},{"task" : "Clean"}],   "seconds" :15}, # Test RunAfter
        {"task" : "CheckStashIsRunning",    "command" : "<stash_path>stash-win.exe",                    "seconds" :10}, # Check if Stash is running.  If not running, start up Stash.      
        # {"task" : "CheckStashIsRunning", "RunAfter" : [{"task" : "Scan"}],   "seconds" :15}, # To test CheckStashIsRunning, kill Stash after starting FileMonitor service via following command:taskkill /F /IM "stash-win.exe"
    ],
    "task_scheduler_set_time": [        
        # Test [Delete Duplicates] with [Delete Duplicate Scheduler] disabled, and then with it enabled.               
        {"task" : "Delete Duplicates", "pluginId" : "DupFileManager",  "validateDir" : "DupFileManager","weekday" : "sunday",   "time" : "17:56"}, # [Plugin Tasks] -> DupFileManager -> [Delete Duplicates]
        {"task" : "Generate",                                                                           "weekday" : "sunday",   "time" : "17:56"},
        {"task" : "Clean",                                                                              "weekday" : "sunday",   "time" : "17:56"},
        {"task" : "Auto Tag",                                                                           "weekday" : "sunday",   "time" : "17:56"},
        {"task" : "Optimise Database",                                                                  "weekday" : "sunday",   "time" : "17:56"},
        {"task" : "Create Tags", "pluginId" : "pathParser",  "validateDir" : "pathParser",              "weekday" : "sunday",   "time" : "17:56"}, # In task queue as -> Running plugin task: Create Tags
        {"task" : "Tag Duplicates", "pluginId" : "DupFileManager",  "validateDir" : "DupFileManager",   "weekday" : "sunday",   "time" : "17:56"}, # [Plugin Tasks] -> DupFileManager -> [Tag Duplicates]
        {"task" : "Scan","paths": [r"B:\_\SpecialSet", r"C:\foo"],                                      "weekday" : "sunday",   "time" : "17:56"},
        {"task" : "GQL", "input" : "mutation OptimiseDatabase { optimiseDatabase }",                    "weekday" : "sunday",   "time" : "17:56"}, # In task queue as -> Optimising database...
        {"task" : "Clean Generated Files",                                                              "weekday" : "sunday",   "time" : "17:56"},
        {"task" : "RenameGeneratedFiles",                                                               "weekday" : "sunday",   "time" : "17:56"}, # In task queue as -> Migrating scene hashes...
        {"task" : "Backup", "maxBackups" : 0,                                                           "weekday" : "sunday",   "time" : "17:56"}, # Does NOT show up in the Task Queue. Must check STASH log file to verify run.
        {"task" : "python", "script" : "<plugin_path>test_hello_world2.py",                             "weekday" : "sunday",   "time" : "17:56"}, # Does NOT show up in the Task Queue. Check FileMonitor log file, and look for -> Task 'python' result=???
        {"task" : "python", "script" : "<plugin_path>test_hello_world.py", "detach" : False,            "weekday" : "sunday",   "time" : "17:56"}, # Does NOT show up in the Task Queue. Check FileMonitor log file, and look for -> Task 'python' result=???
        {"task" : "execute", "command" : "<plugin_path>test_hello_world2.cmd",                          "weekday" : "sunday",   "time" : "17:56"}, # Does NOT show up in the Task Queue. Check FileMonitor log file, and look for -> Task 'execute' result=???
        {"task" : "execute", "command" : "<plugin_path>test_hello_world.bat", "args" : "--name David",  "weekday" : "sunday",   "time" : "17:56"}, # Does NOT show up in the Task Queue. Check FileMonitor log file, and look for -> Task 'execute' result=???
    ],    
    # MUST ToDo: Always set selfUnitTest to False before checking in this code!!!
    "selfUnitTest_repeat"   : False , # Enable to turn on self unit test.
    "selfUnitTest_set_time" : False  , # Enable to turn on self unit test.
}

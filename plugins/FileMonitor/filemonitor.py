# Description: This is a Stash plugin which updates Stash if any changes occurs in the Stash library paths.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/FileMonitor
# Note: To call this script outside of Stash, pass --url and the Stash URL.
#       Example:    python filemonitor.py --url http://localhost:9999
import os
import time
import pathlib
import argparse
from StashPluginHelper import StashPluginHelper
from watchdog.observers import Observer # This is also needed for event attributes
import watchdog  # pip install watchdog  # https://pythonhosted.org/watchdog/
from threading import Lock, Condition
from multiprocessing import shared_memory
from filemonitor_config import config # Import settings from filemonitor_config.py

CONTINUE_RUNNING_SIG = 99
STOP_RUNNING_SIG = 32

parser = argparse.ArgumentParser()
parser.add_argument('--url', '-u', dest='stash_url', type=str, help='Add Stash URL')
parser.add_argument('--trace', '-t', dest='trace', action='store_true', help='Enables debug trace mode.')
parser.add_argument('--stop', '-s', dest='stop', action='store_true', help='Stop (kill) a running FileMonitor task.')
parser.add_argument('--restart', '-r', dest='restart', action='store_true', help='Restart FileMonitor.')
parser.add_argument('--silent', '--quit', '-q', dest='quit', action='store_true', help='Run in silent mode. No output to console or stderr. Use this when running from pythonw.exe')
parse_args = parser.parse_args()

logToErrSet = 0
logToNormSet = 0
if parse_args.quit:
    logToErrSet = 1
    logToNormSet = 1

settings = {
    "recursiveDisabled": False,
    "zzdebugTracing": False,
    "zzdryRun": False,
}
plugin = StashPluginHelper(
        stash_url=parse_args.stash_url,
        debugTracing=parse_args.trace,
        settings=settings,
        config=config,
        logToErrSet=logToErrSet,
        logToNormSet=logToNormSet
        )
plugin.Status()
plugin.Log(f"\nStarting (__file__={__file__}) (plugin.CALLED_AS_STASH_PLUGIN={plugin.CALLED_AS_STASH_PLUGIN}) (plugin.DEBUG_TRACING={plugin.DEBUG_TRACING}) (plugin.DRY_RUN={plugin.DRY_RUN}) (plugin.PLUGIN_TASK_NAME={plugin.PLUGIN_TASK_NAME})************************************************")

exitMsg = "Change success!!"
mutex = Lock()
signal = Condition(mutex)
shouldUpdate = False
TargetPaths = []

RECURSIVE = plugin.pluginSettings["recursiveDisabled"] == False
SCAN_MODIFIED = plugin.pluginConfig["scanModified"]
RUN_CLEAN_AFTER_DELETE = plugin.pluginConfig["runCleanAfterDelete"]
RUN_GENERATE_CONTENT = plugin.pluginConfig['runGenerateContent']
SCAN_ON_ANY_EVENT = plugin.pluginConfig['onAnyEvent']
SIGNAL_TIMEOUT = plugin.pluginConfig['timeOut']

CREATE_SPECIAL_FILE_TO_EXIT = plugin.pluginConfig['createSpecFileToExit']
DELETE_SPECIAL_FILE_ON_STOP = plugin.pluginConfig['deleteSpecFileInStop']
SPECIAL_FILE_DIR = f"{plugin.LOG_FILE_DIR}{os.sep}working"
if not os.path.exists(SPECIAL_FILE_DIR) and CREATE_SPECIAL_FILE_TO_EXIT:
    os.makedirs(SPECIAL_FILE_DIR)
# Unique name to trigger shutting down FileMonitor
SPECIAL_FILE_NAME = f"{SPECIAL_FILE_DIR}{os.sep}trigger_to_kill_filemonitor_by_david_maisonave.txt"

STASHPATHSCONFIG = plugin.STASH_CONFIGURATION['stashes']
stashPaths = []
for item in STASHPATHSCONFIG: 
    stashPaths.append(item["path"])
stashPaths.append(SPECIAL_FILE_DIR)
plugin.Trace(f"(stashPaths={stashPaths})")

if plugin.DRY_RUN:
    plugin.Log("Dry run mode is enabled.")
plugin.Trace(f"(SCAN_MODIFIED={SCAN_MODIFIED}) (SCAN_ON_ANY_EVENT={SCAN_ON_ANY_EVENT}) (RECURSIVE={RECURSIVE})")

StopLibraryMonitorWaitingInTaskQueue = False
def isJobWaitingToRun():
    global StopLibraryMonitorWaitingInTaskQueue
    i = 1
    while i < 999:
        jobDetails = plugin.STASH_INTERFACE.find_job(i)
        if jobDetails:
            plugin.Trace(f"(Job ID({i})={jobDetails})")
            if jobDetails['status'] == "READY":
                if jobDetails['description'] == "Running plugin task: Stop Library Monitor":
                    StopLibraryMonitorWaitingInTaskQueue = True
                return i
        else:
            plugin.Trace(f"Last job {i}")
            break
        i += 1    
    return 0

if plugin.CALLED_AS_STASH_PLUGIN:
    plugin.Trace(f"isJobWaitingToRun() = {isJobWaitingToRun()})")

def start_library_monitor():
    global shouldUpdate
    global TargetPaths    
    try:
        # Create shared memory buffer which can be used as singleton logic or to get a signal to quit task from external script
        shm_a = shared_memory.SharedMemory(name="DavidMaisonaveAxter_FileMonitor", create=True, size=4)
    except:
        plugin.Error("Could not open shared memory map. Change File Monitor must be running. Can not run multiple instance of Change File Monitor.")
        return
    type(shm_a.buf)
    shm_buffer = shm_a.buf
    len(shm_buffer)
    shm_buffer[0] = CONTINUE_RUNNING_SIG
    plugin.Trace(f"Shared memory map opended, and flag set to {shm_buffer[0]}")
    RunCleanMetadata = False

    event_handler = watchdog.events.FileSystemEventHandler()
    def on_created(event):
        global shouldUpdate
        global TargetPaths
        TargetPaths.append(event.src_path)
        plugin.Log(f"CREATE *** '{event.src_path}'")
        with mutex:
            shouldUpdate = True
            signal.notify()

    def on_deleted(event):
        global shouldUpdate
        global TargetPaths
        nonlocal RunCleanMetadata
        TargetPaths.append(event.src_path)
        plugin.Log(f"DELETE ***  '{event.src_path}'")
        with mutex:
            shouldUpdate = True
            RunCleanMetadata = True
            signal.notify()

    def on_modified(event):
        global shouldUpdate
        global TargetPaths
        if SCAN_MODIFIED:
            TargetPaths.append(event.src_path)
            plugin.Log(f"MODIFIED ***  '{event.src_path}'")
            with mutex:
                shouldUpdate = True
                signal.notify()
        else:
            plugin.Trace(f"Ignoring modifications due to plugin UI setting. path='{event.src_path}'")

    def on_moved(event):
        global shouldUpdate
        global TargetPaths
        TargetPaths.append(event.src_path)
        TargetPaths.append(event.dest_path)
        plugin.Log(f"MOVE ***  from '{event.src_path}' to '{event.dest_path}'")
        with mutex:
            shouldUpdate = True
            signal.notify()
    
    def on_any_event(event):
        global shouldUpdate
        global TargetPaths
        if SCAN_ON_ANY_EVENT:
            plugin.Log(f"Any-Event ***  '{event.src_path}'")
            TargetPaths.append(event.src_path)
            with mutex:
                shouldUpdate = True
                signal.notify()
        else:
            plugin.Trace("Ignoring on_any_event trigger.")
    
    plugin.Trace()
    event_handler.on_created = on_created
    event_handler.on_deleted = on_deleted
    event_handler.on_modified = on_modified
    event_handler.on_moved = on_moved
    event_handler.on_any_event = on_any_event
    
    observer = Observer()
    
    # Iterate through stashPaths
    for path in stashPaths:
        observer.schedule(event_handler, path, recursive=RECURSIVE)
        plugin.Trace(f"Observing {path}")
    observer.start()
    JobIsRunning = False
    PutPluginBackOnTaskQueAndExit = False
    plugin.Trace("Starting loop")
    try:
        while True:
            TmpTargetPaths = []
            with mutex:
                while not shouldUpdate:
                    plugin.Trace("Wait start")
                    if plugin.CALLED_AS_STASH_PLUGIN:
                        signal.wait(timeout=SIGNAL_TIMEOUT)
                    else:
                        signal.wait()
                    plugin.Trace("Wait end")
                    if shm_buffer[0] != CONTINUE_RUNNING_SIG:
                        plugin.Log(f"Breaking out of loop. (shm_buffer[0]={shm_buffer[0]})")
                        break
                    JobIdInTheQue = isJobWaitingToRun()
                    if plugin.CALLED_AS_STASH_PLUGIN and JobIdInTheQue:
                        plugin.Log(f"Another task (JobID={JobIdInTheQue}) is waiting on the queue. Will restart FileMonitor to allow other task to run.")
                        JobIsRunning = True
                        shouldUpdate = True
                shouldUpdate = False
                TmpTargetPaths = []
                for TargetPath in TargetPaths:
                    TmpTargetPaths.append(os.path.dirname(TargetPath))
                    if TargetPath == SPECIAL_FILE_DIR:
                        if os.path.isfile(SPECIAL_FILE_NAME):
                            shm_buffer[0] = STOP_RUNNING_SIG
                            plugin.Log(f"Detected trigger file to kill FileMonitor. {SPECIAL_FILE_NAME}", printTo = plugin.LOG_TO_FILE + plugin.LOG_TO_CONSOLE + plugin.LOG_TO_STASH)
                TargetPaths = []
                TmpTargetPaths = list(set(TmpTargetPaths))
            if TmpTargetPaths != []:
                plugin.Log(f"Triggering Stash scan for path(s) {TmpTargetPaths}")
                if len(TmpTargetPaths) > 1 or TmpTargetPaths[0] != SPECIAL_FILE_DIR:
                    if not plugin.DRY_RUN:
                        plugin.STASH_INTERFACE.metadata_scan(paths=TmpTargetPaths)
                    if RUN_CLEAN_AFTER_DELETE and RunCleanMetadata:
                        plugin.STASH_INTERFACE.metadata_clean(paths=TmpTargetPaths, dry_run=plugin.DRY_RUN)
                    if RUN_GENERATE_CONTENT:
                        plugin.STASH_INTERFACE.metadata_generate()
                if plugin.CALLED_AS_STASH_PLUGIN and shm_buffer[0] == CONTINUE_RUNNING_SIG:
                    PutPluginBackOnTaskQueAndExit = True
            else:
                plugin.Trace("Nothing to scan.")
            
            if shm_buffer[0] != CONTINUE_RUNNING_SIG or StopLibraryMonitorWaitingInTaskQueue:               
                plugin.Log(f"Exiting Change File Monitor. (shm_buffer[0]={shm_buffer[0]}) (StopLibraryMonitorWaitingInTaskQueue={StopLibraryMonitorWaitingInTaskQueue})")
                shm_a.close()
                shm_a.unlink()  # Call unlink only once to release the shared memory
                raise KeyboardInterrupt
            elif JobIsRunning or PutPluginBackOnTaskQueAndExit:
                plugin.STASH_INTERFACE.run_plugin_task(plugin_id=plugin.PLUGIN_ID, task_name="Start Library Monitor")
                plugin.Trace("Exiting plugin so that other task can run.")
                return
    except KeyboardInterrupt:
        observer.stop()
        plugin.Trace("Stopping observer")
        if os.path.isfile(SPECIAL_FILE_NAME):
            os.remove(SPECIAL_FILE_NAME)
    observer.join()
    plugin.Trace("Exiting function")

# This function is only useful when called outside of Stash. 
#       Example: python filemonitor.py --stop
def stop_library_monitor():
    if CREATE_SPECIAL_FILE_TO_EXIT:
        if os.path.isfile(SPECIAL_FILE_NAME):
            os.remove(SPECIAL_FILE_NAME)
        pathlib.Path(SPECIAL_FILE_NAME).touch()
        if DELETE_SPECIAL_FILE_ON_STOP:
            os.remove(SPECIAL_FILE_NAME)
    plugin.Trace("Opening shared memory map.")
    try:
        shm_a = shared_memory.SharedMemory(name="DavidMaisonaveAxter_FileMonitor", create=False, size=4)
    except:
        pass
        plugin.Log("Could not open shared memory map. Change File Monitor must not be running.")
        return
    type(shm_a.buf)
    shm_buffer = shm_a.buf
    len(shm_buffer)
    shm_buffer[0] = STOP_RUNNING_SIG
    plugin.Trace(f"Shared memory map opended, and flag set to {shm_buffer[0]}")
    shm_a.close()
    shm_a.unlink()  # Call unlink only once to release the shared memory
    return
    
if parse_args.stop or parse_args.restart or plugin.PLUGIN_TASK_NAME == "stop_library_monitor":
    stop_library_monitor()
    if parse_args.restart:
        time.sleep(5)
        plugin.STASH_INTERFACE.run_plugin_task(plugin_id=plugin.PLUGIN_ID, task_name="Start Library Monitor")
        plugin.Trace(f"Restart FileMonitor EXIT")
    else:
        plugin.Trace(f"Stop FileMonitor EXIT")
elif plugin.PLUGIN_TASK_NAME == "start_library_monitor" or not plugin.CALLED_AS_STASH_PLUGIN:
    start_library_monitor()
    plugin.Trace(f"start_library_monitor EXIT")
else:
    plugin.Log(f"Nothing to do!!! (plugin.PLUGIN_TASK_NAME={plugin.PLUGIN_TASK_NAME})")

plugin.Trace("\n*********************************\nEXITING   ***********************\n*********************************")

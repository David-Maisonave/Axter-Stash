# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager
# Note: To call this script outside of Stash, pass any argument. 
#       Example:    python DupFileManager.py start

# Research:
#   Research following links to complete this plugin:
#       https://github.com/WithoutPants/stash-plugin-duplicate-finder
# Look at stash API find_duplicate_scenes
import os
import sys
import time
import shutil
import fileinput
import hashlib
import json
from pathlib import Path
import requests
import logging
from logging.handlers import RotatingFileHandler
import stashapi.log as log # Importing stashapi.log as log for critical events ONLY
from stashapi.stashapp import StashInterface
from DupFileManager_config import config # Import config from DupFileManager_config.py

# **********************************************************************
# Constant global variables --------------------------------------------
LOG_FILE_PATH = log_file_path = f"{Path(__file__).resolve().parent}\\{Path(__file__).stem}.log" 
FORMAT = "[%(asctime)s - LN:%(lineno)s] %(message)s"
PLUGIN_ARGS_MODE = False
PLUGIN_ID = Path(__file__).stem

RFH = RotatingFileHandler(
    filename=LOG_FILE_PATH, 
    mode='a',
    maxBytes=2*1024*1024, # Configure logging for this script with max log file size of 2000K
    backupCount=2,
    encoding=None,
    delay=0
)
TIMEOUT = 5
CONTINUE_RUNNING_SIG = 99

# **********************************************************************
# Global variables          --------------------------------------------
exitMsg = "Change success!!"
runningInPluginMode = False

# Configure local log file for plugin within plugin folder having a limited max log file size 
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%y%m%d %H:%M:%S", handlers=[RFH])
logger = logging.getLogger(Path(__file__).stem)
    
# **********************************************************************
# ----------------------------------------------------------------------
# Code section to fetch variables from Plugin UI and from DupFileManager_settings.py
# Check if being called as Stash plugin
gettingCalledAsStashPlugin = True
mangeDupFilesTask = True
StdInRead = None
try:
    if len(sys.argv) == 1:
        print(f"Attempting to read stdin. (len(sys.argv)={len(sys.argv)})", file=sys.stderr)
        StdInRead = sys.stdin.read()
        # for line in fileinput.input():
            # StdInRead = line
            # break
    else:
        raise Exception("Not called in plugin mode.") 
except:
    gettingCalledAsStashPlugin = False
    print(f"Either len(sys.argv) not expected value OR sys.stdin.read() failed! (StdInRead={StdInRead}) (len(sys.argv)={len(sys.argv)})", file=sys.stderr)
    pass
    
if gettingCalledAsStashPlugin and StdInRead:
    print(f"StdInRead={StdInRead} (len(sys.argv)={len(sys.argv)})", file=sys.stderr)
    runningInPluginMode = True
    json_input = json.loads(StdInRead)
    FRAGMENT_SERVER = json_input["server_connection"]
else:
    runningInPluginMode = False
    FRAGMENT_SERVER = {'Scheme': config['endpoint_Scheme'], 'Host': config['endpoint_Host'], 'Port': config['endpoint_Port'], 'SessionCookie': {'Name': 'session', 'Value': '', 'Path': '', 'Domain': '', 'Expires': '0001-01-01T00:00:00Z', 'RawExpires': '', 'MaxAge': 0, 'Secure': False, 'HttpOnly': False, 'SameSite': 0, 'Raw': '', 'Unparsed': None}, 'Dir': os.path.dirname(Path(__file__).resolve().parent), 'PluginDir': Path(__file__).resolve().parent}
    print("Running in non-plugin mode!", file=sys.stderr)

stash = StashInterface(FRAGMENT_SERVER)
PLUGINCONFIGURATION = stash.get_configuration()["plugins"]
STASHCONFIGURATION = stash.get_configuration()["general"]
STASHPATHSCONFIG = STASHCONFIGURATION['stashes']
stashPaths = []
settings = {
    "ignoreReparsepoints": True,
    "ignoreSymbolicLinks": True,
    "mergeDupFilename": True,
    "moveToTrashCan": False,
    "zzdebugTracing": False,
    "zzdryRun": False,
}
CanUpdatePluginConfigSettings = False
try:
    plugins_configuration = stash.find_plugins_config()
    CanUpdatePluginConfigSettings = True
except Exception as e:
    logger.exception('Got exception on main handler')
    logger.error('This exception most likely occurred because stashapp-tools needs to be upgraded. To fix this error, run the following command:\npip install --upgrade stashapp-tools')
    pass

if PLUGIN_ID in PLUGINCONFIGURATION and (not CanUpdatePluginConfigSettings or 'INITIAL_VALUES_SET1' in PLUGINCONFIGURATION[PLUGIN_ID]):
    settings.update(PLUGINCONFIGURATION[PLUGIN_ID])
# ----------------------------------------------------------------------
debugTracing = settings["zzdebugTracing"]
debugTracing = True


for item in STASHPATHSCONFIG: 
    stashPaths.append(item["path"])

# Extract dry_run setting from settings
DRY_RUN = settings["zzdryRun"]
dry_run_prefix = ''
try:
    PLUGIN_ARGS_MODE    = json_input['args']["mode"]
except:
    pass
logger.info(f"\nStarting (runningInPluginMode={runningInPluginMode}) (debugTracing={debugTracing}) (DRY_RUN={DRY_RUN}) (PLUGIN_ARGS_MODE={PLUGIN_ARGS_MODE}) (stash.stash_version()={stash.stash_version()})************************************************")
if debugTracing: logger.info(f"Debug Tracing (stash.get_configuration()={stash.get_configuration()})")
if debugTracing: logger.info("settings: %s " % (settings,))
if debugTracing: logger.info(f"Debug Tracing (STASHCONFIGURATION={STASHCONFIGURATION})")
if debugTracing: logger.info(f"Debug Tracing (stashPaths={stashPaths})")
if debugTracing: logger.info(f"Debug Tracing (PLUGIN_ID={PLUGIN_ID})")
if debugTracing: logger.info(f"Debug Tracing (PLUGINCONFIGURATION={PLUGINCONFIGURATION})")

if PLUGIN_ID in PLUGINCONFIGURATION:
    if 'INITIAL_VALUES_SET1' not in PLUGINCONFIGURATION[PLUGIN_ID]:
        if debugTracing: logger.info(f"Initializing plugin ({PLUGIN_ID}) settings (PLUGINCONFIGURATION[PLUGIN_ID]={PLUGINCONFIGURATION[PLUGIN_ID]})")
        try:
            plugins_configuration = stash.find_plugins_config()
            if debugTracing: logger.info(f"Debug Tracing (plugins_configuration={plugins_configuration})")
            stash.configure_plugin(PLUGIN_ID, {"INITIAL_VALUES_SET1": True})
            logger.info('Called stash.configure_plugin(PLUGIN_ID, {"INITIAL_VALUES_SET1": True})')
            plugins_configuration = stash.find_plugins_config()
            if debugTracing: logger.info(f"Debug Tracing (plugins_configuration={plugins_configuration})")
            stash.configure_plugin(PLUGIN_ID, settings)
            logger.info('Called stash.configure_plugin(PLUGIN_ID, settings)')
            plugins_configuration = stash.find_plugins_config()
            if debugTracing: logger.info(f"Debug Tracing (plugins_configuration={plugins_configuration})")
        except Exception as e:
            logger.exception('Got exception on main handler')
            try:
                if debugTracing: logger.info("Debug Tracing................") 
                stash.configure_plugin(plugin_id=PLUGIN_ID, values=[{"zzdebugTracing": False}], init_defaults=True)
                if debugTracing: logger.info("Debug Tracing................") 
            except Exception as e:
                logger.exception('Got exception on main handler')
                pass
            pass
        # stash.configure_plugin(PLUGIN_ID, settings) # , init_defaults=True
    if debugTracing: logger.info("Debug Tracing................")    

if DRY_RUN:
    logger.info("Dry run mode is enabled.")
    dry_run_prefix = "Would've "
if debugTracing: logger.info("Debug Tracing................")
# ----------------------------------------------------------------------
# **********************************************************************

def realpath(path):
    """
    get_symbolic_target for win
    """
    try:
        import win32file
        f = win32file.CreateFile(path, win32file.GENERIC_READ,
                                 win32file.FILE_SHARE_READ, None,
                                 win32file.OPEN_EXISTING,
                                 win32file.FILE_FLAG_BACKUP_SEMANTICS, None)
        target = win32file.GetFinalPathNameByHandle(f, 0)
        # an above gives us something like u'\\\\?\\C:\\tmp\\scalarizr\\3.3.0.7978'
        return target.strip('\\\\?\\')
    except ImportError:
        handle = open_dir(path)
        target = get_symbolic_target(handle)
        check_closed(handle)
        return target

def isReparsePoint(path):
    import win32api
    import win32con
    FinalPathname = realpath(path)
    logger.info(f"(path='{path}') (FinalPathname='{FinalPathname}')")
    if FinalPathname != path:
        logger.info(f"Symbolic link '{path}'")
        return True
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    return win32api.GetFileAttributes(path) & win32con.FILE_ATTRIBUTE_REPARSE_POINT

def mangeDupFiles():
    import platform
    if debugTracing: logger.info(f"Debug Tracing (platform.system()={platform.system()})")
    myTestPath1 = r"B:\V\V\Tip\POV - Holly Molly petite ginger anal slut - RedTube.mp4" # not a reparse point or symbolic link
    myTestPath2 = r"B:\_\SpecialSet\Amateur Anal Attempts\BRCC test studio name.m2ts" # reparse point
    myTestPath3 = r"B:\_\SpecialSet\Amateur Anal Attempts\Amateur Anal Attempts 4.mp4" #symbolic link
    myTestPath4 = r"E:\Stash\plugins\RenameFile\README.md" #symbolic link
    myTestPath5 = r"E:\_\David-Maisonave\Axter-Stash\plugins\RenameFile\README.md" #symbolic link
    myTestPath6 = r"E:\_\David-Maisonave\Axter-Stash\plugins\DeleteMe\Renamer\README.md" # not reparse point
    logger.info(f"Testing '{myTestPath1}'")
    if isReparsePoint(myTestPath1):
        logger.info(f"isSymLink '{myTestPath1}'")
    else:
        logger.info(f"Not isSymLink '{myTestPath1}'")
        
    if isReparsePoint(myTestPath2):
        logger.info(f"isSymLink '{myTestPath2}'")
    else:
        logger.info(f"Not isSymLink '{myTestPath2}'")
        
    if isReparsePoint(myTestPath3):
        logger.info(f"isSymLink '{myTestPath3}'")
    else:
        logger.info(f"Not isSymLink '{myTestPath3}'")
        
    if isReparsePoint(myTestPath4):
        logger.info(f"isSymLink '{myTestPath4}'")
    else:
        logger.info(f"Not isSymLink '{myTestPath4}'")
        
    if isReparsePoint(myTestPath5):
        logger.info(f"isSymLink '{myTestPath5}'")
    else:
        logger.info(f"Not isSymLink '{myTestPath5}'")
        
    if isReparsePoint(myTestPath6):
        logger.info(f"isSymLink '{myTestPath6}'")
    else:
        logger.info(f"Not isSymLink '{myTestPath6}'")
    return

if mangeDupFilesTask:
    mangeDupFiles()
    if debugTracing: logger.info(f"stop_library_monitor EXIT................")
else:
    logger.info(f"Nothing to do!!! (PLUGIN_ARGS_MODE={PLUGIN_ARGS_MODE})")

if debugTracing: logger.info("\n*********************************\nEXITING   ***********************\n*********************************")

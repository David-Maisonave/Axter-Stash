# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager
# Note: To call this script outside of Stash, pass any argument. 
#       Example:    python DupFileManager.py start

# Research:
#   Research following links to complete this plugin:
#       https://github.com/WithoutPants/stash-plugin-duplicate-finder
#
#       Look at options in programs from the following link:
#       https://video.stackexchange.com/questions/25302/how-can-i-find-duplicate-videos-by-content
#
#       Python library for parse-reparsepoint
#       https://pypi.org/project/parse-reparsepoint/
#       pip install parse-reparsepoint
#
# Look at stash API find_duplicate_scenes
import os, sys, time, pathlib, argparse, platform
from StashPluginHelper import StashPluginHelper
from DupFileManager_config import config # Import config from DupFileManager_config.py

parser = argparse.ArgumentParser()
parser.add_argument('--url', '-u', dest='stash_url', type=str, help='Add Stash URL')
parser.add_argument('--trace', '-t', dest='trace', action='store_true', help='Enables debug trace mode.')
parser.add_argument('--remove_dup', '-r', dest='remove', action='store_true', help='Remove (delete) duplicate files.')
parser.add_argument('--dryrun', '-d', dest='dryrun', action='store_true', help='Do dryrun for deleting duplicate files. No files are deleted, and only logging occurs.')
parse_args = parser.parse_args()

settings = {
    "mergeDupFilename": True,
    "moveToTrashCan": False,
    "whitelist": [],
    "zzdebugTracing": False,
    "zzdryRun": False,
}
stash = StashPluginHelper(
        stash_url=parse_args.stash_url,
        debugTracing=parse_args.trace,
        settings=settings,
        config=config
        )
stash.Status()
stash.Log(f"\nStarting (__file__={__file__}) (stash.CALLED_AS_STASH_PLUGIN={stash.CALLED_AS_STASH_PLUGIN}) (stash.DEBUG_TRACING={stash.DEBUG_TRACING}) (stash.DRY_RUN={stash.DRY_RUN}) (stash.PLUGIN_TASK_NAME={stash.PLUGIN_TASK_NAME})************************************************")

stash.Trace(f"(stashPaths={stash.STASH_PATHS})")

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
    from parse_reparsepoint import Navigator
    FinalPathname = realpath(path)
    stash.Log(f"(path='{path}') (FinalPathname='{FinalPathname}')")
    if FinalPathname != path:
        stash.Log(f"Symbolic link '{path}'")
        return True
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    return win32api.GetFileAttributes(path) & win32con.FILE_ATTRIBUTE_REPARSE_POINT

def mangeDupFiles(merge=False, deleteDup=False, DryRun=False):
    stash.Trace(f"Debug Tracing (platform.system()={platform.system()})")
    myTestPath1 = r"B:\V\V\Tip\POV - Holly Molly petite ginger anal slut - RedTube.mp4" # not a reparse point or symbolic link
    myTestPath2 = r"B:\_\SpecialSet\Amateur Anal Attempts\BRCC test studio name.m2ts" # reparse point
    myTestPath3 = r"B:\_\SpecialSet\Amateur Anal Attempts\Amateur Anal Attempts 4.mp4" #symbolic link
    myTestPath4 = r"E:\Stash\plugins\RenameFile\README.md" #symbolic link
    myTestPath5 = r"E:\_\David-Maisonave\Axter-Stash\plugins\RenameFile\README.md" #symbolic link
    myTestPath6 = r"E:\_\David-Maisonave\Axter-Stash\plugins\DeleteMe\Renamer\README.md" # not reparse point
    stash.Log(f"Testing '{myTestPath1}'")
    if isReparsePoint(myTestPath1):
        stash.Log(f"isSymLink '{myTestPath1}'")
    else:
        stash.Log(f"Not isSymLink '{myTestPath1}'")
        
    if isReparsePoint(myTestPath2):
        stash.Log(f"isSymLink '{myTestPath2}'")
    else:
        stash.Log(f"Not isSymLink '{myTestPath2}'")
        
    if isReparsePoint(myTestPath3):
        stash.Log(f"isSymLink '{myTestPath3}'")
    else:
        stash.Log(f"Not isSymLink '{myTestPath3}'")
        
    if isReparsePoint(myTestPath4):
        stash.Log(f"isSymLink '{myTestPath4}'")
    else:
        stash.Log(f"Not isSymLink '{myTestPath4}'")
        
    if isReparsePoint(myTestPath5):
        stash.Log(f"isSymLink '{myTestPath5}'")
    else:
        stash.Log(f"Not isSymLink '{myTestPath5}'")
        
    if isReparsePoint(myTestPath6):
        stash.Log(f"isSymLink '{myTestPath6}'")
    else:
        stash.Log(f"Not isSymLink '{myTestPath6}'")
    return

if stash.PLUGIN_TASK_NAME == "merge_dup_filename_task":
    mangeDupFiles(merge=True)
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif stash.PLUGIN_TASK_NAME == "delete_duplicates":
    mangeDupFiles(deleteDup=True)
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif stash.PLUGIN_TASK_NAME == "dryrun_delete_duplicates":
    mangeDupFiles(deleteDup=True, DryRun=True)
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif parse_args.remove:
    mangeDupFiles(deleteDup=True, DryRun=parse_args.dryrun)
    stash.Trace(f"Delete duplicate (DryRun={parse_args.dryrun}) EXIT")
elif parse_args.dryrun:
    mangeDupFiles(deleteDup=True, DryRun=parse_args.dryrun)
    stash.Trace(f"Dryrun delete duplicate EXIT")
else:
    stash.Log(f"Nothing to do!!! (PLUGIN_ARGS_MODE={PLUGIN_ARGS_MODE})")

stash.Trace("\n*********************************\nEXITING   ***********************\n*********************************")

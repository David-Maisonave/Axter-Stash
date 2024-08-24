# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager
# Note: To call this script outside of Stash, pass argument --url 
#       Example:    python DupFileManager.py --url http://localhost:9999 -a

# Research:
#   Research following links to complete this plugin:
#       Python library for parse-reparsepoint
#       https://pypi.org/project/parse-reparsepoint/
#       pip install parse-reparsepoint
import os, sys, time, pathlib, argparse, platform, shutil
from StashPluginHelper import StashPluginHelper
from DupFileManager_config import config # Import config from DupFileManager_config.py

parser = argparse.ArgumentParser()
parser.add_argument('--url', '-u', dest='stash_url', type=str, help='Add Stash URL')
parser.add_argument('--trace', '-t', dest='trace', action='store_true', help='Enables debug trace mode.')
parser.add_argument('--remove_dup', '-r', dest='remove', action='store_true', help='Remove (delete) duplicate files.')
parser.add_argument('--add_dup_tag', '-a', dest='dup_tag', action='store_true', help='Set a tag to duplicate files.')
parse_args = parser.parse_args()

settings = {
    "dupWhiteListTag": "",
    "dupFileTag": "DuplicateMarkForDeletion",
    "dupFileTagSwap": "DuplicateMarkForSwap",
    "mergeDupFilename": False,
    "permanentlyDelete": False,
    "whitelistDelDupInSameFolder": False,
    "zcleanAfterDel": False,
    "zwhitelist": "",
    "zxgraylist": "",
    "zyblacklist": "",
    "zymaxDupToProcess": 0,
    "zzdebugTracing": False,
}
stash = StashPluginHelper(
        stash_url=parse_args.stash_url,
        debugTracing=parse_args.trace,
        settings=settings,
        config=config,
        maxbytes=100*1024*1024,
        )
stash.Status()
stash.Log(f"\nStarting (__file__={__file__}) (stash.CALLED_AS_STASH_PLUGIN={stash.CALLED_AS_STASH_PLUGIN}) (stash.DEBUG_TRACING={stash.DEBUG_TRACING}) (stash.PLUGIN_TASK_NAME={stash.PLUGIN_TASK_NAME})************************************************")

stash.Trace(f"(stashPaths={stash.STASH_PATHS})")
# stash.encodeToUtf8 = True

listSeparator               = stash.Setting('listSeparator', ',', notEmpty=True)
addPrimaryDupPathToDetails  = stash.Setting('addPrimaryDupPathToDetails') 
mergeDupFilename            = stash.Setting('mergeDupFilename')
moveToTrashCan              = False if stash.Setting('permanentlyDelete') else True
alternateTrashCanPath       = stash.Setting('dup_path')
whitelistDelDupInSameFolder = stash.Setting('whitelistDelDupInSameFolder')
maxDupToProcess             = int(stash.Setting('zymaxDupToProcess'))
swapHighRes                 = stash.Setting('swapHighRes')
swapLongLength              = stash.Setting('swapLongLength')
significantTimeDiff         = stash.Setting('significantTimeDiff')
toRecycleBeforeSwap         = stash.Setting('toRecycleBeforeSwap')
cleanAfterDel               = stash.Setting('zcleanAfterDel')

duplicateMarkForDeletion = stash.Setting('dupFileTag')
if duplicateMarkForDeletion == "":
    duplicateMarkForDeletion = 'DuplicateMarkForDeletion'
    
DuplicateMarkForSwap = stash.Setting('dupFileTagSwap')
if DuplicateMarkForSwap == "":
    DuplicateMarkForSwap = 'DuplicateMarkForSwap'

duplicateWhitelistTag = stash.Setting('dupWhiteListTag')

excludeMergeTags = [duplicateMarkForDeletion, DuplicateMarkForSwap]
if duplicateWhitelistTag != "":
    excludeMergeTags += [duplicateWhitelistTag]
stash.init_mergeMetadata(excludeMergeTags)

graylist = stash.Setting('zxgraylist').split(listSeparator)
graylist = [item.lower() for item in graylist]
if graylist == [""] : graylist = []
stash.Log(f"graylist = {graylist}")   
whitelist = stash.Setting('zwhitelist').split(listSeparator)
whitelist = [item.lower() for item in whitelist]
if whitelist == [""] : whitelist = []
stash.Log(f"whitelist = {whitelist}")   
blacklist = stash.Setting('zyblacklist').split(listSeparator)
blacklist = [item.lower() for item in blacklist]
if blacklist == [""] : blacklist = []
stash.Log(f"blacklist = {blacklist}")
    
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

def testReparsePointAndSymLink(merge=False, deleteDup=False):
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


def createTagId(tagName, tagName_descp, deleteIfExist = False):
    tagId = stash.find_tags(q=tagName)
    if len(tagId):
        tagId = tagId[0]
        if deleteIfExist:
            stash.destroy_tag(int(tagId['id']))
        else:
            return tagId['id']
    tagId = stash.create_tag({"name":tagName, "description":tagName_descp, "ignore_auto_tag": True})
    stash.Log(f"Dup-tagId={tagId['id']}")
    return tagId['id']

def setTagId(tagId, tagName, sceneDetails, PrimeDuplicateScene = ""):
    if PrimeDuplicateScene != "" and addPrimaryDupPathToDetails:
        BaseDupStr = f"BaseDup={PrimeDuplicateScene}"
        if sceneDetails['details'].startswith(BaseDupStr) or sceneDetails['details'].startswith(f"Primary Duplicate = {PrimeDuplicateScene}"):
            PrimeDuplicateScene = ""
        elif sceneDetails['details'] == "":
            PrimeDuplicateScene = BaseDupStr
        else:
            PrimeDuplicateScene = f"{BaseDupStr};\n{sceneDetails['details']}"
    for tag in sceneDetails['tags']:
        if tag['name'] == tagName:
            if PrimeDuplicateScene != "" and addPrimaryDupPathToDetails:
                stash.update_scene({'id' : sceneDetails['id'], 'details' : PrimeDuplicateScene})
            return
    
    if PrimeDuplicateScene == "" or not addPrimaryDupPathToDetails:
        stash.update_scene({'id' : sceneDetails['id'], 'tag_ids' : tagId})
    else:
        stash.update_scene({'id' : sceneDetails['id'], 'tag_ids' : tagId, 'details' : PrimeDuplicateScene})

def isInList(listToCk, pathToCk):
    pathToCk = pathToCk.lower()
    for item in listToCk:
        if pathToCk.startswith(item):
            return True
    return False

def hasSameDir(path1, path2):
    if pathlib.Path(path1).resolve().parent == pathlib.Path(path2).resolve().parent:
        return True
    return False

def sendToTrash(path):
    if not os.path.isfile(path):
        stash.Warn(f"File does not exist: {path}.", toAscii=True)
        return False
    try:
        from send2trash import send2trash # Requirement: pip install Send2Trash
        send2trash(path)
        return True
    except Exception as e:
        stash.Error(f"Failed to send file {path} to recycle bin. Error: {e}", toAscii=True)
        try:
            if os.path.isfile(path):
                os.remove(path)
                return True
        except Exception as e:
            stash.Error(f"Failed to delete file {path}. Error: {e}", toAscii=True)
    return False

def significantLessTime(durrationToKeep, durrationOther):
    timeDiff = durrationToKeep / durrationOther
    if timeDiff < significantTimeDiff:
        return True
    return False

def isBetter(DupFileToKeep, DupFile):
    # Don't move if both are in whitelist
    if isInList(whitelist, DupFileToKeep['files'][0]['path']) and isInList(whitelist, DupFile['files'][0]['path']):
        return False
    if swapHighRes and (int(DupFileToKeep['files'][0]['width']) > int(DupFile['files'][0]['width']) or int(DupFileToKeep['files'][0]['height']) > int(DupFile['files'][0]['height'])):
        if not significantLessTime(int(DupFileToKeep['files'][0]['duration']), int(DupFile['files'][0]['duration'])):
            return True
    if swapLongLength and int(DupFileToKeep['files'][0]['duration']) > int(DupFile['files'][0]['duration']):
        if int(DupFileToKeep['files'][0]['width']) >= int(DupFile['files'][0]['width']) or int(DupFileToKeep['files'][0]['height']) >= int(DupFile['files'][0]['height']):
            return True
    return False

def mangeDupFiles(merge=False, deleteDup=False, tagDuplicates=False):
    duration_diff = 10.00
    duplicateMarkForDeletion_descp = 'Tag added to duplicate scenes so-as to tag them for deletion.'
    stash.Log(f"duplicateMarkForDeletion = {duplicateMarkForDeletion}")    
    dupTagId = createTagId(duplicateMarkForDeletion, duplicateMarkForDeletion_descp)
    stash.Trace(f"dupTagId={dupTagId} name={duplicateMarkForDeletion}")
    
    dupWhitelistTagId = None
    if duplicateWhitelistTag != "":
        stash.Log(f"duplicateWhitelistTag = {duplicateWhitelistTag}")    
        duplicateWhitelistTag_descp = 'Tag added to duplicate scenes which are in the whitelist. This means there are two or more duplicates in the whitelist.'
        dupWhitelistTagId = createTagId(duplicateWhitelistTag, duplicateWhitelistTag_descp)
        stash.Trace(f"dupWhitelistTagId={dupWhitelistTagId} name={duplicateWhitelistTag}")
    
    QtyDupSet = 0
    QtyDup = 0
    QtyExactDup = 0
    QtyAlmostDup = 0
    QtyRealTimeDiff = 0
    QtyTagForDel = 0
    QtySkipForDel = 0
    QtySwap = 0
    QtyMerge = 0
    QtyDeleted = 0
    stash.Log("#########################################################################")
    stash.Log("#########################################################################")
    stash.Log("Waiting for find_duplicate_scenes_diff to return results...")
    DupFileSets = stash.find_duplicate_scenes_diff(duration_diff=duration_diff)
    stash.Log("#########################################################################")
    for DupFileSet in DupFileSets:
        stash.Trace(f"DupFileSet={DupFileSet}")
        QtyDupSet+=1
        SepLine = "---------------------------"
        DupFileToKeep = ""
        DupToCopyFrom = ""
        DupFileDetailList = []
        for DupFile in DupFileSet:
            QtyDup+=1
            Scene = stash.find_scene(DupFile['id'])
            sceneData = f"Scene = {Scene}"
            stash.Trace(sceneData, toAscii=True)
            DupFileDetailList = DupFileDetailList + [Scene]
            if DupFileToKeep != "":
                if int(DupFileToKeep['files'][0]['duration']) == int(Scene['files'][0]['duration']): # Do not count fractions of a second as a difference
                    QtyExactDup+=1
                else:
                    QtyAlmostDup+=1
                    SepLine = "***************************"
                    if significantLessTime(int(DupFileToKeep['files'][0]['duration']), int(Scene['files'][0]['duration'])):
                        QtyRealTimeDiff += 1
                if int(DupFileToKeep['files'][0]['width']) < int(Scene['files'][0]['width']) or int(DupFileToKeep['files'][0]['height']) < int(Scene['files'][0]['height']):
                    DupFileToKeep = Scene
                elif int(DupFileToKeep['files'][0]['duration']) < int(Scene['files'][0]['duration']):
                    DupFileToKeep = Scene
                elif isInList(whitelist, Scene['files'][0]['path']) and not isInList(whitelist, DupFileToKeep['files'][0]['path']):
                    DupFileToKeep = Scene
                elif isInList(blacklist, DupFileToKeep['files'][0]['path']) and not isInList(blacklist, Scene['files'][0]['path']):
                    DupFileToKeep = Scene
                elif isInList(graylist, Scene['files'][0]['path']) and not isInList(graylist, DupFileToKeep['files'][0]['path']):
                    DupFileToKeep = Scene
                elif len(DupFileToKeep['files'][0]['path']) < len(Scene['files'][0]['path']):
                    DupFileToKeep = Scene
                elif int(DupFileToKeep['files'][0]['size']) < int(Scene['files'][0]['size']):
                    DupFileToKeep = Scene
            else:
                DupFileToKeep = Scene
            # stash.Trace(f"DupFileToKeep = {DupFileToKeep}")
            stash.Trace(f"KeepID={DupFileToKeep['id']}, ID={DupFile['id']} duration=({Scene['files'][0]['duration']}), Size=({Scene['files'][0]['size']}), Res=({Scene['files'][0]['width']} x {Scene['files'][0]['height']}) Name={Scene['files'][0]['path']}, KeepPath={DupFileToKeep['files'][0]['path']}", toAscii=True)
        
        for DupFile in DupFileDetailList:
            if DupFile['id'] != DupFileToKeep['id']:
                if merge:
                    result = stash.merge_metadata(DupFile, DupFileToKeep)
                    if result != "Nothing To Merge":
                        QtyMerge += 1
                
                if isInList(whitelist, DupFile['files'][0]['path']) and (not whitelistDelDupInSameFolder or not hasSameDir(DupFile['files'][0]['path'], DupFileToKeep['files'][0]['path'])):
                    if isBetter(DupFileToKeep, DupFile):
                        if merge:
                            stash.merge_metadata(DupFileToKeep, DupFile)
                        if toRecycleBeforeSwap:
                            sendToTrash(DupFile['files'][0]['path'])
                        shutil.move(DupFileToKeep['files'][0]['path'], DupFile['files'][0]['path'])
                        stash.Log(f"Moved better file '{DupFileToKeep['files'][0]['path']}' to '{DupFile['files'][0]['path']}'", toAscii=True)
                        DupFileToKeep = DupFile
                        QtySwap+=1
                    else:
                        stash.Log(f"NOT processing duplicate, because it's in whitelist. '{DupFile['files'][0]['path']}'", toAscii=True)
                        if dupWhitelistTagId and tagDuplicates:
                            setTagId(dupWhitelistTagId, duplicateWhitelistTag, DupFile, DupFileToKeep['files'][0]['path'])
                    QtySkipForDel+=1
                else:
                    if deleteDup:
                        DupFileName = DupFile['files'][0]['path']
                        DupFileNameOnly = pathlib.Path(DupFileName).stem
                        stash.Log(f"Deleting duplicate '{DupFileName}'", toAscii=True)
                        if alternateTrashCanPath != "":
                            destPath = f"{alternateTrashCanPath }{os.sep}{DupFileNameOnly}"
                            if os.path.isfile(destPath):
                                destPath = f"{alternateTrashCanPath }{os.sep}_{time.time()}_{DupFileNameOnly}"
                            shutil.move(DupFileName, destPath)
                        elif moveToTrashCan:
                            sendToTrash(DupFileName)
                        stash.destroy_scene(DupFile['id'], delete_file=True)
                        QtyDeleted += 1
                    elif tagDuplicates:
                        if QtyTagForDel == 0:
                            stash.Log(f"Tagging duplicate {DupFile['files'][0]['path']} for deletion with tag {duplicateMarkForDeletion}.", toAscii=True)
                        else:
                            stash.Log(f"Tagging duplicate {DupFile['files'][0]['path']} for deletion.", toAscii=True)
                        setTagId(dupTagId, duplicateMarkForDeletion, DupFile, DupFileToKeep['files'][0]['path'])
                    QtyTagForDel+=1
        stash.Log(SepLine)
        if maxDupToProcess > 0 and QtyDup > maxDupToProcess:
            break
    
    stash.Log(f"QtyDupSet={QtyDupSet}, QtyDup={QtyDup}, QtyDeleted={QtyDeleted}, QtySwap={QtySwap}, QtyTagForDel={QtyTagForDel}, QtySkipForDel={QtySkipForDel}, QtyExactDup={QtyExactDup}, QtyAlmostDup={QtyAlmostDup}, QtyMerge={QtyMerge}, QtyRealTimeDiff={QtyRealTimeDiff}")
    if cleanAfterDel:
        stash.Log("Adding clean jobs to the Task Queue")
        stash.metadata_clean(paths=stash.STASH_PATHS)
        stash.metadata_clean_generated()
        stash.optimise_database()

def testSetDupTagOnScene(sceneId):
    scene = stash.find_scene(sceneId)
    stash.Log(f"scene={scene}")
    stash.Log(f"scene tags={scene['tags']}")
    tag_ids = [dupTagId]
    for tag in scene['tags']:
        tag_ids = tag_ids + [tag['id']]
    stash.Log(f"tag_ids={tag_ids}")
    stash.update_scene({'id' : scene['id'], 'tag_ids' : tag_ids})

if stash.PLUGIN_TASK_NAME == "merge_dup_filename_task":
    mangeDupFiles(merge=True)
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif stash.PLUGIN_TASK_NAME == "delete_duplicates":
    mangeDupFiles(deleteDup=True)
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif parse_args.dup_tag:
    mangeDupFiles(tagDuplicates=True, merge=mergeDupFilename)
    stash.Trace(f"Tag duplicate EXIT")
elif parse_args.remove:
    mangeDupFiles(deleteDup=True, merge=mergeDupFilename)
    stash.Trace(f"Delete duplicate EXIT")

else:
    stash.Log(f"Nothing to do!!! (PLUGIN_ARGS_MODE={stash.PLUGIN_TASK_NAME})")





stash.Trace("\n*********************************\nEXITING   ***********************\n*********************************")

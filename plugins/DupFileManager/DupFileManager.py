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
import os, sys, time, pathlib, argparse, platform
from StashPluginHelper import StashPluginHelper
from DupFileManager_config import config # Import config from DupFileManager_config.py

parser = argparse.ArgumentParser()
parser.add_argument('--url', '-u', dest='stash_url', type=str, help='Add Stash URL')
parser.add_argument('--trace', '-t', dest='trace', action='store_true', help='Enables debug trace mode.')
parser.add_argument('--remove_dup', '-r', dest='remove', action='store_true', help='Remove (delete) duplicate files.')
parser.add_argument('--add_dup_tag', '-a', dest='dup_tag', action='store_true', help='Set a tag to duplicate files.')
parse_args = parser.parse_args()

settings = {
    "mergeDupFilename": True,
    "moveToTrashCan": False,
    "dupFileTag": "DuplicateMarkForDeletion",
    "dupWhiteListTag": "",
    "zxgraylist": "",
    "zwhitelist": "",
    "zzblacklist": "",
    "zzdebugTracing": False,
}
stash = StashPluginHelper(
        stash_url=parse_args.stash_url,
        debugTracing=parse_args.trace,
        settings=settings,
        config=config
        )
stash.Status()
stash.Log(f"\nStarting (__file__={__file__}) (stash.CALLED_AS_STASH_PLUGIN={stash.CALLED_AS_STASH_PLUGIN}) (stash.DEBUG_TRACING={stash.DEBUG_TRACING}) (stash.PLUGIN_TASK_NAME={stash.PLUGIN_TASK_NAME})************************************************")

stash.Trace(f"(stashPaths={stash.STASH_PATHS})")

listSeparator = stash.pluginConfig['listSeparator'] if stash.pluginConfig['listSeparator'] != "" else ','
addPrimaryDupPathToDetails = stash.pluginConfig['addPrimaryDupPathToDetails'] 

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
        if sceneDetails['details'].startswith(f"Primary Duplicate = {PrimeDuplicateScene}"):
            PrimeDuplicateScene = ""
        elif sceneDetails['details'] == ""
            PrimeDuplicateScene = f"Primary Duplicate = {PrimeDuplicateScene}"
        else:
            PrimeDuplicateScene = f"Primary Duplicate = {PrimeDuplicateScene}; {sceneDetails['details']}"
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

def mangeDupFiles(merge=False, deleteDup=False, tagDuplicates=False):
    duration_diff = 10.00
    duplicateMarkForDeletion = stash.pluginSettings['dupFileTag']
    duplicateMarkForDeletion_descp = 'Tag added to duplicate scenes so-as to tag them for deletion.'
    if duplicateMarkForDeletion == "":
        duplicateMarkForDeletion = 'DuplicateMarkForDeletion'
    stash.Log(f"duplicateMarkForDeletion = {duplicateMarkForDeletion}")    
    dupTagId = createTagId(duplicateMarkForDeletion, duplicateMarkForDeletion_descp)
    stash.Trace(f"dupTagId={dupTagId} name={duplicateMarkForDeletion}")
    
    duplicateWhitelistTag = stash.pluginSettings['dupWhiteListTag']
    dupWhitelistTagId = None
    if duplicateWhitelistTag != "":
        stash.Log(f"duplicateWhitelistTag = {duplicateWhitelistTag}")    
        duplicateWhitelistTag_descp = 'Tag added to duplicate scenes which are in the whitelist. This means there are two or more duplicates in the whitelist.'
        dupWhitelistTagId = createTagId(duplicateWhitelistTag, duplicateWhitelistTag_descp)
        stash.Trace(f"dupWhitelistTagId={dupWhitelistTagId} name={duplicateWhitelistTag}")
    
    
    graylist = stash.pluginSettings['zxgraylist'].split(listSeparator)
    graylist = [item.lower() for item in graylist]
    if graylist == [""] : graylist = []
    stash.Log(f"graylist = {graylist}")   
    whitelist = stash.pluginSettings['zwhitelist'].split(listSeparator)
    whitelist = [item.lower() for item in whitelist]
    if whitelist == [""] : whitelist = []
    stash.Log(f"whitelist = {whitelist}")   
    blacklist = stash.pluginSettings['zzblacklist'].split(listSeparator)
    blacklist = [item.lower() for item in blacklist]
    if blacklist == [""] : blacklist = []
    stash.Log(f"blacklist = {blacklist}")
    
    QtyDupSet = 0
    QtyDup = 0
    QtyExactDup = 0
    QtyAlmostDup = 0
    QtyTagForDel = 0
    QtySkipForDel = 0
    stash.Log("Waiting for find_duplicate_scenes_diff to return results...")
    DupFileSets = stash.find_duplicate_scenes_diff(duration_diff=duration_diff)
    stash.Log("#########################################################################")
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
            stash.Trace(f"Scene = {Scene.encode('ascii','ignore')}")
            DupFileDetailList = DupFileDetailList + [Scene]
            if DupFileToKeep != "":
                if DupFileToKeep['files'][0]['duration'] == Scene['files'][0]['duration']:
                    QtyExactDup+=1
                else:
                    QtyAlmostDup+=1
                    SepLine = "***************************"
                if int(DupFileToKeep['files'][0]['width']) < int(Scene['files'][0]['width']) or int(DupFileToKeep['files'][0]['height']) < int(Scene['files'][0]['height']):
                    DupFileToKeep = Scene
                elif int(DupFileToKeep['files'][0]['duration']) < int(Scene['files'][0]['duration']):
                    DupFileToKeep = Scene
                elif int(DupFileToKeep['files'][0]['size']) < int(Scene['files'][0]['size']):
                    DupFileToKeep = Scene
                elif len(DupFileToKeep['files'][0]['path']) < len(Scene['files'][0]['path']):
                    DupFileToKeep = Scene
                elif isInList(whitelist, Scene['files'][0]['path']) and not isInList(whitelist, DupFileToKeep['files'][0]['path']):
                    DupFileToKeep = Scene
                elif isInList(blacklist, DupFileToKeep['files'][0]['path']) and not isInList(blacklist, Scene['files'][0]['path']):
                    DupFileToKeep = Scene
                elif isInList(graylist, Scene['files'][0]['path']) and not isInList(graylist, DupFileToKeep['files'][0]['path']):
                    DupFileToKeep = Scene
            else:
                DupFileToKeep = Scene
            # stash.Log(f"DupFileToKeep = {DupFileToKeep}")
            stash.Trace(f"KeepID={DupFileToKeep['id']}, ID={DupFile['id']} duration=({Scene['files'][0]['duration']}), Size=({Scene['files'][0]['size']}), Res=({Scene['files'][0]['width']} x {Scene['files'][0]['height']}) Name={Scene['files'][0]['path'].encode('ascii','ignore')}")
        
        for DupFile in DupFileDetailList:
            if DupFile['id'] != DupFileToKeep['id']:
                if isInList(whitelist, DupFile['files'][0]['path']):
                    stash.Log(f"NOT tagging duplicate, because it's in whitelist. '{DupFile['files'][0]['path'].encode('ascii','ignore')}'")
                    if dupWhitelistTagId and tagDuplicates:
                        setTagId(dupWhitelistTagId, duplicateWhitelistTag, DupFile, DupFileToKeep['files'][0]['path'])
                    QtySkipForDel+=1
                else:
                    if deleteDup:
                        stash.Log(f"Deleting duplicate '{DupFile['files'][0]['path'].encode('ascii','ignore')}'")
                        # ToDo: Add logic to check if moving file to deletion folder, or doing full delete.
                        # ToDo: Add logic to check if tag merging is needed before performing deletion.
                    elif tagDuplicates:
                        if QtyTagForDel == 0:
                            stash.Log(f"Tagging duplicate {DupFile['files'][0]['path'].encode('ascii','ignore')} for deletion with tag {duplicateMarkForDeletion}.")
                        else:
                            stash.Log(f"Tagging duplicate {DupFile['files'][0]['path'].encode('ascii','ignore')} for deletion.")
                        setTagId(dupTagId, duplicateMarkForDeletion, DupFile, DupFileToKeep['files'][0]['path'])
                    QtyTagForDel+=1
        stash.Log(SepLine)
        if QtyDup > 200:
            break
    
    stash.Log(f"QtyDupSet={QtyDupSet}, QtyDup={QtyDup}, QtyTagForDel={QtyTagForDel}, QtySkipForDel={QtySkipForDel}, QtyExactDup={QtyExactDup}, QtyAlmostDup={QtyAlmostDup}")

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
    mangeDupFiles(tagDuplicates=True)
    stash.Trace(f"Tag duplicate EXIT")
elif parse_args.remove:
    mangeDupFiles(deleteDup=True)
    stash.Trace(f"Delete duplicate EXIT")

else:
    stash.Log(f"Nothing to do!!! (PLUGIN_ARGS_MODE={stash.PLUGIN_TASK_NAME})")





stash.Trace("\n*********************************\nEXITING   ***********************\n*********************************")

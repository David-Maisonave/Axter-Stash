# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager
# Note: To call this script outside of Stash, pass argument --url 
#       Example:    python DupFileManager.py --url http://localhost:9999 -a
import os, sys, time, pathlib, argparse, platform, shutil, logging
from StashPluginHelper import StashPluginHelper
from stashapi.stash_types import PhashDistance
from DupFileManager_config import config # Import config from DupFileManager_config.py

parser = argparse.ArgumentParser()
parser.add_argument('--url', '-u', dest='stash_url', type=str, help='Add Stash URL')
parser.add_argument('--trace', '-t', dest='trace', action='store_true', help='Enables debug trace mode.')
parser.add_argument('--add_dup_tag', '-a', dest='dup_tag', action='store_true', help='Set a tag to duplicate files.')
parser.add_argument('--clear_dup_tag', '-c', dest='clear_tag', action='store_true', help='Clear duplicates of duplicate tags.')
parser.add_argument('--del_tag_dup', '-d', dest='del_tag', action='store_true', help='Only delete scenes having DuplicateMarkForDeletion tag.')
parser.add_argument('--remove_dup', '-r', dest='remove', action='store_true', help='Remove (delete) duplicate files.')
parse_args = parser.parse_args()

settings = {
    "doNotGeneratePhash": False,
    "mergeDupFilename": False,
    "permanentlyDelete": False,
    "whitelistDelDupInSameFolder": False,
    "whitelistDoTagLowResDup": False,
    "zCleanAfterDel": False,
    "zSwapHighRes": False,
    "zSwapLongLength": False,
    "zSwapBetterBitRate": False,
    "zSwapCodec": False,
    "zSwapBetterFrameRate": False,
    "zWhitelist": "",
    "zxGraylist": "",
    "zyBlacklist": "",
    "zyMatchDupDistance": 0,
    "zyMaxDupToProcess": 0,
    "zzdebugTracing": False,
}
stash = StashPluginHelper(
        stash_url=parse_args.stash_url,
        debugTracing=parse_args.trace,
        settings=settings,
        config=config,
        maxbytes=10*1024*1024,
        )
if len(sys.argv) > 1:
    stash.Log(f"argv = {sys.argv}")
else:
    stash.Trace(f"No command line arguments. JSON_INPUT['args'] = {stash.JSON_INPUT['args']}")
stash.status(logLevel=logging.DEBUG)

stash.modulesInstalled(["send2trash", "requests"])

# stash.Trace(f"\nStarting (__file__={__file__}) (stash.CALLED_AS_STASH_PLUGIN={stash.CALLED_AS_STASH_PLUGIN}) (stash.DEBUG_TRACING={stash.DEBUG_TRACING}) (stash.PLUGIN_TASK_NAME={stash.PLUGIN_TASK_NAME})************************************************")
# stash.encodeToUtf8 = True


LOG_STASH_N_PLUGIN = stash.LOG_TO_STASH if stash.CALLED_AS_STASH_PLUGIN else stash.LOG_TO_CONSOLE + stash.LOG_TO_FILE
listSeparator               = stash.Setting('listSeparator', ',', notEmpty=True)
addPrimaryDupPathToDetails  = stash.Setting('addPrimaryDupPathToDetails') 
doNotGeneratePhash          = stash.Setting('doNotGeneratePhash')
mergeDupFilename            = stash.Setting('mergeDupFilename')
moveToTrashCan              = False if stash.Setting('permanentlyDelete') else True
alternateTrashCanPath       = stash.Setting('dup_path')
whitelistDelDupInSameFolder = stash.Setting('whitelistDelDupInSameFolder')
whitelistDoTagLowResDup     = stash.Setting('whitelistDoTagLowResDup')
maxDupToProcess             = int(stash.Setting('zyMaxDupToProcess'))
significantTimeDiff         = stash.Setting('significantTimeDiff')
toRecycleBeforeSwap         = stash.Setting('toRecycleBeforeSwap')
cleanAfterDel               = stash.Setting('zCleanAfterDel')

swapHighRes                 = stash.Setting('zSwapHighRes')
swapLongLength              = stash.Setting('zSwapLongLength')
swapBetterBitRate           = stash.Setting('zSwapBetterBitRate')
swapCodec                   = stash.Setting('zSwapCodec')
swapBetterFrameRate         = stash.Setting('zSwapBetterFrameRate')
favorLongerFileName         = stash.Setting('favorLongerFileName')
favorLargerFileSize         = stash.Setting('favorLargerFileSize')
favorBitRateChange          = stash.Setting('favorBitRateChange')
favorHighBitRate            = stash.Setting('favorHighBitRate')
favorFrameRateChange        = stash.Setting('favorFrameRateChange')
favorHigherFrameRate        = stash.Setting('favorHigherFrameRate')
favorCodecRanking           = stash.Setting('favorCodecRanking')
codecRankingSetToUse        = stash.Setting('codecRankingSetToUse')
if   codecRankingSetToUse == 4:
    codecRanking            = stash.Setting('codecRankingSet4')
elif codecRankingSetToUse == 3:
    codecRanking            = stash.Setting('codecRankingSet3')
elif codecRankingSetToUse == 2:
    codecRanking            = stash.Setting('codecRankingSet2')
else:
    codecRanking            = stash.Setting('codecRankingSet1')

matchDupDistance            = int(stash.Setting('zyMatchDupDistance'))
matchPhaseDistance          = PhashDistance.EXACT
matchPhaseDistanceText      = "Exact Match"
if matchDupDistance == 1:
    matchPhaseDistance      = PhashDistance.HIGH
    matchPhaseDistanceText  = "High Match"
elif matchDupDistance == 2:
    matchPhaseDistance      = PhashDistance.MEDIUM
    matchPhaseDistanceText  = "Medium Match"

# significantTimeDiff can not be higher than 1 and shouldn't be lower than .5
if significantTimeDiff > 1:
    significantTimeDiff = 1
if significantTimeDiff < .5:
    significantTimeDiff = .5


duplicateMarkForDeletion = stash.Setting('DupFileTag')
if duplicateMarkForDeletion == "":
    duplicateMarkForDeletion = 'DuplicateMarkForDeletion'

duplicateWhitelistTag = stash.Setting('DupWhiteListTag')
if duplicateWhitelistTag == "":
    duplicateWhitelistTag = '_DuplicateWhitelistFile'

excludeDupFileDeleteTag = stash.Setting('excludeDupFileDeleteTag')
if excludeDupFileDeleteTag == "":
    excludeDupFileDeleteTag = '_ExcludeDuplicateMarkForDeletion'

excludeMergeTags = [duplicateMarkForDeletion, duplicateWhitelistTag, excludeDupFileDeleteTag]
stash.initMergeMetadata(excludeMergeTags)

graylist = stash.Setting('zxGraylist').split(listSeparator)
graylist = [item.lower() for item in graylist]
if graylist == [""] : graylist = []
stash.Trace(f"graylist = {graylist}")   
whitelist = stash.Setting('zWhitelist').split(listSeparator)
whitelist = [item.lower() for item in whitelist]
if whitelist == [""] : whitelist = []
stash.Trace(f"whitelist = {whitelist}")   
blacklist = stash.Setting('zyBlacklist').split(listSeparator)
blacklist = [item.lower() for item in blacklist]
if blacklist == [""] : blacklist = []
stash.Trace(f"blacklist = {blacklist}")
    
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

detailPrefix = "BaseDup="
detailPostfix = "<BaseDup>\n"

def setTagId(tagName, sceneDetails, DupFileToKeep):
    details = ""
    ORG_DATA_DICT = {'id' : sceneDetails['id']}
    dataDict = ORG_DATA_DICT.copy()
    doAddTag = True
    if addPrimaryDupPathToDetails:
        BaseDupStr = f"{detailPrefix}{DupFileToKeep['files'][0]['path']}\n{stash.STASH_URL}/scenes/{DupFileToKeep['id']}\n(matchDupDistance={matchPhaseDistanceText})\n{detailPostfix}"
        if sceneDetails['details'] == "":
            details = BaseDupStr
        elif not sceneDetails['details'].startswith(detailPrefix):
            details = f"{BaseDupStr};\n{sceneDetails['details']}"
    for tag in sceneDetails['tags']:
        if tag['name'] == tagName:
            doAddTag = False
            break
    if doAddTag:
        stash.addTag(sceneDetails, tagName)
    if details != "":
        dataDict.update({'details' : details})
    if dataDict != ORG_DATA_DICT:
        stash.update_scene(dataDict)
        stash.Trace(f"[setTagId] Updated {sceneDetails['files'][0]['path']} with metadata {dataDict}", toAscii=True)
    else:
        stash.Trace(f"[setTagId] Nothing to update {sceneDetails['files'][0]['path']}.", toAscii=True)


def isInList(listToCk, itemToCk):
    itemToCk = itemToCk.lower()
    for item in listToCk:
        if itemToCk.startswith(item):
            return True
    return False

NOT_IN_LIST = 65535
def indexInList(listToCk, itemToCk):
    itemToCk = itemToCk.lower()
    index = -1
    lenItemMatch = 0
    returnValue = NOT_IN_LIST
    for item in listToCk:
        index += 1
        if itemToCk.startswith(item):
            if len(item) > lenItemMatch: # Make sure the best match is selected by getting match with longest string.
                lenItemMatch = len(item)
                returnValue = index
    return returnValue

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

def isBetterVideo(scene1, scene2, swapCandidateCk = False):
    # Prioritize higher reslution over codec, bit rate, and frame rate
    if int(scene1['files'][0]['width']) > int(scene2['files'][0]['width']) or int(scene1['files'][0]['height']) > int(scene2['files'][0]['height']):
        return False
    if (favorBitRateChange and swapCandidateCk == False) or (swapCandidateCk and swapBetterBitRate):
        if (favorHighBitRate and int(scene2['files'][0]['bit_rate']) > int(scene1['files'][0]['bit_rate'])) or (not favorHighBitRate and int(scene2['files'][0]['bit_rate']) < int(scene1['files'][0]['bit_rate'])):
            stash.Trace(f"[isBetterVideo]:[favorHighBitRate={favorHighBitRate}] Better bit rate. {scene1['files'][0]['path']}={scene1['files'][0]['bit_rate']} v.s. {scene2['files'][0]['path']}={scene2['files'][0]['bit_rate']}")
            return True
    if (favorCodecRanking and swapCandidateCk == False) or (swapCandidateCk and swapCodec):
        scene1CodecRank = indexInList(codecRanking, scene1['files'][0]['video_codec'])
        scene2CodecRank = indexInList(codecRanking, scene2['files'][0]['video_codec'])
        if scene2CodecRank < scene1CodecRank:
            stash.Trace(f"[isBetterVideo] Better codec. {scene1['files'][0]['path']}={scene1['files'][0]['video_codec']}:Rank={scene1CodecRank} v.s. {scene2['files'][0]['path']}={scene2['files'][0]['video_codec']}:Rank={scene2CodecRank}")
            return True
    if (favorFrameRateChange and swapCandidateCk == False) or (swapCandidateCk and swapBetterFrameRate):
        if (favorHigherFrameRate and int(scene2['files'][0]['frame_rate']) > int(scene1['files'][0]['frame_rate'])) or (not favorHigherFrameRate and int(scene2['files'][0]['frame_rate']) < int(scene1['files'][0]['frame_rate'])):
            stash.Trace(f"[isBetterVideo]:[favorHigherFrameRate={favorHigherFrameRate}] Better frame rate. {scene1['files'][0]['path']}={scene1['files'][0]['frame_rate']} v.s. {scene2['files'][0]['path']}={scene2['files'][0]['frame_rate']}")
            return True
    return False

def isSwapCandidate(DupFileToKeep, DupFile):
    # Don't move if both are in whitelist
    if isInList(whitelist, DupFileToKeep['files'][0]['path']) and isInList(whitelist, DupFile['files'][0]['path']):
        return False
    if swapHighRes and (int(DupFileToKeep['files'][0]['width']) > int(DupFile['files'][0]['width']) or int(DupFileToKeep['files'][0]['height']) > int(DupFile['files'][0]['height'])):
        if not significantLessTime(int(DupFileToKeep['files'][0]['duration']), int(DupFile['files'][0]['duration'])):
            return True
        else:
            stash.Warn(f"File '{DupFileToKeep['files'][0]['path']}' has a higher resolution than '{DupFile['files'][0]['path']}', but the duration is significantly shorter.", toAscii=True)
    if swapLongLength and int(DupFileToKeep['files'][0]['duration']) > int(DupFile['files'][0]['duration']):
        if int(DupFileToKeep['files'][0]['width']) >= int(DupFile['files'][0]['width']) or int(DupFileToKeep['files'][0]['height']) >= int(DupFile['files'][0]['height']):
            return True
    if isBetterVideo(DupFile, DupFileToKeep, swapCandidateCk=True):
        if not significantLessTime(int(DupFileToKeep['files'][0]['duration']), int(DupFile['files'][0]['duration'])):
            return True
        else:
            stash.Warn(f"File '{DupFileToKeep['files'][0]['path']}' has better codec/bit-rate than '{DupFile['files'][0]['path']}', but the duration is significantly shorter.", toAscii=True)
    return False

dupWhitelistTagId = None
def addDupWhitelistTag():
    global dupWhitelistTagId
    stash.Trace(f"Adding tag duplicateWhitelistTag = {duplicateWhitelistTag}")    
    descp = 'Tag added to duplicate scenes which are in the whitelist. This means there are two or more duplicates in the whitelist.'
    dupWhitelistTagId = stash.createTagId(duplicateWhitelistTag, descp, ignoreAutoTag=True)
    stash.Trace(f"dupWhitelistTagId={dupWhitelistTagId} name={duplicateWhitelistTag}")

excludeDupFileDeleteTagId = None
def addExcludeDupTag():
    global excludeDupFileDeleteTagId
    stash.Trace(f"Adding tag excludeDupFileDeleteTag = {excludeDupFileDeleteTag}")    
    descp = 'Excludes duplicate scene from DupFileManager tagging and deletion process. A scene having this tag will not get deleted by DupFileManager'
    excludeDupFileDeleteTagId = stash.createTagId(excludeDupFileDeleteTag, descp, ignoreAutoTag=True)
    stash.Trace(f"dupWhitelistTagId={excludeDupFileDeleteTagId} name={excludeDupFileDeleteTag}")

def isTaggedExcluded(Scene):
    for tag in Scene['tags']:
        if tag['name'] == excludeDupFileDeleteTag:
            return True
    return False

def isWorseKeepCandidate(DupFileToKeep, Scene):
    if not isInList(whitelist, Scene['files'][0]['path']) and isInList(whitelist, DupFileToKeep['files'][0]['path']):
        return True
    if not isInList(graylist, Scene['files'][0]['path']) and isInList(graylist, DupFileToKeep['files'][0]['path']):
        return True
    if not isInList(blacklist, DupFileToKeep['files'][0]['path']) and isInList(blacklist, Scene['files'][0]['path']):
        return True
    
    if isInList(graylist, Scene['files'][0]['path']) and isInList(graylist, DupFileToKeep['files'][0]['path']) and indexInList(graylist, DupFileToKeep['files'][0]['path']) < indexInList(graylist, Scene['files'][0]['path']):
        return True
    if isInList(blacklist, DupFileToKeep['files'][0]['path']) and isInList(blacklist, Scene['files'][0]['path']) and indexInList(blacklist, DupFileToKeep['files'][0]['path']) < indexInList(blacklist, Scene['files'][0]['path']):
        return True      
    return False

stopProcessBarSpin = True
def spinProcessBar(sleepSeconds = 1):
    pos = 1
    maxPos = 30
    while stopProcessBarSpin == False:
        stash.progressBar(pos, maxPos)
        pos +=1
        if pos > maxPos:
            pos = 1
        time.sleep(sleepSeconds)

def mangeDupFiles(merge=False, deleteDup=False, tagDuplicates=False):
    global stopProcessBarSpin
    duplicateMarkForDeletion_descp = 'Tag added to duplicate scenes so-as to tag them for deletion.'
    stash.Trace(f"duplicateMarkForDeletion = {duplicateMarkForDeletion}")    
    dupTagId = stash.createTagId(duplicateMarkForDeletion, duplicateMarkForDeletion_descp, ignoreAutoTag=True)
    stash.Trace(f"dupTagId={dupTagId} name={duplicateMarkForDeletion}")
    
    addDupWhitelistTag()
    addExcludeDupTag()
    
    QtyDupSet = 0
    QtyDup = 0
    QtyExactDup = 0
    QtyAlmostDup = 0
    QtyRealTimeDiff = 0
    QtyTagForDel = 0
    QtySkipForDel = 0
    QtyExcludeForDel = 0
    QtySwap = 0
    QtyMerge = 0
    QtyDeleted = 0
    stash.Log("#########################################################################")
    stash.Trace("#########################################################################")
    stash.Log(f"Waiting for find_duplicate_scenes_diff to return results; matchDupDistance={matchPhaseDistanceText}; significantTimeDiff={significantTimeDiff}", printTo=LOG_STASH_N_PLUGIN)
    stopProcessBarSpin = False
    stash.submit(spinProcessBar)
    DupFileSets = stash.find_duplicate_scenes(matchPhaseDistance)
    stopProcessBarSpin = True
    time.sleep(1) # Make sure we give time for spinProcessBar to exit
    qtyResults = len(DupFileSets)
    stash.Trace("#########################################################################")
    for DupFileSet in DupFileSets:
        stash.Trace(f"DupFileSet={DupFileSet}")
        QtyDupSet+=1
        stash.progressBar(QtyDupSet, qtyResults)
        SepLine = "---------------------------"
        DupFileToKeep = ""
        DupToCopyFrom = ""
        DupFileDetailList = []
        for DupFile in DupFileSet:
            QtyDup+=1
            time.sleep(2)
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
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=resolution: {DupFileToKeep['files'][0]['width']}x{DupFileToKeep['files'][0]['height']} < {Scene['files'][0]['width']}x{Scene['files'][0]['height']}")
                    DupFileToKeep = Scene
                elif int(DupFileToKeep['files'][0]['duration']) < int(Scene['files'][0]['duration']):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=duration: {DupFileToKeep['files'][0]['duration']} < {Scene['files'][0]['duration']}")
                    DupFileToKeep = Scene
                elif isBetterVideo(DupFileToKeep, Scene):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=codec,bit_rate, or frame_rate: {DupFileToKeep['files'][0]['video_codec']}, {DupFileToKeep['files'][0]['bit_rate']}, {DupFileToKeep['files'][0]['frame_rate']} : {Scene['files'][0]['video_codec']}, {Scene['files'][0]['bit_rate']}, {Scene['files'][0]['frame_rate']}")
                    DupFileToKeep = Scene
                elif isInList(whitelist, Scene['files'][0]['path']) and not isInList(whitelist, DupFileToKeep['files'][0]['path']):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=not whitelist vs whitelist")
                    DupFileToKeep = Scene
                elif isTaggedExcluded(Scene) and not isTaggedExcluded(DupFileToKeep):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=not ExcludeTag vs ExcludeTag")
                    DupFileToKeep = Scene
                elif isInList(blacklist, DupFileToKeep['files'][0]['path']) and not isInList(blacklist, Scene['files'][0]['path']):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=blacklist vs not blacklist")
                    DupFileToKeep = Scene
                elif isInList(blacklist, DupFileToKeep['files'][0]['path']) and isInList(blacklist, Scene['files'][0]['path']) and indexInList(blacklist, DupFileToKeep['files'][0]['path']) > indexInList(blacklist, Scene['files'][0]['path']):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=blacklist-index {indexInList(blacklist, DupFileToKeep['files'][0]['path'])} > {indexInList(blacklist, Scene['files'][0]['path'])}")
                    DupFileToKeep = Scene
                elif isInList(graylist, Scene['files'][0]['path']) and not isInList(graylist, DupFileToKeep['files'][0]['path']):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=not graylist vs graylist")
                    DupFileToKeep = Scene
                elif isInList(graylist, Scene['files'][0]['path']) and isInList(graylist, DupFileToKeep['files'][0]['path']) and indexInList(graylist, DupFileToKeep['files'][0]['path']) > indexInList(graylist, Scene['files'][0]['path']):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=graylist-index {indexInList(graylist, DupFileToKeep['files'][0]['path'])} > {indexInList(graylist, Scene['files'][0]['path'])}")
                    DupFileToKeep = Scene
                elif favorLongerFileName and len(DupFileToKeep['files'][0]['path']) < len(Scene['files'][0]['path']) and not isWorseKeepCandidate(DupFileToKeep, Scene):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=path-len {len(DupFileToKeep['files'][0]['path'])} < {len(Scene['files'][0]['path'])}")
                    DupFileToKeep = Scene
                elif favorLargerFileSize and int(DupFileToKeep['files'][0]['size']) < int(Scene['files'][0]['size']) and not isWorseKeepCandidate(DupFileToKeep, Scene):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=size {DupFileToKeep['files'][0]['size']} < {Scene['files'][0]['size']}")
                    DupFileToKeep = Scene
                elif not favorLongerFileName and len(DupFileToKeep['files'][0]['path']) > len(Scene['files'][0]['path']) and not isWorseKeepCandidate(DupFileToKeep, Scene):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=path-len {len(DupFileToKeep['files'][0]['path'])} > {len(Scene['files'][0]['path'])}")
                    DupFileToKeep = Scene
                elif not favorLargerFileSize and int(DupFileToKeep['files'][0]['size']) > int(Scene['files'][0]['size']) and not isWorseKeepCandidate(DupFileToKeep, Scene):
                    stash.Trace(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason=size {DupFileToKeep['files'][0]['size']} > {Scene['files'][0]['size']}")
                    DupFileToKeep = Scene
            else:
                DupFileToKeep = Scene
            # stash.Trace(f"DupFileToKeep = {DupFileToKeep}")
            stash.Trace(f"KeepID={DupFileToKeep['id']}, ID={DupFile['id']} duration=({Scene['files'][0]['duration']}), Size=({Scene['files'][0]['size']}), Res=({Scene['files'][0]['width']} x {Scene['files'][0]['height']}) Name={Scene['files'][0]['path']}, KeepPath={DupFileToKeep['files'][0]['path']}", toAscii=True)
        
        for DupFile in DupFileDetailList:
            if DupFile['id'] != DupFileToKeep['id']:
                if merge:
                    result = stash.mergeMetadata(DupFile, DupFileToKeep)
                    if result != "Nothing To Merge":
                        QtyMerge += 1
                
                if isInList(whitelist, DupFile['files'][0]['path']) and (not whitelistDelDupInSameFolder or not hasSameDir(DupFile['files'][0]['path'], DupFileToKeep['files'][0]['path'])):
                    if isSwapCandidate(DupFileToKeep, DupFile):
                        if merge:
                            stash.mergeMetadata(DupFileToKeep, DupFile)
                        if toRecycleBeforeSwap:
                            sendToTrash(DupFile['files'][0]['path'])
                        shutil.move(DupFileToKeep['files'][0]['path'], DupFile['files'][0]['path'])
                        stash.Log(f"Moved better file '{DupFileToKeep['files'][0]['path']}' to '{DupFile['files'][0]['path']}'", toAscii=True, printTo=LOG_STASH_N_PLUGIN)
                        DupFileToKeep = DupFile
                        QtySwap+=1
                    else:
                        stash.Log(f"NOT processing duplicate, because it's in whitelist. '{DupFile['files'][0]['path']}'", toAscii=True)
                        if dupWhitelistTagId and tagDuplicates:
                            setTagId(duplicateWhitelistTag, DupFile, DupFileToKeep)
                    QtySkipForDel+=1
                else:
                    if isTaggedExcluded(DupFile):
                        stash.Log(f"Excluding file {DupFile['files'][0]['path']} because tagged for exclusion via tag {excludeDupFileDeleteTag}")
                        QtyExcludeForDel+=1
                    else:
                        if deleteDup:
                            DupFileName = DupFile['files'][0]['path']
                            DupFileNameOnly = pathlib.Path(DupFileName).stem
                            stash.Warn(f"Deleting duplicate '{DupFileName}'", toAscii=True, printTo=LOG_STASH_N_PLUGIN)
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
                                stash.Log(f"Tagging duplicate {DupFile['files'][0]['path']} for deletion with tag {duplicateMarkForDeletion}.", toAscii=True, printTo=LOG_STASH_N_PLUGIN)
                            else:
                                stash.Log(f"Tagging duplicate {DupFile['files'][0]['path']} for deletion.", toAscii=True, printTo=LOG_STASH_N_PLUGIN)
                            setTagId(duplicateMarkForDeletion, DupFile, DupFileToKeep)
                        QtyTagForDel+=1
        stash.Trace(SepLine)
        if maxDupToProcess > 0 and QtyDup > maxDupToProcess:
            break
    
    stash.Log(f"QtyDupSet={QtyDupSet}, QtyDup={QtyDup}, QtyDeleted={QtyDeleted}, QtySwap={QtySwap}, QtyTagForDel={QtyTagForDel}, QtySkipForDel={QtySkipForDel}, QtyExcludeForDel={QtyExcludeForDel}, QtyExactDup={QtyExactDup}, QtyAlmostDup={QtyAlmostDup}, QtyMerge={QtyMerge}, QtyRealTimeDiff={QtyRealTimeDiff}", printTo=LOG_STASH_N_PLUGIN)
    if doNotGeneratePhash == False:
        stash.metadata_generate({"phashes": True})
    if cleanAfterDel:
        stash.Log("Adding clean jobs to the Task Queue", printTo=LOG_STASH_N_PLUGIN)
        stash.metadata_clean(paths=stash.STASH_PATHS)
        stash.metadata_clean_generated()
        stash.optimise_database()

def manageTagggedDuplicates(clearTag=False):
    global stopProcessBarSpin
    tagId = stash.find_tags(q=duplicateMarkForDeletion)
    if len(tagId) > 0 and 'id' in tagId[0]:
        tagId = tagId[0]['id']
    else:
        stash.Warn(f"Could not find tag ID for tag '{duplicateMarkForDeletion}'.")
        return
    QtyDup = 0
    QtyDeleted = 0
    QtyClearedTags = 0
    QtyFailedQuery = 0
    stash.Trace("#########################################################################")
    stopProcessBarSpin = False
    stash.submit(spinProcessBar)
    sceneIDs = stash.find_scenes(f={"tags": {"value":tagId, "modifier":"INCLUDES"}}, fragment='id')
    stopProcessBarSpin = True
    time.sleep(1) # Make sure we give time for spinProcessBar to exit
    qtyResults = len(sceneIDs)
    stash.Trace(f"Found {qtyResults} scenes with tag ({duplicateMarkForDeletion}): sceneIDs = {sceneIDs}")
    for sceneID in sceneIDs:
        # stash.Trace(f"Getting scene data for scene ID {sceneID['id']}.")
        QtyDup += 1
        prgs = QtyDup / qtyResults
        stash.progressBar(QtyDup, qtyResults)
        scene = stash.find_scene(sceneID['id'])
        if scene == None or len(scene) == 0:
            stash.Warn(f"Could not get scene data for scene ID {sceneID['id']}.")
            QtyFailedQuery += 1
            continue
        # stash.Trace(f"scene={scene}")
        if clearTag:
            tags = [int(item['id']) for item in scene["tags"] if item['id'] != tagId]
            stash.TraceOnce(f"tagId={tagId}, len={len(tags)}, tags = {tags}")
            dataDict = {'id' : scene['id']}
            if addPrimaryDupPathToDetails:
                sceneDetails = scene['details']
                if sceneDetails.find(detailPrefix) == 0 and sceneDetails.find(detailPostfix) > 1:
                    Pos1 = sceneDetails.find(detailPrefix)
                    Pos2 = sceneDetails.find(detailPostfix)
                    sceneDetails = sceneDetails[0:Pos1] + sceneDetails[Pos2 + len(detailPostfix):]                
                dataDict.update({'details' : sceneDetails})
            dataDict.update({'tag_ids' : tags})
            stash.Log(f"Updating scene with {dataDict}")
            stash.update_scene(dataDict)
            # stash.removeTag(scene, duplicateMarkForDeletion)
            QtyClearedTags += 1            
        else:
            DupFileName = scene['files'][0]['path']
            DupFileNameOnly = pathlib.Path(DupFileName).stem
            stash.Warn(f"Deleting duplicate '{DupFileName}'", toAscii=True, printTo=LOG_STASH_N_PLUGIN)
            if alternateTrashCanPath != "":
                destPath = f"{alternateTrashCanPath }{os.sep}{DupFileNameOnly}"
                if os.path.isfile(destPath):
                    destPath = f"{alternateTrashCanPath }{os.sep}_{time.time()}_{DupFileNameOnly}"
                shutil.move(DupFileName, destPath)
            elif moveToTrashCan:
                sendToTrash(DupFileName)
            result = stash.destroy_scene(scene['id'], delete_file=True)
            stash.Trace(f"destroy_scene result={result} for file {DupFileName}", toAscii=True)
            QtyDeleted += 1
    stash.Log(f"QtyDup={QtyDup}, QtyClearedTags={QtyClearedTags}, QtyDeleted={QtyDeleted}, QtyFailedQuery={QtyFailedQuery}", printTo=LOG_STASH_N_PLUGIN)
    if doNotGeneratePhash == False and clearTag == False:
        stash.metadata_generate({"phashes": True})

if stash.PLUGIN_TASK_NAME == "tag_duplicates_task":
    mangeDupFiles(tagDuplicates=True, merge=mergeDupFilename)
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif stash.PLUGIN_TASK_NAME == "delete_tagged_duplicates_task":
    manageTagggedDuplicates()
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif stash.PLUGIN_TASK_NAME == "delete_duplicates_task":
    mangeDupFiles(deleteDup=True, merge=mergeDupFilename)
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif stash.PLUGIN_TASK_NAME == "clear_duplicate_tags_task":
    manageTagggedDuplicates(clearTag=True)
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif stash.PLUGIN_TASK_NAME == "generate_phash_task":
    stash.metadata_generate({"phashes": True})
    stash.Trace(f"{stash.PLUGIN_TASK_NAME} EXIT")
elif parse_args.dup_tag:
    mangeDupFiles(tagDuplicates=True, merge=mergeDupFilename)
    stash.Trace(f"Tag duplicate EXIT")
elif parse_args.del_tag:
    manageTagggedDuplicates()
    stash.Trace(f"Delete Tagged duplicates EXIT")
elif parse_args.clear_tag:
    manageTagggedDuplicates(clearTag=True)
    stash.Trace(f"Clear duplicate tags EXIT")
elif parse_args.remove:
    mangeDupFiles(deleteDup=True, merge=mergeDupFilename)
    stash.Trace(f"Delete duplicate EXIT")
else:
    stash.Log(f"Nothing to do!!! (PLUGIN_ARGS_MODE={stash.PLUGIN_TASK_NAME})")





stash.Trace("\n*********************************\nEXITING   ***********************\n*********************************")

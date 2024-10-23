# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager
# Note: To call this script outside of Stash, pass argument --url 
#       Example:    python DupFileManager.py --url http://localhost:9999 -a
import ModulesValidate
ModulesValidate.modulesInstalled(["send2trash", "requests"])
import os, sys, time, pathlib, argparse, platform, shutil, traceback, logging, requests
from datetime import datetime
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
    "mergeDupFilename": False,
    "whitelistDelDupInSameFolder": False,
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
    "zzDebug": False,
    "zzTracing": False,
}
stash = StashPluginHelper(
        stash_url=parse_args.stash_url,
        debugTracing=parse_args.trace,
        settings=settings,
        config=config,
        maxbytes=10*1024*1024,
        DebugTraceFieldName="zzTracing",
        DebugFieldName="zzDebug",
        )
stash.convertToAscii = True
stash.Log("******************* Starting   *******************")
if len(sys.argv) > 1:
    stash.Log(f"argv = {sys.argv}")
else:
    stash.Trace(f"No command line arguments. JSON_INPUT['args'] = {stash.JSON_INPUT['args']}")
stash.status(logLevel=logging.DEBUG)


# stash.Trace(f"\nStarting (__file__={__file__}) (stash.CALLED_AS_STASH_PLUGIN={stash.CALLED_AS_STASH_PLUGIN}) (stash.DEBUG_TRACING={stash.DEBUG_TRACING}) (stash.PLUGIN_TASK_NAME={stash.PLUGIN_TASK_NAME})************************************************")
# stash.encodeToUtf8 = True


LOG_STASH_N_PLUGIN = stash.LogTo.STASH if stash.CALLED_AS_STASH_PLUGIN else stash.LogTo.CONSOLE + stash.LogTo.FILE
listSeparator               = stash.Setting('listSeparator', ',', notEmpty=True)
addPrimaryDupPathToDetails  = stash.Setting('addPrimaryDupPathToDetails') 
clearAllDupfileManagerTags  = stash.Setting('clearAllDupfileManagerTags')
doGeneratePhash             = stash.Setting('doGeneratePhash')
mergeDupFilename            = stash.Setting('mergeDupFilename')
moveToTrashCan              = False if stash.Setting('permanentlyDelete') else True
alternateTrashCanPath       = stash.Setting('dup_path')
whitelistDelDupInSameFolder = stash.Setting('whitelistDelDupInSameFolder')
graylistTagging             = stash.Setting('graylistTagging')
maxDupToProcess             = int(stash.Setting('zyMaxDupToProcess'))
significantTimeDiff         = stash.Setting('significantTimeDiff')
toRecycleBeforeSwap         = stash.Setting('toRecycleBeforeSwap')
cleanAfterDel               = stash.Setting('cleanAfterDel')

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
skipIfTagged                = stash.Setting('skipIfTagged')
killScanningPostProcess     = stash.Setting('killScanningPostProcess')
tagLongDurationLowRes       = stash.Setting('tagLongDurationLowRes')
bitRateIsImporantComp       = stash.Setting('bitRateIsImporantComp')
codecIsImporantComp         = stash.Setting('codecIsImporantComp')

matchDupDistance            = int(stash.Setting('zyMatchDupDistance'))
matchPhaseDistance          = PhashDistance.EXACT
matchPhaseDistanceText      = "Exact Match"
if matchDupDistance == 1:
    matchPhaseDistance      = PhashDistance.HIGH
    matchPhaseDistanceText  = "High Match"
elif matchDupDistance == 2:
    matchPhaseDistance      = PhashDistance.MEDIUM
    matchPhaseDistanceText  = "Medium Match"
elif matchDupDistance == 3:
    matchPhaseDistance      = PhashDistance.LOW
    matchPhaseDistanceText  = "Low Match"

# significantTimeDiff can not be higher than 1 and shouldn't be lower than .5
if significantTimeDiff > 1:
    significantTimeDiff = 1
if significantTimeDiff < .5:
    significantTimeDiff = .5


duplicateMarkForDeletion = stash.Setting('DupFileTag')
if duplicateMarkForDeletion == "":
    duplicateMarkForDeletion = 'DuplicateMarkForDeletion'

base1_duplicateWhitelistTag = duplicateMarkForDeletion

duplicateWhitelistTag = stash.Setting('DupWhiteListTag')
if duplicateWhitelistTag == "":
    duplicateWhitelistTag = '_DuplicateWhitelistFile'

excludeDupFileDeleteTag = stash.Setting('excludeDupFileDeleteTag')
if excludeDupFileDeleteTag == "":
    excludeDupFileDeleteTag = '_ExcludeDuplicateMarkForDeletion'

graylistMarkForDeletion = stash.Setting('graylistMarkForDeletion')
if graylistMarkForDeletion == "":
    graylistMarkForDeletion = '_GraylistMarkForDeletion'

longerDurationLowerResolution = stash.Setting('longerDurationLowerResolution')
if longerDurationLowerResolution == "":
    longerDurationLowerResolution = '_LongerDurationLowerResolution'

excludeMergeTags = [duplicateMarkForDeletion, duplicateWhitelistTag, excludeDupFileDeleteTag]

if stash.Setting('underscoreDupFileTag') and not duplicateMarkForDeletion.startswith('_'):
    duplicateMarkForDeletionWithOutUnderscore = duplicateMarkForDeletion
    duplicateMarkForDeletion = "_" + duplicateMarkForDeletion
    if stash.renameTag(duplicateMarkForDeletionWithOutUnderscore, duplicateMarkForDeletion):
        stash.Log(f"Renamed tag {duplicateMarkForDeletionWithOutUnderscore} to {duplicateMarkForDeletion}")
    stash.Trace(f"Added underscore to {duplicateMarkForDeletionWithOutUnderscore} = {duplicateMarkForDeletion}")
    excludeMergeTags += [duplicateMarkForDeletion]
else:
    stash.Trace(f"duplicateMarkForDeletion = {duplicateMarkForDeletion}")

base2_duplicateWhitelistTag = duplicateMarkForDeletion

if stash.Setting('appendMatchDupDistance'):
    duplicateMarkForDeletion += f"_{matchDupDistance}"
    excludeMergeTags += [duplicateMarkForDeletion]

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

def setTagId(tagName, sceneDetails, DupFileToKeep, TagReason="", ignoreAutoTag=False):
    details = ""
    ORG_DATA_DICT = {'id' : sceneDetails['id']}
    dataDict = ORG_DATA_DICT.copy()
    doAddTag = True
    if addPrimaryDupPathToDetails:
        BaseDupStr = f"{detailPrefix}{DupFileToKeep['files'][0]['path']}\n{stash.STASH_URL}/scenes/{DupFileToKeep['id']}\n{TagReason}(matchDupDistance={matchPhaseDistanceText})\n{detailPostfix}"
        if sceneDetails['details'] == "":
            details = BaseDupStr
        elif not sceneDetails['details'].startswith(detailPrefix):
            details = f"{BaseDupStr};\n{sceneDetails['details']}"
    for tag in sceneDetails['tags']:
        if tag['name'] == tagName:
            doAddTag = False
            break
    if doAddTag:
        stash.addTag(sceneDetails, tagName, ignoreAutoTag=ignoreAutoTag)
    if details != "":
        dataDict.update({'details' : details})
    if dataDict != ORG_DATA_DICT:
        stash.updateScene(dataDict)
        stash.Trace(f"[setTagId] Updated {sceneDetails['files'][0]['path']} with metadata {dataDict} and tag {tagName}", toAscii=True)
    else:
        stash.Trace(f"[setTagId] Nothing to update {sceneDetails['files'][0]['path']} already has tag {tagName}.", toAscii=True)
    return doAddTag

def setTagId_withRetry(tagName, sceneDetails, DupFileToKeep, TagReason="", ignoreAutoTag=False, retryCount = 12, sleepSecondsBetweenRetry = 5):
    errMsg = None
    for i in range(0, retryCount):
        try:
            if errMsg != None:
                stash.Warn(errMsg)
            return setTagId(tagName, sceneDetails, DupFileToKeep, TagReason, ignoreAutoTag)
        except (requests.exceptions.ConnectionError, ConnectionResetError):
            tb = traceback.format_exc()
            errMsg = f"[setTagId] Exception calling setTagId. Will retry; count({i}); Error: {e}\nTraceBack={tb}"
        except Exception as e:
            tb = traceback.format_exc()
            errMsg = f"[setTagId] Unknown exception calling setTagId. Will retry; count({i}); Error: {e}\nTraceBack={tb}"
        time.sleep(sleepSecondsBetweenRetry)

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
# If ckTimeDiff=False: Does durration2 have significant more time than durration1
def significantTimeDiffCheck(durration1, durration2, ckTimeDiff = False): # If ckTimeDiff=True: is time different significant in either direction. 
    if not isinstance(durration1, int) and 'files' in durration1:
        durration1 = int(durration1['files'][0]['duration'])
        durration2 = int(durration2['files'][0]['duration'])
    timeDiff = getTimeDif(durration1, durration2)
    if ckTimeDiff and timeDiff > 1:
        timeDiff = getTimeDif(durration2, durration1)
    if timeDiff < significantTimeDiff:
        return True
    return False

def getTimeDif(durration1, durration2): # Where durration1 is ecpected to be smaller than durration2 IE(45/60=.75)
    return durration1 / durration2

def isBetterVideo(scene1, scene2, swapCandidateCk = False): # is scene2 better than scene1
    # Prioritize higher reslution over codec, bit rate, and frame rate
    if int(scene1['files'][0]['width']) * int(scene1['files'][0]['height']) > int(scene2['files'][0]['width']) * int(scene2['files'][0]['height']):
        return False
    # if int(scene1['files'][0]['width']) > int(scene2['files'][0]['width']) or int(scene1['files'][0]['height']) > int(scene2['files'][0]['height']):
        # return False
    if (favorBitRateChange and swapCandidateCk == False) or (swapCandidateCk and swapBetterBitRate):
        if (favorHighBitRate and int(scene2['files'][0]['bit_rate']) > int(scene1['files'][0]['bit_rate'])) or (not favorHighBitRate and int(scene2['files'][0]['bit_rate']) < int(scene1['files'][0]['bit_rate'])):
            stash.Trace(f"[isBetterVideo]:[favorHighBitRate={favorHighBitRate}] Better bit rate. {scene1['files'][0]['path']}={scene1['files'][0]['bit_rate']} v.s. {scene2['files'][0]['path']}={scene2['files'][0]['bit_rate']}")
            return True
    if (favorCodecRanking and swapCandidateCk == False) or (swapCandidateCk and swapCodec):
        scene1CodecRank = stash.indexStartsWithInList(codecRanking, scene1['files'][0]['video_codec'])
        scene2CodecRank = stash.indexStartsWithInList(codecRanking, scene2['files'][0]['video_codec'])
        if scene2CodecRank < scene1CodecRank:
            stash.Trace(f"[isBetterVideo] Better codec. {scene1['files'][0]['path']}={scene1['files'][0]['video_codec']}:Rank={scene1CodecRank} v.s. {scene2['files'][0]['path']}={scene2['files'][0]['video_codec']}:Rank={scene2CodecRank}")
            return True
    if (favorFrameRateChange and swapCandidateCk == False) or (swapCandidateCk and swapBetterFrameRate):
        if (favorHigherFrameRate and int(scene2['files'][0]['frame_rate']) > int(scene1['files'][0]['frame_rate'])) or (not favorHigherFrameRate and int(scene2['files'][0]['frame_rate']) < int(scene1['files'][0]['frame_rate'])):
            stash.Trace(f"[isBetterVideo]:[favorHigherFrameRate={favorHigherFrameRate}] Better frame rate. {scene1['files'][0]['path']}={scene1['files'][0]['frame_rate']} v.s. {scene2['files'][0]['path']}={scene2['files'][0]['frame_rate']}")
            return True
    return False

def significantMoreTimeCompareToBetterVideo(scene1, scene2): # is scene2 better than scene1
    if isinstance(scene1, int):
        scene1 = stash.find_scene(scene1)
        scene2 = stash.find_scene(scene2)
    if int(scene1['files'][0]['duration']) >= int(scene2['files'][0]['duration']):
        return False
    if int(scene1['files'][0]['width']) * int(scene1['files'][0]['height']) > int(scene2['files'][0]['width']) * int(scene2['files'][0]['height']):
        if significantTimeDiffCheck(scene1, scene2):
            if tagLongDurationLowRes:
                didAddTag = setTagId_withRetry(longerDurationLowerResolution, scene2, scene1, ignoreAutoTag=True)
                stash.Log(f"Tagged sene2 with tag {longerDurationLowerResolution}, because scene1 is better video, but it has significant less time ({getTimeDif(int(scene1['files'][0]['duration']), int(scene2['files'][0]['duration']))}%) compare to scene2; scene1={scene1['files'][0]['path']} (ID={scene1['id']})(duration={scene1['files'][0]['duration']}); scene2={scene2['files'][0]['path']} (ID={scene2['id']}) (duration={scene1['files'][0]['duration']}); didAddTag={didAddTag}")
            else:
                stash.Warn(f"Scene1 is better video, but it has significant less time ({getTimeDif(int(scene1['files'][0]['duration']), int(scene2['files'][0]['duration']))}%) compare to scene2; Scene1={scene1['files'][0]['path']} (ID={scene1['id']})(duration={scene1['files'][0]['duration']}); Scene2={scene2['files'][0]['path']} (ID={scene2['id']}) (duration={scene1['files'][0]['duration']})")            
        return False
    return True

def allThingsEqual(scene1, scene2): # If all important things are equal, return true
    if int(scene1['files'][0]['duration']) != int(scene2['files'][0]['duration']):
        return False
    if scene1['files'][0]['width'] != scene2['files'][0]['width']:
        return False
    if scene1['files'][0]['height'] != scene2['files'][0]['height']:
        return False
    if bitRateIsImporantComp and scene1['files'][0]['bit_rate'] != scene2['files'][0]['bit_rate']:
        return False
    if codecIsImporantComp and scene1['files'][0]['video_codec'] != scene2['files'][0]['video_codec']:
        return False
    return True

def isSwapCandidate(DupFileToKeep, DupFile):
    # Don't move if both are in whitelist
    if stash.startsWithInList(whitelist, DupFileToKeep['files'][0]['path']) and stash.startsWithInList(whitelist, DupFile['files'][0]['path']):
        return False
    # if swapHighRes and (int(DupFileToKeep['files'][0]['width']) > int(DupFile['files'][0]['width']) or int(DupFileToKeep['files'][0]['height']) > int(DupFile['files'][0]['height'])):
    if swapHighRes and int(DupFileToKeep['files'][0]['width']) * int(DupFileToKeep['files'][0]['height']) > int(DupFile['files'][0]['width']) * int(DupFile['files'][0]['height']):
        if not significantTimeDiffCheck(DupFileToKeep, DupFile):
            return True
        else:
            stash.Warn(f"File '{DupFileToKeep['files'][0]['path']}' has a higher resolution than '{DupFile['files'][0]['path']}', but the duration is significantly shorter.", toAscii=True)
    if swapLongLength and int(DupFileToKeep['files'][0]['duration']) > int(DupFile['files'][0]['duration']):
        if int(DupFileToKeep['files'][0]['width']) >= int(DupFile['files'][0]['width']) or int(DupFileToKeep['files'][0]['height']) >= int(DupFile['files'][0]['height']):
            return True
    if isBetterVideo(DupFile, DupFileToKeep, swapCandidateCk=True):
        if not significantTimeDiffCheck(DupFileToKeep, DupFile):
            return True
        else:
            stash.Warn(f"File '{DupFileToKeep['files'][0]['path']}' has better codec/bit-rate than '{DupFile['files'][0]['path']}', but the duration is significantly shorter; DupFileToKeep-ID={DupFileToKeep['id']};DupFile-ID={DupFile['id']};BitRate {DupFileToKeep['files'][0]['bit_rate']} vs {DupFile['files'][0]['bit_rate']};Codec {DupFileToKeep['files'][0]['video_codec']} vs {DupFile['files'][0]['video_codec']};FrameRate {DupFileToKeep['files'][0]['frame_rate']} vs {DupFile['files'][0]['frame_rate']};", toAscii=True)
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
    if not stash.startsWithInList(whitelist, Scene['files'][0]['path']) and stash.startsWithInList(whitelist, DupFileToKeep['files'][0]['path']):
        return True
    if not stash.startsWithInList(graylist, Scene['files'][0]['path']) and stash.startsWithInList(graylist, DupFileToKeep['files'][0]['path']):
        return True
    if not stash.startsWithInList(blacklist, DupFileToKeep['files'][0]['path']) and stash.startsWithInList(blacklist, Scene['files'][0]['path']):
        return True
    
    if stash.startsWithInList(graylist, Scene['files'][0]['path']) and stash.startsWithInList(graylist, DupFileToKeep['files'][0]['path']) and stash.indexStartsWithInList(graylist, DupFileToKeep['files'][0]['path']) < stash.indexStartsWithInList(graylist, Scene['files'][0]['path']):
        return True
    if stash.startsWithInList(blacklist, DupFileToKeep['files'][0]['path']) and stash.startsWithInList(blacklist, Scene['files'][0]['path']) and stash.indexStartsWithInList(blacklist, DupFileToKeep['files'][0]['path']) < stash.indexStartsWithInList(blacklist, Scene['files'][0]['path']):
        return True      
    return False

def killScanningJobs():
    try:
        if killScanningPostProcess:
            stash.stopJobs(0, "Scanning...")
    except Exception as e:
        tb = traceback.format_exc()
        stash.Error(f"Exception while trying to kill scan jobs; Error: {e}\nTraceBack={tb}")

def getPath(Scene, getParent = False):
    path = stash.asc2(Scene['files'][0]['path'])
    path = path.replace("'", "")
    path = path.replace("\\\\", "\\")
    if getParent:
        return pathlib.Path(path).resolve().parent
    return path

def getHtmlReportTableRow(qtyResults):
    htmlReportPrefix = stash.Setting('htmlReportPrefix')
    htmlReportPrefix = htmlReportPrefix.replace('http://localhost:9999/graphql', stash.url)
    htmlReportPrefix = htmlReportPrefix.replace('(QtyPlaceHolder)', f'{qtyResults}')
    htmlReportPrefix = htmlReportPrefix.replace('(MatchTypePlaceHolder)', f'(Match Type = {matchPhaseDistanceText})')
    htmlReportPrefix = htmlReportPrefix.replace('(DateCreatedPlaceHolder)', datetime.now().strftime("%d-%b-%Y, %H:%M:%S"))
    return htmlReportPrefix

htmlDetailDiffTextColor = stash.Setting('htmlDetailDiffTextColor')
htmlSupperHighlight     = stash.Setting('htmlSupperHighlight')
htmlLowerHighlight      = stash.Setting('htmlLowerHighlight')
def getColor(Scene1, Scene2, ifScene1HigherChangeColor = False, roundUpNumber = False, qtyDiff=0):
    if (Scene1 == Scene2) or (roundUpNumber and int(Scene1) == int(Scene2)):
        return ""
    if ifScene1HigherChangeColor and int(Scene1) > int(Scene2):
        if (int(Scene1) - int(Scene2)) > qtyDiff:
            return f' style="color:{htmlDetailDiffTextColor};background-color:{htmlSupperHighlight};"'
        return f' style="color:{htmlDetailDiffTextColor};background-color:{htmlLowerHighlight};"'
    return f' style="color:{htmlDetailDiffTextColor};"'

def getRes(Scene):
    return int(Scene['files'][0]['width']) * int(Scene['files'][0]['height'])

reasonDict = {}

def logReason(DupFileToKeep, Scene, reason):
    global reasonDict
    reasonDict[Scene['id']] = reason
    reasonDict[DupFileToKeep['id']] = reason
    stash.Debug(f"Replacing {DupFileToKeep['files'][0]['path']} with {Scene['files'][0]['path']} for candidate to keep. Reason={reason}")

def mangeDupFiles(merge=False, deleteDup=False, tagDuplicates=False):
    global reasonDict
    duplicateMarkForDeletion_descp = 'Tag added to duplicate scenes so-as to tag them for deletion.'
    stash.Trace(f"duplicateMarkForDeletion = {duplicateMarkForDeletion}")    
    dupTagId = stash.createTagId(duplicateMarkForDeletion, duplicateMarkForDeletion_descp, ignoreAutoTag=True)
    stash.Trace(f"dupTagId={dupTagId} name={duplicateMarkForDeletion}")
    createHtmlReport        = stash.Setting('createHtmlReport')
    previewOrStream         = "stream" if stash.Setting('streamOverPreview') else "preview"
    htmlReportName          = f"{stash.PLUGINS_PATH}{os.sep}{stash.Setting('htmlReportName')}"
    htmlReportNameHomePage  = htmlReportName
    htmlReportTableRow      = stash.Setting('htmlReportTableRow')
    htmlReportTableData     = stash.Setting('htmlReportTableData')
    htmlReportVideoPreview  = stash.Setting('htmlReportVideoPreview')
    htmlHighlightTimeDiff   = stash.Setting('htmlHighlightTimeDiff')
    htmlReportPaginate      = stash.Setting('htmlReportPaginate')
    
    addDupWhitelistTag()
    addExcludeDupTag()
    
    QtyDupSet = 0
    QtyDup = 0
    QtyExactDup = 0
    QtyAlmostDup = 0
    QtyRealTimeDiff = 0
    QtyTagForDel = 0
    QtyTagForDelPaginate = 0
    PaginateId = 0
    QtyNewlyTag = 0
    QtySkipForDel = 0
    QtyExcludeForDel = 0
    QtySwap = 0
    QtyMerge = 0
    QtyDeleted = 0
    stash.Log("#########################################################################")
    stash.Trace("#########################################################################")
    stash.Log(f"Waiting for find_duplicate_scenes_diff to return results; matchDupDistance={matchPhaseDistanceText}; significantTimeDiff={significantTimeDiff}", printTo=LOG_STASH_N_PLUGIN)
    stash.startSpinningProcessBar()
    htmlFileData = " paths {screenshot " + previewOrStream + "} " if createHtmlReport else ""
    mergeFieldData = " code director title rating100 date studio {id} movies {movie {id} } galleries {id} performers {id} urls " if merge else ""
    DupFileSets = stash.find_duplicate_scenes(matchPhaseDistance, fragment='id tags {id name} files {path width height duration size video_codec bit_rate frame_rate} details ' + mergeFieldData + htmlFileData)
    stash.stopSpinningProcessBar()
    qtyResults = len(DupFileSets)
    stash.setProgressBarIter(qtyResults)
    stash.Trace("#########################################################################")
    stash.Log(f"Found {qtyResults} duplicate sets...")
    fileHtmlReport = None
    if createHtmlReport:
        fileHtmlReport = open(htmlReportName, "w")
        fileHtmlReport.write(f"{getHtmlReportTableRow(qtyResults)}\n")
        fileHtmlReport.write(f"{stash.Setting('htmlReportTable')}\n")
        htmlReportTableHeader   = stash.Setting('htmlReportTableHeader')
        fileHtmlReport.write(f"{htmlReportTableRow}{htmlReportTableHeader}Scene</th>{htmlReportTableHeader}Duplicate to Delete</th>{htmlReportTableHeader}Scene-ToKeep</th>{htmlReportTableHeader}Duplicate to Keep</th></tr>\n")
    
    for DupFileSet in DupFileSets:
        # stash.Trace(f"DupFileSet={DupFileSet}", toAscii=True)
        QtyDupSet+=1
        stash.progressBar(QtyDupSet, qtyResults)
        SepLine = "---------------------------"
        DupFileToKeep = None
        DupToCopyFrom = ""
        DupFileDetailList = []
        for DupFile in DupFileSet:
            QtyDup+=1
            # Scene = stash.find_scene(DupFile['id'])
            Scene = DupFile
            if skipIfTagged and createHtmlReport == False and duplicateMarkForDeletion in Scene['tags']:
                stash.Trace(f"Skipping scene '{Scene['files'][0]['path']}' because already tagged with {duplicateMarkForDeletion}")
                continue
            stash.TraceOnce(f"Scene = {Scene}", toAscii=True)
            DupFileDetailList = DupFileDetailList + [Scene]
            if os.path.isfile(Scene['files'][0]['path']):
                if DupFileToKeep != None:
                    if int(DupFileToKeep['files'][0]['duration']) == int(Scene['files'][0]['duration']): # Do not count fractions of a second as a difference
                        QtyExactDup+=1
                    else:
                        QtyAlmostDup+=1
                        SepLine = "***************************"
                        if significantTimeDiffCheck(DupFileToKeep, Scene):
                            QtyRealTimeDiff += 1
                    
                    # if int(DupFileToKeep['files'][0]['width']) < int(Scene['files'][0]['width']) or int(DupFileToKeep['files'][0]['height']) < int(Scene['files'][0]['height']):
                    if int(DupFileToKeep['files'][0]['width']) * int(DupFileToKeep['files'][0]['height']) < int(Scene['files'][0]['width']) * int(Scene['files'][0]['height']):
                        logReason(DupFileToKeep, Scene, f"resolution: {DupFileToKeep['files'][0]['width']}x{DupFileToKeep['files'][0]['height']} < {Scene['files'][0]['width']}x{Scene['files'][0]['height']}")
                        DupFileToKeep = Scene
                    elif significantMoreTimeCompareToBetterVideo(DupFileToKeep, Scene):
                        if significantTimeDiffCheck(DupFileToKeep, Scene):
                            theReason = f"significant-duration: <b style='color:red;background-color:bright green;'>{DupFileToKeep['files'][0]['duration']} < {Scene['files'][0]['duration']}</b>"
                        else:
                            theReason = f"duration: {DupFileToKeep['files'][0]['duration']} < {Scene['files'][0]['duration']}"
                        reasonKeyword = "significant-duration" if significantTimeDiffCheck(DupFileToKeep, Scene) else "duration"
                        logReason(DupFileToKeep, Scene, theReason)
                        DupFileToKeep = Scene
                    elif isBetterVideo(DupFileToKeep, Scene):
                        logReason(DupFileToKeep, Scene, f"codec,bit_rate, or frame_rate: {DupFileToKeep['files'][0]['video_codec']}, {DupFileToKeep['files'][0]['bit_rate']}, {DupFileToKeep['files'][0]['frame_rate']} : {Scene['files'][0]['video_codec']}, {Scene['files'][0]['bit_rate']}, {Scene['files'][0]['frame_rate']}")
                        DupFileToKeep = Scene
                    elif stash.startsWithInList(whitelist, Scene['files'][0]['path']) and not stash.startsWithInList(whitelist, DupFileToKeep['files'][0]['path']):
                        logReason(DupFileToKeep, Scene, f"not whitelist vs whitelist")
                        DupFileToKeep = Scene
                    elif isTaggedExcluded(Scene) and not isTaggedExcluded(DupFileToKeep):
                        logReason(DupFileToKeep, Scene, f"not ExcludeTag vs ExcludeTag")
                        DupFileToKeep = Scene
                    elif allThingsEqual(DupFileToKeep, Scene):
                        # Only do below checks if all imporant things are equal.
                        if stash.startsWithInList(blacklist, DupFileToKeep['files'][0]['path']) and not stash.startsWithInList(blacklist, Scene['files'][0]['path']):
                            logReason(DupFileToKeep, Scene, f"blacklist vs not blacklist")
                            DupFileToKeep = Scene
                        elif stash.startsWithInList(blacklist, DupFileToKeep['files'][0]['path']) and stash.startsWithInList(blacklist, Scene['files'][0]['path']) and stash.indexStartsWithInList(blacklist, DupFileToKeep['files'][0]['path']) > stash.indexStartsWithInList(blacklist, Scene['files'][0]['path']):
                            logReason(DupFileToKeep, Scene, f"blacklist-index {stash.indexStartsWithInList(blacklist, DupFileToKeep['files'][0]['path'])} > {stash.indexStartsWithInList(blacklist, Scene['files'][0]['path'])}")
                            DupFileToKeep = Scene
                        elif stash.startsWithInList(graylist, Scene['files'][0]['path']) and not stash.startsWithInList(graylist, DupFileToKeep['files'][0]['path']):
                            logReason(DupFileToKeep, Scene, f"not graylist vs graylist")
                            DupFileToKeep = Scene
                        elif stash.startsWithInList(graylist, Scene['files'][0]['path']) and stash.startsWithInList(graylist, DupFileToKeep['files'][0]['path']) and stash.indexStartsWithInList(graylist, DupFileToKeep['files'][0]['path']) > stash.indexStartsWithInList(graylist, Scene['files'][0]['path']):
                            logReason(DupFileToKeep, Scene, f"graylist-index {stash.indexStartsWithInList(graylist, DupFileToKeep['files'][0]['path'])} > {stash.indexStartsWithInList(graylist, Scene['files'][0]['path'])}")
                            DupFileToKeep = Scene
                        elif favorLongerFileName and len(DupFileToKeep['files'][0]['path']) < len(Scene['files'][0]['path']) and not isWorseKeepCandidate(DupFileToKeep, Scene):
                            logReason(DupFileToKeep, Scene, f"path-len {len(DupFileToKeep['files'][0]['path'])} < {len(Scene['files'][0]['path'])}")
                            DupFileToKeep = Scene
                        elif favorLargerFileSize and int(DupFileToKeep['files'][0]['size']) < int(Scene['files'][0]['size']) and not isWorseKeepCandidate(DupFileToKeep, Scene):
                            logReason(DupFileToKeep, Scene, f"size {DupFileToKeep['files'][0]['size']} < {Scene['files'][0]['size']}")
                            DupFileToKeep = Scene
                        elif not favorLongerFileName and len(DupFileToKeep['files'][0]['path']) > len(Scene['files'][0]['path']) and not isWorseKeepCandidate(DupFileToKeep, Scene):
                            logReason(DupFileToKeep, Scene, f"path-len {len(DupFileToKeep['files'][0]['path'])} > {len(Scene['files'][0]['path'])}")
                            DupFileToKeep = Scene
                        elif not favorLargerFileSize and int(DupFileToKeep['files'][0]['size']) > int(Scene['files'][0]['size']) and not isWorseKeepCandidate(DupFileToKeep, Scene):
                            logReason(DupFileToKeep, Scene, f"size {DupFileToKeep['files'][0]['size']} > {Scene['files'][0]['size']}")
                            DupFileToKeep = Scene
                else:
                    DupFileToKeep = Scene
                # stash.Trace(f"DupFileToKeep = {DupFileToKeep}")
                stash.Debug(f"KeepID={DupFileToKeep['id']}, ID={DupFile['id']} duration=({Scene['files'][0]['duration']}), Size=({Scene['files'][0]['size']}), Res=({Scene['files'][0]['width']} x {Scene['files'][0]['height']}) Name={Scene['files'][0]['path']}, KeepPath={DupFileToKeep['files'][0]['path']}", toAscii=True)
            else:
                stash.Error(f"Scene does NOT exist; path={Scene['files'][0]['path']}; ID={Scene['id']}")
        
        for DupFile in DupFileDetailList:
            if DupFileToKeep != None and DupFile['id'] != DupFileToKeep['id']:
                if merge:
                    result = stash.mergeMetadata(DupFile, DupFileToKeep)
                    if result != "Nothing To Merge":
                        QtyMerge += 1
                didAddTag = False
                if stash.startsWithInList(whitelist, DupFile['files'][0]['path']) and (not whitelistDelDupInSameFolder or not hasSameDir(DupFile['files'][0]['path'], DupFileToKeep['files'][0]['path'])):
                    QtySkipForDel+=1
                    if isSwapCandidate(DupFileToKeep, DupFile):
                        if merge:
                            stash.mergeMetadata(DupFileToKeep, DupFile)
                        if toRecycleBeforeSwap:
                            sendToTrash(DupFile['files'][0]['path'])
                        stash.Log(f"Moving better file '{DupFileToKeep['files'][0]['path']}' to '{DupFile['files'][0]['path']}'; SrcID={DupFileToKeep['id']};DescID={DupFile['id']};QtyDup={QtyDup};Set={QtyDupSet} of {qtyResults};QtySwap={QtySwap};QtySkipForDel={QtySkipForDel}", toAscii=True, printTo=LOG_STASH_N_PLUGIN)
                        try:
                            shutil.move(DupFileToKeep['files'][0]['path'], DupFile['files'][0]['path'])
                            QtySwap+=1
                        except Exception as e:
                            tb = traceback.format_exc()
                            stash.Error(f"Exception while moving file '{DupFileToKeep['files'][0]['path']}' to '{DupFile['files'][0]['path']}; SrcID={DupFileToKeep['id']};DescID={DupFile['id']}'; Error: {e}\nTraceBack={tb}")
                        DupFileToKeep = DupFile
                    else:
                        if dupWhitelistTagId and tagDuplicates:
                            didAddTag = setTagId_withRetry(duplicateWhitelistTag, DupFile, DupFileToKeep, ignoreAutoTag=True)
                        stash.Log(f"NOT processing duplicate, because it's in whitelist. '{DupFile['files'][0]['path']}';AddTagW={didAddTag};QtyDup={QtyDup};Set={QtyDupSet} of {qtyResults};QtySkipForDel={QtySkipForDel}", toAscii=True)
                else:
                    if isTaggedExcluded(DupFile):
                        QtyExcludeForDel+=1
                        stash.Log(f"Excluding file {DupFile['files'][0]['path']} because tagged for exclusion via tag {excludeDupFileDeleteTag};QtyDup={QtyDup};Set={QtyDupSet} of {qtyResults}")
                    else:
                        # ToDo: Add merge logic here
                        if deleteDup:
                            QtyDeleted += 1
                            DupFileName = DupFile['files'][0]['path']
                            DupFileNameOnly = pathlib.Path(DupFileName).stem
                            stash.Warn(f"Deleting duplicate '{DupFileName}';QtyDup={QtyDup};Set={QtyDupSet} of {qtyResults};QtyDeleted={QtyDeleted}", toAscii=True, printTo=LOG_STASH_N_PLUGIN)
                            if alternateTrashCanPath != "":
                                destPath = f"{alternateTrashCanPath }{os.sep}{DupFileNameOnly}"
                                if os.path.isfile(destPath):
                                    destPath = f"{alternateTrashCanPath }{os.sep}_{time.time()}_{DupFileNameOnly}"
                                shutil.move(DupFileName, destPath)
                            elif moveToTrashCan:
                                sendToTrash(DupFileName)
                            stash.destroyScene(DupFile['id'], delete_file=True)
                        elif tagDuplicates:
                            QtyTagForDel+=1
                            QtyTagForDelPaginate+=1
                            didAddTag = setTagId_withRetry(duplicateMarkForDeletion, DupFile, DupFileToKeep, ignoreAutoTag=True)
                            if fileHtmlReport != None:
                                stash.Debug(f"Adding scene {DupFile['id']} to HTML report.")
                                dupFileExist = True if os.path.isfile(DupFile['files'][0]['path']) else False
                                toKeepFileExist = True if os.path.isfile(DupFileToKeep['files'][0]['path']) else False
                                
                                fileHtmlReport.write(f"{htmlReportTableRow}")
                                
                                fileHtmlReport.write(f"{htmlReportTableData}<video {htmlReportVideoPreview} poster=\"{DupFile['paths']['screenshot']}\"><source src=\"{DupFile['paths'][previewOrStream]}\" type=\"video/mp4\"></video></td>")
                                fileHtmlReport.write(f"{htmlReportTableData}<a href=\"{stash.STASH_URL}/scenes/{DupFile['id']}\" target=\"_blank\" rel=\"noopener noreferrer\">{getPath(DupFile)}</a>")
                                fileHtmlReport.write(f"<p><table><tr class=\"scene-details\"><th>Res</th><th>Durration</th><th>BitRate</th><th>Codec</th><th>FrameRate</th><th>size</th><th>ID</th><th>index</th></tr>")
                                fileHtmlReport.write(f"<tr class=\"scene-details\"><td {getColor(getRes(DupFile), getRes(DupFileToKeep), True)}>{DupFile['files'][0]['width']}x{DupFile['files'][0]['height']}</td><td {getColor(DupFile['files'][0]['duration'], DupFileToKeep['files'][0]['duration'], True, True, htmlHighlightTimeDiff)}>{DupFile['files'][0]['duration']}</td><td {getColor(DupFile['files'][0]['bit_rate'], DupFileToKeep['files'][0]['bit_rate'])}>{DupFile['files'][0]['bit_rate']}</td><td {getColor(DupFile['files'][0]['video_codec'], DupFileToKeep['files'][0]['video_codec'])}>{DupFile['files'][0]['video_codec']}</td><td {getColor(DupFile['files'][0]['frame_rate'], DupFileToKeep['files'][0]['frame_rate'])}>{DupFile['files'][0]['frame_rate']}</td><td {getColor(DupFile['files'][0]['size'], DupFileToKeep['files'][0]['size'])}>{DupFile['files'][0]['size']}</td><td>{DupFile['id']}</td><td>{QtyTagForDel}</td></tr>")
                                
                                if DupFile['id'] in reasonDict:
                                    fileHtmlReport.write(f"<tr class=\"reason-details\"><td colspan='8'>Reason: {reasonDict[DupFile['id']]}</td></tr>")
                                # elif DupFileToKeep['id'] in reasonDict:
                                    # fileHtmlReport.write(f"<tr class=\"reason-details\"><td colspan='8'>Reason: {reasonDict[DupFileToKeep['id']]}</td></tr>")
                                elif int(DupFileToKeep['files'][0]['width']) * int(DupFileToKeep['files'][0]['height']) > int(DupFile['files'][0]['width']) * int(DupFile['files'][0]['height']):
                                    fileHtmlReport.write(f"<tr class=\"reason-details\"><td colspan='8'>Reason: Resolution {DupFile['files'][0]['width']}x{DupFile['files'][0]['height']} < {DupFileToKeep['files'][0]['width']}x{DupFileToKeep['files'][0]['height']}</td></tr>")
                                elif significantMoreTimeCompareToBetterVideo(DupFile, DupFileToKeep):
                                    if significantTimeDiffCheck(DupFile, DupFileToKeep):
                                        theReason = f"Significant-Duration: <b style='color:red;background-color:neon green;'>{DupFile['files'][0]['duration']} < {DupFileToKeep['files'][0]['duration']}</b>"
                                    else:
                                        theReason = f"Duration: {DupFile['files'][0]['duration']} < {DupFileToKeep['files'][0]['duration']}"
                                    fileHtmlReport.write(f"<tr class=\"reason-details\"><td colspan='8'>Reason: {theReason}</td></tr>")
                                elif isBetterVideo(DupFile, DupFileToKeep):
                                    fileHtmlReport.write(f"<tr class=\"reason-details\"><td colspan='8'>Reason: Better Video</td></tr>")
                                elif stash.startsWithInList(DupFileToKeep, DupFile['files'][0]['path']) and not stash.startsWithInList(whitelist, DupFile['files'][0]['path']):
                                    fileHtmlReport.write(f"<tr class=\"reason-details\"><td colspan='8'>Reason: not whitelist vs whitelist</td></tr>")
                                elif isTaggedExcluded(DupFileToKeep) and not isTaggedExcluded(DupFile):
                                    fileHtmlReport.write(f"<tr class=\"reason-details\"><td colspan='8'>Reason: not ExcludeTag vs ExcludeTag</td></tr>")
                                
                                fileHtmlReport.write("</table>")
                                fileHtmlReport.write(f"<button class=\"link-button\" title=\"Delete file and remove scene from stash\" value=\"Duplicate\" id=\"{DupFile['id']}\">[Delete]</button>")
                                if dupFileExist:
                                    fileHtmlReport.write(f"<button class=\"link-button\" title=\"Remove duplicate tag from scene\" value=\"RemoveDupTag\" id=\"{DupFile['id']}\">[Remove Tag]</button>")
                                fileHtmlReport.write(f"<button class=\"link-button\" title=\"Add exclude scene from deletion tag\" value=\"AddExcludeTag\" id=\"{DupFile['id']}\">[Add Exclude Tag]</button>")
                                fileHtmlReport.write(f"<button class=\"link-button\" title=\"Merge duplicate scene tags with ToKeep scene tags\" value=\"mergeTags\" id=\"{DupFile['id']}:{DupFileToKeep['id']}\">[Merge Tags]</button>")
                                if dupFileExist:
                                    fileHtmlReport.write(f"<a class=\"link-items\" title=\"Open folder\" href=\"file://{getPath(DupFile, True)}\">[Folder]</a>")
                                    fileHtmlReport.write(f"<a class=\"link-items\" title=\"Play file locally\" href=\"file://{getPath(DupFile)}\">[Play]</a>")
                                else:
                                    fileHtmlReport.write("<b style='color:red;'>[File NOT Exist]<b>")
                                # ToDo: Add following buttons:
                                #       Copy file name from duplicate to ToKeep
                                #       Copy *file* from duplicate to ToKeep
                                fileHtmlReport.write("</p></td>")
                                
                                fileHtmlReport.write(f"{htmlReportTableData}<video {htmlReportVideoPreview} poster=\"{DupFileToKeep['paths']['screenshot']}\"><source src=\"{DupFileToKeep['paths'][previewOrStream]}\" type=\"video/mp4\"></video></td>")
                                fileHtmlReport.write(f"{htmlReportTableData}<a href=\"{stash.STASH_URL}/scenes/{DupFileToKeep['id']}\" target=\"_blank\" rel=\"noopener noreferrer\">{getPath(DupFileToKeep)}</a>")
                                fileHtmlReport.write(f"<p><table><tr class=\"scene-details\"><th>Res</th><th>Durration</th><th>BitRate</th><th>Codec</th><th>FrameRate</th><th>size</th><th>ID</th></tr>")
                                fileHtmlReport.write(f"<tr class=\"scene-details\"><td>{DupFileToKeep['files'][0]['width']}x{DupFileToKeep['files'][0]['height']}</td><td>{DupFileToKeep['files'][0]['duration']}</td><td>{DupFileToKeep['files'][0]['bit_rate']}</td><td>{DupFileToKeep['files'][0]['video_codec']}</td><td>{DupFileToKeep['files'][0]['frame_rate']}</td><td>{DupFileToKeep['files'][0]['size']}</td><td>{DupFileToKeep['id']}</td></tr></table>")
                                fileHtmlReport.write(f"<button class=\"link-button\" title=\"Delete [DupFileToKeep] and remove scene from stash\" value=\"ToKeep\" id=\"{DupFileToKeep['id']}\">[Delete]</button>")
                                if isTaggedExcluded(DupFileToKeep):
                                    fileHtmlReport.write(f"<button class=\"link-button\" title=\"Remove exclude scene from deletion tag\" value=\"RemoveExcludeTag\" id=\"{DupFileToKeep['id']}\">[Remove Exclude Tag]</button>")
                                fileHtmlReport.write(f"<a class=\"link-items\" title=\"Open folder\" href=\"file://{getPath(DupFileToKeep, True)}\">[Folder]</a>")
                                if toKeepFileExist:
                                    fileHtmlReport.write(f"<a class=\"link-items\" title=\"Play file locally\" href=\"file://{getPath(DupFileToKeep)}\">[Play]</a>")
                                else:
                                    fileHtmlReport.write("<b style='color:red;'>[File NOT Exist]<b>")
                                fileHtmlReport.write(f"</p></td>")
                                
                                fileHtmlReport.write("</tr>\n")
                                
                                if QtyTagForDelPaginate >= htmlReportPaginate:
                                    QtyTagForDelPaginate = 0
                                    fileHtmlReport.write("</table>\n")
                                    homeHtmReportLink = f"<a class=\"link-items\" title=\"Home Page\" href=\"file://{htmlReportNameHomePage}\">[Home]</a>"
                                    prevHtmReportLink = ""
                                    if PaginateId > 0:
                                        if PaginateId > 1:
                                            prevHtmReport = htmlReportNameHomePage.replace(".html", f"_{PaginateId-1}.html")
                                        else:
                                            prevHtmReport = htmlReportNameHomePage
                                        prevHtmReportLink = f"<a class=\"link-items\" title=\"Previous Page\" href=\"file://{prevHtmReport}\">[Prev]</a>"
                                    nextHtmReport = htmlReportNameHomePage.replace(".html", f"_{PaginateId+1}.html")
                                    nextHtmReportLink = f"<a class=\"link-items\" title=\"Next Page\" href=\"file://{nextHtmReport}\">[Next]</a>"
                                    fileHtmlReport.write(f"<center><table><tr><td>{homeHtmReportLink}</td><td>{prevHtmReportLink}</td><td>{nextHtmReportLink}</td></tr></table></center>")
                                    fileHtmlReport.write(f"{stash.Setting('htmlReportPostfix')}")
                                    fileHtmlReport.close()
                                    PaginateId+=1
                                    fileHtmlReport = open(nextHtmReport, "w")
                                    fileHtmlReport.write(f"{getHtmlReportTableRow(qtyResults)}\n")
                                    if PaginateId > 1:
                                        prevHtmReport = htmlReportNameHomePage.replace(".html", f"_{PaginateId-1}.html")
                                    else:
                                        prevHtmReport = htmlReportNameHomePage
                                    prevHtmReportLink = f"<a class=\"link-items\" title=\"Previous Page\" href=\"file://{prevHtmReport}\">[Prev]</a>"
                                    if len(DupFileSets) > (QtyTagForDel + htmlReportPaginate):
                                        nextHtmReport = htmlReportNameHomePage.replace(".html", f"_{PaginateId+1}.html")
                                        nextHtmReportLink = f"<a class=\"link-items\" title=\"Next Page\" href=\"file://{nextHtmReport}\">[Next]</a>"
                                        fileHtmlReport.write(f"<center><table><tr><td>{homeHtmReportLink}</td><td>{prevHtmReportLink}</td><td>{nextHtmReportLink}</td></tr></table></center>")
                                    else:
                                        stash.Debug(f"DupFileSets Qty = {len(DupFileSets)}; DupFileDetailList Qty = {len(DupFileDetailList)}; QtyTagForDel = {QtyTagForDel}; htmlReportPaginate = {htmlReportPaginate}; QtyTagForDel + htmlReportPaginate = {QtyTagForDel+htmlReportPaginate}")
                                        fileHtmlReport.write(f"<center><table><tr><td>{homeHtmReportLink}</td><td>{prevHtmReportLink}</td></tr></table></center>")
                                    fileHtmlReport.write(f"{stash.Setting('htmlReportTable')}\n")
                                    fileHtmlReport.write(f"{htmlReportTableRow}{htmlReportTableHeader}Scene</th>{htmlReportTableHeader}Duplicate to Delete</th>{htmlReportTableHeader}Scene-ToKeep</th>{htmlReportTableHeader}Duplicate to Keep</th></tr>\n")
                            
                            if graylistTagging and stash.startsWithInList(graylist, DupFile['files'][0]['path']):
                                stash.addTag(DupFile, graylistMarkForDeletion, ignoreAutoTag=True)
                            if didAddTag:
                                QtyNewlyTag+=1
                            if QtyTagForDel == 1:
                                stash.Log(f"Tagging duplicate {DupFile['files'][0]['path']} for deletion with tag {duplicateMarkForDeletion}", toAscii=True, printTo=LOG_STASH_N_PLUGIN)
                            else:
                                didAddTag = 1 if didAddTag else 0
                                stash.Log(f"Tagging duplicate {DupFile['files'][0]['path']} for deletion;AddTag={didAddTag};Qty={QtyDup};Set={QtyDupSet} of {qtyResults};NewlyTag={QtyNewlyTag};isTag={QtyTagForDel}", toAscii=True, printTo=LOG_STASH_N_PLUGIN)
        stash.Trace(SepLine)
        if maxDupToProcess > 0 and QtyDup > maxDupToProcess:
            break
    
    if fileHtmlReport != None:
        fileHtmlReport.write("</table>\n")
        if PaginateId > 0:
            homeHtmReportLink = f"<a class=\"link-items\" title=\"Home Page\" href=\"file://{htmlReportNameHomePage}\">[Home]</a>"
            if PaginateId > 1:
                prevHtmReport = htmlReportNameHomePage.replace(".html", f"_{PaginateId-1}.html")
            else:
                prevHtmReport = htmlReportNameHomePage
            prevHtmReportLink = f"<a class=\"link-items\" title=\"Previous Page\" href=\"file://{prevHtmReport}\">[Prev]</a>"
            fileHtmlReport.write(f"<center><table><tr><td>{homeHtmReportLink}</td><td>{prevHtmReportLink}</td></tr></table></center>")
        fileHtmlReport.write(f"<h2>Total Tagged for Deletion {QtyTagForDel}</h2>\n")
        # ToDo: Add a menu after the report with the following options:
        #       Delete all Dup tagged files (any match)
        #       Remove all Dup tagged files (Just remove from stash, and leave file)
        #       Delete Blacklist Dup tagged files
        #       Remove Blacklist Dup tagged files
        #       Delete all Dup tagged files (Exact Match)
        #       Remove all Dup tagged files (Exact Match)
        #       Delete all Dup tagged files (High Match)
        #       Remove all Dup tagged files (High Match)
        #       Delete all Dup tagged files (Medium Match)
        #       Remove all Dup tagged files (Medium Match)
        #       Delete all Dup tagged files (Low Match)
        #       Remove all Dup tagged files (Low Match)
        #       Clear dup tag from all scenes
        #       Delete dup tag
        #       Clear ExcludeDup tag
        #       Delete ExcludeDup tag
        #       Clear GraylistMarkForDel tag
        #       Delete GraylistMarkForDel tag
        #       Clear all DupFileManager created tags
        #       Delete all DupFileManager created tags
        fileHtmlReport.write(f"{stash.Setting('htmlReportPostfix')}")
        fileHtmlReport.close()
        # ToDo: Add a better working method to open HTML page htmlReportName
        stash.Log(f"Opening web page {htmlReportName}")
        import webbrowser
        webbrowser.open(htmlReportName, new=2, autoraise=True)
        os.system(f"start file://{htmlReportName}")
        stash.Log(f"************************************************************", printTo = stash.LogTo.STASH)
        stash.Log(f"************************************************************", printTo = stash.LogTo.STASH)
        stash.Log(f"View Stash duplicate report using the following link:         file://{htmlReportName}", printTo = stash.LogTo.STASH)
        stash.Log(f"************************************************************", printTo = stash.LogTo.STASH)
        stash.Log(f"************************************************************", printTo = stash.LogTo.STASH)

        
    stash.Debug("#####################################################")
    stash.Log(f"QtyDupSet={QtyDupSet}, QtyDup={QtyDup}, QtyDeleted={QtyDeleted}, QtySwap={QtySwap}, QtyTagForDel={QtyTagForDel}, QtySkipForDel={QtySkipForDel}, QtyExcludeForDel={QtyExcludeForDel}, QtyExactDup={QtyExactDup}, QtyAlmostDup={QtyAlmostDup}, QtyMerge={QtyMerge}, QtyRealTimeDiff={QtyRealTimeDiff}", printTo=LOG_STASH_N_PLUGIN)
    killScanningJobs()
    if cleanAfterDel and deleteDup:
        stash.Log("Adding clean jobs to the Task Queue", printTo=LOG_STASH_N_PLUGIN)
        stash.metadata_clean()
        stash.metadata_clean_generated()
        stash.optimise_database()
    if doGeneratePhash:
        stash.metadata_generate({"phashes": True})

def findCurrentTagId(tagNames):
    tagNames = [i for n, i in enumerate(tagNames) if i not in tagNames[:n]]
    for tagName in tagNames:
        tagId = stash.find_tags(q=tagName)
        if len(tagId) > 0 and 'id' in tagId[0]:
            stash.Debug("Using tag name {tagName} with Tag ID {tagId[0]['id']}")
            return tagId[0]['id']
    return "-1"

def manageTagggedDuplicates(deleteScenes=False, clearTag=False, setGrayListTag=False):
    tagId = findCurrentTagId([duplicateMarkForDeletion, base1_duplicateWhitelistTag, base2_duplicateWhitelistTag, 'DuplicateMarkForDeletion', '_DuplicateMarkForDeletion'])
    if int(tagId) < 0:
        stash.Warn(f"Could not find tag ID for tag '{duplicateMarkForDeletion}'.")
        return

    excludedTags = [duplicateMarkForDeletion]
    if clearAllDupfileManagerTags:
        excludedTags = [duplicateMarkForDeletion, duplicateWhitelistTag, excludeDupFileDeleteTag, graylistMarkForDeletion, longerDurationLowerResolution]
    
    QtyDup = 0
    QtyDeleted = 0
    QtyClearedTags = 0
    QtySetGraylistTag = 0
    QtyFailedQuery = 0
    stash.Debug("#########################################################################")
    stash.startSpinningProcessBar()
    scenes = stash.find_scenes(f={"tags": {"value":tagId, "modifier":"INCLUDES"}}, fragment='id tags {id name} files {path width height duration size video_codec bit_rate frame_rate} details')
    stash.stopSpinningProcessBar()
    qtyResults = len(scenes)
    stash.Log(f"Found {qtyResults} scenes with tag ({duplicateMarkForDeletion})")
    stash.setProgressBarIter(qtyResults)
    for scene in scenes:
        QtyDup += 1
        stash.progressBar(QtyDup, qtyResults)
        # scene = stash.find_scene(sceneID['id'])
        # if scene == None or len(scene) == 0:
            # stash.Warn(f"Could not get scene data for scene ID {scene['id']}.")
            # QtyFailedQuery += 1
            # continue
        # stash.Trace(f"scene={scene}")
        if clearTag:
            QtyClearedTags += 1 
            # ToDo: Add logic to exclude graylistMarkForDeletion
            tags = [int(item['id']) for item in scene["tags"] if item['name'] not in excludedTags]
            # if clearAllDupfileManagerTags:
                # tags = []
                # for tag in scene["tags"]:
                    # if tag['name'] in excludedTags:
                        # continue
                    # tags += [int(tag['id'])]
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
            stash.Log(f"Updating scene with {dataDict};QtyClearedTags={QtyClearedTags};Count={QtyDup} of {qtyResults}")
            stash.updateScene(dataDict)
            # stash.removeTag(scene, duplicateMarkForDeletion)
        elif setGrayListTag:
            if stash.startsWithInList(graylist, scene['files'][0]['path']):
                QtySetGraylistTag+=1
                if stash.addTag(scene, graylistMarkForDeletion, ignoreAutoTag=True):
                    stash.Log(f"Added tag {graylistMarkForDeletion} to scene {scene['files'][0]['path']};QtySetGraylistTag={QtySetGraylistTag};Count={QtyDup} of {qtyResults}")
                else:
                    stash.Trace(f"Scene already had tag {graylistMarkForDeletion}; {scene['files'][0]['path']}")
        elif deleteScenes:
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
            result = stash.destroyScene(scene['id'], delete_file=True)
            QtyDeleted += 1
            stash.Debug(f"destroyScene result={result} for file {DupFileName};QtyDeleted={QtyDeleted};Count={QtyDup} of {qtyResults}", toAscii=True)
        else:
            stash.Error("manageTagggedDuplicates called with invlaid input arguments. Doing early exit.")
            return
    stash.Debug("#####################################################")
    stash.Log(f"QtyDup={QtyDup}, QtyClearedTags={QtyClearedTags}, QtySetGraylistTag={QtySetGraylistTag}, QtyDeleted={QtyDeleted}, QtyFailedQuery={QtyFailedQuery}", printTo=LOG_STASH_N_PLUGIN)
    killScanningJobs()
    if deleteScenes:
        if cleanAfterDel:
            stash.Log("Adding clean jobs to the Task Queue", printTo=LOG_STASH_N_PLUGIN)
            stash.metadata_clean()
            stash.metadata_clean_generated()
            stash.optimise_database()
        if doNotGeneratePhash:
            stash.metadata_generate({"phashes": True})

def removeDupTag():
    if 'removeDupTag' not in stash.JSON_INPUT['args']:
        stash.Error(f"Could not find removeDupTag in JSON_INPUT ({stash.JSON_INPUT['args']})")
        return
    sceneToRemoveTag = stash.JSON_INPUT['args']['removeDupTag']
    stash.removeTag(sceneToRemoveTag, duplicateMarkForDeletion)
    stash.Log(f"Done removing tag from scene {sceneToRemoveTag}.")

def addExcludeForDelTag():
    if 'addExcludeForDelTag' not in stash.JSON_INPUT['args']:
        stash.Error(f"Could not find addExcludeForDelTag in JSON_INPUT ({stash.JSON_INPUT['args']})")
        return
    scene = stash.JSON_INPUT['args']['addExcludeForDelTag']
    stash.addTag(scene, excludeDupFileDeleteTag)
    stash.Log(f"Done adding exclude tag to scene {scene}.")

def removeExcludeForDelTag():
    if 'removeExcludeForDelTag' not in stash.JSON_INPUT['args']:
        stash.Error(f"Could not find removeExcludeForDelTag in JSON_INPUT ({stash.JSON_INPUT['args']})")
        return
    scene = stash.JSON_INPUT['args']['removeExcludeForDelTag']
    stash.removeTag(scene, excludeDupFileDeleteTag)
    stash.Log(f"Done removing exclude tag from scene {scene}.")

def mergeTags():
    if 'mergeScenes' not in stash.JSON_INPUT['args']:
        stash.Error(f"Could not find mergeScenes in JSON_INPUT ({stash.JSON_INPUT['args']})")
        return
    mergeScenes = stash.JSON_INPUT['args']['mergeScenes']
    scenes = mergeScenes.split(":")
    if len(scenes) < 2:
        stash.Error(f"Could not get both scenes from string {mergeScenes}")
        return
    stash.Log(f"Merging tags for scene {scenes[0]} and scene {scenes[1]}")
    scene1 = stash.find_scene(int(scenes[0]))
    scene2 = stash.find_scene(int(scenes[1]))
    stash.mergeMetadata(scene1, scene2)
    stash.Log(f"Done merging scenes for scene {scenes[0]} and scene {scenes[1]}")

# ToDo: Add additional menu items option only for bottom of report:
#   Remove from stash all files no longer part of stash library 
#   Remove from stash all files in the Exclusion list (Not supporting regexps)

try:
    if stash.PLUGIN_TASK_NAME == "tag_duplicates_task":
        mangeDupFiles(tagDuplicates=True, merge=mergeDupFilename)
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif stash.PLUGIN_TASK_NAME == "delete_tagged_duplicates_task":
        manageTagggedDuplicates(deleteScenes=True)
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif stash.PLUGIN_TASK_NAME == "delete_duplicates_task":
        mangeDupFiles(deleteDup=True, merge=mergeDupFilename)
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif stash.PLUGIN_TASK_NAME == "clear_duplicate_tags_task":
        manageTagggedDuplicates(clearTag=True)
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif stash.PLUGIN_TASK_NAME == "graylist_tag_task":
        manageTagggedDuplicates(setGrayListTag=True)
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif stash.PLUGIN_TASK_NAME == "generate_phash_task":
        stash.metadata_generate({"phashes": True})
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif stash.PLUGIN_TASK_NAME == "remove_a_duplicate_tag":
        removeDupTag()
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif stash.PLUGIN_TASK_NAME == "add_an_exclude_tag":
        addExcludeForDelTag()
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif stash.PLUGIN_TASK_NAME == "remove_an_exclude_tag":
        removeExcludeForDelTag()
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif stash.PLUGIN_TASK_NAME == "merge_tags":
        mergeTags()
        stash.Debug(f"{stash.PLUGIN_TASK_NAME} EXIT")
    elif parse_args.dup_tag:
        stash.PLUGIN_TASK_NAME = "dup_tag"
        mangeDupFiles(tagDuplicates=True, merge=mergeDupFilename)
        stash.Debug(f"Tag duplicate EXIT")
    elif parse_args.del_tag:
        stash.PLUGIN_TASK_NAME = "del_tag"
        manageTagggedDuplicates(deleteScenes=True)
        stash.Debug(f"Delete Tagged duplicates EXIT")
    elif parse_args.clear_tag:
        stash.PLUGIN_TASK_NAME = "clear_tag"
        manageTagggedDuplicates(clearTag=True)
        stash.Debug(f"Clear duplicate tags EXIT")
    elif parse_args.remove:
        stash.PLUGIN_TASK_NAME = "remove"
        mangeDupFiles(deleteDup=True, merge=mergeDupFilename)
        stash.Debug(f"Delete duplicate EXIT")
    else:
        stash.Log(f"Nothing to do!!! (PLUGIN_ARGS_MODE={stash.PLUGIN_TASK_NAME})")
except Exception as e:
    tb = traceback.format_exc()
    
    stash.Error(f"Exception while running DupFileManager Task({stash.PLUGIN_TASK_NAME}); Error: {e}\nTraceBack={tb}")
    killScanningJobs()
    stash.convertToAscii = False
    stash.Error(f"Error: {e}\nTraceBack={tb}")

stash.Log("\n*********************************\nEXITING   ***********************\n*********************************")

# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager
config = {
    # Character used to seperate items on the whitelist, blacklist, and graylist
    "listSeparator" : ",",
    # If enabled, adds the primary duplicate path to the scene detail.
    "addPrimaryDupPathToDetails" : True,
   
    # If enabled, ignore reparsepoints. For Windows NT drives only.
    "ignoreReparsepoints" : True,
    # If enabled, ignore symbolic links.
    "ignoreSymbolicLinks" : True,
    
    
    # If enabled, swap higher resolution duplicate files to preferred path.
    "swapHighRes" : True,
    # If enabled, swap longer length media files to preferred path. Longer will be determine by significantLongerTime value.
    "swapLongLength" : True,
    # If enabled, swap longer file name to preferred path.
    "swapLongFileName" : False,
    
    # If enabled, when finding exact duplicate files, keep file with the shorter name. The default is to keep file name with the longer name.
    "keepShorterFileName" : False,
    # If enabled, when finding duplicate files, keep media with the shorter time length. The default is to keep media with longer time length.
    "keepShorterLength" : False,
    # If enabled, when finding duplicate files, keep media with the lower resolution. The default is to keep media with higher resolution.
    "keepLowerResolution" : False,
    # If enabled, keep duplicate media with high resolution over media with significant longer time.
    "keepHighResOverLen" : False, # Requires keepBothHighResAndLongerLen = False
    # The threshold as to what percentage is consider a significant longer time. Default is 15% longer.
    "significantLongerTime" : 15, # 15% longer time
    # If enabled, keep both duplicate files if the LOWER resolution file is significantly longer.
    "keepBothHighResAndLongerLen" : True,
    
    # Define ignore list to avoid specific directories. No action is taken on any file in the ignore list.
    "ignore_paths": [],     #Example: "ignore_paths": ['C:\\SomeMediaPath\\subpath', "E:\\YetAnotherPath\\subpath', "E:\\YetAnotherPath\\secondSubPath']
    # Keep empty to check all paths, or populate it with the only paths to check for duplicates
    "onlyCheck_paths": [],     #Example: "onlyCheck_paths": ['C:\\SomeMediaPath\\subpath', "E:\\YetAnotherPath\\subpath', "E:\\YetAnotherPath\\secondSubPath']
    # Alternative path to move duplicate files. Path needs to be in the same drive as the duplicate file.
    "dup_path": "", #Example: "C:\\TempDeleteFolder"
    
    # The following fields are ONLY used when running DupFileManager in script mode
    "endpoint_Scheme" : "http", # Define endpoint to use when contacting the Stash server
    "endpoint_Host" : "0.0.0.0", # Define endpoint to use when contacting the Stash server
    "endpoint_Port" : 9999, # Define endpoint to use when contacting the Stash server
}

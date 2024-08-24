# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager
config = {
    # If enabled, adds the primary duplicate path to the scene detail.
    "addPrimaryDupPathToDetails" : True,
    # Alternative path to move duplicate files.
    "dup_path": "", #Example: "C:\\TempDeleteFolder"
    # If enabled, swap higher resolution duplicate files to preferred path.
    "swapHighRes" : True,
    # If enabled, swap longer length media files to preferred path. Longer will be determine by significantLongerTime value.
    "swapLongLength" : True,
    # The threshold as to what percentage is consider a significant shorter time.
    "significantTimeDiff" : .90, # 95% threshold
    # If enabled, moves destination file to recycle bin before swapping Hi-Res file.
    "toRecycleBeforeSwap" : True,
    # Character used to seperate items on the whitelist, blacklist, and graylist
    "listSeparator" : ",",
    
    # The following fields are ONLY used when running DupFileManager in script mode
    "endpoint_Scheme" : "http", # Define endpoint to use when contacting the Stash server
    "endpoint_Host" : "0.0.0.0", # Define endpoint to use when contacting the Stash server
    "endpoint_Port" : 9999, # Define endpoint to use when contacting the Stash server
}

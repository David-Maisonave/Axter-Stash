# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager
config = {
    # Define white list of preferential paths to determine which duplicate should be the primary.
    "whitelist_paths": [],     #Example: "whitelist_paths": ['C:\SomeMediaPath\subpath', 'E:\YetAnotherPath\subpath', 'E:\YetAnotherPath\secondSubPath']
    # Define black list to determine which duplicates should be deleted first.
    "blacklist_paths": [],     #Example: "blacklist_paths": ['C:\SomeMediaPath\subpath', 'E:\YetAnotherPath\subpath', 'E:\YetAnotherPath\secondSubPath']
    # Define ignore list to avoid specific directories. No action is taken on any file in the ignore list.
    "ignore_paths": [],     #Example: "ignore_paths": ['C:\SomeMediaPath\subpath', 'E:\YetAnotherPath\subpath', 'E:\YetAnotherPath\secondSubPath']
    # Keep empty to check all paths, or populate it with the only paths to check for duplicates
    "onlyCheck_paths": [],     #Example: "onlyCheck_paths": ['C:\SomeMediaPath\subpath', 'E:\YetAnotherPath\subpath', 'E:\YetAnotherPath\secondSubPath']
    # Alternative path to move duplicate files. Path needs to be in the same drive as the duplicate file.
    "dup_path": "", #Example: "C:\TempDeleteFolder"
    
    # The following fields are ONLY used when running DupFileManager in script mode
    "endpoint_Scheme" : "http", # Define endpoint to use when contacting the Stash server
    "endpoint_Host" : "0.0.0.0", # Define endpoint to use when contacting the Stash server
    "endpoint_Port" : 9999, # Define endpoint to use when contacting the Stash server
}

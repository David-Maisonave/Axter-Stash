# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager
config = {
    # Character used to seperate items on the whitelist, blacklist, and graylist
    "listSeparator" : ",",
    # If enabled, adds the primary duplicate path to the scene detail.
    "addPrimaryDupPathToDetails" : True,
    # Alternative path to move duplicate files. Path needs to be in the same drive as the duplicate file.
    "dup_path": "", #Example: "C:\\TempDeleteFolder"
    
    # The following fields are ONLY used when running DupFileManager in script mode
    "endpoint_Scheme" : "http", # Define endpoint to use when contacting the Stash server
    "endpoint_Host" : "0.0.0.0", # Define endpoint to use when contacting the Stash server
    "endpoint_Port" : 9999, # Define endpoint to use when contacting the Stash server
}

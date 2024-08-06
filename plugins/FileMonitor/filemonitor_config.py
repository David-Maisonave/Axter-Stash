# Description: This is a Stash plugin which updates Stash if any changes occurs in the Stash library paths.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link: https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/FileMonitor
config = {
    # Enable to run metadata_generate (Generate Content) after metadata scan.
    "runGenerateContent": False,
    # Enable to run scan when triggered by on_any_event.
    "onAnyEvent": False,
    # Timeout in seconds. This is how often it will check if a stop signal is sent.
    "timeOut": 60,
    # Enable to exit FileMonitor by creating special file in plugin folder\working
    "createSpecFileToExit": True,
    # Enable to delete special file imediately after it's created in stop process
    "deleteSpecFileInStop": False,
    # When enabled, if CREATE flag is triggered, DupFileManager task is called if the plugin is installed.
    "onCreateCallDupFileManager": False, # Not yet implemented!!!!
    
    # The following fields are ONLY used when running FileMonitor in script mode
    "endpoint_Scheme" : "http", # Define endpoint to use when contacting the Stash server
    "endpoint_Host" : "0.0.0.0", # Define endpoint to use when contacting the Stash server
    "endpoint_Port" : 9999, # Define endpoint to use when contacting the Stash server
}

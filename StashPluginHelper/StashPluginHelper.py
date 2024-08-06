import stashapi.log as stashLog # stashapi.log by default for error and critical logging
from stashapi.stashapp import StashInterface
from logging.handlers import RotatingFileHandler
import inspect
import sys
import os
import pathlib
import logging
import json
import __main__

# StashPluginHelper (By David Maisonave aka Axter)
    # See end of this file for example usage
    # Log Features:
        # Can optionally log out to multiple outputs for each Log or Trace call.
        # Logging includes source code line number
        # Sets a maximum plugin log file size
    # Stash Interface Features:
        # Sets STASH_INTERFACE with StashInterface
        # Gets STASH_URL value from command line argument and/or from STDIN_READ
        # Sets FRAGMENT_SERVER based on command line arguments or STDIN_READ
        # Sets PLUGIN_ID based on the main script file name (in lower case)
        # Gets PLUGIN_TASK_NAME value
        # Sets pluginSettings (The plugin UI settings)
    # Misc Features:
        # Gets DRY_RUN value from command line argument and/or from UI and/or from config file
        # Gets DEBUG_TRACING value from command line argument and/or from UI and/or from config file
        # Sets RUNNING_IN_COMMAND_LINE_MODE to True if detects multiple arguments
        # Sets CALLED_AS_STASH_PLUGIN to True if it's able to read from STDIN_READ
class StashPluginHelper:
    # Primary Members for external reference
    PLUGIN_TASK_NAME = None
    PLUGIN_ID = None
    PLUGIN_CONFIGURATION = None
    pluginSettings = None
    pluginConfig = None
    STASH_INTERFACE = None
    STASH_URL = None
    STASH_CONFIGURATION = None
    JSON_INPUT = None
    DEBUG_TRACING = False
    DRY_RUN = False
    CALLED_AS_STASH_PLUGIN = False
    RUNNING_IN_COMMAND_LINE_MODE = False
    
    # printTo argument
    LOG_TO_FILE = 1
    LOG_TO_CONSOLE = 2  # Note: Only see output when running in command line mode. In plugin mode, this output is lost.
    LOG_TO_STDERR = 4   # Note: In plugin mode, output to StdErr ALWAYS gets sent to stash logging as an error.
    LOG_TO_STASH = 8
    LOG_TO_WARN = 16
    LOG_TO_ERROR = 32
    LOG_TO_CRITICAL = 64
    LOG_TO_ALL = LOG_TO_FILE + LOG_TO_CONSOLE + LOG_TO_STDERR + LOG_TO_STASH
    
    # Misc class variables
    MAIN_SCRIPT_NAME = None
    LOG_LEVEL = logging.INFO
    LOG_FILE_DIR = None
    LOG_FILE_NAME = None
    STDIN_READ = None
    FRAGMENT_SERVER = None
    logger = None
    
    # Prefix message value
    LEV_TRACE = "TRACE: "
    LEV_DBG = "DBG: "
    LEV_INF = "INF: "
    LEV_WRN = "WRN: "
    LEV_ERR = "ERR: "
    LEV_CRITICAL = "CRITICAL: "
    
    # Default format
    LOG_FORMAT = "[%(asctime)s] %(message)s"
    
    # Externally modifiable variables
    log_to_err_set = LOG_TO_FILE + LOG_TO_STDERR # This can be changed by the calling source in order to customize what targets get error messages
    log_to_norm = LOG_TO_FILE + LOG_TO_CONSOLE # Can be change so-as to set target output for normal logging
    log_to_wrn_set = LOG_TO_FILE + LOG_TO_STASH # This can be changed by the calling source in order to customize what targets get warning messages
    
    def __init__(self, 
                    debugTracing = None,            # Set debugTracing to True so as to output debug and trace logging
                    logFormat = LOG_FORMAT,         # Plugin log line format
                    dateFmt = "%y%m%d %H:%M:%S",    # Date format when logging to plugin log file
                    maxbytes = 2*1024*1024,         # Max size of plugin log file
                    backupcount = 2,                # Backup counts when log file size reaches max size
                    logToWrnSet = 0,                # Customize the target output set which will get warning logging
                    logToErrSet = 0,                # Customize the target output set which will get error logging
                    logToNormSet = 0,               # Customize the target output set which will get normal logging
                    logFilePath = "",               # Plugin log file. If empty, the log file name will be set based on current python file name and path
                    mainScriptName = "",            # The main plugin script file name (full path)
                    pluginID = "",
                    settings = None,                # Default settings for UI fields
                    config = None,                  # From pluginName_config.py or pluginName_setting.py
                    fragmentServer = None,
                    stash_url = None,               # Stash URL (endpoint URL) Example: http://localhost:9999
                    DebugTraceFieldName = "zzdebugTracing",
                    DryRunFieldName = "zzdryRun"):              
        if logToWrnSet: self.log_to_wrn_set = logToWrnSet
        if logToErrSet: self.log_to_err_set = logToErrSet
        if logToNormSet: self.log_to_norm = logToNormSet
        if stash_url and len(stash_url): self.STASH_URL = stash_url
        self.MAIN_SCRIPT_NAME = mainScriptName if mainScriptName != "" else __main__.__file__
        self.PLUGIN_ID = pluginID if pluginID != "" else pathlib.Path(self.MAIN_SCRIPT_NAME).stem.lower()
        print(f"self.MAIN_SCRIPT_NAME={self.MAIN_SCRIPT_NAME}, self.PLUGIN_ID={self.PLUGIN_ID}", file=sys.stderr)
        self.LOG_FILE_NAME = logFilePath if logFilePath != "" else f"{pathlib.Path(self.MAIN_SCRIPT_NAME).resolve().parent}{os.sep}{pathlib.Path(self.MAIN_SCRIPT_NAME).stem}.log" 
        self.LOG_FILE_DIR = pathlib.Path(self.LOG_FILE_NAME).resolve().parent 
        RFH = RotatingFileHandler(
            filename=self.LOG_FILE_NAME, 
            mode='a',
            maxBytes=maxbytes,
            backupCount=backupcount,
            encoding=None,
            delay=0
        )
        if fragmentServer:
            self.FRAGMENT_SERVER = fragmentServer
        else:
            self.FRAGMENT_SERVER = {'Scheme': 'http', 'Host': '0.0.0.0', 'Port': '9999', 'SessionCookie': {'Name': 'session', 'Value': '', 'Path': '', 'Domain': '', 'Expires': '0001-01-01T00:00:00Z', 'RawExpires': '', 'MaxAge': 0, 'Secure': False, 'HttpOnly': False, 'SameSite': 0, 'Raw': '', 'Unparsed': None}, 'Dir': os.path.dirname(pathlib.Path(self.MAIN_SCRIPT_NAME).resolve().parent), 'PluginDir': pathlib.Path(self.MAIN_SCRIPT_NAME).resolve().parent}
        
        if debugTracing: self.DEBUG_TRACING = debugTracing        
        if config:
            self.pluginConfig = config        
            if DebugTraceFieldName in self.pluginConfig:
                self.DEBUG_TRACING = self.pluginConfig[DebugTraceFieldName]
            if DryRunFieldName in self.pluginConfig:
                self.DRY_RUN = self.pluginConfig[DryRunFieldName]
                
        if len(sys.argv) > 1:
            RUNNING_IN_COMMAND_LINE_MODE = True
            if not debugTracing or not stash_url:
                for argValue in sys.argv[1:]:
                    if argValue.lower() == "--trace":
                        self.DEBUG_TRACING = True
                    elif argValue.lower() == "--dry_run" or argValue.lower() == "--dryrun":
                        self.DRY_RUN = True
                    elif ":" in argValue and not self.STASH_URL:
                        self.STASH_URL = argValue
            if self.STASH_URL:
                endpointUrlArr = self.STASH_URL.split(":")
                if len(endpointUrlArr) == 3:
                    self.FRAGMENT_SERVER['Scheme'] = endpointUrlArr[0]
                    self.FRAGMENT_SERVER['Host'] = endpointUrlArr[1][2:]
                    self.FRAGMENT_SERVER['Port'] = endpointUrlArr[2]
            self.STASH_INTERFACE = StashInterface(self.FRAGMENT_SERVER)
        else:
            try:
                self.STDIN_READ = sys.stdin.read()
                self.CALLED_AS_STASH_PLUGIN = True
            except:
                pass
        if self.STDIN_READ:
            self.JSON_INPUT = json.loads(self.STDIN_READ)
            if "args" in self.JSON_INPUT and "mode" in self.JSON_INPUT["args"]:
                self.PLUGIN_TASK_NAME = self.JSON_INPUT["args"]["mode"]
            self.FRAGMENT_SERVER = self.JSON_INPUT["server_connection"]
            self.STASH_URL = f"{self.FRAGMENT_SERVER['Scheme']}://{self.FRAGMENT_SERVER['Host']}:{self.FRAGMENT_SERVER['Port']}"
            self.STASH_INTERFACE = StashInterface(self.FRAGMENT_SERVER)
            
        if self.STASH_INTERFACE:
            self.PLUGIN_CONFIGURATION = self.STASH_INTERFACE.get_configuration()["plugins"]
            self.STASH_CONFIGURATION = self.STASH_INTERFACE.get_configuration()["general"]
            if settings:
                self.pluginSettings = settings
                if self.PLUGIN_ID in self.PLUGIN_CONFIGURATION:
                    self.pluginSettings.update(self.PLUGIN_CONFIGURATION[self.PLUGIN_ID])
                if DebugTraceFieldName in self.pluginSettings:
                    self.DEBUG_TRACING = self.pluginSettings[DebugTraceFieldName]
                if DryRunFieldName in self.pluginSettings:
                    self.DRY_RUN = self.pluginSettings[DryRunFieldName]
        if self.DEBUG_TRACING: self.LOG_LEVEL = logging.DEBUG
        
        logging.basicConfig(level=self.LOG_LEVEL, format=logFormat, datefmt=dateFmt, handlers=[RFH])
        self.logger = logging.getLogger(pathlib.Path(self.MAIN_SCRIPT_NAME).stem)
    
    def Log(self, logMsg, printTo = 0, logLevel = logging.INFO, lineNo = -1, levelStr = "", logAlways = False):
        if printTo == 0: 
            printTo = self.log_to_norm
        elif printTo == self.LOG_TO_ERROR and logLevel == logging.INFO:
            logLevel = logging.ERROR
            printTo = self.log_to_err_set
        elif printTo == self.LOG_TO_CRITICAL and logLevel == logging.INFO:
            logLevel = logging.CRITICAL
            printTo = self.log_to_err_set
        elif printTo == self.LOG_TO_WARN and logLevel == logging.INFO:
            logLevel = logging.WARN
            printTo = self.log_to_wrn_set
        if lineNo == -1:
            lineNo = inspect.currentframe().f_back.f_lineno
        LN_Str = f"[LN:{lineNo}]"
        # print(f"{LN_Str}, {logAlways}, {self.LOG_LEVEL}, {logging.DEBUG}, {levelStr}, {logMsg}")
        if logLevel == logging.DEBUG and (logAlways == False or self.LOG_LEVEL == logging.DEBUG):
            if levelStr == "": levelStr = self.LEV_DBG
            if printTo & self.LOG_TO_FILE: self.logger.debug(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: stashLog.debug(f"{LN_Str} {levelStr}{logMsg}")
        elif logLevel == logging.INFO or logLevel == logging.DEBUG:
            if levelStr == "": levelStr = self.LEV_INF if logLevel == logging.INFO else self.LEV_DBG
            if printTo & self.LOG_TO_FILE: self.logger.info(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: stashLog.info(f"{LN_Str} {levelStr}{logMsg}")
        elif logLevel == logging.WARN:
            if levelStr == "": levelStr = self.LEV_WRN
            if printTo & self.LOG_TO_FILE: self.logger.warning(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: stashLog.warning(f"{LN_Str} {levelStr}{logMsg}")
        elif logLevel == logging.ERROR:
            if levelStr == "": levelStr = self.LEV_ERR
            if printTo & self.LOG_TO_FILE: self.logger.error(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: stashLog.error(f"{LN_Str} {levelStr}{logMsg}")
        elif logLevel == logging.CRITICAL:
            if levelStr == "": levelStr = self.LEV_CRITICAL
            if printTo & self.LOG_TO_FILE: self.logger.critical(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: stashLog.error(f"{LN_Str} {levelStr}{logMsg}")
        if (printTo & self.LOG_TO_CONSOLE) and (logLevel != logging.DEBUG or self.DEBUG_TRACING or logAlways):
            print(f"{LN_Str} {levelStr}{logMsg}")
        if (printTo & self.LOG_TO_STDERR) and (logLevel != logging.DEBUG or self.DEBUG_TRACING or logAlways):
            print(f"StdErr: {LN_Str} {levelStr}{logMsg}", file=sys.stderr)
    
    def Trace(self, logMsg = "", printTo = 0, logAlways = False):
        if printTo == 0: printTo = self.LOG_TO_FILE
        lineNo = inspect.currentframe().f_back.f_lineno
        logLev = logging.INFO if logAlways else logging.DEBUG
        if self.DEBUG_TRACING or logAlways:
            if logMsg == "":
                logMsg = f"Line number {lineNo}..."
            self.Log(logMsg, printTo, logLev, lineNo, self.LEV_TRACE, logAlways)
    
    def Warn(self, logMsg, printTo = 0):
        if printTo == 0: printTo = self.log_to_wrn_set
        lineNo = inspect.currentframe().f_back.f_lineno
        self.Log(logMsg, printTo, logging.WARN, lineNo)
    
    def Error(self, logMsg, printTo = 0):
        if printTo == 0: printTo = self.log_to_err_set
        lineNo = inspect.currentframe().f_back.f_lineno
        self.Log(logMsg, printTo, logging.ERROR, lineNo)

    def Status(self, printTo = 0, logLevel = logging.INFO, lineNo = -1):
        if printTo == 0: printTo = self.log_to_norm
        if lineNo == -1:
            lineNo = inspect.currentframe().f_back.f_lineno
        self.Log(f"StashPluginHelper Status: (CALLED_AS_STASH_PLUGIN={self.CALLED_AS_STASH_PLUGIN}), (RUNNING_IN_COMMAND_LINE_MODE={self.RUNNING_IN_COMMAND_LINE_MODE}), (DEBUG_TRACING={self.DEBUG_TRACING}), (DRY_RUN={self.DRY_RUN}), (PLUGIN_ID={self.PLUGIN_ID}), (PLUGIN_TASK_NAME={self.PLUGIN_TASK_NAME}), (STASH_URL={self.STASH_URL}), (MAIN_SCRIPT_NAME={self.MAIN_SCRIPT_NAME})",
            printTo, logLevel, lineNo)
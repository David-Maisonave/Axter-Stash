from stashapi.stashapp import StashInterface
from logging.handlers import RotatingFileHandler
import re, inspect, sys, os, pathlib, logging, json, platform, subprocess, traceback, time
import concurrent.futures
from stashapi.stash_types import PhashDistance
import __main__

_ARGUMENT_UNSPECIFIED_ = "_ARGUMENT_UNSPECIFIED_"

# StashPluginHelper (By David Maisonave aka Axter)
    # See end of this file for example usage
    # Log Features:
        # Can optionally log out to multiple outputs for each Log or Trace call.
        # Logging includes source code line number
        # Sets a maximum plugin log file size
    # Stash Interface Features:
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
class StashPluginHelper(StashInterface):
    # Primary Members for external reference
    PLUGIN_TASK_NAME = None
    PLUGIN_ID = None
    PLUGIN_CONFIGURATION = None
    PLUGINS_PATH = None
    pluginSettings = None
    pluginConfig = None
    STASH_URL = None
    STASH_CONFIGURATION = None
    JSON_INPUT = None
    DEBUG_TRACING = False
    DRY_RUN = False
    CALLED_AS_STASH_PLUGIN = False
    RUNNING_IN_COMMAND_LINE_MODE = False
    FRAGMENT_SERVER = None
    STASHPATHSCONFIG = None
    STASH_PATHS = []
    API_KEY = None
    excludeMergeTags = None
    
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
    stopProcessBarSpin = True
    
    IS_DOCKER = False
    IS_WINDOWS = False
    IS_LINUX = False
    IS_FREEBSD = False
    IS_MAC_OS = False
    
    pluginLog = None
    logLinePreviousHits = []
    thredPool = None
    STASH_INTERFACE_INIT = False
    _mergeMetadata = None
    encodeToUtf8 = False
    convertToAscii = False # If set True, it takes precedence over encodeToUtf8
    
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
    # Warn message goes to both plugin log file and stash when sent to Stash log file.
    log_to_wrn_set = LOG_TO_STASH # This can be changed by the calling source in order to customize what targets get warning messages

    def __init__(self, 
                    debugTracing = None,            # Set debugTracing to True so as to output debug and trace logging
                    logFormat = LOG_FORMAT,         # Plugin log line format
                    dateFmt = "%y%m%d %H:%M:%S",    # Date format when logging to plugin log file
                    maxbytes = 8*1024*1024,         # Max size of plugin log file
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
                    apiKey = None,                  # API Key only needed when username and password set while running script via command line
                    DebugTraceFieldName = "zzdebugTracing",
                    DryRunFieldName = "zzdryRun",
                    setStashLoggerAsPluginLogger = False):              
        self.thredPool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        if any(platform.win32_ver()):
            self.IS_WINDOWS = True
        elif platform.system().lower().startswith("linux"):
            self.IS_LINUX = True
            if self.isDocker():
                self.IS_DOCKER = True
        elif platform.system().lower().startswith("freebsd"):
            self.IS_FREEBSD = True
        elif sys.platform == "darwin":
            self.IS_MAC_OS = True
        if logToWrnSet: self.log_to_wrn_set = logToWrnSet
        if logToErrSet: self.log_to_err_set = logToErrSet
        if logToNormSet: self.log_to_norm = logToNormSet
        if stash_url and len(stash_url): self.STASH_URL = stash_url
        self.MAIN_SCRIPT_NAME = mainScriptName if mainScriptName != "" else __main__.__file__
        self.PLUGIN_ID = pluginID if pluginID != "" else pathlib.Path(self.MAIN_SCRIPT_NAME).stem
        # print(f"self.MAIN_SCRIPT_NAME={self.MAIN_SCRIPT_NAME}, self.PLUGIN_ID={self.PLUGIN_ID}", file=sys.stderr)
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
            if self.Setting('apiKey', "") != "":
                self.FRAGMENT_SERVER['ApiKey'] = self.Setting('apiKey')

        
        if apiKey and apiKey != "":
            self.FRAGMENT_SERVER['ApiKey'] = apiKey
        
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
            super().__init__(self.FRAGMENT_SERVER)
            self.STASH_INTERFACE_INIT = True
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
            super().__init__(self.FRAGMENT_SERVER)
            self.STASH_INTERFACE_INIT = True
            
        if self.STASH_URL.startswith("http://0.0.0.0:"):
            self.STASH_URL = self.STASH_URL.replace("http://0.0.0.0:", "http://localhost:")
        
        if self.STASH_INTERFACE_INIT:
            self.PLUGIN_CONFIGURATION = self.get_configuration()["plugins"]
            self.STASH_CONFIGURATION = self.get_configuration()["general"]
            self.STASHPATHSCONFIG = self.STASH_CONFIGURATION['stashes']
            if 'pluginsPath' in self.STASH_CONFIGURATION:
                self.PLUGINS_PATH = self.STASH_CONFIGURATION['pluginsPath']
            for item in self.STASHPATHSCONFIG: 
                self.STASH_PATHS.append(item["path"])
            if settings:
                self.pluginSettings = settings
                if self.PLUGIN_ID in self.PLUGIN_CONFIGURATION:
                    self.pluginSettings.update(self.PLUGIN_CONFIGURATION[self.PLUGIN_ID])
            if 'apiKey' in self.STASH_CONFIGURATION:
                self.API_KEY = self.STASH_CONFIGURATION['apiKey']
        
        self.DRY_RUN = self.Setting(DryRunFieldName, self.DRY_RUN)
        self.DEBUG_TRACING = self.Setting(DebugTraceFieldName, self.DEBUG_TRACING)
        if self.DEBUG_TRACING: self.LOG_LEVEL = logging.DEBUG
        
        logging.basicConfig(level=self.LOG_LEVEL, format=logFormat, datefmt=dateFmt, handlers=[RFH])
        self.pluginLog = logging.getLogger(pathlib.Path(self.MAIN_SCRIPT_NAME).stem)
        if setStashLoggerAsPluginLogger:
            self.log = self.pluginLog
    
    def __del__(self):
        self.thredPool.shutdown(wait=False)
    
    def Setting(self, name, default=_ARGUMENT_UNSPECIFIED_, raiseEx=True, notEmpty=False):
        if self.pluginSettings != None and name in self.pluginSettings:
            if notEmpty == False or self.pluginSettings[name] != "":
                return self.pluginSettings[name]
        if self.pluginConfig != None and name in self.pluginConfig:
            if notEmpty == False or self.pluginConfig[name] != "":
                return self.pluginConfig[name]
        if default == _ARGUMENT_UNSPECIFIED_ and raiseEx:
            raise Exception(f"Missing {name} from both UI settings and config file settings.") 
        return default
    
    def Log(self, logMsg, printTo = 0, logLevel = logging.INFO, lineNo = -1, levelStr = "", logAlways = False, toAscii = None):
        if toAscii or (toAscii == None and (self.encodeToUtf8 or self.convertToAscii)):
            logMsg = self.asc2(logMsg)
        else:
            logMsg = logMsg
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
            if printTo & self.LOG_TO_FILE: self.pluginLog.debug(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: self.log.debug(f"{LN_Str} {levelStr}{logMsg}")
        elif logLevel == logging.INFO or logLevel == logging.DEBUG:
            if levelStr == "": levelStr = self.LEV_INF if logLevel == logging.INFO else self.LEV_DBG
            if printTo & self.LOG_TO_FILE: self.pluginLog.info(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: self.log.info(f"{LN_Str} {levelStr}{logMsg}")
        elif logLevel == logging.WARN:
            if levelStr == "": levelStr = self.LEV_WRN
            if printTo & self.LOG_TO_FILE: self.pluginLog.warning(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: self.log.warning(f"{LN_Str} {levelStr}{logMsg}")
        elif logLevel == logging.ERROR:
            if levelStr == "": levelStr = self.LEV_ERR
            if printTo & self.LOG_TO_FILE: self.pluginLog.error(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: self.log.error(f"{LN_Str} {levelStr}{logMsg}")
        elif logLevel == logging.CRITICAL:
            if levelStr == "": levelStr = self.LEV_CRITICAL
            if printTo & self.LOG_TO_FILE: self.pluginLog.critical(f"{LN_Str} {levelStr}{logMsg}")
            if printTo & self.LOG_TO_STASH: self.log.error(f"{LN_Str} {levelStr}{logMsg}")
        if (printTo & self.LOG_TO_CONSOLE) and (logLevel != logging.DEBUG or self.DEBUG_TRACING or logAlways):
            print(f"{LN_Str} {levelStr}{logMsg}")
        if (printTo & self.LOG_TO_STDERR) and (logLevel != logging.DEBUG or self.DEBUG_TRACING or logAlways):
            print(f"StdErr: {LN_Str} {levelStr}{logMsg}", file=sys.stderr)
    
    def Trace(self, logMsg = "", printTo = 0, logAlways = False, lineNo = -1, toAscii = None):
        if printTo == 0: printTo = self.LOG_TO_FILE
        if lineNo == -1:
            lineNo = inspect.currentframe().f_back.f_lineno
        logLev = logging.INFO if logAlways else logging.DEBUG
        if self.DEBUG_TRACING or logAlways:
            if logMsg == "":
                logMsg = f"Line number {lineNo}..."
            self.Log(logMsg, printTo, logLev, lineNo, self.LEV_TRACE, logAlways, toAscii=toAscii)
    
    # Log once per session. Only logs the first time called from a particular line number in the code.
    def TraceOnce(self, logMsg = "", printTo = 0, logAlways = False, toAscii = None):
        lineNo = inspect.currentframe().f_back.f_lineno
        if self.DEBUG_TRACING or logAlways:
            FuncAndLineNo = f"{inspect.currentframe().f_back.f_code.co_name}:{lineNo}"
            if FuncAndLineNo in self.logLinePreviousHits:
                return
            self.logLinePreviousHits.append(FuncAndLineNo)
            self.Trace(logMsg, printTo, logAlways, lineNo, toAscii=toAscii)

    # Log INFO on first call, then do Trace on remaining calls.
    def LogOnce(self, logMsg = "", printTo = 0, logAlways = False, traceOnRemainingCalls = True, toAscii = None):
        if printTo == 0: printTo = self.LOG_TO_FILE
        lineNo = inspect.currentframe().f_back.f_lineno
        FuncAndLineNo = f"{inspect.currentframe().f_back.f_code.co_name}:{lineNo}"
        if FuncAndLineNo in self.logLinePreviousHits:
            if traceOnRemainingCalls:
                self.Trace(logMsg, printTo, logAlways, lineNo, toAscii=toAscii) 
        else:
            self.logLinePreviousHits.append(FuncAndLineNo)
            self.Log(logMsg, printTo, logging.INFO, lineNo, toAscii=toAscii)   
    
    def Warn(self, logMsg, printTo = 0, toAscii = None):
        if printTo == 0: printTo = self.log_to_wrn_set
        lineNo = inspect.currentframe().f_back.f_lineno
        self.Log(logMsg, printTo, logging.WARN, lineNo, toAscii=toAscii)
    
    def Error(self, logMsg, printTo = 0, toAscii = None):
        if printTo == 0: printTo = self.log_to_err_set
        lineNo = inspect.currentframe().f_back.f_lineno
        self.Log(logMsg, printTo, logging.ERROR, lineNo, toAscii=toAscii)
    
    # Above logging functions all use UpperCamelCase naming convention to avoid conflict with parent class logging function names.
    # The below non-loggging functions use (lower) camelCase naming convention.
    def status(self, printTo = 0, logLevel = logging.INFO, lineNo = -1):
        if printTo == 0: printTo = self.log_to_norm
        if lineNo == -1:
            lineNo = inspect.currentframe().f_back.f_lineno
        self.Log(f"StashPluginHelper Status: (CALLED_AS_STASH_PLUGIN={self.CALLED_AS_STASH_PLUGIN}), (RUNNING_IN_COMMAND_LINE_MODE={self.RUNNING_IN_COMMAND_LINE_MODE}), (DEBUG_TRACING={self.DEBUG_TRACING}), (DRY_RUN={self.DRY_RUN}), (PLUGIN_ID={self.PLUGIN_ID}), (PLUGIN_TASK_NAME={self.PLUGIN_TASK_NAME}), (STASH_URL={self.STASH_URL}), (MAIN_SCRIPT_NAME={self.MAIN_SCRIPT_NAME})",
            printTo, logLevel, lineNo)
    
    def executeProcess(self, args, ExecDetach=False):
        pid = None
        self.Trace(f"self.IS_WINDOWS={self.IS_WINDOWS} args={args}")
        if self.IS_WINDOWS:
            if ExecDetach:
                self.Trace(f"Executing process using Windows DETACHED_PROCESS; args=({args})")
                DETACHED_PROCESS = 0x00000008
                pid = subprocess.Popen(args,creationflags=DETACHED_PROCESS, shell=True).pid
            else:
                pid = subprocess.Popen(args, shell=True).pid
        else:
            if ExecDetach:
                # For linux detached, use nohup. I.E. subprocess.Popen(["nohup", "python", "test.py"])
                if self.IS_LINUX:
                    args = ["nohup"] + args
                self.Trace(f"Executing detached process using Popen({args})")
            else:
                self.Trace(f"Executing process using normal Popen({args})")
            pid = subprocess.Popen(args).pid # On detach, may need the following for MAC OS subprocess.Popen(args, shell=True, start_new_session=True)
        self.Trace(f"pid={pid}")
        return pid
    
    def executePythonScript(self, args, ExecDetach=True):
        PythonExe = f"{sys.executable}"
        argsWithPython = [f"{PythonExe}"] + args
        return self.executeProcess(argsWithPython,ExecDetach=ExecDetach)
    
    def submit(self, *args, **kwargs):
        return self.thredPool.submit(*args, **kwargs)
    
    def asc2(self, data, convertToAscii=None):
        if convertToAscii or (convertToAscii == None and self.convertToAscii):
            return ascii(data)
        return str(str(data).encode('utf-8'))[2:-1] # This works better for logging than ascii function
        # data = str(data).encode('ascii','ignore') # This works better for logging than ascii function
        # return str(data)[2:-1] # strip out b'str'
    
    def initMergeMetadata(self, excludeMergeTags=None):
        self.excludeMergeTags = excludeMergeTags
        self._mergeMetadata = mergeMetadata(self, self.excludeMergeTags)
    
    # Must call initMergeMetadata, before calling mergeMetadata
    def mergeMetadata(self, SrcData, DestData): # Input arguments can be scene ID or scene metadata
        if type(SrcData) is int:
            SrcData = self.find_scene(SrcData)
            DestData = self.find_scene(DestData)
        return self._mergeMetadata.merge(SrcData, DestData)
    
    def progressBar(self, currentIndex, maxCount):
        progress = (currentIndex / maxCount) if currentIndex < maxCount else (maxCount / currentIndex)
        self.log.progress(progress)
    
    # Test via command line: pip uninstall -y pyYAML watchdog schedule requests
    def modulesInstalled(self, moduleNames, install=True, silent=False): # moduleNames=["stashapp-tools", "requests", "pyYAML"]
        retrnValue = True
        for moduleName in moduleNames:
            try: # Try Python 3.3 > way
                import importlib
                import importlib.util
                if moduleName in sys.modules:
                    if not silent: self.Trace(f"{moduleName!r} already in sys.modules")
                elif self.isModuleInstalled(moduleName):
                    if not silent: self.Trace(f"Module {moduleName!r} is available.")
                else:
                    if install and (results:=self.installModule(moduleName)) > 0:
                        if results == 1:
                            self.Log(f"Module {moduleName!r} has been installed")
                        else:
                            if not silent: self.Trace(f"Module {moduleName!r} is already installed")
                        continue
                    else:
                        if install:
                            self.Error(f"Can't find the {moduleName!r} module") 
                        retrnValue = False
            except Exception as e:
                try:
                    i = importlib.import_module(moduleName)
                except ImportError as e:
                    if install and (results:=self.installModule(moduleName)) > 0:
                        if results == 1:
                            self.Log(f"Module {moduleName!r} has been installed")
                        else:
                            if not silent: self.Trace(f"Module {moduleName!r} is already installed")
                        continue
                    else:
                        if install:
                            tb = traceback.format_exc()
                            self.Error(f"Can't find the {moduleName!r} module! Error: {e}\nTraceBack={tb}") 
                        retrnValue = False
        return retrnValue
    
    def isModuleInstalled(self, moduleName):
        try:
            __import__(moduleName)
            # self.Trace(f"Module {moduleName!r} is installed")
            return True
        except Exception as e:
            tb = traceback.format_exc()
            self.Warn(f"Module {moduleName!r} is NOT installed!") 
            self.Trace(f"Error: {e}\nTraceBack={tb}")
            pass
        return False
    
    def installModule(self,moduleName):
        # if not self.IS_DOCKER:
            # try:
                # self.Log(f"Attempting to install package {moduleName!r} using pip import method.")
                # First try pip import method. (This may fail in a future version of pip.)
                # self.installPackage(moduleName)
                # self.Trace(f"installPackage called for module {moduleName!r}")
                # if self.modulesInstalled(moduleNames=[moduleName], install=False):
                    # self.Trace(f"Module {moduleName!r} installed")
                    # return 1
                # self.Trace(f"Module {moduleName!r} still not installed.")
            # except Exception as e:
                # tb = traceback.format_exc()
                # self.Warn(f"pip import method failed for module {moduleName!r}. Will try command line method; Error: {e}\nTraceBack={tb}") 
                # pass
        # else:
            # self.Trace("Running in Docker, so skipping pip import method.")
        try:
            if self.IS_LINUX:
                # Note: Linux may first need : sudo apt install python3-pip
                #       if error starts with "Command 'pip' not found"
                #       or includes "No module named pip"
                self.Log("Checking if pip installed.")
                results = os.popen(f"pip --version").read()
                if results.find("Command 'pip' not found") != -1 or results.find("No module named pip") != -1:
                    results = os.popen(f"sudo apt install python3-pip").read()
                    results = os.popen(f"pip --version").read()
                    if results.find("Command 'pip' not found") != -1 or results.find("No module named pip") != -1:
                        self.Error(f"Error while calling 'pip'. Make sure pip is installed, and make sure module {moduleName!r} is installed. Results = '{results}'")
                        return -1
                self.Trace("pip good.")
            if self.IS_FREEBSD:
                self.Warn("installModule may NOT work on freebsd")
            pipArg = ""
            if self.IS_DOCKER:
                pipArg = " --break-system-packages"
            self.Log(f"Attempting to install package {moduleName!r} via popen.")
            results = os.popen(f"{sys.executable} -m pip install {moduleName}{pipArg}").read() # May need to be f"{sys.executable} -m pip install {moduleName}"
            results = results.strip("\n")
            self.Trace(f"pip results = {results}")
            if results.find("Requirement already satisfied:") > -1:
                self.Trace(f"Requirement already satisfied for module {moduleName!r}")
                return 2
            elif results.find("Successfully installed") > -1:
                self.Trace(f"Successfully installed module {moduleName!r}")
                return 1
            elif self.modulesInstalled(moduleNames=[moduleName], install=False):
                self.Trace(f"modulesInstalled returned True for module {moduleName!r}")
                return 1
            self.Error(f"Failed to install module {moduleName!r}")
        except Exception as e:
            tb = traceback.format_exc()
            self.Error(f"Failed to install module {moduleName!r}. Error: {e}\nTraceBack={tb}") 
        return 0
    
    def installPackage(self,package): # Should delete this.  It doesn't work consistently
        try:
            import pip
            if hasattr(pip, 'main'):
                pip.main(['install', package])
                self.Trace()
            else:
                pip._internal.main(['install', package])
                self.Trace()
        except Exception as e:
            tb = traceback.format_exc()
            self.Error(f"Failed to install module {moduleName!r}. Error: {e}\nTraceBack={tb}")
            return False
        return True
    
    def isDocker(self):
        cgroup = pathlib.Path('/proc/self/cgroup')
        return pathlib.Path('/.dockerenv').is_file() or cgroup.is_file() and 'docker' in cgroup.read_text()
    
    def spinProcessBar(self, sleepSeconds = 1, maxPos = 30, trace = False):
        if trace:
            self.Trace(f"Starting spinProcessBar loop; sleepSeconds={sleepSeconds}, maxPos={maxPos}")
        pos = 1
        while self.stopProcessBarSpin == False:
            if trace:
                self.Trace(f"progressBar({pos}, {maxPos})")
            self.progressBar(pos, maxPos)
            pos +=1
            if pos > maxPos:
                pos = 1
            time.sleep(sleepSeconds)
    
    def startSpinningProcessBar(self, sleepSeconds = 1, maxPos = 30, trace = False):
        self.stopProcessBarSpin = False
        if trace:
            self.Trace(f"submitting spinProcessBar; sleepSeconds={sleepSeconds}, maxPos={maxPos}, trace={trace}")
        self.submit(self.spinProcessBar, sleepSeconds, maxPos, trace)
    
    def stopSpinningProcessBar(self, sleepSeconds = 1):
        self.stopProcessBarSpin = True
        time.sleep(sleepSeconds)
    
    def createTagId(self, tagName, tagName_descp = "", deleteIfExist = False, ignoreAutoTag = False):
        tagId = self.find_tags(q=tagName)
        if len(tagId):
            tagId = tagId[0]
            if deleteIfExist:
                self.destroy_tag(int(tagId['id']))
            else:
                return tagId['id']
        tagId = self.create_tag({"name":tagName, "description":tagName_descp, "ignore_auto_tag": ignoreAutoTag})
        self.Log(f"Dup-tagId={tagId['id']}")
        return tagId['id']
    
    def removeTag(self, scene, tagName): # scene can be scene ID or scene metadata
        scene_details = scene
        if 'id' not in scene:
            scene_details = self.find_scene(scene)
        tagIds = []
        doesHaveTagName = False
        for tag in scene_details['tags']:
            if tag['name'] != tagName:
                tagIds += [tag['id']]
            else:
                doesHaveTagName = True
        if doesHaveTagName:
            dataDict = {'id' : scene_details['id']}
            dataDict.update({'tag_ids' : tagIds})
            self.update_scene(dataDict)
        return doesHaveTagName
    
    def addTag(self, scene, tagName): # scene can be scene ID or scene metadata
        scene_details = scene
        if 'id' not in scene:
            scene_details = self.find_scene(scene)
        tagIds = [self.createTagId(tagName)]
        for tag in scene_details['tags']:
            if tag['name'] != tagName:
                tagIds += [tag['id']]
        dataDict = {'id' : scene_details['id']}
        dataDict.update({'tag_ids' : tagIds})
        self.update_scene(dataDict)
    
    def runPlugin(self, plugin_id, task_mode=None, args:dict={}, asyn=False):
        """Runs a plugin operation.
           The operation is run immediately and does not use the job queue.
           This is a blocking call, and does not return until plugin completes.
        Args:
            plugin_id (ID):             plugin_id
            task_name (str, optional):  Plugin task to perform
            args (dict, optional):      Arguments to pass to plugin. Plugin access via JSON_INPUT['args']
        Returns:
            A map of the result.
        """
        query = """mutation RunPluginOperation($plugin_id: ID!, $args: Map!) {
            runPluginOperation(plugin_id: $plugin_id, args: $args)
            }"""        
        if task_mode != None:
            args.update({"mode" : task_mode})
        variables = {
            "plugin_id": plugin_id,
            "args": args,
        }
        if asyn:
            self.submit(self.call_GQL, query, variables)
            return f"Made asynchronous call for plugin {plugin_id}"
        else:
            return self.call_GQL(query, variables)
    
    # ############################################################################################################
    # Functions which are candidates to be added to parent class use snake_case naming convention.
    # ############################################################################################################
    # The below functions extends class StashInterface with functions which are not yet in the class or
    # fixes for functions which have not yet made it into official class.
    def metadata_scan(self, paths:list=[], flags={}): # ToDo: Add option to add path to library if path not included when calling metadata_scan
        query = "mutation MetadataScan($input:ScanMetadataInput!) { metadataScan(input: $input) }"
        scan_metadata_input = {"paths": paths}
        if flags:
            scan_metadata_input.update(flags)
        elif scan_config := self.get_configuration_defaults("scan { ...ScanMetadataOptions }").get("scan"):
            scan_metadata_input.update(scan_config)
        result = self.call_GQL(query, {"input": scan_metadata_input})
        return result["metadataScan"]
        
    def get_all_scenes(self):
        query_all_scenes = """
            query AllScenes {
                allScenes {
                    id
                    updated_at
                }
            }
        """
        return self.call_GQL(query_all_scenes)
    
    def metadata_autotag(self, paths:list=[], performers:list=[], studios:list=[], tags:list=[]):
        query = """
        mutation MetadataAutoTag($input:AutoTagMetadataInput!) {
            metadataAutoTag(input: $input)
        }
        """
        metadata_autotag_input = {
            "paths":paths,
            "performers": performers,
            "studios":studios,
            "tags":tags,
        }
        result = self.call_GQL(query, {"input": metadata_autotag_input})
        return result
    
    def backup_database(self):
        return self.call_GQL("mutation { backupDatabase(input: {download: false})}")

    def optimise_database(self):
        return self.call_GQL("mutation OptimiseDatabase { optimiseDatabase }")
    
    def metadata_clean_generated(self, blobFiles=True, dryRun=False, imageThumbnails=True, markers=True, screenshots=True, sprites=True, transcodes=True):
        query = """
        mutation MetadataCleanGenerated($input: CleanGeneratedInput!) {
          metadataCleanGenerated(input: $input)
        }
        """
        clean_metadata_input = {
            "blobFiles": blobFiles,
            "dryRun": dryRun,
            "imageThumbnails": imageThumbnails,
            "markers": markers,
            "screenshots": screenshots,
            "sprites": sprites,
            "transcodes": transcodes,
        }
        result = self.call_GQL(query, {"input": clean_metadata_input})
        return result
    
    def rename_generated_files(self):
        return self.call_GQL("mutation MigrateHashNaming {migrateHashNaming}")
       
    def find_duplicate_scenes_diff(self, distance: PhashDistance=PhashDistance.EXACT, fragment='id', duration_diff: float=10.00 ):
        query = """
        	query FindDuplicateScenes($distance: Int, $duration_diff: Float) {
        		findDuplicateScenes(distance: $distance, duration_diff: $duration_diff) {
        			...SceneSlim
        		}
        	}
        """
        if fragment:
        	query = re.sub(r'\.\.\.SceneSlim', fragment, query)
        else:
        	query += "fragment SceneSlim on Scene { id  }"
        
        variables = { "distance": distance, "duration_diff": duration_diff }
        result = self.call_GQL(query, variables)
        return result['findDuplicateScenes'] 
    
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Direct SQL associated functions
    def get_file_metadata(self, data, raw_data = False): # data is either file ID or scene metadata
        results = None
        if data == None:
            return results
        if 'files' in data and len(data['files']) > 0 and 'id' in data['files'][0]:
            results = self.sql_query(f"select * from files where id =  {data['files'][0]['id']}")
        else:
            results = self.sql_query(f"select * from files where id =  {data}")
        if raw_data:
            return results
        if 'rows' in results:
            return results['rows'][0]
        self.Error(f"Unknown error while SQL query with data='{data}'; Results='{results}'.")
        return None
    
    def set_file_basename(self, id, basename):
        return self.sql_commit(f"update files set basename = '{basename}' where id = {id}")

class mergeMetadata: # A class to merge scene metadata from source scene to destination scene
    srcData = None
    destData = None
    stash = None
    excludeMergeTags = None
    dataDict = None
    result = "Nothing To Merge"
    def __init__(self, stash, excludeMergeTags=None):
        self.stash = stash
        self.excludeMergeTags = excludeMergeTags
    
    def merge(self, SrcData, DestData):
        self.srcData = SrcData
        self.destData = DestData
        ORG_DATA_DICT = {'id' : self.destData['id']}
        self.dataDict = ORG_DATA_DICT.copy()
        self.mergeItems('tags', 'tag_ids', [], excludeName=self.excludeMergeTags)
        self.mergeItems('performers', 'performer_ids', [])
        self.mergeItems('galleries', 'gallery_ids', [])
        self.mergeItems('movies', 'movies', [])
        self.mergeItems('urls', listToAdd=self.destData['urls'], NotStartWith=self.stash.STASH_URL)
        self.mergeItem('studio', 'studio_id', 'id')
        self.mergeItem('title')
        self.mergeItem('director')
        self.mergeItem('date')
        self.mergeItem('details')
        self.mergeItem('rating100')
        self.mergeItem('code')
        if self.dataDict != ORG_DATA_DICT:
            self.stash.Trace(f"Updating scene ID({self.destData['id']}) with {self.dataDict}; path={self.destData['files'][0]['path']}", toAscii=True)
            self.result = self.stash.update_scene(self.dataDict)
        return self.result
    
    def Nothing(self, Data):
        if not Data or Data == "" or (type(Data) is str and Data.strip() == ""):
            return True
        return False
    
    def mergeItem(self,fieldName, updateFieldName=None, subField=None):
        if updateFieldName == None:
            updateFieldName = fieldName
        if self.Nothing(self.destData[fieldName]) and not self.Nothing(self.srcData[fieldName]):
            if subField == None:
                self.dataDict.update({ updateFieldName : self.srcData[fieldName]})
            else:
                self.dataDict.update({ updateFieldName : self.srcData[fieldName][subField]})
    def mergeItems(self, fieldName, updateFieldName=None, listToAdd=[], NotStartWith=None, excludeName=None):
        dataAdded = ""
        for item in self.srcData[fieldName]:
            if item not in self.destData[fieldName]:
                if NotStartWith == None or not item.startswith(NotStartWith):
                    if excludeName == None or item['name'] not in excludeName:
                        if fieldName == 'movies':
                            listToAdd += [{"movie_id" : item['movie']['id'], "scene_index" : item['scene_index']}]
                            dataAdded += f"{item['movie']['id']} "                    
                        elif updateFieldName == None:
                            listToAdd += [item]
                            dataAdded += f"{item} "
                        else:
                            listToAdd += [item['id']]
                            dataAdded += f"{item['id']} "
        if dataAdded != "":
            if updateFieldName == None:
                updateFieldName = fieldName
            else:
                for item in self.destData[fieldName]:
                    if fieldName == 'movies':
                        listToAdd += [{"movie_id" : item['movie']['id'], "scene_index" : item['scene_index']}]
                    else:
                        listToAdd += [item['id']]
            self.dataDict.update({ updateFieldName : listToAdd})
            # self.stash.Trace(f"Added {fieldName} ({dataAdded}) to scene ID({self.destData['id']})", toAscii=True)

class taskQueue:
    taskqueue = None
    def __init__(self, taskqueue):
        self.taskqueue = taskqueue
    
    def tooManyScanOnTaskQueue(self, tooManyQty = 5):
        count = 0
        if self.taskqueue == None:
            return False
        for jobDetails in self.taskqueue:
            if jobDetails['description'] == "Scanning...":
                count += 1
        if count < tooManyQty:
            return False
        return True
    
    def cleanJobOnTaskQueue(self):
        for jobDetails in self.taskqueue:
            if jobDetails['description'] == "Cleaning...":
                return True
        return False
    
    def cleanGeneratedJobOnTaskQueue(self):
        for jobDetails in self.taskqueue:
            if jobDetails['description'] == "Cleaning generated files...":
                return True
        return False
    
    def isRunningPluginTaskJobOnTaskQueue(self, taskName):
        for jobDetails in self.taskqueue:
            if jobDetails['description'] == "Running plugin task: {taskName}":
                return True
        return False
    
    def tagDuplicatesJobOnTaskQueue(self):
        return self.isRunningPluginTaskJobOnTaskQueue("Tag Duplicates")
    
    def clearDupTagsJobOnTaskQueue(self):
        return self.isRunningPluginTaskJobOnTaskQueue("Clear Tags")
    
    def generatePhashMatchingJobOnTaskQueue(self):
        return self.isRunningPluginTaskJobOnTaskQueue("Generate PHASH Matching")
    
    def deleteDuplicatesJobOnTaskQueue(self):
        return self.isRunningPluginTaskJobOnTaskQueue("Delete Duplicates")
    
    def deleteTaggedScenesJobOnTaskQueue(self):
        return self.isRunningPluginTaskJobOnTaskQueue("Delete Tagged Scenes")



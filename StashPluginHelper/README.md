# StashPluginHelper: Ver 0.1.0 (By David Maisonave)
StashPluginHelper is a class that performs common implementation used in most plugins.

## Features
- Log Features:
  - Logs out to multiple outputs for each Log or Trace call.
  - Logging includes source code line number.
  - Sets a maximum plugin log file size.
- Stash Interface Features:
  - Sets STASH_INTERFACE with StashInterface
  - Gets STASH_URL value from command line argument and/or from STDIN_READ
  - Sets FRAGMENT_SERVER based on command line arguments or STDIN_READ
  - Sets PLUGIN_ID based on the main script file name (in lower case)
  - Gets PLUGIN_TASK_NAME value
  - Sets pluginSettings (The plugin UI settings)
- Misc Features:
  - Gets DRY_RUN value from command line argument and/or from UI and/or from config file.
  - Gets DEBUG_TRACING value from command line argument and/or from UI and/or from config file.
  - Sets RUNNING_IN_COMMAND_LINE_MODE to True if detects multiple arguments
  - Sets CALLED_AS_STASH_PLUGIN to True if it's able to read from STDIN_READ

## StashPluginHelper Usage
#### Example #1
- All the arguments for **StashPluginHelper** class are optional.
  - StashPluginHelper can be called with no arguments if the plugin has NO UI settings and NO associated (*_config.py) file.
``` python
from StashPluginHelper import StashPluginHelper
plugin = StashPluginHelper()

# Trace command which logs out only when DEBUG_TRACING is enabled, and by default only logs to plugin log file.
plugin.Trace()
```

#### Example #2
- This is an example for a plugin that has UI settings and settings from MyPlugin_config.py file.
``` python
from StashPluginHelper import StashPluginHelper
from MyPlugin_config import config
settings = {
    "enableFooFoo": False,
    "zzdebugTracing": False,
    "zzdryRun": False,
}

plugin = StashPluginHelper(settings=settings, config=config)

fooFoo = plugin.pluginSettings["enableFooFoo"]  # Gets plugin UI setting named enableFooFoo
TIMEOUT = plugin.pluginConfig['timeOut'] # Gets setting from MyPlugin_config.py

 # By default, logging level is INFO, and output goes to the console and plugin log file.
plugin.Log(f"Value for TIMEOUT = {TIMEOUT}")

# Trace logs out only when DEBUG_TRACING is enabled.
plugin.Trace(f"plugin.PLUGIN_TASK_NAME = {plugin.PLUGIN_TASK_NAME}")
```
#### Example #3
- An example for a plugin that can also run in command line mode. It parses command line argument using argparse before calling StashPluginHelper. This allows it to pass in the stash-url and/or trace option to StashPluginHelper constructor.
``` python
from StashPluginHelper import StashPluginHelper
from MyPlugin_config import config
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--url', '-u', dest='stash_url', type=str, help='Add Stash URL')
parser.add_argument('--trace', '-t', dest='trace', action='store_true', help='Enables debug trace mode.')
parse_args = parser.parse_args()

plugin = StashPluginHelper(
        stash_url=parse_args.stash_url,
        debugTracing=parse_args.trace,
        config=config)

plugin.Log(f"plugin.DEBUG_TRACING = {plugin.DEBUG_TRACING}")

plugin.Log(f"Value for RUNNING_IN_COMMAND_LINE_MODE = {plugin.RUNNING_IN_COMMAND_LINE_MODE}")

plugin.Log(f"Value for CALLED_AS_STASH_PLUGIN = {plugin.CALLED_AS_STASH_PLUGIN}")

if not plugin.RUNNING_IN_COMMAND_LINE_MODE and not plugin.CALLED_AS_STASH_PLUGIN:
    # By default, errors go out to both plugin log file and std-err.
    #     In plugin mode, std-err get sent to stash log file.
    #     In command line mode, std-err goes out to console.
    plugin.Error("This should never happen.")
```

## StashPluginHelper Arguments
- debugTracing
  - Default: False
  - Set to true to enable debug tracing, and to open the plugin log file with logging level logging.DEBUG.
  - When debugTracing is false, the Trace logging does not output any logging unless argument (**logAlways**=True) is pass to Trace.
- logFormat
  - Plugin log line format. Default = `"[%(asctime)s] %(message)s"`
- dateFmt
  - Date format when logging to plugin log file. Default = `"%y%m%d %H:%M:%S"`
  - The default value is design to be compact, and it's **not** designed to look pretty.
  - For a more pleasent look try the following format instead: `"%y-%m-%d %H:%M:%S"`
- maxbytes
  - Maximum size of plugin log file. Default = 1MB
- backupcount
  - The number of backup log files when log file size reaches max size.
- logToWrnSet
  - Customize the target output set which will get warning logging
- logToErrSet
  - Customize the target output set which will get error logging
- logToNormSet
  - Customize the target output set which will get normal logging
- mainScriptName
  - The main plugin script file name (full path).
  - If empty, value is set based on \_\_main\_\_.\_\_file\_\_
    - **Warning**: \_\_main\_\_.\_\_file\_\_ will fail if the main script uses `if __name__ == "__main__": `
      - For the above type of code, the **mainScriptName** field becomes a **required** field.
- logFilePath
  - Plugin log file.
  - If empty, the log file name will be set based on the mainScriptName.
    - `f"{pathlib.Path(self.MAIN_SCRIPT_NAME).resolve().parent}{os.sep}{pathlib.Path(self.MAIN_SCRIPT_NAME).stem}.log" `
- pluginID
  - Plugin ID
- settings
  - Default settings for the plugin UI fields
- config
  - From pluginName_config.py or pluginName_setting.py
- fragmentServer
  - Fragment server data.
- stash_url
  - Stash URL (endpoint URL) Example: http://localhost:9999
- DebugTraceFieldName
  - Field name (in settings or config) for DebugTrace. Default = `"zzdebugTracing"`
- DryRunFieldName
  - Field name (in settings or config) for DryRun. Default = `"zzdryRun"`

## StashPluginHelper Functions
### Log
By default, logs out messages to both plugin log file and to console. And it logs at logging level INFO.
It automatically gets the source code line number of the calling source code, unless lineNo is set.
#### Log Arguments
- logMsg
  - The message to log out.
  - This is the only **required** argument.
- printTo
  - What to log out to. Default = log_to_norm which by default equals (LOG_TO_FILE + LOG_TO_CONSOLE)
  - Possible values which can be combined:
    - LOG_TO_FILE
    - LOG_TO_CONSOLE
    - LOG_TO_STDERR
    - LOG_TO_STASH
- logLevel
  - Logging level. Default = logging.INFO.
  - Possible values:
    - logging.DEBUG
    - logging.INFO
    - logging.WARN
    - logging.ERROR
    - logging.CRITICAL
- lineNo
  - Calling source code line number. Default = -1.
  - When value is -1, the Log function will automatically get line number using `inspect.currentframe().f_back.f_lineno`.
- levelStr
  - Use this variable to override the default level prefix message.
- logAlways
  - When set to True, it will cause logging to occur even if log file was open with logging level INFO.
  - Only applies to the plugin log file.

### Trace
By default, only logs out if debug trace is enabled, and it logs in logging level DEBUG and only the the plugin log file.
#### Trace Arguments
- logMsg
  - Message to log out.
  - This is an optional argument. If empty the message value is set to `f"Line number {lineNo}..."`.
- printTo
  - What to log out to. Default = LOG_TO_FILE
    - Default value logs to the plugin log file only.
  - Possible values which can be combined:
    - LOG_TO_FILE
    - LOG_TO_CONSOLE
    - LOG_TO_STDERR
    - LOG_TO_STASH
- logAlways
  - When set to True, it will cause logging to occur even if log file was open with logging level INFO.

### Error
By default, logs out message to LOG_TO_FILE and LOG_TO_STDERR.
In plugin mode, LOG_TO_STDERR goes to the Stash primary log file.
In command line mode, LOG_TO_STDERR gets sent to the console screen.
Logs in logging level logging.ERROR.
#### Error Arguments
- logMsg
  - Message to log out.
  - This is the only **required** argument.
- printTo
  - What to log out to. Default = LOG_TO_FILE + LOG_TO_STDERR

### Warn
By default, logs out message to LOG_TO_FILE and LOG_TO_STASH.
Logs in logging level logging.WARN.
#### Warn Arguments
- logMsg
  - Message to log out.
  - This is the only **required** argument.
- printTo
  - What to log out to. Default = LOG_TO_FILE + LOG_TO_STASH


## Requirements
`pip install stashapp-tools --upgrade`

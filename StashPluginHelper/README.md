# StashPluginHelper: Ver 0.1.0 (By David Maisonave)
StashPluginHelper is a class that performs common implementation used in most plugins.

### Features
- Log Features:
  - Optionally log out to multiple outputs for each Log or Trace call.
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

### StashPluginHelper Usage
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

### StashPluginHelper arguments
- debugTracing
  - Default: False
  - Set to true to enable debug tracing, and to open the plugin log file with logging level logging.DEBUG.
  - When debugTracing is false, the Trace logging does not output any logging unless argument (**logAlways**=True) is pass to Trace.
- logFormat
  - Plugin log line format. Default = `"[%(asctime)s] %(message)s"`
- dateFmt
  - Date format when logging to plugin log file. Default = `"%y%m%d %H:%M:%S"`
- maxbytes
  - Maximum size of plugin log file. Default = 1MB
- backupcount
  - Backup counts when log file size reaches max size
- logToWrnSet
  - Customize the target output set which will get warning logging
- logToErrSet
  - Customize the target output set which will get error logging
- logToNormSet
  - Customize the target output set which will get normal logging
- logFilePath
  - Plugin log file. If empty, the log file name will be set based on current python file name and path
- mainScriptName
  - The main plugin script file name (full path)
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



### Requirements
`pip install stashapp-tools --upgrade`

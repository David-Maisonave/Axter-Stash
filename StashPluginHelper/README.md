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
- All the arguments for StashPluginHelper class are optional.
  - It can be called with no arguments if the plugin has NO UI settings and NO associated (*_config.py) file.
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

### Requirements
`pip install stashapp-tools --upgrade`

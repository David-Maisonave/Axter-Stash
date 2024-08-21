@ECHO OFF
echo Hello, world from batch script! arg = %*

echo Hello, world from batch script! arg = %* > %~dp0\\MyDummyFileFromBatchTestFor_FileMonitor.txt

exit /b 0
@ECHO OFF
echo Hello, world#2 from batch script! arg = %*

echo Hello, world#2 from batch script! arg = %* > %~dp0\\MyDummyFileFromBatch2TestFor_FileMonitor.txt

exit /b 0
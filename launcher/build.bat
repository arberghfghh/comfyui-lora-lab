@echo off
rem Rebuilds LoRALab.exe with the C# compiler that ships with Windows.
"%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /codepage:65001 /target:winexe /win32icon:LoRALab.ico ^
  /r:System.Windows.Forms.dll /r:System.Drawing.dll /r:System.Core.dll /r:System.Web.Extensions.dll /out:LoRALab.exe LoRALab.cs

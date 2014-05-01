# pydown # 
## Idee ##
Die Idee ist, pydown auf einem Server immer im Hintergrund laufen zu lassen. In bestimmten Intervallen überprüft pydown in Konfigurationsdateien definierte Seiten und läd, wenn es neue Dateien die z.B. einem bestimmten Regrulären Ausdruck genügen, diese Dateien in einen definierten Ordner. 
Somit soll insbesondere der Übungsaufgabenblatt Download automatisiert werden.
## Aufbau ##
pydown besteht aus mehreren Teilen. Das Hauptprogramm parsed die Konfigurationsdateien und initiiert die Downloads etc. 
Zudem gibt es eine einfache Möglichkeit zum Loggen der Ereignisse, für das Ilias sowie die ExPhysSeite und die Ana Seite (möglicherweise auch Mediendownload) Downloader. 
## Licence ##
-
## to do ##
* Spezifikation in welche Module man die Programmierarbeit aufteilen will
* Implementierung der Authetifizierung (jeweils)
* Logger
* Waypoints? 
* Licence
* Welche Libraries
* Test schreiben? :D
* Je nachdem welche libs wir brauchen: https://wiki.python.org/moin/Python2orPython3

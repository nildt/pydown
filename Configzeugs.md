https://wiki.python.org/moin/ConfigParserExamples

* Im Configfile sollte enthalten sein: 
* Die Art des Downloads (Ilias, HttpGet, HttpPost, whatever) [Kann man vllt sogar noch besser zusammenfassen, je nach Implementierung]
* Der Speicherpfad
* Ein Regulärer Ausdruck zum Herunterladen der Dateien
* Benutzername und Passwort (Je nachdem welcher Typ... --> In Ana braucht man schließlich kein PW...)
* Unter Umständen der Name, unter dem das Heruntergeladene gespeichert werden soll, mit einer Zählvariable oder so 
* Andere Einstellungen...?
* Vielleicht einige Programm Einstellungen, z.B. ob DebugMeldungen ausgegeben werden sollen etc.

Bsp:

	[Blub]
	url     = url.bei/der/nach/neuen_dateien/gesucht/werden/soll
	regex   = downloads/regex[0-9]*\.pdf
	
	#Optional:
	outDir  = output/direcory/
	
	login   = meinName
	pssw    = passw234
	#askAuth sorgt dafür, dass login und pssw mit einer Consoleneingabe überschieben werden
	askAuth = true


# NLP-Wiki-Crawler
Ich habe für mehr Testdaten einen Crawler geschrieben, der Wikipedia
Pages abgrast und sich ein csv anlegt mit [language;url;text]
Wobei language = G , E oder X
Der Crawler besucht nur Seiten, die er nicht bereits besucht hat.
Der Crawler entfernt Zahlen und einige Sonderzeichen, sowie Begriffe,
die nicht zum eigentlichen Artikelinhalt gehören.

Ihr könnt mit der Funktion Spider#append eigene Einstiegs-Urls angeben.
Mit Spider#crawl startet ihr den Vorgang.
Beim Contructor Spider den Parameter resume=True setzen, um mit der
letzten abgelegten URL weiter zu machen.
 
Zum Abbrechen einfach jederzeit Ctrl+C drücken (Die Resultate werden
fortlaufend abgelegt, gehen also nicht verloren).

In der Konsole das Python-Script starten mit

> conda activate base

> python ./crawl.py

(allfällig Module mit `conda install` nachinstallieren)

# NLP-Wiki-Crawler
Ich habe für mehr Testdaten einen Crawler geschrieben, der Wikipedia Pages abgrast und sich ein csv anlegt mit `language;url;text` (Wobei language = 'G' , 'E' oder 'X').

Der Crawler besucht nur Seiten, die er nicht bereits besucht hat. <br>
Der Crawler entfernt Zahlen und einige Sonderzeichen, sowie Begriffe, die nicht zum eigentlichen Artikelinhalt gehören.

Ihr könnt mit der Funktion `Spider#append` eigene Einstiegs-Urls angeben.
Mit `Spider#crawl` startet ihr den Vorgang. <br>
Beim Contructor Spider den Parameter `resume=True` setzen, um mit den zuletzt abgelegten URLs weiter zu machen.
 
Zum Abbrechen einfach jederzeit `Ctrl+C` drücken (Die Resultate werden fortlaufend abgelegt, gehen also nicht verloren). Auch wird der state in Spider.state gespeichert. <br> Dieser wird wieder aufgenommen, wenn `resume=True`.

In der Konsole das Python-Script starten mit

> conda activate base

> python ./crawl.py

(allfällig Module mit `conda install` nachinstallieren)

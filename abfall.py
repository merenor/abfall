#!/usr/bin/env python

# Abfallkalender-Skript für die neue Wohnung. 07.08.2016

import csv
import datetime
import locale
import logging
import pickle
import random
import smtplib
from email.mime.text import MIMEText

# Einige lustige Variablen
ini = {
    'kalenderdatei':    '/home/felix/Dokumente/py/abfall/abfallkalender2016.csv',
    'pickle':           '/home/felix/Dokumente/py/abfall/datum.p',
    'log':              '/home/felix/Dokumente/py/abfall/abfall.log',
    'empfaenger':       ['felix@werthschulte.info', 'lena@werthschulte.info'],
    'absender':         'f.werthschulte@gmx.de',
    'passwort':         'DDR19swr08hr?',
    'serveradresse':    'mail.gmx.net',
    'namen':            ["Gustave Millebotte", "Antonnia Forditura", 
                        "Lasse di Tonni-Abole", "James Mylbott", "Supermindt", 
                        "Rumpel von Ohnesorg", "Malthilda Allt-Bapyr",
                        "Oscar Tönnerich", "Walther von der Kirschenplantage"],
}


# Auf Deutsch, bitte
locale.setlocale(locale.LC_ALL, '')

# Logging konfigurieren
logging.basicConfig(filename = ini['log'],level = logging.DEBUG, 
    format='%(asctime)s - %(message)s', datefmt='%d.%m.%Y %I:%M')


class Termin:

    def __init__(self, tag, monat, muell):
        self.datum = datetime.date(2016, int(monat), int(tag))
        self.tag = tag
        self.monat = monat
        self.muell = muell

    def getDatum(self):
        return self.datum.strftime("%A, %d.%m.")
        
    def getMuell(self):
        return self.muell
        
    def istMorgen(self):
        return self.datum == datetime.date.today() + datetime.timedelta(1)
        
    def istInnerhalbEinerWoche(self):
        wert = False
        
        for i in range(0, 7):
            if self.datum == datetime.date.today() + datetime.timedelta(i):
                wert = True
        
        return wert


def readAbfallkalender(file):

    """
    Liest den Abfallkalender aus einer CSV-Datei namens (standard)
    abfallkalender2016.csv in eine Liste mit Termin-Objekten
    
    """
    
    kalender = []
    
    with open(file) as f:
        reader = csv.DictReader(f)
        for r in reader:
            kalender.append(Termin(r['tag'], r['monat'], r['muell']))
        f.close()
    
    return kalender


def logSendeEMail():

    """
    Schreibt das heutige Datum als String in eine Pickle-Datei
    
    """

    with open(ini['pickle'], 'wb') as f:
        pickle.dump(str(datetime.date.today()), f)
        f.close()


def istBereitsGesendet():

    """
    Versucht die Pickle-Datei zu öffnen. Falls sie existisrt und die
    dort hinterlegten Daten dem heutigen Tag entsprechen, gibt die
    Funktion True zurück
    
    """

    try:
        with open(ini['pickle'], 'rb') as f:
            gespeichertesDatum = pickle.load(f)
            f.close()
    
        return gespeichertesDatum == str(datetime.date.today())
    
    except:
        return False


def sendeEMail(t):

    namen = ini['namen']
    
    #empfaenger    = ['felix@werthschulte.info']
    empfaenger    = ini['empfaenger']
        
    absender      = ini['absender']
    passwort      = ini['passwort']
    serveradresse = ini['serveradresse']
        
    server = smtplib.SMTP(serveradresse)
    server.starttls()
    server.ehlo()
    server.login(absender, passwort)
    
    name = random.choice(namen)
    
    nachricht = MIMEText("Hallo ihr Lieben,\n\nhier ist {}. ".format(name) +
    "Ich habe einen neuen Abfalltermin für euch:\n\n" +
    "Für den morgigen {} müsst ihr heute die *{}-Tonne* rausstellen.\n\n".format(t.getDatum(), t.getMuell()) +
    "Viel Vergnügen!\n{}".format(name))
    nachricht['Subject'] = "Abfalltermin morgen, {}".format(t.getDatum())
    nachricht['From'] = "{} <{}>".format(name, absender)
    nachricht['To'] = ", ".join(empfaenger)
    
    server.sendmail(absender, empfaenger, nachricht.as_string())
    server.quit()

    # Loggen, dass wir die Mail gesendet haben
    logSendeEMail()


def main():
    
    logging.info("Programm gestartet.")
    
    # Einlesen des Abfallkalenders aus CSV-Datei
    termine = readAbfallkalender(ini['kalenderdatei'])
    
    # Alle Termine durchlaufen. Wenn ein Termin morgen ansteht,
    # überprüfen, ob heute bereits eine Mail gesendet wurde. Falls nicht,
    # eine Mail senden
    
    gefunden = False
    
    for t in termine:
        if t.istMorgen():
            gefunden = True
            if istBereitsGesendet():
                logging.info("E-Mail wurde heute bereits verschickt.")
            else:
                logging.info("Termin gefunden. Sende E-Mail...")
                sendeEMail(t)
        
    if not gefunden:
        logging.info("Nichts zu tun.")
    
    logging.info("Programm beendet.")

if __name__ == '__main__':
    main()

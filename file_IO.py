#!usr/bin/python
# -*- coding: UTF-8 -*-

# fileIO.py
# 
import sqlite3

from class_def import User
from class_def import Database
from class_def import SQLCommand


# Kts. SQLite ohje.
# Avaa ja yhdistää SQLite3-muotoiseen tietokantaan.
# 
def bindSQLite3DB():
    database = Database() # Kts. luokan määritys
    database.path = input("\nSyötä avattavan tietokantatiedoston polku tai hyväksy oletusarvo (tietokanta2.db) painamalla [enter]: > ")

    if database.path == "": # Annetaan oletuspolku
        database.path = "tietokanta2.db"

    try: # Onnistuuko yhteyden luominen?
        database.connection = sqlite3.connect(database.path)
    except:
        print("VIRHE: SQLite3-tietokantayhteyttä ei voida muodostaa (" + database.path + ")")
        return None # Virhetilan kontrollointiin.
    else:
        # Asetetaan vierasavainten eheystarkistukset päälle.
        cursor = database.connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        database.connection.commit()
 
        print("\nYhdistettiin '" + database.path + "'")
 
        return database # Palautetaan Database()-objekti.


# Lataa käyttäjätiedot tiedostosta.
# Kts. users.data -tiedosto
# 
def loadUserData():
    users = []

    try:
        file_r = open("users.data", "r", encoding="utf-8")
   
        while True:
            line = file_r.readline()
            if len(line) == 0:
                break
            elif line[0] == "\n":
                break
            elif line[0] == "#": # Kommenttirivi
                continue

            # Rivi koostuu ":"-merkillä erotelluista elementeistä, joten
            # pätkitään sen perusteella osiin.
            line_data = line[:-1].split(":")
            new_user = User()
            new_user.ID = line_data[0]
            new_user.passwd = line_data[1]
            new_user.group = line_data[2]
            users.append(new_user)
        # while

        if len(users) < 1:
            print("VIRHE: Tiedostossa 'users.data' ei ole määritetty yhtäkään käyttäjää.")
            return None # None-arvo signaloi virheestä

    except IOError:
        print("\nVIRHE: Tiedoston 'users.data' avaaminen ei onnistu.")
        return None   
    except Exception as error:
        print("\nVIRHE: Tiedoston 'users.data' parseroinnissa tapahtui virhe:", error)
        return None
    else:
        return users # Virhetilaa ei tapahtunut.


# loadSQLCommands:n -apufunktio. Prosessoi yksittäisen rivin.
# alempi funktio on vain pilkottu pienemmäksi kahteen osaan.
#
def parseCmdLine(line, mode, sub_mode, sql_cmd, sql_set):
    # Sub_mode kontrolloi {}-pareja, jotta hanskataan
    # sisäkkäsiet {]-osiot, esim osana SQL:ää. Pidetään kirjaa
    # miten "syvällä" merkkipareissa ollaan. 

    # Prosessoidaan tässä funktiossa aina vain saatu rivi
    for i in range(len(line)):
        if line[i] == "{": 
            sub_mode += 1
            continue # Ei prosessoida kaarisulkua lisää.
                    
        elif line[i] == "}":
            sub_mode -= 1 # Pari sulkeutui.
      
            # Jos viimeinen kaarisulkupari sulkeutui,
            # kasvatetaan modea.
            # Tukee siis usealle riville jaettuja komentoja
            # Jos mode on jo 4, lopetetaan koko query.
            if sub_mode == 0:
                if mode < 4:
                    mode += 1
                    continue # Aloita uusi for-kierros
                else:
                    sql_set.append(sql_cmd) # Valmis -> listaan.
                    mode = 0
                    break # Lopeta for -> return
              
        # Käsitellään muita merkkejä:
              
        # Ollaan nimike-rivillä
        if mode == 1:
            sql_cmd.descr += line[i]

        # Käyttäjäryhmät-rivillä.          
        elif mode == 2:
            if line[i] == ",": 
                sql_cmd.groups.append("")
                continue
            else:
                sql_cmd.groups[-1] += line[i]

        # Muuttujat-rivillä
        elif mode == 3: 
            if line[i] == ",":
               sql_cmd.variables.append("")
               continue
            else:
               sql_cmd.variables[-1] += line[i]

        # SQL-komento-rivillä
        else: # mode == 4
            sql_cmd.SQL += line[i]  

        # if..elif..else
    # for

    return mode, sub_mode, sql_cmd
  

# Lataa tiedostosta SQL-kyselyt ja niiden suorittamiseen
# vaadittavat tiedot ja palauttaa ne listana.
# Kts. HT-ohjeesta lisätietoja.
#        
# Muistio: Kunkin kyselyn formaatti tiedostossa, esim:  
# Query:
# {Listaa pelaajan tiedot.}
# {secretary}
# {Pelaajan nimi}
# {SELECT * FROM Pelaaja WHERE NIMI = "\1\"}
# 
# Kukin {}-tagi voi jakautua usealle riville. 
#
def loadSQLCommands(user, database):
    sql_set = [] # Lista ladatuista SQL-komennoista (tässä versiossa vain kyselyjä)
    path = ""
    mode = 0 # kontrollimuuttuja, kts. myös parseCmdLine. 
    sub_mode = 0 # kontrolli

    # Muodostetaan tiedostopolku, joka on tietokannan polku
    # .sql päätteellä. Esim tietokanta -> tietokanta.sql
    # tai varasto_db.lite3 -> varasto_db.sql, jne.
    if ("." in database.path):
        temp = database.path.split(".")[:-1] + [".sql"]
        for i in range(len(temp)):
            path = path + temp[i]
    else:
        path = path + ".sql"

    # Parsitaan tiedosto...
    try:
        file_r = open(path, "r")

        # Luetaan rivi kerrallaan
        for line in file_r:
            if line[0] == "#":
                continue
            elif line[0] == "\n":
                continue # Skipataan nämä rivit.
           
            line = line[:-1] # Poistetaan rivinvaihto.

            # Aloitetaanko komennon parsiminen?
            # Mode kasvaa jatkossa 1..4 riippuen, mitä komennon osa-aluetta luetaan.
            if line == "Query:":
                mode = 1 
                sql_cmd = SQLCommand() # Aloita uusi komento
                sql_cmd.groups = [""]
                sql_cmd.variables = [""]

                continue # Aloita uusi for-kierros, eli lue taas uusi rivi
            
            if mode > 0: # Parsitaan komentoon kuuluva rivi
                mode, sub_mode, sql_cmd = parseCmdLine(line, mode, sub_mode, sql_cmd, sql_set)
            else:
                pass # Tuntematon käsky tässä versiossa, skipataan.

    except IOError:
        print("VIRHE: Yritettiin lukea SQL-kyselykomentoja.")
        print("Tiedostoa '" + path + "' ei voida avata.")
        return None
    except Exception as error:
        print("VIRHE:", error, "-virhetilanne parsittaessa kyselykomentoja tiedostosta '" + path + "'.")
        return None
    else: # Kaikki meni OK; palautetaan lista.
        return sql_set



#!usr/bin/python
# -*- coding:UTF-8 -*-

# UI.PY
# 
# 
import sys
from copy import deepcopy
from file_IO import *
from query import *
from insert_alter import *


# Aliohjelma antaa käyttäjän valita, mikä kysely suoritetaan.
# Ksyelyt listataan dynaamisesti käyttöoikeuksien perusteella.
# Vrt. Kiinteät INSERT INTO yms. SQL-lausekkeet koodissa.
# Tämä on vaihtoehtoinen tapa "upottaa" SQL:ää.
#
def selectQuery(user_group, sql_set, database):
    sql_queries = [] # Kyselyt, joihin suoritusoikeus.

    # Viedään erilliseen listaan ne kyselyt, joihin käyttäjällä
    # on oikeus.
    for sql_cmd in sql_set:
        for group in sql_cmd.groups:
            if user_group == group: # Käyttöoikeus löytyy.
                sql_queries.append(sql_cmd)     
                break # Ei tarvitse lukea listaa pidemmälle.
    
    # Tulostetaan kyselyt-valikko kuvauskenttien perusteella:
    # (1) Listaa Pelaajat, joilla on....
    # (2) Tulosta otteluiden....
    # ...jne dynaamisesti.
    # (0) Paluu. 
    while True:
        print("\nValitse suoritettava kysely:\n")
        for index, sql_cmd in enumerate(sql_queries):
            print("(" + str(index + 1) + ")", sql_cmd.descr)
        
        print("(0) Palaa tehtävävalikkoon.")

        selection = int(input("> "))

        if selection <= 0:
            break # -> return
        elif selection <= len(sql_queries): # Valittu lemassaoleva kysely.
            # Emme lähetä suoraan listan alkiota, koska
            # emme halua viitata/osoittaa siihen.
            # Näin voimme muokata sitä turvallisesti.
            sql_cmd = deepcopy(sql_queries[selection-1])
            runQuery(sql_cmd, database)
            input()
                 
    return


def selectInsertRecord(user_group, db_connection):
    
    if user_group == "varastomies":
        print("Käyttäjtunnuksella ei ole tällä hetkellä lisäämisoikeuksia.")
        return

    print("\nValitse syötettävä tietue:\n")
    print("(1) Uusi asiakas")
    print("(2) Uusi asiakkaan tilaus")
    print("(3) Uusi kuriiri")
    print("(4) Uusi työntekijä")
    print("(5) Uusi omatilaus")
    print("(6) Uusi tuote")
    print("(7) Uusi toimittaja")

    print("(0) Palaa edelliseen valikkoon.")    

    selection = int(input("> "))

    # Käytetään räätälöityjä lisäysfunktioita.
    
  #  if selection == 1:
    #    insertRecordGame(db_connection)
    #elif selection == 2:
     #   insertRecordPlayer(db_connection)

    # Käytetään geneeristä lisäysfunktiota.
    
    if selection == 1:
        insertRecordAsiakas(db_connection)
    elif selection == 2:
        insertRecordAsiakkaan_tilaus(db_connection)
    elif selection == 3:
        insertRecordKuriiri(db_connection)
    elif selection == 4:
        insertRecordTyontekija(db_connection)
    elif selection == 5:
        insertRecordOmatilaus(db_connection)
    elif selection == 6:
        insertRecordTuote(db_connection)
    elif selection == 7:
        insertRecordToimittaja(db_connection)
    else:
        print("Tunnistamaton valinta!")


    input()
    return


# Toimintovalikko, joka esitetään käyttäjälle, kun tämä on
# kirjautunut, tietokantayhteys on muodostettu ja 
# SQL-kyselyt ovat ladattu tiedostosta.
# Funktio tuo vastaavat tietorakenteet tietysti parametreina.
# 
def displayTaskMenu(user, sql_set, database):

    while True:
        print("\nDATAMARKET VARASTO v1.0 (user:" + user.ID, "db:" + database.path + ")")
        print("*************")
        print("(1) Suorita kysely")
        print("(2) Syötä uusi tietue")
        print("(3) Muuta tietueen arvoja")
        print("(0) Sulje tietokanta")

        selection = int(input("> "))

        if selection == 1:
            selectQuery(user.group, sql_set, database)
        elif selection == 2:
            selectInsertRecord(user.group, database.connection)
        elif selection == 3:
            alterRecord(user.group, database.connection)
        elif selection == 0: # Nollalla suljetaan tietokanta
            database.connection.close()
            return
        else:
            print("Tunnistamaton valinta!")


# Esittää valikon, josta voidaan avata tietokanta.
# Käyttäjätieto-objekti saadaan parametrina, joten käyttäjä 
# tulee olla asetettu ennen kutsua.
# 
def connectDatabase(user):
    while True:
        print("\nDATAMARKET VARASTO v1.0 (user:" + user.ID + ")")
        print("*************")
        print("(1) Avaa tietokanta")
        print("(0) Kirjaudu ulos")

        selection = int(input("> "))
                
        if selection == 1:
            database = bindSQLite3DB()
            if database != None: # Yhdistäminen onnistui.
                sql_set = loadSQLCommands(user, database)
                if sql_set != None: # Kyselyiden lataus onnistui.
                    displayTaskMenu(user, sql_set, database)
        else:
            return


# Aliohjelma esittää valikon, jossa tunnistetaan käyttäjä.
# 
# 
def selectUser():
    # Ladataan ensin käyttäjätiedot listaan tiedostosta.
    users = loadUserData()
    if users == None: # Jos tapahtui virhe, ei jatketa.
        return None # Signaloidaan virhetilasta alemmas.

    print("\nKirjaudu syöttämällä käyttäjätunnus ja salasana.")
    ID = input("Käyttäjätunnus: ")    
    passwd = input("Salasana: ")
    
    # Onko käyttäjätunnus olemassa?
    # Jos pari löytyy, palautetaan vastaava users-listan alkio
    for user in users:
        if user.ID == ID and user.passwd == passwd:
            return user
    else: # Huom. Pythonin for-else rakenne! 
        print("Käyttäjätunnus ja salasana eivät täsmää.")
        return None



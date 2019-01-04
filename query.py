#!usr/bin/python
# -*- coding: UTF-8 -*-

# QUERY.PY
# 

from class_def import debug_mode


# Aliohjelma on executeQuery:n apufunktio, joka ottaa
# parametrina SQLCoomand()-objektin ja korvaa sen SQL-
# lauseke osiossa olevat muuttuja-tägit käyttäjän
# syöttämillä arvoilla niin, että kysely voidaan 
# suorittaa.
# esim: SELECT * From Pelaaja WHERE Nimi = "\1\" 
# -> SELECT * From Pelaaja WHERE Nimi = "Matti" 
# 
def fillVariableValuesinQuery(sql_cmd):
    var_values = [] # Muuttujien arvot
    var_filled_cmd = "" # Muuttuja-arvoilla täydennetty lauseke

    print("\nSyötä kyselyn tiedot:")
    for var_descr in sql_cmd.variables:
        var_values.append(input(var_descr + ": "))

    # Syötetään var_values-listan arvot nyt niille tarkoi-
    # tettuihin kohtiin kyselykoodissa.
    # Muuttujan järjestysluku 1..10..100 on mielivaltainen.
    # Myös järjestys SQL-koodissa on vapaa.
    # Huom. '\'-merkki = '\\' Python-literaalina.
    # Python ei salli for-silmukkamuuttujan päivittämistä
    # silmukan sisällä, joten ulompi silmukka tehdään
    # whilella ja kasvatetaan indeksiä manuaalisesti.

    i = 0

    while (i < len(sql_cmd.SQL)):
        if sql_cmd.SQL[i] != "\\":
            var_filled_cmd += sql_cmd.SQL[i]
        else: # Luetaan \-merkkein väli
            index = "" # Muuttujan järjestysluku
            for i in range(i+1, len(sql_cmd.SQL)):
                if (sql_cmd.SQL[i] == "\\"):
                    # Haetaan aiemmin luodusta listasta.
                    var_filled_cmd += var_values[int(index)-1]
                    break

                index = index + sql_cmd.SQL[i]

        i += 1 # Kasvatetaan i:tä whilea varten.

    return var_filled_cmd


# executeQuery:n apufunktio. Aliohjelma tulostaa kyselyn 
# tulokset muotoillusti käyttäjälle.
#
def printQueryResults(sql3_output, sql3_descr, flag=False):
    max_lens = [] # Lista sarakkeiden maksimipituuksista
    titles = []
    num_dashes = 0

    # Täytetään nollilla, sarakkeiden lukumäärän verran.
    if len(sql3_output) > 0:
        max_lens = len(sql3_output[0]) * [0]
    else:
        print("\nEi tuloksia.")
        return 0

    # Tutkitaan, montako merkkiä pitää kullekin sarakkeelle
    # maksimissaan varata muotoiltua tulostusta varten.
    
    # Poimitaan ensin attribuuttien nimet.
    for row in sql3_descr:
        titles.append(row[0])

    # Liitetään ne tuloslistan alkuun.
    sql3_output.insert(0, titles)

    # Käydään lista läpi riveittäin ja laitetaan muistiin 
    # sarakekohtainen merkkijonon maksimipituus.
    for row in sql3_output:
        for i, column in enumerate(row):
            if len(str(column)) > max_lens[i]:
                max_lens[i] = len(str(column)) +30

    # Voidaan nyt tulostaa muotoillusti.
    # Tasataan vasemmalle kukin sarake maksimipituuden verran.
    num_dashes = sum(max_lens) + len(sql3_output[0]) - 1
    first = True

    for row in sql3_output:
        print()
        for i, column in enumerate(row):
            print(str(column).ljust(max_lens[i]), end="")
        if (first):
            print("\n" + num_dashes * "-", end="")
            first = False

    print()
    # Tulostetaanko taulukon alle lisätietoa?
    # Ei käytetä esim. INSERTtien yhteydessä.
    if (flag):
        print(num_dashes * "-")
        print("(Tietueita:", str(len(sql3_output) - 1) + ")")
     
    return


# Funktio suorittaa vapaamuotoisen kyselyn.
# Kysely suoritetaan eri tavalla kuin lisäys ja 
# päivitystoiminnot. Tämä on vaihtoehtoinen tapa
# "upottaa" SQL:ää niin, että koodi on kompaktimpaa, mutta
# komennot määritetään erillisessä tiedostossa.
# 
def runQuery(sql_cmd, database):

    # Jos komennolla on muuttujia, kysytään kunkin arvo käyttäjältä ja lisätään ne erillsieen listaam. 
    # Muuten suoritetaan lauseke suoraan.
    if (sql_cmd.variables[0] != ""):
        sql_cmd.SQL = fillVariableValuesinQuery(sql_cmd)

    # Voidaan edetä suorittamaan itse kysely.
    if (debug_mode):
        print("\nDebug (runQuery):", sql_cmd.SQL)

    cursor = database.connection.cursor()  
    cursor.execute(sql_cmd.SQL)

    printQueryResults(cursor.fetchall(), cursor.description, True)

    return


#!usr/bin/python
# -*- coding: UTF-8 -*-

# CLASS_DEF:PY
#

# Globaalit "vakiot."
 
debug_mode = False


# ******************************************************
# Luokkamääritykset:
# ******************************************************
# Käytetään kuin C:n strukteja. Emme olio-ohjelmoi tässä vaan
# pitäydymme Ohjelm.perusteet-kurssin ratkaisutavoissa.

# SQLite 3-tietokantayhteyden hallinnointiin.
class Database:
    path = ""
    connection = None # sqlite3.connect()
    cursor = None # connection.cursor()

# Käyttöoikeuksien hallintaam.
class User:
    ID = str()
    passwd = str()
    group = str()

# Kyselyjen (tai muiden) tiedostosta luettavien SQL-komentojen
# hallinnointiin.
class SQLCommand:
    descr = str() # description, kuvaus
    groups = [""] # käyttöoikeudet omaavat ryhmät
    variables = [""] # SQL-koodiin upotettvat muuttujat
    SQL = str() # SQL-lauseke 



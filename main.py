#!usr/bin/python
# -*- coding: UTF-8 -*-
# Tuodaan kirjastot ja moduulit.
import sqlite3

from UI import *

# Huomautuksia:
# 
#  
# Ohjelman päävalikko.
#  
def main():

    while True:
        print("\nDATAMARKET VARASTO v1.0")
        print("*************")
        print("(1) Kirjaudu käyttäjätunnuksella")
        print("(0) Lopeta")

        selection = int(input("> "))

        if selection == 1:
            user = selectUser()
            if user != None:
                connectDatabase(user)

        # Ohjelmassa ylipäätään mikä vain muukin numero, joka
        # ei ole valikossa käytössä kuin vain nolla vastaa 
        # "palaa" toimintoa. Näin ei tarvitse joka kerta kirjoittaa 
        # monimutkaista if-else-else -rakennetta. 
        else:
            break

    return

### ALOITETAAN TÄSTÄ 

main()


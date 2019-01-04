# INSERT_ALTER.PY
#

from query import printQueryResults
from class_def import debug_mode


# Yleiskäyttöinen aliohjelma, joka suorittaa SQL-INSERT-
# komennon tietokantaa vastaan. Funktio ottaa INSERTin
# parametrina merkkijonona. Toinen parametri on sqlite3.
# connection-tyyppinen objekti.
# 
def executeSQLInsert(sql_cmd, db_connection):
    cursor = db_connection.cursor()    
    try:
        cursor.execute(sql_cmd)
        db_connection.commit()
    except Exception as error: 
        db_connection.rollback() 
        print("\nVIRHE: Tietueen lisäys ei onnistunut.")
        print("SQLite:", error,)
    else:
        print("\nLisäys suoritettu.")

    return


# Aliohjelmaa hyödynnetään räätälöidyissä insert* 
# funktioissa. Palauttaa seuraavan vapaana olevan
# pääavainarvon, kun parametrina on annettu attribuutin
# nimi, taulu, ja sqlite3.connection.cursor-objekti.
# Huom: tulisi päivittää seuraavasti:
# - Ei tarvita attribute-parametria, koska se voidaan selvittää
#   taulun nimen avulla kyselyllä.
# - Tällöin voidaan tukea n-osaisia avaimia ja palauttaa aina
#   n-pituinen lista, jossa uusi avainarvoyhdistelmä (1..N)
# 
def fetchNextPrimaryKeyValue(attribute, table, cursor):
    cursor.execute("SELECT " + attribute + " FROM " + table)
    lite3_output = cursor.fetchall()
    # [-1] --> viimeinen alkio, [-1][0] --> 2-ulotteisen
    # listan 1. alkio.
    return (int(lite3_output[-1][0]) + 1)


# Aliohjelman avulla voidaan suorittaa UPDATE ja DELETE
# SQL-komentoja mielivaltaista tietokantaa vastaan.
# 
def alterRecord(user_group, db_connection):  # Tietokannan tietoja muokkaamalla voidaan tuottaa suurta haittaa tietokannan eheydelle. Tämän takia tietoja voi muokata vain admin
    if user_group == "varastomies":
        print("Käyttäjtunnuksella ei ole tällä hetkellä muokkausoikeuksia.")    
        return
    if user_group == "sihteeri":
        print("Käyttäjtunnuksella ei ole tällä hetkellä muokkausoikeuksia.")    
        return

    cursor = db_connection.cursor()

    print("\nValitse taulu, jonka tietoja muutetaan:\n")

    cursor.execute("SELECT name AS 'Taulu' FROM sqlite_master WHERE type = 'table'")
    printQueryResults(cursor.fetchall(), cursor.description)
    table = str(input("\n> "))

    print("\nValitse kohteena oleva tietue:\n")

    cursor.execute("SELECT * FROM " + table)
    printQueryResults(cursor.fetchall(), cursor.description)

    print("\nSyötä ID päivittääksesi tietueen.")
    print("Syötä P ID poistaaksesi tietueen.")
    print("Syötä (P) ID ID ... kun kysessä on moniosainen avain.")

    # .split palauttaa listan; kts. Python funktiot.
    ID_set = input("(ID) > ").split(" ")

    if ID_set[0] == "P": 
        # Lähetetään leikkaus [1:] -> alkiot 1, 2, 3...
        # Koska aliohjelma ei odota muuta kuin ID-settiä.
        deleteRecord(ID_set[1:], table, db_connection)        
    else:
        updateRecord(ID_set, table, db_connection)

    input()
    return


# Aliohjelma suorittaa varsinaisen DELETE-komennon tietokantaa
# vastaan. Ottaa parametrina listan, jossa ovat poistettavan
# tietueen pääavainattribuuttien arvot, esim. [1, 'P']
# Funktio selvittää tämän tiedon perusteella tarvistemansa 
# DELETE-lauseen muut parametrit. 
# 
def deleteRecord(ID_set, table, db_connection):
    p_key_values = [] # pääavaimet

    # Haetaan taulun SQLite3 schema. pragma tuottaa
    # 2-ulotteisen listan [attribuutin nimi][ominaisuus] 
    cursor = db_connection.cursor()
    cursor.execute("pragma table_info(" + table + ")")

    i = 0
    for column in cursor.fetchall():
        if column[5] == 1: # Onko pääavainatribuutti?
            p_key_values.append([column[1], None])
            if "VARCHAR" in column[2]:
                p_key_values[-1][1] = "'" + ID_set[i] + "'"
            else: 
                p_key_values[-1][1] = ID_set[i]
            i += 1

    # p_key_values on nyt 2-ulotteinen lista, jossa on:
    # [p-avain attribuutin nimi] [arvo] 
    # esim. [[PelaajaID, 6], [JoukkueID, 1]]

    # Voidaan rakentaa DELETE-käsky:
    sql_cmd = "DELETE FROM " + table + " WHERE "
    for i in range(len(p_key_values)):
        if i > 0:
            sql_cmd += " AND "
        sql_cmd += p_key_values[i][0] + "=" + p_key_values[i][1]

    if (debug_mode):        
        print("\nDEBUG (deleteRecord):", sql_cmd)

    try:
        cursor.execute(sql_cmd)
        db_connection.commit()
    except Exception as error: 
        db_connection.rollback() 
        print("\nVIRHE: Tietuetta ei voitu poistaa.")
        print("SQLite:", error)
    else:
        print("\nTietue poistettu.")

    return


# Kuten deleteRecord, aliohjelma suorittaa varsinaisen UPDATE-
# käskyn tietokantaa vastaam. Toimintaperiaate on vastaava kuin
# deletessä, mutta UPDATE-käskyn useiden osien vuoksi 
# joudutaan se rakentamaan vastaavasti useammin tövaihein.
# Saa parametrina kohdetietueen pääavainarvojoukon listana.
# Aliohjelma rakentaa UPDATE-käskyn tämän tiedon pohjalta.
#
def updateRecord(ID_set, table, db_connection):
    p_key_values = [] # pääavainarvot
    cursor = db_connection.cursor()

    # kts. deleteRecord
    cursor.execute("pragma table_info(" + table + ")")
    columns = cursor.fetchall()

    i = 0
    for column in columns:
        if column[5] == 1:
            if "INTEGER" in column[2]: 
                p_key_values.append([column[1], ID_set[i]])
            else:
                p_key_values.append([column[1], "'" + ID_set[i] + "'"])                            
            i += 1

    # Pitää selvittää ensin, mitkä ovat kohteena olevan
    # tietueen nykyiset arvot, jotta niitä voidaan ehdottaa 
    # käyttäjälle oletusarvoina, kun pyydetään syötteitä. 
    sql_cmd = "SELECT * FROM " + table + " WHERE "
    for i in range(len(p_key_values)):
        if i > 0:
            sql_cmd += " AND "
        sql_cmd += p_key_values[i][0] + "=" + p_key_values[i][1]

    if (debug_mode):        
        print("\nDEBUG (updateRecord):", sql_cmd)

    cursor.execute(sql_cmd)
    old_values = cursor.fetchone() 

    if (debug_mode):        
        print("DEBUG (deleteRecord):", old_values)

    print("\nSyötä kullekin attribuutille uusi arvo tai hyväksy nykyinen painamalla [enter].")

    # Voidaan alkaa rakentaa päivitettävää joukkoa.
    # Kysytään käyttäjältä kunkin kohdalla uusi arvo.
    # Pelkällä enterillä käytetään vanhaa arvoa.
    sql_cmd = "UPDATE " + table + " SET "
    for i in range(len(columns)):
        # Tulostetaan vanha arvo
        new_value = input(columns[i][1] + " (" + str(old_values[i]) + ") : ")     
        
        if new_value == "": # -> pelkkä enter
            new_value = str(old_values[i])
     
        # Lisätään pilkku eteen vasta toisesta kierroksesta lukien.
        # SET ATTR1=JokuArvo, ATTR2=JokuArvo2, ...
        if i > 0: 
            sql_cmd += ", "

        # Muistetaan lisätä '-meerkit, jos ei numeerinen arvo.
        if ("INTEGER" in columns[i][2]): 
            sql_cmd += columns[i][1] + "=" + new_value
        else:
            sql_cmd += columns[i][1] + "='" + new_value + "'"
        
    # SET-lauseke on valmis. Tarvitaan WHERE-osio, joka kertoo,
    # mikä tietue päivitetään. Käytetään muistiin laitettuja 
    # pääavaianrvoja, koska ne ainakin dentifioivat haluamamme
    # tietueen oikein. Nyt nähdään p_key_values:n tarkoitus.
    sql_cmd += " WHERE" 
    for i in range(len(p_key_values)):
        if i > 0: # Ei ANDia 1. Attr=Arvo:n eteen...
            sql_cmd += " AND"
        sql_cmd += " " + p_key_values[i][0] + "=" + p_key_values[i][1]

    if (debug_mode):        
        print("\nDEBUG (deleteRecord):", sql_cmd)
      
    try:
        cursor.execute(sql_cmd)
        db_connection.commit()
    except Exception as error: 
        db_connection.rollback() 
        print("\nVIRHE: Tietuetta ei voitu päivittää.")
        print("SQLite:", error)
    else:
        print("\nTietue päivitetty.")      

    return



##def insertRecordGame(db_connection):
##    cursor = db_connection.cursor()
##
##    newID = fetchNextPrimaryKeyValue("OtteluID", "Ottelu", cursor)
##
##    print("\nValitse kotijoukkue ja vierasjoukkue:")
##
##    cursor.execute("SELECT JoukkueID, Nimi FROM Joukkue")
##    printQueryResults(cursor.fetchall(), cursor.description)
##    home_team = input("\nKotijoukkue (ID): ")
##    visiting_team = input("Vierasjoukkue (ID): ")
##
##    category = '"' + input("Valiste otteluluokka (V/E): ") + '"'
##    score = '"' + input("Ottelun tulos: ") + '"'
##    date = input("Päiväys (pp.kk.vvvv): ")
##    temp = date.split(".")
##    date = '"' + temp[2] + "-" + temp[1] + "-" + temp[0] + '"'
## 
##    print("Valitse pelipaikka:")
##    cursor.execute("SELECT PelipaikkaID FROM Pelipaikka")
##    printQueryResults(cursor.fetchall(), cursor.description)
##
##    location = '"' + input("\nPelipaikka (ID): ") + '"'
##
##    # Rakennetaan SQL-lauseke:
##    sql_cmd = "INSERT INTO Ottelu VALUES ("
##    sql_cmd += str(newID) + "," + home_team + "," + visiting_team + "," + category + "," + score + "," + date + "," + location + ")"
##
##    if (debug_mode):        
##        print("DEBUG (insertRecordGame):", sql_cmd)
##
##    executeSQLInsert(sql_cmd, db_connection)
##
##    return

##
##def insertRecordPlayer(db_connection):
##    cursor = db_connection.cursor()
##    newID = fetchNextPrimaryKeyValue("PelaajaID", "Pelaaja", cursor)
##
##    print("\nSyötä pelaajan tiedot:\n")
##    name = '"' + input("Nimi: ") + '"'
##    number = str(input("Pelinumero: "))
##    address = '"' + input("Osoite: ") + '"'
##    phone_num = '"' + str(input("Puhelinnumero: ")) + '"'
##    score = str(input("Pisteet: "))
##    print("Joukkue:")
##
##    cursor.execute("SELECT JoukkueID, Nimi FROM Joukkue")
##    printQueryResults(cursor.fetchall(), cursor.description)
##    team = str(input("\n(ID) > "))
##
##    # Rakennetaan SQL-lauseke:
##    sql_cmd = "INSERT INTO Pelaaja VALUES ("
##    sql_cmd += str(newID) + "," + team + "," + name + "," + number + "," + score + "," + address + "," + phone_num + ")"
##
##    if (debug_mode):
##        print("DEBUG (insertRecordPlayer):", sql_cmd)
##
##    executeSQLInsert(sql_cmd, db_connection)
##
##    return


#Tämä alihjelma lisää tietoa asiakas tauluun
def insertRecordAsiakas(db_connection):
    cursor = db_connection.cursor()

    newID = fetchNextPrimaryKeyValue("Asiakas_ID","Asiakas",cursor)

    print("Syötä asiakkaan tiedot:\n")

    nimi = '"' +input("Nimi: ") +  '"'
    asiakkaantilaukset = str(input("Asiakkaan tilaukset: "))



    #Haetaan asuinpaikka taulusta asiakkaalle asuinpaikka
    print("Asuinpaikka_ID")
    cursor.execute("SELECT * FROM Asuinpaikka")
    printQueryResults(cursor.fetchall(), cursor.description)

    valinta = input("Onko asuinpaikkaid listassa K/E?")
    #Yleisesti kun lisätään uutta asiakasta, niin hänen asuinpaikkaansa ei ole asuinpaikkaluettelossa.
    if valinta =="K":
        asuinpaikka = input("\nAsuinpaikkaid: ") # Mikäli asiakkaan asuinpaikka oli asuinpaikkaluettelossa, niin se voidaan valita suoraan

    elif valinta == "E": # Mikäli asiakkaan asuinpaikka ei ollut asuinpaikkataulussa, se pitää luoda sinne
        insertRecordAsuinpaikka(db_connection)
        print("Asuinpaikka lisätty asiakasta varten\n")
        cursor.execute("SELECT * FROM Asuinpaikka")
        printQueryResults(cursor.fetchall(), cursor.description)
        asuinpaikka = input("\nAsuinpaikkaid: ")
    else:
        print("Tunnistamaton valinta!\n")

    sql_cmd = "INSERT INTO Asiakas VALUES(" # Syötetään asiakastauluun uusi asiakas
    sql_cmd+=nimi+"," + str(newID)+"," + asiakkaantilaukset+"," + asuinpaikka + ")"

    if (debug_mode):
        print("DEBUG (insertRecordAsiakas):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    return


# Tämän aliohjelman tarkoituksena on lisätä tietoja asuinpaikkatauluun
def insertRecordAsuinpaikka(db_connection):
    cursor = db_connection.cursor()

    newID = fetchNextPrimaryKeyValue("AsuinpaikkaID","Asuinpaikka",cursor)

    print("Syötä asuinpaikan tiedot:\n")

    katu = '"' +input("Katu: ")  +'"'
    postinumero = str(input("Postinumero: "))

    sql_cmd = "INSERT INTO Asuinpaikka VALUES("
    sql_cmd+=katu + "," + postinumero+ "," + str(newID) + ")"

    if (debug_mode):
        print("DEBUG (insertRecordAsuinpaikka):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    print("Etsitään postinumerolla kaupunkia tietokannasta:\n")  # Tietokannassani ei ole muistinkäytön optimoimiseksi listattuna jokaista maailman kuntaa, joten kun tulee uusi asikas uudesta kunnasta, yhdistetään postinumero kuntaan
    cursor.execute("SELECT * FROM Postinumerotaulukko WHERE postinumero = " + postinumero)
    if printQueryResults(cursor.fetchall(), cursor.description) == 0:  # Mikäli postinumerolle ei löydy kuntaa, pitää se yhdistää siihen
        insertRecordPostinumerotaulukko(db_connection, postinumero,newID)

    return


    # Tämän aliohjelman tarkoituksena on asettaa uusia postinumeroita asuinpaikkoihin
def insertRecordPostinumerotaulukko(db_connection, postinumero,newID):

    cursor = db_connection.cursor()

    print("Syötä paikkakunta joka vastaa postinumeroa: ",postinumero)

    paikkakunta = '"' +input("Paikkakunta: ")  +'"'

    sql_cmd = "INSERT INTO Postinumerotaulukko VALUES("
    sql_cmd+=paikkakunta + "," + str(postinumero) + "," + str(newID) +  ")" # liitetään tauluun paikkakuntaa vastaava postinumero

    if (debug_mode):
        print("DEBUG (insertRecordPostinumerotaulukko):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    return


# Tämän aliohjelman tarkoituksena on listata perustiedot asiakkaan uudesta tilauksesta tietokantaan
def insertRecordAsiakkaan_tilaus(db_connection):
    cursor = db_connection.cursor()

    newID = fetchNextPrimaryKeyValue("Tilaus_ID","Asiakkaan_Tilaus",cursor) # Tilaus_ID toimii aina tilausken identifioimana tekijänä. Tietokannassa yksi tilaus on tuoterivi kokonaisesta tilauksesta

    print("Syötä Asiakkaan tilauksen tiedot:\n")


    #Käsitellään aikamääreet SQLLiten haluamaan muotoon
    date1 = input("TilausPäiväys (pp.kk.vvvv): ") 
    Tilauskellonaika = input("Tilauskellonaika (hh:mm:ss): ")
    temp1 = date1.split(".")
    temp2 = Tilauskellonaika.split(":")
    tilauspvmklo = '"' + temp1[2] + "-" + temp1[1] + "-" + temp1[0] + " " +temp2[0] + ":" + temp2[1] + ":" + temp2[2] +'"'


    date2 = input("Toimituspvm (arvioitu (pp.kk.vvvv)): ")
    temp3 = date2.split(".")
    toimituspvm = '"' + temp3[2] + "-" + temp3[1] + "-" + temp3[0] + '"'

    print("Tilauksen käsittelijätyöntekijä:\n")

    cursor.execute("SELECT * FROM Tyontekija") # Tilauksella on aina käsittelijä, joka syötetään tilaukseen, jotta voidaan tarkastella yrityksen toiminnan ohjausta
    printQueryResults(cursor.fetchall(), cursor.description)
    
    henkilotunnus = input("Tilauksen käsittelijä ")

    print("Tilauksen toimittaja kuriiri:\n")

    cursor.execute("SELECT * FROM Kuriiri")
    printQueryResults(cursor.fetchall(), cursor.description)

    kuriirinimi = '"' +input("Kuriirinimi: ")  +'"'

    print("Asiakkaan ID: \n")  # Haetaan asiakastaulusta kaikki asiakkaat, ja valitaan sitten oikea asiakas_ID

    cursor.execute("SELECT Asiakas.Asiakkaan_nimi, Asiakas.Asiakas_ID, Asiakas.AsuinpaikkaID FROM Asiakas") #
    printQueryResults(cursor.fetchall(), cursor.description)

    valinta = input("Onko asiakas uusi asiakas (K/E)?") # Asiakas voi olla täysin uusi, jolloin se ei ole asiakas taulussa!

    if valinta =="K":
    	insertRecordAsiakas(db_connection)
    	print("Uusi asiakas lisätty!\n")
    	cursor.execute("SELECT Asiakas.Asiakkaan_nimi, Asiakas.Asiakas_ID, Asiakas.AsuinpaikkaID FROM Asiakas")
    	printQueryResults(cursor.fetchall(), cursor.description)
    	asiakasid = input("\nAsiakkaan ID: ")
    elif valinta == "E":     # Mikäli asiakas on uusi, pitää se ensin lisätä asiakas tauluun
    	asiakasid = input("Asiakkaan ID:")  #jos asiakas on nykyinen asikas, voidaan se valita suoraan luettelosta
    else:
        print("Tunnistamaton valinta!\n")
    
    # Voi olla että tilaus on lähetetty, ja se ei ole tietokannassa. Täten tilauksen tila pitää pystyä valitsemaan tilausta asettaessa tietokantaan.
    tilauksentila =  '"' +input("Tilauksen tila (V =vastaanotettutilaus, K = käsittelyssä oleva tilaus, L = lähetetty tilaus: ")  +'"'

    sql_cmd = "INSERT INTO Asiakkaan_tilaus VALUES("
    sql_cmd+=str(newID) + "," + tilauspvmklo + "," + toimituspvm + "," + henkilotunnus + "," + kuriirinimi + "," + asiakasid + "," + tilauksentila +")"

    if (debug_mode):
        print("DEBUG (insertRecordAsiakkaan_tilaus):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    insertRecordAsiakkaantilauskoostuu(db_connection,newID) # Asiakkaan_tilaus taulussa ei ole tilausken tuotetta tai määrää, joten se pitää lisätä toiseen tauluun. 

    return


# Tietokantaan syötetään aina tilausrivejä! Eli yksittäisiä tuotteita per tilaus_ID
def insertRecordAsiakkaantilauskoostuu(db_connection,newID):

    cursor = db_connection.cursor()

    newID2 = fetchNextPrimaryKeyValue("Asiakastilausrivi_ID","Asiakastilauskoostuu",cursor) #luodaan ID asiakastilausriville


    print("Tilauksen tuote:") #oletetaan, että asiakas ei rupeasisi tilaamaan tuotetta, jota ei löydy kaupan valikoimasta. Täten ei tarvitse katsoa onko tuote tuotetaulussa
    cursor.execute("SELECT * FROM Tuote")
    printQueryResults(cursor.fetchall(), cursor.description)

    tuote_ID = str(input("Tilauksen tuoteID: "))

    Maara = str(input("Kuinka monta kpl tilattiin?:"))

    tilaus_ID = str(newID)

    sql_cmd = "INSERT INTO Asiakastilauskoostuu VALUES("
    sql_cmd+=str(newID2)+ "," +Maara + "," + tuote_ID + "," + tilaus_ID + ")"

    if (debug_mode):
        print("DEBUG (insertRecordAsiakkaantilauskoostuu:", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    return
   

# Tähän tauluun voidaan lisätä kuriireja, jotka toimittavat asiakkaille paketteja
def insertRecordKuriiri(db_connection):
    cursor = db_connection.cursor()
    print("Syötä kuriirin tiedot:\n")

    kuriirinimi = '"' + input("Anna kuriirin nimi: ") + '"'

    maine = str(input("Anna kuriirin maine: ")) # maine on muuttuja joka kuvaa kuriirin luotettavuutta vertaa Suomen Posti vs. UPS

    sql_cmd = "INSERT INTO Kuriiri VALUES("
    sql_cmd += kuriirinimi + "," + maine + ")"

    if (debug_mode):
        print("DEBUG (insertRecordAsiakas):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    return


# Tämä aliohjelma syöttää uusia työntekijöitä tyontekija tauluun
def insertRecordTyontekija(db_connection):
    cursor = db_connection.cursor()

    newID = fetchNextPrimaryKeyValue("Henkilotunnus","Tyontekija",cursor) # tyontekija identifioidaan aina henkilötunnuksen perusteella

    print("Syötä työntekijän tiedot:\n")

    nimi = '"' +input("Ryöukon nimi: ") +  '"'
    Puhelinnumero = str(input("Anna ryöukon puhelinnummero: "))
    sposti = '"' +input("Ryöukon sposti: ") +  '"'

    print("Ryöukon Asunpaikka_ID") # Kun työpaikalle tulee uusi ryöukko, hänen asuinpaikka ei ole todennäköisesti tietokannassa. Täten asuinpaikkoihin pitää lisätä ryöukon ryökoti
    cursor.execute("SELECT * FROM Asuinpaikka")
    printQueryResults(cursor.fetchall(), cursor.description)

    valinta = input("Onko Ryöukon asuinpaikkaid listassa K/E?")

    if valinta =="K":
        asuinpaikka = input("\nAsuinpaikkaid: ")

    elif valinta == "E":
        insertRecordAsuinpaikka(db_connection)
        print("Asuinpaikka lisätty työntekijää varten\n")
        cursor.execute("SELECT * FROM Asuinpaikka")
        printQueryResults(cursor.fetchall(), cursor.description)
        asuinpaikka = input("\nRyöukon Asuinpaikkaid: ")
    else:
        print("Tunnistamaton valinta!\n")

    sql_cmd = "INSERT INTO Tyontekija VALUES("
    sql_cmd+= nimi + "," + str(newID) + "," + Puhelinnumero + "," + sposti + "," + asuinpaikka + ")"

    if (debug_mode):
        print("DEBUG (insertRecordAsiakas):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    return


# Tämä aliohjelma syötää omia tilauksia tietokantaan. Eli siis varastontäydennystilauksia (RIVEITTÄIN)
def insertRecordOmatilaus(db_connection):
    cursor = db_connection.cursor()

    newID = fetchNextPrimaryKeyValue("Tilausnumero","Omatilaus",cursor) # Omatilaus identifioidaan aina tilausnumerolla

    print("Syötä oman tilaukset tiedot:\n")


    # Syötetään tarkat aikatiedot tilauksen asettamiselle
    date1 = input("TilausPäiväys (pp.kk.vvvv): ") 
    Tilauskellonaika = input("Tilauskellonaika (hh:mm:ss): ")
    temp1 = date1.split(".")
    temp2 = Tilauskellonaika.split(":")
    tilauspvmklo = '"' + temp1[2] + "-" + temp1[1] + "-" + temp1[0] + " " +temp2[0] + ":" + temp2[1] + ":" + temp2[2] +'"'


    # Syötetään aikatieto tilauksen arvioidulle saapumisajalle, jotta voidaan ihmetellä missä helevetissä o meidän kamat
    date2 = input("Toimituspvm (arvioitu (pp.kk.vvvv)): ")
    temp3 = date2.split(".")
    toimituspvm = '"' + temp3[2] + "-" + temp3[1] + "-" + temp3[0] + '"'

    print("Toimittajayrityksen nimi:")
    cursor.execute("SELECT * FROM Toimittaja")
    printQueryResults(cursor.fetchall(), cursor.description)


    # Toimittajayritys voi olla täysin uusi, jolloin omaa täydennystilausta tehdessä pitää huomioida toimittajan lisääminen
    valinta = input("Onko toimittaja listassa K/E?") # toimittaja voi olla jo olemassa

    if valinta =="K":
        toimittaja = '"' +input("Toimittajan nimi : ") +  '"'

    elif valinta == "E":
        insertRecordToimittaja(db_connection)
        print("Toimittaja lisätty omaa tilausta varten\n")
        cursor.execute("SELECT * FROM Toimittaja")
        printQueryResults(cursor.fetchall(), cursor.description)
        toimittaja = '"' +input("Toimittajan nimi : ") +  '"'
    else:
        print("Tunnistamaton valinta!\n")

    sql_cmd = "INSERT INTO Omatilaus VALUES ("
    sql_cmd += tilauspvmklo + "," + toimituspvm + "," + str(newID) + "," + toimittaja + ")"

    if (debug_mode):
        print("DEBUG (insertRecordOmatilaus):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    insertRecordOmatilauskoostuu(db_connection,newID) # Koska omatilaus taulussa ei ole kaikkia olennaisia tietoja tilasrivistä tietokannan eheyssääntöjen takia, joudutaan menemään muokkaamaan vielä toista taulua

    return


# tämä aliohjelma syötää omalle tilausriville tuotteen ja tilatun määrän
def insertRecordOmatilauskoostuu(db_connection,newID):

    cursor = db_connection.cursor()

    newID2 = fetchNextPrimaryKeyValue("Omatilausrivi_ID","Omatilauskoostuu",cursor)


    print("Tilauksen tuote:")
    cursor.execute("SELECT * FROM Tuote")
    printQueryResults(cursor.fetchall(), cursor.description)

    valinta = input("Onko tilattava tuote listassa K/E?") # tilattava tuote voi olla olematta nykyisessä tuotekatalogissa, jolloin se täytyy lisätä Tuote tauluun

    if valinta =="K":
        tuote_ID = str(input("Tuotteen ID : ")) #Mikäli tuote on jo olemassa tuotetaulussa, voidaan se nopeasti valita tällä valintahaaralla

    elif valinta == "E":
        insertRecordTuote(db_connection)
        print("Tuote lisätty varastolistaan omaa tilausta varten\n")
        cursor.execute("SELECT * FROM Tuote")
        printQueryResults(cursor.fetchall(), cursor.description)
        tuote_ID = str(input("Tuotteen ID : "))
    else:
        print("Tunnistamaton valinta!\n")


    Maara = str(input("Kuinka monta kpl tilattiin?:")) 

    sql_cmd = "INSERT INTO Omatilauskoostuu VALUES("
    sql_cmd+=str(newID2) + "," +Maara + "," + str(newID) + "," + tuote_ID + ")"

    if (debug_mode):
        print("DEBUG (insertRecordAsiakkaantilauskoostuu:", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    return

# Tällä aliohjelmalla pystytään lisäämään toimittajia yrityksen tarpeisiin, usein toimittajat lisäys yhdistyy automaagisesti omaa tilausta tehdessä, koska jos toimittaja on uusi täytyy se tilausta tehdessä joka tapauksessa syöttää
def insertRecordToimittaja(db_connection):
    cursor = db_connection.cursor()

    toimittajanimi = '"' +input("Toimittajan nimi : ") +  '"'

    puhelinnumero = str(input("Syötä toimittajan puhelinnumero: "))


    #Käsitellään toimittajan sidosryhmäaikataulu SQLLiten haluamaan muotoon
    date = input("Toimittajan lähtien (pp.kk.vvvv): ")
    temp = date.split(".")
    lahtien = '"' + temp[2] + "-" + temp[1] + "-" + temp[0] + '"'

    print("Toimittajan toimipaikka") #toimittaja on tärkeä sidosryhmä yritykselle, joten tarvitaan tietää toimittajan toimipiste
    cursor.execute("SELECT * FROM Asuinpaikka")
    printQueryResults(cursor.fetchall(), cursor.description)

    valinta = input("Onko Toimittajan toimipaikka (asuinpaikkaID) listassa K/E?") #toimittaja voi olla tunnetussa asuinpaikassa, tai sitten pitää syöttää uusi asuinpaikka

    if valinta =="K":
        asuinpaikka = input("\nToimittajan toimipaikka (Asuinpaikkaid): ")

    elif valinta == "E":
        insertRecordAsuinpaikka(db_connection) # luodaan toimittajalle oma asuinpaikka
        print("Asuinpaikka lisätty toimittajaa varten\n")
        cursor.execute("SELECT * FROM Asuinpaikka")  
        printQueryResults(cursor.fetchall(), cursor.description)
        asuinpaikka = input("\nToimittajan toimipaikka (asuinpaikkaID): ")
    else:
        print("Tunnistamaton valinta!\n")

    sql_cmd = "INSERT INTO Toimittaja VALUES ("
    sql_cmd+= toimittajanimi + "," + lahtien + "," + asuinpaikka + "," + puhelinnumero + ")"

    if (debug_mode):
        print("DEBUG (insertRecordAsiakas):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    return


# Syötetään uusi tuote tietokantaan Tuote tauluun
def insertRecordTuote(db_connection):
    cursor = db_connection.cursor()

    newID = fetchNextPrimaryKeyValue("Tuote_ID","Tuote",cursor) #tuotteen identifioi sen tuote_ID

    print("Syötä tuotteen tiedot")

    tuotenimi = '"' +input("Tuotteen nimi : ") +  '"'

    varastosaldo = str(input("Syötä varaston saldo: "))

    varmuusvarastoraja = str(input("Syötä varmuusvaraston määrä: "))

    hinta = str(input("Syötä tuotten hinta euroissa: "))

    sql_cmd = "INSERT INTO Tuote VALUES ("
    sql_cmd += tuotenimi + "," + str(newID) + "," + varastosaldo + "," + varmuusvarastoraja + "," + hinta + ")"

    if (debug_mode):
        print("DEBUG (insertRecordTuote):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    return

# Tleiskäyttöinen INSERT-komennon suorittava aliohjelma,
# joka lisää tietueen parametrina annetun nimsieen tauluun.
# Koska geneerinen, toimii minkä vain tietokannan kanssa, mutta
# ei siedä syötevirheitä eikä soaa kysyä tietoja "älykkäästi."
# 

def insertRecordGeneric(db_connection, table):
    columns = []

    # Esitetään käyttäjälle taulun tietueet helpottamaan
    # uuden lisäämistä.
    cursor = db_connection.cursor()
    cursor.execute("SELECT * FROM " + table)
    printQueryResults(cursor.fetchall(), cursor.description)

    print("\nSyötä uusi tietue:\n")

    # pragma palauttaa taulun scheman
    # kts. deleteRecord ja updateRecord.
    cursor = db_connection.cursor()
    cursor.execute("pragma table_info(" + table + ")")
    sql_cmd = "INSERT INTO " + table + " VALUES("

    # Emme saa kirjoittaa pilkkua 1. attr=arvo parin eteen,
    # joten kontrolloidaan millä kierroksella ollaan.
    first = True 
    # Edetään attribuutti kerrallaan.
    for column in cursor.fetchall():
        # column[1]:ssä on attribuutin nimi
        value = input(column[1] + ": ")
        if not("INTEGER" in column[2]): # Muistetaan '-merkit.
            value = "'" + value + "'"
        if (first):
            sql_cmd += value # Ei pilkkua.
            first = False # Ensi kierroksella kyllä.
        else:
            sql_cmd += ", " + value # Pilkku eteen, ei jälkeen.

    sql_cmd += ")"

    if (debug_mode):
        print("\nDEBUG (insertRecordGeneric):", sql_cmd)

    executeSQLInsert(sql_cmd, db_connection)

    return



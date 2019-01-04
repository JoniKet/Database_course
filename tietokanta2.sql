# DATAWARASTON QUERYT


#Query:
# 1. Käyttäjälle tulostettava kuvaus
# 2. käyttäjäryhmät
# 3. Muuttujien kuvaus käyttäjälle
# 4. SQL-lauseke


Query:
{Listaa kaikki asiakkaat.}
{admin,sihteeri}
{}
{SELECT Asiakas.Asiakkaan_nimi,Asiakas.Asiakas_ID,Asiakas.Asiakkaan_tilaukset,
	 Asuinpaikka.Katu ,Postinumerotaulukko.Paikkakunta, Postinumerotaulukko.Postinumero 
	FROM Asiakas
	INNER JOIN Asuinpaikka ON Asiakas.AsuinpaikkaID = Asuinpaikka.AsuinpaikkaID
	INNER JOIN Postinumerotaulukko ON Asuinpaikka.Postinumero = Postinumerotaulukko.Postinumero}


Query:
{Listaa kaikki lahettamattomat paketit.}
{admin,sihteeri,varastomies}
{}
{SELECT Asiakkaan_tilaus.Tilaus_ID,Asiakas.Asiakkaan_nimi,Asuinpaikka.Katu,Asuinpaikka.Postinumero,Postinumerotaulukko.Paikkakunta,
	Asiakkaan_tilaus.Tilauspvmklo, Tuote.Tuotenimi, Asiakastilauskoostuu.Maara
	FROM Asiakkaan_tilaus
	INNER JOIN Asiakas ON Asiakkaan_tilaus.Asiakas_ID = Asiakas.Asiakas_ID
	INNER JOIN Asuinpaikka ON Asiakas.AsuinpaikkaID = Asuinpaikka.AsuinpaikkaID
	INNER JOIN Postinumerotaulukko ON Asuinpaikka.Postinumero = Postinumerotaulukko.Postinumero
	INNER JOIN Asiakastilauskoostuu ON Asiakkaan_tilaus.Tilaus_ID = Asiakastilauskoostuu.Tilaus_ID
	INNER JOIN Tuote ON Asiakastilauskoostuu.Tuote_ID = Tuote.Tuote_ID
	WHERE Asiakkaan_tilaus.Tilauksentila = "V" OR "K";}

Query:
{Listaa tietyn asiakkaan kaikki lahettamattomat paketit.}
{admin,sihteeri,varastomies}
{Asiakas ID }
{SELECT Asiakkaan_tilaus.Tilaus_ID,Asiakas.Asiakkaan_nimi,Asuinpaikka.Katu,Asuinpaikka.Postinumero,Postinumerotaulukko.Paikkakunta,
	Asiakkaan_tilaus.Tilauspvmklo, Tuote.Tuotenimi, Asiakastilauskoostuu.Maara
	FROM Asiakkaan_tilaus
	INNER JOIN Asiakas ON Asiakkaan_tilaus.Asiakas_ID = Asiakas.Asiakas_ID
	INNER JOIN Asuinpaikka ON Asiakas.AsuinpaikkaID = Asuinpaikka.AsuinpaikkaID
	INNER JOIN Postinumerotaulukko ON Asuinpaikka.Postinumero = Postinumerotaulukko.Postinumero
	INNER JOIN Asiakastilauskoostuu ON Asiakkaan_tilaus.Tilaus_ID = Asiakastilauskoostuu.Tilaus_ID
	INNER JOIN Tuote ON Asiakastilauskoostuu.Tuote_ID = Tuote.Tuote_ID
	WHERE (Asiakkaan_tilaus.Tilauksentila = "V" OR "K") AND Asiakas.Asiakas_ID = "\1\"}

Query:
{Listaa kaikki omat tilaukset}
{admin,sihteeri}
{}
{SELECT Omatilaus.Tilausnumero,Omatilaus.Tilauspvmklo,Omatilaus.Toimitus_pvm,Omatilaus.Toimittajanimi,Tuote.Tuotenimi,Omatilauskoostuu.Maara 
	FROM Omatilaus
	INNER JOIN Omatilauskoostuu ON Omatilaus.Tilausnumero = Omatilauskoostuu.Tilausnumero
	INNER JOIN Tuote ON Omatilauskoostuu.Tuote_ID = Tuote.Tuote_ID}


Query:
{Listaa varaston esineiden tiedot}
{admin, sihteeri}
{}
{SELECT * FROM Tuote}

Query:
{Listaa yksittaisen esineen varastosaldo ja kysyntatieto}
{admin, sihteeri}
{Tuote_ID}
{SELECT Tuote.Tuotenimi,Tuote.Varastosaldo,sum(Asiakastilauskoostuu.Maara) AS "Tilauksia tullut yhteensa" FROM Asiakastilauskoostuu
	INNER JOIN Tuote ON Asiakastilauskoostuu.Tuote_ID = Tuote.Tuote_ID
	WHERE Tuote.Tuote_ID = "\1\"
	Group by Asiakastilauskoostuu.Tuote_ID}


Query:
{Listaa varaston esineet, joita pitaa tilata lisaa. (varmuusvaraston raja alittuu)}
{admin, sihteeri}
{}
{SELECT Tuote.Tuotenimi,Tuote.Varastosaldo,Tuote.Varmuusvarastoraja,Tuote.Tuote_ID , sum(Asiakastilauskoostuu.Maara) AS "Asiakkaan tilauksia tuotteelle", sum(Omatilauskoostuu.Maara) AS "JO TILATUT EI SAAPUNEET LASKURI EI LASKE NÄITÄ"
	FROM Asiakastilauskoostuu
	LEFT OUTER JOIN Tuote ON Asiakastilauskoostuu.Tuote_ID = Tuote.Tuote_ID
	LEFT OUTER JOIN Omatilauskoostuu ON Asiakastilauskoostuu.Tuote_ID = Omatilauskoostuu.Tuote_ID
	GROUP BY Tuote.Tuote_ID
	HAVING 
	(Tuote.Varastosaldo - sum(Asiakastilauskoostuu.Maara) < Tuote.Varmuusvarastoraja)}

Query:
{Tyontekijoiden tilausten kasittelyajat}
{admin}
{}
{SELECT Asiakkaan_tilaus.Tilauspvmklo, Asiakkaan_tilaus.Toimituspvm, Tyontekija.Tyontekijan_nimi FROM Asiakkaan_tilaus
	INNER JOIN Tyontekija ON Asiakkaan_tilaus.Henkilotunnus = Tyontekija.Henkilotunnus
	WHERE Asiakkaan_tilaus.Tilauksentila = "L"
	Group by Asiakkaan_tilaus.Tilaus_ID}


Query:
{Listaa kaikki toimittajat}
{admin}
{}
{SELECT * FROM Toimittaja}


Query:
{Toimittajien tilausten kasittelyajat}
{admin}
{}
{SELECT Omatilaus.Tilausnumero AS "Täydennystilausnumero", Omatilaus.Tilauspvmklo, Omatilaus.Toimitus_pvm, Omatilaus.Toimittajanimi, Toimittaja.Lahtien AS "Toimittanut lähtien" FROM Omatilaus
	INNER JOIN Toimittaja ON Omatilaus.Toimittajanimi = Toimittaja.Toimittajanimi}


Query:
{Listaa kaytettavissa olevat kuriirit ja niiden maine}
{admin,sihteeri}
{}
{SELECT * FROM Kuriiri}

Query:
{Listaa kaikki tyontekijat ja heidan tiedot}
{admin}
{}
{SELECT * FROM Tyontekija}



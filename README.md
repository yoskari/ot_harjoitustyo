# Ohjelmistotekniikan harjoitustyö
## Northlands unspaghettified
Tämän projektin idea on uudelleenkirjoittaa ja siistiä vanha sotkuinen peliprojekti.

## Pelin idea
Northlands on 2D seikkailupeli, jossa pelaaja seikkailee satunnaisesti generoidussa maailmassa keräten resursseja, rakentaen ja yrittäen selvitä vihollisilta. Sain inspiraatiota peliin Minecraftin, Terrarian ja Valheimin tapaisista peleistä.

## Toteutus
Peli on kirjoitettu Pythonilla ja toteutettu käyttäen pygame-grafiikkakirjastoa sekä yksi- ja kaksiulotteista noise-algorytmia maailman generoimiseen.

## Linkit:

[Vaatimusmäärittely](https://github.com/yoskari/ot_harjoitustyo/blob/main/dokumentaatio/maarittely.md)

[Tuntikirjanpito](https://github.com/yoskari/ot_harjoitustyo/blob/main/dokumentaatio/tuntikirjanpito.md)

[Arkkitehtuuri](https://github.com/yoskari/ot_harjoitustyo/blob/main/dokumentaatio/arkkitehtuuri.md)

[Screenshots](https://github.com/yoskari/ot_harjoitustyo/blob/main/dokumentaatio/screenshots.md)

[viikko 5 release](https://github.com/yoskari/ot_harjoitustyo/releases/tag/viikko5)

[viikko 6 release](https://github.com/yoskari/ot_harjoitustyo/releases/tag/viikko6)
 ( bugi: peli pitää ajaa kerran ennen testausta )

[loppupalautus](https://github.com/yoskari/ot_harjoitustyo/releases/tag/loppupalautus)

## Asennus
1. Asenna riippuvuudet komennolla:

```bash
poetry install
```

## Komentorivitoiminnot

### Ohjelman suorittaminen

Ohjelman pystyy suorittamaan komennolla:

```bash
poetry run invoke start
```

### Käyttöohje
[Käyttöohje](https://github.com/yoskari/ot_harjoitustyo/blob/main/dokumentaatio/manual.md)

### Testaus

Testit suoritetaan komennolla:

```bash
poetry run invoke test
```

### Testikattavuus

Testikattavuusraportin voi generoida komennolla:

```bash
poetry run invoke coverage-report
```

Raportti generoituu htmlcov-hakemistoon.

### Known Issues

- peli luo välillä mysteerisiä "None" nimisiä kopioita maailmoista

- slabien fysiikat ovat bugiset

- fps tippuu välillä rankasti, tämä johtuu varmaan osittain itse ohjelmointikielestä ja pelin laajuudesta

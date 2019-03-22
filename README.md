# AutoFavourites
Everyone knows how is boring when channels change and you get a "UNKNOWN" on your Favourites.
AutoFavourites Plugin can generate favourites based on a configuration file and channel names.
If you use EPGRefresh, AutoFavourites generate a Favourite with one channel for each transponder.
Is possible too update satellites.xml from OE-Alliance or other sources.

## Installation
opkg install enigma2-plugin-extensions-autofavourites.ipk

## Usage
Create a file /etc/bouquetRules.cfg with content as example:
```
Documentaries:Animal Planet|Discovery Channel|H2|National Geographic|The History Channel|Nat Geo
Movies and Series:AXN|Canal Brasil|Cinemax|^Fox$|^Fox HD$|FX|^HBO|I-SAT|^Max|MegaPix|Paramount|Prime Box|Sony|Space|Studio Universal|Syfy|TBS|TCM|^Telecine|TNT|Universal Channel|^Warner
Varieties:(?=Discovery)(?!Discovery Channel|Discovery Kids)|E!|Fox Life|Glitz|GNT|Ideal TV|Lifetime|MTV|Multishow|OFF|TLC|truTV|Viva|WooHoo
EPGRefresh:^(?!TVEXEC|TVTEC|Teste)\w*
```

Syntax is:
(Favourite Name):(Regular expression to find channels by name)

Some examples for regular expressions:
```
^startwith
endwith$
^exact$
contains
regexp1|regexp2|regexp3
(?=contains)(?!butnotequal|butnotequal)
```

You can test your regular expressions and learn a little bit here http://pythex.org/.

## Examples

### StarOne C2
```
Abertos:^Globo |Aparecida|^Canção Nova|Bandeirantes|RecordTV|Rede TV|Rede Vida|SBT|TV Anhanguera Goiânia|TV Cultura|^TV Globo|TV Bahia|^TV Verdes
Documentários:Animal Planet|Discovery Channel|H2|National Geographic|The History Channel|Nat Geo|NatGeo|^History|^Zoo
Esportes:^EL$|Band Alternativo|Band Sports|Bandsports|Combate|^ESPN|^Fox Sports|Premiere|^SporTV|^Ei Maxx
Filmes e Séries:AMC|AXN|Canal Brasil|Cinemax|^Fox$|^Fox HD$|FX|^HBO|I-SAT|^Max|MegaPix|Paramount|Prime Box|Sony|Space|Studio Universal|Syfy|TBS|TCM|^Telecine|TNT|^Universal|^Warner
Internacional:^NHK|^RAI$|^SIC|TV España|TV5 Monde|Deutsche Welle|^DW|^TVE$
Infantis:Boomerang|^Cartoon|Discovery Kids|^Disney|^Gloob|^Nick|Play TV|Tooncast|TV Rá Tim Bum
Noticias:^CNN|CNT|GloboNews|Record News|Band News
Publico:Canal Claro|Canal Rural|Futura|NBR|Polishop|Rede Brasil|RIT|Terra Viva|TV Brasil|TV Câmara|TV Escola|TV Justiça|TV Senado
Variedades:Globosat|A&E|Arte 1|^BIS|Comedy Central|Curta!|^Disc. Home|(?=Discovery)(?!Discovery Channel|Discovery Kids)|E!|Fox Life|Glitz|GNT|Ideal TV|Lifetime|MTV|Multishow|Music Box Brazil|OFF|TLC|truTV|^Viva|WooHoo|^VH1|BBB
EPGRefresh:^(?!TVEXEC|TVTEC|Teste)\w*
```

# Screenshots
![image1](https://raw.githubusercontent.com/lazaronixon/autofavourites/master/screenshots/image1.jpg)
![image2](https://raw.githubusercontent.com/lazaronixon/autofavourites/master/screenshots/image2.jpg)
![image3](https://raw.githubusercontent.com/lazaronixon/autofavourites/master/screenshots/image3.jpg)

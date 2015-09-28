# AutoFavourites
Everyone knows how is boring when channels change and you get a "UNKNOWN" on your Favourites. AutoFavourites Plugin can generate favourites based on a configuration file and channel names.

Installation
------------
opkg install enigma2-plugin-extensions-autofavourites.ipk

Usage
------------
Create a file /etc/autoFavourites.cfg with content as example:
```
Documentaries==Animal Planet|Discovery Channel|H2|National Geographic|The History Channel|Nat Geo
Movies and Series==AXN|Canal Brasil|Cinemax|^Fox$|^Fox HD$|FX|^HBO|I-SAT|^Max|MegaPix|Paramount|Prime Box|Sony|Space|Studio Universal|Syfy|TBS|TCM|^Telecine|TNT|Universal Channel|^Warner
Varieties==(?=Discovery)(?!Discovery Channel|Discovery Kids)|E!|Fox Life|Glitz|GNT|Ideal TV|Lifetime|MTV|Multishow|OFF|TLC|truTV|Viva|WooHoo
```

Syntax is:
(Favourite Name)=(Regular expression to find channels by name)

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

ChangeLog
------------
0.2.0
Change Config File delimiter from = to == to prevent mismatch with regexp.

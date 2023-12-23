# AutoFavourites
Everyone knows how is boring when channels change and you get a "UNKNOWN" on your Favourites.
AutoFavourites Plugin can generate favourites based on a configuration file and channel names.
If you use EPGRefresh, AutoFavourites generate a Favourite with one channel for each transponder.
Is possible too update satellites.xml from OE-Alliance or other sources.

## Installation
## TODO: provide packages for installation
~~opkg install enigma2-plugin-extensions-autofavourites.ipk~~

## Usage
Create a file /etc/enigma2/bouquetRules.json with content as example:
```
{
    "rules": [
        {
            "name": "Hauptsender",
            "stations": [
                {"regexp": "^Das Erste HD$", "ns": "c00000"},
                {"regexp": "^ZDF HD$", "ns": "c00000"}
            ]
        },
        {
            "name": "dritte-regional",
            "stations": [
                {
                    "p": ["ARD", "BMT"],
                    "!regexp": "(?i)arte|ARD|Erste|tagesschau|phoenix|ONE|Mediathek",
                    "ns": "c00000"
                },
                {
                    "regexp": "(?i)DR",
                    "p": "SES ASTRA",
                    "ns": "c00000"
                },
                {
                    "regexp": "(?i)(?:^|\\W)(?:rhein\\smain|REGIO|Baden|SACHSEN|rfo)(?:\\W|$)",
                    "ns": "c00000"
                },
                {
                    "regexp": "(?i)(?:^|\\W)L-TV(?:\\W|$)",
                    "ns": "c00000",
                    "replace": {
                        "reftype": 4097,
                        "path": "https://live2.telvi.de/hls/l-tv_s1_hd720.m3u8"
                    }
                }
            ]
        }
    ]
}
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

# Screenshots
![image1](https://raw.githubusercontent.com/lazaronixon/autofavourites/master/screenshots/image1.jpg)
![image2](https://raw.githubusercontent.com/lazaronixon/autofavourites/master/screenshots/image2.jpg)
![image3](https://raw.githubusercontent.com/lazaronixon/autofavourites/master/screenshots/image3.jpg)

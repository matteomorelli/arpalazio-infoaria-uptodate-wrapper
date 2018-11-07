## arpalazio-infoaria-uptodate-wrapper
This repository host a wrapper designed for automated data processing and transmission. Air Quality data are extracted from a postgreSQL database and sent via FTP. Wrapper is designed to interact with EcomanagerWEB platform and ISPRA Server.

Code is developed as part of project [InfoARIA SINAnet](http://www.webinfoaria.sinanet.isprambiente.it) which envisages the development of a new SINAnet national information system for data managment and public information on air quality data, focus is on the pubblication of data reports in compliance with European Directives.

## License

This project is licensed under the EUROPEAN UNION PUBLIC LICENCE v. 1.2 - see the [LICENSE](LICENSE) file for details

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

All code and configuration files are designed to process data of Lazio region, wrapper should work for any data it process, but beware that this is an orchestrator all muscle work is done by DataOrganizer, MainElab, InfoAria_v8_UptoDate. Please ask the [author](https://github.com/andrea-bolignano) how to contribute

### Prerequisites
* DataOrganizer
* MainElab
* InfoAria_v8_UptoDate
* [ecomanager_db_download](https://github.com/matteomorelli/arpalazio-ecomanager-db-download)

Binary of abovementioned software are packaged within this repository, source code will be released from the author.

### Installing
Check out a clone of this repo to a location of your choice, such as `git clone --depth=1 https://github.com/matteomorelli/arpalazio-infoaria-uptodate-wrapper.git` or make a copy of all files, folders and `LICENSE` files

All configuration files are self-descriptive, you can find them into ini folder. You must configure file accordingly to your environment, sample is provided.
arpalazio-infoaria-uptodate wrapper configuration file:
*sample_conf.ini* 

DataOrganizer/MainElab configuration file, further detail will be available from author repository:
*AnaMatrix.txt* Air quality station configuration file
*DataOrganizer.ini* Air quality station data processing selector
*History.txt* Air quality instrument that are no longer in use should be written here

InfoAria_v8_UptoDate configuration file, further detail will be available from author repository:
*pollutant.list* Pollutant data file for conversion of local ID to EEA ID
*SamplingPoints_Lazio.csv* Air Quality station metadata according to EEA format
*station.list* Air Quality station data file for conversion of local ID to EEA ID

Install any python requirements as follow:
`pip install -r requirements.txt`

Run helper for usage: run `python infoaria_uptodate_wrapper.py -h`
```
usage: infoaria_uptodate_wrapper.py [-h] [-v] [-s START] [-e END] [-H HOUR]
                                    ini_file

positional arguments:
  ini_file              Location of wrapper configuration file

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Increase output verbosity
  -s START, --start START
                        Starting day YYYY/MM/DD. Default: yesterday
  -e END, --end END     Ending day YYYY/MM/DD. Default: today
  -H HOUR, --hour HOUR  Hour to be processed/transmitted, format HH. Default:
                        current hour.

```

You can schedule wrapper execution using crontab, like this:
```
# If you put this line into crontab configuration
# wrapper will be executed every hour on minute 40
40 * * * * python /path/to/infoaria_uptodate_wrapper.py /path/to/sample_conf.ini 
```

### Folder structure
```
infoaria_uptodate_wrapper/
├── bin/
│   ├── cygwin_x86/
│   │   ├── DataOrganizer_InfoAria.exe
│   │   ├── InfoAria_v8_UptoDate.exe
│   │   └── MainElab.exe
│   └── linux_x86_64/
│       ├── DataOrganizer_InfoAria.exe
│       ├── InfoAria_v8_UptoDate.exe
│       └── MainElab.exe
├── ini/
│   ├── AnaMatrix.txt
│   ├── DataOrganizer.ini
│   ├── History.txt
│   ├── pollutant.list
│   ├── SamplingPoints_Lazio.csv
│   └── station.list
└── output/
    ├── CC
    │   ├── DatiOrari
    │   ├── GiornoTipo
    │   ├── MedieAnnuali
    │   ├── MedieGiornaliere
    │   └── MedieMensili    
    ├── FR
    │   ├── DatiOrari
    │   ├── GiornoTipo
    │   ├── MedieAnnuali
    │   ├── MedieGiornaliere
    │   └── MedieMensili 
    ├── LT
    │   ├── DatiOrari
    │   ├── GiornoTipo
    │   ├── MedieAnnuali
    │   ├── MedieGiornaliere
    │   └── MedieMensili 
    ├── RI
    │   ├── DatiOrari
    │   ├── GiornoTipo
    │   ├── MedieAnnuali
    │   ├── MedieGiornaliere
    │   └── MedieMensili 
    ├── RM
    │   ├── DatiOrari
    │   ├── GiornoTipo
    │   ├── MedieAnnuali
    │   ├── MedieGiornaliere
    │   └── MedieMensili 
    └── VT
        ├── DatiOrari
        ├── GiornoTipo
        ├── MedieAnnuali
        ├── MedieGiornaliere
        └── MedieMensili 
```

## Versioning

We use [SemVer](http://semver.org/) for versioning.

## Authors

* **Matteo Morelli** - *Initial work* - [matteomorelli](https://github.com/matteomorelli)

See also the list of [contributors](https://github.com/matteomorelli/arpalazio-infoaria-uptodate-wrapper/contributors) who participated in this project.

* **Andrea Bolignano** - [andrea-bolignano](https://github.com/andrea-bolignano)

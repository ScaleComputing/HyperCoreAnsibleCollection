#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
module: time_zone

author:
  - Ana Zobec (@anazobec)
short_description: Modify Time Zone configuration on HyperCore API
description:
  - Use this module to modify an existing Time Zone configuration on HyperCore API.
version_added: 1.2.0
extends_documentation_fragment:
  - scale_computing.hypercore.cluster_instance
seealso:
  - module: scale_computing.hypercore.time_zone_info
  - module: scale_computing.hypercore.time_server
  - module: scale_computing.hypercore.time_server_info
options:
  zone:
    type: str
    required: True
    choices:
      - Africa/Abidjan
      - Africa/Accra
      - Africa/Addis_Ababa
      - Africa/Algiers
      - Africa/Asmara
      - Africa/Bamako
      - Africa/Bangui
      - Africa/Banjul
      - Africa/Bissau
      - Africa/Blantyre
      - Africa/Brazzaville
      - Africa/Bujumbura
      - Africa/Cairo
      - Africa/Casablanca
      - Africa/Ceuta
      - Africa/Conakry
      - Africa/Dakar
      - Africa/Dar_es_Salaam
      - Africa/Djibouti
      - Africa/Douala
      - Africa/El_Aaiun
      - Africa/Freetown
      - Africa/Gaborone
      - Africa/Harare
      - Africa/Johannesburg
      - Africa/Juba
      - Africa/Kampala
      - Africa/Khartoum
      - Africa/Kigali
      - Africa/Kinshasa
      - Africa/Lagos
      - Africa/Libreville
      - Africa/Lome
      - Africa/Luanda
      - Africa/Lubumbashi
      - Africa/Lusaka
      - Africa/Malabo
      - Africa/Maputo
      - Africa/Maseru
      - Africa/Mbabane
      - Africa/Mogadishu
      - Africa/Monrovia
      - Africa/Nairobi
      - Africa/Ndjamena
      - Africa/Niamey
      - Africa/Nouakchott
      - Africa/Ouagadougou
      - Africa/Porto-Novo
      - Africa/Sao_Tome
      - Africa/Tripoli
      - Africa/Tunis
      - Africa/Windhoek
      - America/Adak
      - America/Anchorage
      - America/Anguilla
      - America/Antigua
      - America/Araguaina
      - America/Argentina/Buenos_Aires
      - America/Argentina/Catamarca
      - America/Argentina/Cordoba
      - America/Argentina/Jujuy
      - America/Argentina/La_Rioja
      - America/Argentina/Mendoza
      - America/Argentina/Rio_Gallegos
      - America/Argentina/Salta
      - America/Argentina/San_Juan
      - America/Argentina/San_Luis
      - America/Argentina/Tucuman
      - America/Argentina/Ushuaia
      - America/Aruba
      - America/Asuncion
      - America/Atikokan
      - America/Bahia
      - America/Bahia_Banderas
      - America/Barbados
      - America/Belem
      - America/Belize
      - America/Blanc-Sablon
      - America/Boa_Vista
      - America/Bogota
      - America/Boise
      - America/Cambridge_Bay
      - America/Campo_Grande
      - America/Cancun
      - America/Caracas
      - America/Cayenne
      - America/Cayman
      - America/Chicago
      - America/Chihuahua
      - America/Costa_Rica
      - America/Creston
      - America/Cuiaba
      - America/Curacao
      - America/Danmarkshavn
      - America/Dawson
      - America/Dawson_Creek
      - America/Denver
      - America/Detroit
      - America/Dominica
      - America/Edmonton
      - America/Eirunepe
      - America/El_Salvador
      - America/Fort_Nelson
      - America/Fortaleza
      - America/Glace_Bay
      - America/Goose_Bay
      - America/Grand_Turk
      - America/Grenada
      - America/Guadeloupe
      - America/Guatemala
      - America/Guayaquil
      - America/Guyana
      - America/Halifax
      - America/Havana
      - America/Hermosillo
      - America/Indiana/Indianapolis
      - America/Indiana/Knox
      - America/Indiana/Marengo
      - America/Indiana/Petersburg
      - America/Indiana/Tell_City
      - America/Indiana/Vevay
      - America/Indiana/Vincennes
      - America/Indiana/Winamac
      - America/Inuvik
      - America/Iqaluit
      - America/Jamaica
      - America/Juneau
      - America/Kentucky/Louisville
      - America/Kentucky/Monticello
      - America/Kralendijk
      - America/La_Paz
      - America/Lima
      - America/Los_Angeles
      - America/Lower_Princes
      - America/Maceio
      - America/Managua
      - America/Manaus
      - America/Marigot
      - America/Martinique
      - America/Matamoros
      - America/Mazatlan
      - America/Menominee
      - America/Merida
      - America/Metlakatla
      - America/Mexico_City
      - America/Miquelon
      - America/Moncton
      - America/Monterrey
      - America/Montevideo
      - America/Montserrat
      - America/Nassau
      - America/New_York
      - America/Nipigon
      - America/Nome
      - America/Noronha
      - America/North_Dakota/Beulah
      - America/North_Dakota/Center
      - America/North_Dakota/New_Salem
      - America/Nuuk
      - America/Ojinaga
      - America/Panama
      - America/Pangnirtung
      - America/Paramaribo
      - America/Phoenix
      - America/Port-au-Prince
      - America/Port_of_Spain
      - America/Porto_Velho
      - America/Puerto_Rico
      - America/Punta_Arenas
      - America/Rainy_River
      - America/Rankin_Inlet
      - America/Recife
      - America/Regina
      - America/Resolute
      - America/Rio_Branco
      - America/Santarem
      - America/Santiago
      - America/Santo_Domingo
      - America/Sao_Paulo
      - America/Scoresbysund
      - America/Sitka
      - America/St_Barthelemy
      - America/St_Johns
      - America/St_Kitts
      - America/St_Lucia
      - America/St_Thomas
      - America/St_Vincent
      - America/Swift_Current
      - America/Tegucigalpa
      - America/Thule
      - America/Thunder_Bay
      - America/Tijuana
      - America/Toronto
      - America/Tortola
      - America/Vancouver
      - America/Whitehorse
      - America/Winnipeg
      - America/Yakutat
      - America/Yellowknife
      - Antarctica/Casey
      - Antarctica/Davis
      - Antarctica/DumontDUrville
      - Antarctica/Macquarie
      - Antarctica/Mawson
      - Antarctica/McMurdo
      - Antarctica/Palmer
      - Antarctica/Rothera
      - Antarctica/Syowa
      - Antarctica/Troll
      - Antarctica/Vostok
      - Arctic/Longyearbyen
      - Asia/Aden
      - Asia/Almaty
      - Asia/Amman
      - Asia/Anadyr
      - Asia/Aqtau
      - Asia/Aqtobe
      - Asia/Ashgabat
      - Asia/Atyrau
      - Asia/Baghdad
      - Asia/Bahrain
      - Asia/Baku
      - Asia/Bangkok
      - Asia/Barnaul
      - Asia/Beirut
      - Asia/Bishkek
      - Asia/Brunei
      - Asia/Chita
      - Asia/Choibalsan
      - Asia/Colombo
      - Asia/Damascus
      - Asia/Dhaka
      - Asia/Dili
      - Asia/Dubai
      - Asia/Dushanbe
      - Asia/Famagusta
      - Asia/Gaza
      - Asia/Hebron
      - Asia/Ho_Chi_Minh
      - Asia/Hong_Kong
      - Asia/Hovd
      - Asia/Irkutsk
      - Asia/Jakarta
      - Asia/Jayapura
      - Asia/Jerusalem
      - Asia/Kabul
      - Asia/Kamchatka
      - Asia/Karachi
      - Asia/Kathmandu
      - Asia/Khandyga
      - Asia/Kolkata
      - Asia/Krasnoyarsk
      - Asia/Kuala_Lumpur
      - Asia/Kuching
      - Asia/Kuwait
      - Asia/Macau
      - Asia/Magadan
      - Asia/Makassar
      - Asia/Manila
      - Asia/Muscat
      - Asia/Nicosia
      - Asia/Novokuznetsk
      - Asia/Novosibirsk
      - Asia/Omsk
      - Asia/Oral
      - Asia/Phnom_Penh
      - Asia/Pontianak
      - Asia/Pyongyang
      - Asia/Qatar
      - Asia/Qostanay
      - Asia/Qyzylorda
      - Asia/Riyadh
      - Asia/Sakhalin
      - Asia/Samarkand
      - Asia/Seoul
      - Asia/Shanghai
      - Asia/Singapore
      - Asia/Srednekolymsk
      - Asia/Taipei
      - Asia/Tashkent
      - Asia/Tbilisi
      - Asia/Tehran
      - Asia/Thimphu
      - Asia/Tokyo
      - Asia/Tomsk
      - Asia/Ulaanbaatar
      - Asia/Urumqi
      - Asia/Ust-Nera
      - Asia/Vientiane
      - Asia/Vladivostok
      - Asia/Yakutsk
      - Asia/Yangon
      - Asia/Yekaterinburg
      - Asia/Yerevan
      - Atlantic/Azores
      - Atlantic/Bermuda
      - Atlantic/Canary
      - Atlantic/Cape_Verde
      - Atlantic/Faroe
      - Atlantic/Madeira
      - Atlantic/Reykjavik
      - Atlantic/South_Georgia
      - Atlantic/St_Helena
      - Atlantic/Stanley
      - Australia/Adelaide
      - Australia/Brisbane
      - Australia/Broken_Hill
      - Australia/Darwin
      - Australia/Eucla
      - Australia/Hobart
      - Australia/Lindeman
      - Australia/Lord_Howe
      - Australia/Melbourne
      - Australia/Perth
      - Australia/Sydney
      - Europe/Amsterdam
      - Europe/Andorra
      - Europe/Astrakhan
      - Europe/Athens
      - Europe/Belgrade
      - Europe/Berlin
      - Europe/Bratislava
      - Europe/Brussels
      - Europe/Bucharest
      - Europe/Budapest
      - Europe/Busingen
      - Europe/Chisinau
      - Europe/Copenhagen
      - Europe/Dublin
      - Europe/Gibraltar
      - Europe/Guernsey
      - Europe/Helsinki
      - Europe/Isle_of_Man
      - Europe/Istanbul
      - Europe/Jersey
      - Europe/Kaliningrad
      - Europe/Kiev
      - Europe/Kirov
      - Europe/Lisbon
      - Europe/Ljubljana
      - Europe/London
      - Europe/Luxembourg
      - Europe/Madrid
      - Europe/Malta
      - Europe/Mariehamn
      - Europe/Minsk
      - Europe/Monaco
      - Europe/Moscow
      - Europe/Oslo
      - Europe/Paris
      - Europe/Podgorica
      - Europe/Prague
      - Europe/Riga
      - Europe/Rome
      - Europe/Samara
      - Europe/San_Marino
      - Europe/Sarajevo
      - Europe/Saratov
      - Europe/Simferopol
      - Europe/Skopje
      - Europe/Sofia
      - Europe/Stockholm
      - Europe/Tallinn
      - Europe/Tirane
      - Europe/Ulyanovsk
      - Europe/Uzhgorod
      - Europe/Vaduz
      - Europe/Vatican
      - Europe/Vienna
      - Europe/Vilnius
      - Europe/Volgograd
      - Europe/Warsaw
      - Europe/Zagreb
      - Europe/Zaporozhye
      - Europe/Zurich
      - Indian/Antananarivo
      - Indian/Chagos
      - Indian/Christmas
      - Indian/Cocos
      - Indian/Comoro
      - Indian/Kerguelen
      - Indian/Mahe
      - Indian/Maldives
      - Indian/Mauritius
      - Indian/Mayotte
      - Indian/Reunion
      - Pacific/Apia
      - Pacific/Auckland
      - Pacific/Bougainville
      - Pacific/Chatham
      - Pacific/Chuuk
      - Pacific/Easter
      - Pacific/Efate
      - Pacific/Enderbury
      - Pacific/Fakaofo
      - Pacific/Fiji
      - Pacific/Funafuti
      - Pacific/Galapagos
      - Pacific/Gambier
      - Pacific/Guadalcanal
      - Pacific/Guam
      - Pacific/Honolulu
      - Pacific/Kiritimati
      - Pacific/Kosrae
      - Pacific/Kwajalein
      - Pacific/Majuro
      - Pacific/Marquesas
      - Pacific/Midway
      - Pacific/Nauru
      - Pacific/Niue
      - Pacific/Norfolk
      - Pacific/Noumea
      - Pacific/Pago_Pago
      - Pacific/Palau
      - Pacific/Pitcairn
      - Pacific/Pohnpei
      - Pacific/Port_Moresby
      - Pacific/Rarotonga
      - Pacific/Saipan
      - Pacific/Tahiti
      - Pacific/Tarawa
      - Pacific/Tongatapu
      - Pacific/Wake
      - Pacific/Wallis
      - US/Eastern
      - UTC
    description:
      - A time zone string used to replace the existing one.
      - If the given time zone already exist in the Time Zone configuration,
        there will be no changes made.
notes:
 - C(check_mode) is not supported.
"""


EXAMPLES = r"""
- name: Change time zone
  scale_computing.hypercore.time_zone:
    source: Europe/Ljubljana
"""

RETURN = r"""
record:
  description:
    - Time Zone configuration record.
  returned: success
  type: dict
  contains:
    uuid:
      description: Unique identifer
      type: str
      sample: timezone_guid
    zone:
      description: Time zone
      type: str
      sample: US/Eastern
    latest_task_tag:
      description: Latest Task Tag
      type: dict
      sample:
        completed: 1675170961
        created: 1675170954
        descriptionParameters: []
        formattedDescription: TimeZone Update
        formattedMessage: ""
        messageParameters: []
        modified: 1675170961
        nodeUUIDs:
          - 32c5012d-7d7b-49b4-9201-70e02b0d8758
        objectUUID: timezone_guid
        progressPercent: 100
        sessionID: 7157e957-bfad-4506-8713-124d5eb2397d
        state: COMPLETE
        taskTag: 687
"""

from typing import Tuple
from ansible.module_utils.basic import AnsibleModule

from ..module_utils.task_tag import TaskTag
from ..module_utils import arguments, errors
from ..module_utils.client import Client
from ..module_utils.rest_client import RestClient
from ..module_utils.time_zone import TimeZone

SUPPORTED_ZONES = [
    "Africa/Abidjan",
    "Africa/Accra",
    "Africa/Addis_Ababa",
    "Africa/Algiers",
    "Africa/Asmara",
    "Africa/Bamako",
    "Africa/Bangui",
    "Africa/Banjul",
    "Africa/Bissau",
    "Africa/Blantyre",
    "Africa/Brazzaville",
    "Africa/Bujumbura",
    "Africa/Cairo",
    "Africa/Casablanca",
    "Africa/Ceuta",
    "Africa/Conakry",
    "Africa/Dakar",
    "Africa/Dar_es_Salaam",
    "Africa/Djibouti",
    "Africa/Douala",
    "Africa/El_Aaiun",
    "Africa/Freetown",
    "Africa/Gaborone",
    "Africa/Harare",
    "Africa/Johannesburg",
    "Africa/Juba",
    "Africa/Kampala",
    "Africa/Khartoum",
    "Africa/Kigali",
    "Africa/Kinshasa",
    "Africa/Lagos",
    "Africa/Libreville",
    "Africa/Lome",
    "Africa/Luanda",
    "Africa/Lubumbashi",
    "Africa/Lusaka",
    "Africa/Malabo",
    "Africa/Maputo",
    "Africa/Maseru",
    "Africa/Mbabane",
    "Africa/Mogadishu",
    "Africa/Monrovia",
    "Africa/Nairobi",
    "Africa/Ndjamena",
    "Africa/Niamey",
    "Africa/Nouakchott",
    "Africa/Ouagadougou",
    "Africa/Porto-Novo",
    "Africa/Sao_Tome",
    "Africa/Tripoli",
    "Africa/Tunis",
    "Africa/Windhoek",
    "America/Adak",
    "America/Anchorage",
    "America/Anguilla",
    "America/Antigua",
    "America/Araguaina",
    "America/Argentina/Buenos_Aires",
    "America/Argentina/Catamarca",
    "America/Argentina/Cordoba",
    "America/Argentina/Jujuy",
    "America/Argentina/La_Rioja",
    "America/Argentina/Mendoza",
    "America/Argentina/Rio_Gallegos",
    "America/Argentina/Salta",
    "America/Argentina/San_Juan",
    "America/Argentina/San_Luis",
    "America/Argentina/Tucuman",
    "America/Argentina/Ushuaia",
    "America/Aruba",
    "America/Asuncion",
    "America/Atikokan",
    "America/Bahia",
    "America/Bahia_Banderas",
    "America/Barbados",
    "America/Belem",
    "America/Belize",
    "America/Blanc-Sablon",
    "America/Boa_Vista",
    "America/Bogota",
    "America/Boise",
    "America/Cambridge_Bay",
    "America/Campo_Grande",
    "America/Cancun",
    "America/Caracas",
    "America/Cayenne",
    "America/Cayman",
    "America/Chicago",
    "America/Chihuahua",
    "America/Costa_Rica",
    "America/Creston",
    "America/Cuiaba",
    "America/Curacao",
    "America/Danmarkshavn",
    "America/Dawson",
    "America/Dawson_Creek",
    "America/Denver",
    "America/Detroit",
    "America/Dominica",
    "America/Edmonton",
    "America/Eirunepe",
    "America/El_Salvador",
    "America/Fort_Nelson",
    "America/Fortaleza",
    "America/Glace_Bay",
    "America/Goose_Bay",
    "America/Grand_Turk",
    "America/Grenada",
    "America/Guadeloupe",
    "America/Guatemala",
    "America/Guayaquil",
    "America/Guyana",
    "America/Halifax",
    "America/Havana",
    "America/Hermosillo",
    "America/Indiana/Indianapolis",
    "America/Indiana/Knox",
    "America/Indiana/Marengo",
    "America/Indiana/Petersburg",
    "America/Indiana/Tell_City",
    "America/Indiana/Vevay",
    "America/Indiana/Vincennes",
    "America/Indiana/Winamac",
    "America/Inuvik",
    "America/Iqaluit",
    "America/Jamaica",
    "America/Juneau",
    "America/Kentucky/Louisville",
    "America/Kentucky/Monticello",
    "America/Kralendijk",
    "America/La_Paz",
    "America/Lima",
    "America/Los_Angeles",
    "America/Lower_Princes",
    "America/Maceio",
    "America/Managua",
    "America/Manaus",
    "America/Marigot",
    "America/Martinique",
    "America/Matamoros",
    "America/Mazatlan",
    "America/Menominee",
    "America/Merida",
    "America/Metlakatla",
    "America/Mexico_City",
    "America/Miquelon",
    "America/Moncton",
    "America/Monterrey",
    "America/Montevideo",
    "America/Montserrat",
    "America/Nassau",
    "America/New_York",
    "America/Nipigon",
    "America/Nome",
    "America/Noronha",
    "America/North_Dakota/Beulah",
    "America/North_Dakota/Center",
    "America/North_Dakota/New_Salem",
    "America/Nuuk",
    "America/Ojinaga",
    "America/Panama",
    "America/Pangnirtung",
    "America/Paramaribo",
    "America/Phoenix",
    "America/Port-au-Prince",
    "America/Port_of_Spain",
    "America/Porto_Velho",
    "America/Puerto_Rico",
    "America/Punta_Arenas",
    "America/Rainy_River",
    "America/Rankin_Inlet",
    "America/Recife",
    "America/Regina",
    "America/Resolute",
    "America/Rio_Branco",
    "America/Santarem",
    "America/Santiago",
    "America/Santo_Domingo",
    "America/Sao_Paulo",
    "America/Scoresbysund",
    "America/Sitka",
    "America/St_Barthelemy",
    "America/St_Johns",
    "America/St_Kitts",
    "America/St_Lucia",
    "America/St_Thomas",
    "America/St_Vincent",
    "America/Swift_Current",
    "America/Tegucigalpa",
    "America/Thule",
    "America/Thunder_Bay",
    "America/Tijuana",
    "America/Toronto",
    "America/Tortola",
    "America/Vancouver",
    "America/Whitehorse",
    "America/Winnipeg",
    "America/Yakutat",
    "America/Yellowknife",
    "Antarctica/Casey",
    "Antarctica/Davis",
    "Antarctica/DumontDUrville",
    "Antarctica/Macquarie",
    "Antarctica/Mawson",
    "Antarctica/McMurdo",
    "Antarctica/Palmer",
    "Antarctica/Rothera",
    "Antarctica/Syowa",
    "Antarctica/Troll",
    "Antarctica/Vostok",
    "Arctic/Longyearbyen",
    "Asia/Aden",
    "Asia/Almaty",
    "Asia/Amman",
    "Asia/Anadyr",
    "Asia/Aqtau",
    "Asia/Aqtobe",
    "Asia/Ashgabat",
    "Asia/Atyrau",
    "Asia/Baghdad",
    "Asia/Bahrain",
    "Asia/Baku",
    "Asia/Bangkok",
    "Asia/Barnaul",
    "Asia/Beirut",
    "Asia/Bishkek",
    "Asia/Brunei",
    "Asia/Chita",
    "Asia/Choibalsan",
    "Asia/Colombo",
    "Asia/Damascus",
    "Asia/Dhaka",
    "Asia/Dili",
    "Asia/Dubai",
    "Asia/Dushanbe",
    "Asia/Famagusta",
    "Asia/Gaza",
    "Asia/Hebron",
    "Asia/Ho_Chi_Minh",
    "Asia/Hong_Kong",
    "Asia/Hovd",
    "Asia/Irkutsk",
    "Asia/Jakarta",
    "Asia/Jayapura",
    "Asia/Jerusalem",
    "Asia/Kabul",
    "Asia/Kamchatka",
    "Asia/Karachi",
    "Asia/Kathmandu",
    "Asia/Khandyga",
    "Asia/Kolkata",
    "Asia/Krasnoyarsk",
    "Asia/Kuala_Lumpur",
    "Asia/Kuching",
    "Asia/Kuwait",
    "Asia/Macau",
    "Asia/Magadan",
    "Asia/Makassar",
    "Asia/Manila",
    "Asia/Muscat",
    "Asia/Nicosia",
    "Asia/Novokuznetsk",
    "Asia/Novosibirsk",
    "Asia/Omsk",
    "Asia/Oral",
    "Asia/Phnom_Penh",
    "Asia/Pontianak",
    "Asia/Pyongyang",
    "Asia/Qatar",
    "Asia/Qostanay",
    "Asia/Qyzylorda",
    "Asia/Riyadh",
    "Asia/Sakhalin",
    "Asia/Samarkand",
    "Asia/Seoul",
    "Asia/Shanghai",
    "Asia/Singapore",
    "Asia/Srednekolymsk",
    "Asia/Taipei",
    "Asia/Tashkent",
    "Asia/Tbilisi",
    "Asia/Tehran",
    "Asia/Thimphu",
    "Asia/Tokyo",
    "Asia/Tomsk",
    "Asia/Ulaanbaatar",
    "Asia/Urumqi",
    "Asia/Ust-Nera",
    "Asia/Vientiane",
    "Asia/Vladivostok",
    "Asia/Yakutsk",
    "Asia/Yangon",
    "Asia/Yekaterinburg",
    "Asia/Yerevan",
    "Atlantic/Azores",
    "Atlantic/Bermuda",
    "Atlantic/Canary",
    "Atlantic/Cape_Verde",
    "Atlantic/Faroe",
    "Atlantic/Madeira",
    "Atlantic/Reykjavik",
    "Atlantic/South_Georgia",
    "Atlantic/St_Helena",
    "Atlantic/Stanley",
    "Australia/Adelaide",
    "Australia/Brisbane",
    "Australia/Broken_Hill",
    "Australia/Darwin",
    "Australia/Eucla",
    "Australia/Hobart",
    "Australia/Lindeman",
    "Australia/Lord_Howe",
    "Australia/Melbourne",
    "Australia/Perth",
    "Australia/Sydney",
    "Europe/Amsterdam",
    "Europe/Andorra",
    "Europe/Astrakhan",
    "Europe/Athens",
    "Europe/Belgrade",
    "Europe/Berlin",
    "Europe/Bratislava",
    "Europe/Brussels",
    "Europe/Bucharest",
    "Europe/Budapest",
    "Europe/Busingen",
    "Europe/Chisinau",
    "Europe/Copenhagen",
    "Europe/Dublin",
    "Europe/Gibraltar",
    "Europe/Guernsey",
    "Europe/Helsinki",
    "Europe/Isle_of_Man",
    "Europe/Istanbul",
    "Europe/Jersey",
    "Europe/Kaliningrad",
    "Europe/Kiev",
    "Europe/Kirov",
    "Europe/Lisbon",
    "Europe/Ljubljana",
    "Europe/London",
    "Europe/Luxembourg",
    "Europe/Madrid",
    "Europe/Malta",
    "Europe/Mariehamn",
    "Europe/Minsk",
    "Europe/Monaco",
    "Europe/Moscow",
    "Europe/Oslo",
    "Europe/Paris",
    "Europe/Podgorica",
    "Europe/Prague",
    "Europe/Riga",
    "Europe/Rome",
    "Europe/Samara",
    "Europe/San_Marino",
    "Europe/Sarajevo",
    "Europe/Saratov",
    "Europe/Simferopol",
    "Europe/Skopje",
    "Europe/Sofia",
    "Europe/Stockholm",
    "Europe/Tallinn",
    "Europe/Tirane",
    "Europe/Ulyanovsk",
    "Europe/Uzhgorod",
    "Europe/Vaduz",
    "Europe/Vatican",
    "Europe/Vienna",
    "Europe/Vilnius",
    "Europe/Volgograd",
    "Europe/Warsaw",
    "Europe/Zagreb",
    "Europe/Zaporozhye",
    "Europe/Zurich",
    "Indian/Antananarivo",
    "Indian/Chagos",
    "Indian/Christmas",
    "Indian/Cocos",
    "Indian/Comoro",
    "Indian/Kerguelen",
    "Indian/Mahe",
    "Indian/Maldives",
    "Indian/Mauritius",
    "Indian/Mayotte",
    "Indian/Reunion",
    "Pacific/Apia",
    "Pacific/Auckland",
    "Pacific/Bougainville",
    "Pacific/Chatham",
    "Pacific/Chuuk",
    "Pacific/Easter",
    "Pacific/Efate",
    "Pacific/Enderbury",
    "Pacific/Fakaofo",
    "Pacific/Fiji",
    "Pacific/Funafuti",
    "Pacific/Galapagos",
    "Pacific/Gambier",
    "Pacific/Guadalcanal",
    "Pacific/Guam",
    "Pacific/Honolulu",
    "Pacific/Kiritimati",
    "Pacific/Kosrae",
    "Pacific/Kwajalein",
    "Pacific/Majuro",
    "Pacific/Marquesas",
    "Pacific/Midway",
    "Pacific/Nauru",
    "Pacific/Niue",
    "Pacific/Norfolk",
    "Pacific/Noumea",
    "Pacific/Pago_Pago",
    "Pacific/Palau",
    "Pacific/Pitcairn",
    "Pacific/Pohnpei",
    "Pacific/Port_Moresby",
    "Pacific/Rarotonga",
    "Pacific/Saipan",
    "Pacific/Tahiti",
    "Pacific/Tarawa",
    "Pacific/Tongatapu",
    "Pacific/Wake",
    "Pacific/Wallis",
    "US/Eastern",  # was missing from list, keep it?
    "UTC",
]


# Remove implementation not needed
def modify_time_zone(
    module: AnsibleModule, rest_client: RestClient
) -> Tuple[bool, dict, dict]:
    # GET method to get the Time Server by UUID
    time_zone = TimeZone.get_by_uuid(module.params, rest_client)

    # Get new time zone
    new_time_zone_entry = module.params["zone"]

    # If Time Zone doesn't exist, create one
    if not time_zone:
        create_task_tag = rest_client.create_record(
            endpoint="/rest/v1/TimeZone",
            payload=dict(timeZone=new_time_zone_entry),
            check_mode=module.check_mode,
        )
        TaskTag.wait_task(rest_client, create_task_tag)
        new_state = TimeZone.get_state(rest_client)
        return True, {}, dict(before={}, after=new_state)

    # Otherwise, continue with modifying the configuration
    before = time_zone.to_ansible()
    old_state = TimeZone.get_state(
        rest_client=rest_client
    )  # get the state of Time Server before modification

    # Init return values and return if no changes were made
    change, record, diff = (
        new_time_zone_entry != before.get("zone"),
        old_state,
        dict(before=before, after=old_state),
    )
    if not change:
        return change, record, diff

    if new_time_zone_entry not in SUPPORTED_ZONES:
        raise errors.ScaleComputingError("Time Zone: Time zone not supported.")

    # Set the task tag:
    # update_record -> PATCH
    update_task_tag = rest_client.update_record(
        endpoint="{0}/{1}".format("/rest/v1/TimeZone", time_zone.uuid),
        payload=dict(timeZone=new_time_zone_entry),
        check_mode=module.check_mode,
    )

    TaskTag.wait_task(rest_client, update_task_tag)  # wait for the task to finish

    new_time_zone = TimeZone.get_by_uuid(module.params, rest_client)
    after = new_time_zone.to_ansible()
    record, diff = TimeZone.get_state(rest_client), dict(before=before, after=after)
    change = old_state != record

    return change, record, diff


def run(module: AnsibleModule, rest_client: RestClient) -> Tuple[bool, dict, dict]:
    return modify_time_zone(module, rest_client)


def main() -> None:
    module = AnsibleModule(
        argument_spec=dict(
            arguments.get_spec("cluster_instance"),
            zone=dict(
                type="str",
                required=True,
                choices=SUPPORTED_ZONES,
            ),
        ),
    )

    try:
        client = Client.get_client(module.params["cluster_instance"])
        rest_client = RestClient(client)
        changed, record, diff = run(module, rest_client)
        module.exit_json(changed=changed, record=record, diff=diff)
    except errors.ScaleComputingError as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()

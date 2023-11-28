#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, XLAB Steampunk <steampunk@xlab.si>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


# language=yaml
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
      - Africa/Asmera
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
      - Africa/Timbuktu
      - Africa/Tripoli
      - Africa/Tunis
      - Africa/Windhoek
      - America/Adak
      - America/Anchorage
      - America/Anguilla
      - America/Antigua
      - America/Araguaina
      - America/Aruba
      - America/Asuncion
      - America/Barbados
      - America/Belem
      - America/Belize
      - America/Boa_Vista
      - America/Bogota
      - America/Boise
      - America/Buenos_Aires
      - America/Cambridge_Bay
      - America/Cancun
      - America/Caracas
      - America/Catamarca
      - America/Cayenne
      - America/Cayman
      - America/Chicago
      - America/Chihuahua
      - America/Cordoba
      - America/Costa_Rica
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
      - America/Fortaleza
      - America/Glace_Bay
      - America/Godthab
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
      - America/Indiana/Vevay
      - America/Indianapolis
      - America/Inuvik
      - America/Iqaluit
      - America/Jamaica
      - America/Jujuy
      - America/Juneau
      - America/Kentucky/Louisville
      - America/Kentucky/Monticello
      - America/La_Paz
      - America/Lima
      - America/Los_Angeles
      - America/Louisville
      - America/Maceio
      - America/Managua
      - America/Manaus
      - America/Martinique
      - America/Mazatlan
      - America/Mendoza
      - America/Menominee
      - America/Merida
      - America/Mexico_City
      - America/Miquelon
      - America/Monterrey
      - America/Montevideo
      - America/Montreal
      - America/Montserrat
      - America/Nassau
      - America/New_York
      - America/Nipigon
      - America/Nome
      - America/Noronha
      - America/North_Dakota/Center
      - America/Panama
      - America/Pangnirtung
      - America/Paramaribo
      - America/Phoenix
      - America/Port-au-Prince
      - America/Port_of_Spain
      - America/Porto_Velho
      - America/Puerto_Rico
      - America/Rainy_River
      - America/Rankin_Inlet
      - America/Recife
      - America/Regina
      - America/Rio_Branco
      - America/Rosario
      - America/Santiago
      - America/Santo_Domingo
      - America/Sao_Paulo
      - America/Scoresbysund
      - America/Shiprock
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
      - America/Tortola
      - America/Vancouver
      - America/Whitehorse
      - America/Winnipeg
      - America/Yakutat
      - America/Yellowknife
      - Antarctica/Casey
      - Antarctica/Davis
      - Antarctica/DumontDUrville
      - Antarctica/Mawson
      - Antarctica/McMurdo
      - Antarctica/Palmer
      - Antarctica/South_Pole
      - Antarctica/Syowa
      - Antarctica/Vostok
      - Arctic/Longyearbyen
      - Asia/Aden
      - Asia/Almaty
      - Asia/Amman
      - Asia/Anadyr
      - Asia/Aqtau
      - Asia/Aqtobe
      - Asia/Ashgabat
      - Asia/Baghdad
      - Asia/Bahrain
      - Asia/Baku
      - Asia/Bangkok
      - Asia/Beirut
      - Asia/Bishkek
      - Asia/Brunei
      - Asia/Calcutta
      - Asia/Choibalsan
      - Asia/Chongqing
      - Asia/Colombo
      - Asia/Damascus
      - Asia/Dhaka
      - Asia/Dili
      - Asia/Dubai
      - Asia/Dushanbe
      - Asia/Gaza
      - Asia/Harbin
      - Asia/Hong_Kong
      - Asia/Hovd
      - Asia/Irkutsk
      - Asia/Istanbul
      - Asia/Jakarta
      - Asia/Jayapura
      - Asia/Jerusalem
      - Asia/Kabul
      - Asia/Kamchatka
      - Asia/Karachi
      - Asia/Kashgar
      - Asia/Katmandu
      - Asia/Krasnoyarsk
      - Asia/Kuala_Lumpur
      - Asia/Kuching
      - Asia/Kuwait
      - Asia/Macao
      - Asia/Macau
      - Asia/Magadan
      - Asia/Makassar
      - Asia/Manila
      - Asia/Muscat
      - Asia/Nicosia
      - Asia/Novosibirsk
      - Asia/Omsk
      - Asia/Oral
      - Asia/Phnom_Penh
      - Asia/Pontianak
      - Asia/Pyongyang
      - Asia/Qyzylorda
      - Asia/Qatar
      - Asia/Rangoon
      - Asia/Riyadh
      - Asia/Saigon
      - Asia/Sakhalin
      - Asia/Samarkand
      - Asia/Seoul
      - Asia/Shanghai
      - Asia/Singapore
      - Asia/Taipei
      - Asia/Tashkent
      - Asia/Tbilisi
      - Asia/Tehran
      - Asia/Thimphu
      - Asia/Tokyo
      - Asia/Ujung_Pandang
      - Asia/Ulaanbaatar
      - Asia/Urumqi
      - Asia/Vientiane
      - Asia/Vladivostok
      - Asia/Yakutsk
      - Asia/Yekaterinburg
      - Asia/Yerevan
      - Atlantic/Azores
      - Atlantic/Bermuda
      - Atlantic/Canary
      - Atlantic/Cape_Verde
      - Atlantic/Faeroe
      - Atlantic/Jan_Mayen
      - Atlantic/Madeira
      - Atlantic/Reykjavik
      - Atlantic/South_Georgia
      - Atlantic/St_Helena
      - Atlantic/Stanley
      - Australia/Adelaide
      - Australia/Brisbane
      - Australia/Broken_Hill
      - Australia/Darwin
      - Australia/Hobart
      - Australia/Lindeman
      - Australia/Lord_Howe
      - Australia/Melbourne
      - Australia/Perth
      - Australia/Sydney
      - Europe/Amsterdam
      - Europe/Andorra
      - Europe/Athens
      - Europe/Belfast
      - Europe/Belgrade
      - Europe/Berlin
      - Europe/Bratislava
      - Europe/Brussels
      - Europe/Bucharest
      - Europe/Budapest
      - Europe/Chisinau
      - Europe/Copenhagen
      - Europe/Dublin
      - Europe/Gibraltar
      - Europe/Helsinki
      - Europe/Istanbul
      - Europe/Kaliningrad
      - Europe/Kiev
      - Europe/Lisbon
      - Europe/Ljubljana
      - Europe/London
      - Europe/Luxembourg
      - Europe/Madrid
      - Europe/Malta
      - Europe/Minsk
      - Europe/Monaco
      - Europe/Moscow
      - Europe/Nicosia
      - Europe/Oslo
      - Europe/Paris
      - Europe/Prague
      - Europe/Riga
      - Europe/Rome
      - Europe/Samara
      - Europe/San_Marino
      - Europe/Sarajevo
      - Europe/Simferopol
      - Europe/Skopje
      - Europe/Sofia
      - Europe/Stockholm
      - Europe/Tallinn
      - Europe/Tirane
      - Europe/Uzhgorod
      - Europe/Vaduz
      - Europe/Vatican
      - Europe/Vienna
      - Europe/Vilnius
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
      - Pacific/Chatham
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
      - Pacific/Johnston
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
      - Pacific/Ponape
      - Pacific/Port_Moresby
      - Pacific/Rarotonga
      - Pacific/Saipan
      - Pacific/Tahiti
      - Pacific/Tarawa
      - Pacific/Tongatapu
      - Pacific/Truk
      - Pacific/Wake
      - Pacific/Wallis
      - Pacific/Yap
      - US/Alaska
      - US/Aleutian
      - US/Arizona
      - US/Central
      - US/Eastern
      - US/East-Indiana
      - US/Hawaii
      - US/Indiana-Starke
      - US/Michigan
      - US/Mountain
      - US/Pacific
      - US/Pacific-New
      - US/Samoa
      - UTC
    description:
      - A time zone string used to replace the existing one.
      - If the given time zone already exist in the Time Zone configuration,
        there will be no changes made.
notes:
 - C(check_mode) is not supported.
"""


# language=yaml
EXAMPLES = r"""
- name: Change time zone
  scale_computing.hypercore.time_zone:
    source: Europe/Ljubljana
"""

# language=yaml
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

# List is based on date_time_zonespec.csv.
SUPPORTED_ZONES = [
    "Africa/Abidjan",
    "Africa/Accra",
    "Africa/Addis_Ababa",
    "Africa/Algiers",
    "Africa/Asmera",
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
    "Africa/Timbuktu",
    "Africa/Tripoli",
    "Africa/Tunis",
    "Africa/Windhoek",
    "America/Adak",
    "America/Anchorage",
    "America/Anguilla",
    "America/Antigua",
    "America/Araguaina",
    "America/Aruba",
    "America/Asuncion",
    "America/Barbados",
    "America/Belem",
    "America/Belize",
    "America/Boa_Vista",
    "America/Bogota",
    "America/Boise",
    "America/Buenos_Aires",
    "America/Cambridge_Bay",
    "America/Cancun",
    "America/Caracas",
    "America/Catamarca",
    "America/Cayenne",
    "America/Cayman",
    "America/Chicago",
    "America/Chihuahua",
    "America/Cordoba",
    "America/Costa_Rica",
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
    "America/Fortaleza",
    "America/Glace_Bay",
    "America/Godthab",
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
    "America/Indiana/Vevay",
    "America/Indianapolis",
    "America/Inuvik",
    "America/Iqaluit",
    "America/Jamaica",
    "America/Jujuy",
    "America/Juneau",
    "America/Kentucky/Louisville",
    "America/Kentucky/Monticello",
    "America/La_Paz",
    "America/Lima",
    "America/Los_Angeles",
    "America/Louisville",
    "America/Maceio",
    "America/Managua",
    "America/Manaus",
    "America/Martinique",
    "America/Mazatlan",
    "America/Mendoza",
    "America/Menominee",
    "America/Merida",
    "America/Mexico_City",
    "America/Miquelon",
    "America/Monterrey",
    "America/Montevideo",
    "America/Montreal",
    "America/Montserrat",
    "America/Nassau",
    "America/New_York",
    "America/Nipigon",
    "America/Nome",
    "America/Noronha",
    "America/North_Dakota/Center",
    "America/Panama",
    "America/Pangnirtung",
    "America/Paramaribo",
    "America/Phoenix",
    "America/Port-au-Prince",
    "America/Port_of_Spain",
    "America/Porto_Velho",
    "America/Puerto_Rico",
    "America/Rainy_River",
    "America/Rankin_Inlet",
    "America/Recife",
    "America/Regina",
    "America/Rio_Branco",
    "America/Rosario",
    "America/Santiago",
    "America/Santo_Domingo",
    "America/Sao_Paulo",
    "America/Scoresbysund",
    "America/Shiprock",
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
    "America/Tortola",
    "America/Vancouver",
    "America/Whitehorse",
    "America/Winnipeg",
    "America/Yakutat",
    "America/Yellowknife",
    "Antarctica/Casey",
    "Antarctica/Davis",
    "Antarctica/DumontDUrville",
    "Antarctica/Mawson",
    "Antarctica/McMurdo",
    "Antarctica/Palmer",
    "Antarctica/South_Pole",
    "Antarctica/Syowa",
    "Antarctica/Vostok",
    "Arctic/Longyearbyen",
    "Asia/Aden",
    "Asia/Almaty",
    "Asia/Amman",
    "Asia/Anadyr",
    "Asia/Aqtau",
    "Asia/Aqtobe",
    "Asia/Ashgabat",
    "Asia/Baghdad",
    "Asia/Bahrain",
    "Asia/Baku",
    "Asia/Bangkok",
    "Asia/Beirut",
    "Asia/Bishkek",
    "Asia/Brunei",
    "Asia/Calcutta",
    "Asia/Choibalsan",
    "Asia/Chongqing",
    "Asia/Colombo",
    "Asia/Damascus",
    "Asia/Dhaka",
    "Asia/Dili",
    "Asia/Dubai",
    "Asia/Dushanbe",
    "Asia/Gaza",
    "Asia/Harbin",
    "Asia/Hong_Kong",
    "Asia/Hovd",
    "Asia/Irkutsk",
    "Asia/Istanbul",
    "Asia/Jakarta",
    "Asia/Jayapura",
    "Asia/Jerusalem",
    "Asia/Kabul",
    "Asia/Kamchatka",
    "Asia/Karachi",
    "Asia/Kashgar",
    "Asia/Katmandu",
    "Asia/Krasnoyarsk",
    "Asia/Kuala_Lumpur",
    "Asia/Kuching",
    "Asia/Kuwait",
    "Asia/Macao",
    "Asia/Macau",
    "Asia/Magadan",
    "Asia/Makassar",
    "Asia/Manila",
    "Asia/Muscat",
    "Asia/Nicosia",
    "Asia/Novosibirsk",
    "Asia/Omsk",
    "Asia/Oral",
    "Asia/Phnom_Penh",
    "Asia/Pontianak",
    "Asia/Pyongyang",
    "Asia/Qyzylorda",
    "Asia/Qatar",
    "Asia/Rangoon",
    "Asia/Riyadh",
    "Asia/Saigon",
    "Asia/Sakhalin",
    "Asia/Samarkand",
    "Asia/Seoul",
    "Asia/Shanghai",
    "Asia/Singapore",
    "Asia/Taipei",
    "Asia/Tashkent",
    "Asia/Tbilisi",
    "Asia/Tehran",
    "Asia/Thimphu",
    "Asia/Tokyo",
    "Asia/Ujung_Pandang",
    "Asia/Ulaanbaatar",
    "Asia/Urumqi",
    "Asia/Vientiane",
    "Asia/Vladivostok",
    "Asia/Yakutsk",
    "Asia/Yekaterinburg",
    "Asia/Yerevan",
    "Atlantic/Azores",
    "Atlantic/Bermuda",
    "Atlantic/Canary",
    "Atlantic/Cape_Verde",
    "Atlantic/Faeroe",
    "Atlantic/Jan_Mayen",
    "Atlantic/Madeira",
    "Atlantic/Reykjavik",
    "Atlantic/South_Georgia",
    "Atlantic/St_Helena",
    "Atlantic/Stanley",
    "Australia/Adelaide",
    "Australia/Brisbane",
    "Australia/Broken_Hill",
    "Australia/Darwin",
    "Australia/Hobart",
    "Australia/Lindeman",
    "Australia/Lord_Howe",
    "Australia/Melbourne",
    "Australia/Perth",
    "Australia/Sydney",
    "Europe/Amsterdam",
    "Europe/Andorra",
    "Europe/Athens",
    "Europe/Belfast",
    "Europe/Belgrade",
    "Europe/Berlin",
    "Europe/Bratislava",
    "Europe/Brussels",
    "Europe/Bucharest",
    "Europe/Budapest",
    "Europe/Chisinau",
    "Europe/Copenhagen",
    "Europe/Dublin",
    "Europe/Gibraltar",
    "Europe/Helsinki",
    "Europe/Istanbul",
    "Europe/Kaliningrad",
    "Europe/Kiev",
    "Europe/Lisbon",
    "Europe/Ljubljana",
    "Europe/London",
    "Europe/Luxembourg",
    "Europe/Madrid",
    "Europe/Malta",
    "Europe/Minsk",
    "Europe/Monaco",
    "Europe/Moscow",
    "Europe/Nicosia",
    "Europe/Oslo",
    "Europe/Paris",
    "Europe/Prague",
    "Europe/Riga",
    "Europe/Rome",
    "Europe/Samara",
    "Europe/San_Marino",
    "Europe/Sarajevo",
    "Europe/Simferopol",
    "Europe/Skopje",
    "Europe/Sofia",
    "Europe/Stockholm",
    "Europe/Tallinn",
    "Europe/Tirane",
    "Europe/Uzhgorod",
    "Europe/Vaduz",
    "Europe/Vatican",
    "Europe/Vienna",
    "Europe/Vilnius",
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
    "Pacific/Chatham",
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
    "Pacific/Johnston",
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
    "Pacific/Ponape",
    "Pacific/Port_Moresby",
    "Pacific/Rarotonga",
    "Pacific/Saipan",
    "Pacific/Tahiti",
    "Pacific/Tarawa",
    "Pacific/Tongatapu",
    "Pacific/Truk",
    "Pacific/Wake",
    "Pacific/Wallis",
    "Pacific/Yap",
    "US/Alaska",
    "US/Aleutian",
    "US/Arizona",
    "US/Central",
    "US/Eastern",
    "US/East-Indiana",
    "US/Hawaii",
    "US/Indiana-Starke",
    "US/Michigan",
    "US/Mountain",
    "US/Pacific",
    "US/Pacific-New",
    "US/Samoa",
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

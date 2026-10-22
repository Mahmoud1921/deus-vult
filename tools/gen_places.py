"""Rename modern city (victory point) and region (state) names to their 1187 forms.

Run from the repo root: python3 tools/gen_places.py .
Writes localisation/english/replace/dv_place_names_l_english.yml, which overrides
the vanilla VICTORY_POINTS_<province> and STATE_<id> keys.
"""
import os
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'

# province id -> 1187 name
CITIES = {
    # Kingdom of Jerusalem, Syria, Egypt
    4206: 'Jaffa', 7151: 'Kerak', 11976: 'Montréal', 4486: 'Bosra', 1088: 'Latakia',
    12029: 'Antioch', 3942: 'Rahba', 1549: 'Nisibis', 6883: 'Saruj', 10099: 'Mount Sinai',
    12049: 'Damietta', 4073: 'Qulzum', 1071: 'Taposiris', 12071: 'Qus', 12002: 'Qusayr',
    11954: 'Barqa', 10061: 'Paraetonium', 9989: 'Sollum', 1130: 'Antipyrgos',
    # Arabia and the Gulf
    12727: 'Hajr', 8085: 'Kazima', 7960: 'Julfar', 8051: 'Qatar', 12702: 'Qatif', 13313: 'Awal',
    # Iraq
    6826: 'Shahrazur', 12413: 'Anbar', 2089: 'Basra', 12726: 'Wasit',
    # Persia
    10837: 'Rayy', 7602: 'Astarabad', 10782: 'Bampur', 4928: 'Arrajan', 7982: 'Hormuz',
    12832: 'Siraf', 7953: 'Ahwaz', 5029: 'Tus', 8040: 'Hamadan', 2065: 'Qom', 8093: 'Bistam',
    7604: 'Urmiya', 1822: 'Maragha', 7969: 'Qazvin', 4943: 'Dinawar', 5098: 'Qirmisin',
    7990: "Qa'in",
    # Caucasus
    12320: 'Dvin', 12441: 'Ani', 1599: 'Tiflis', 6701: 'Tarki', 9663: 'Nikopsis',
    3720: 'Zichia', 719: 'Bata', 3734: 'Kuban', 11696: 'Majar', 9753: 'Saqsin',
    11724: 'Caspian Steppe', 775: 'Manych', 3672: 'Magas', 11617: 'Tskhumi',
    11614: 'Kabarda', 9628: 'Dariali',
    # Anatolia and Constantinople
    9833: 'Constantinople', 11747: 'Ancyra', 804: 'Kalecik', 3951: 'Dorylaeum',
    4112: 'Smyrna', 928: 'Magnesia', 947: 'Prusa', 9799: 'Achyraous', 11842: 'Adrianople',
    1005: 'Attaleia', 10041: 'Laodicea', 9878: 'Akroinon', 3856: 'Kotyaion',
    9893: 'Aintab', 7620: 'Melitene', 6813: 'Marash', 10056: 'Korykos', 9861: 'Iconium',
    6807: 'Laranda', 784: 'Baris', 11811: 'Nicomedia', 904: 'Nicaea', 3870: 'Caesarea',
    9777: 'Sebasteia', 4512: 'Amid', 9823: 'Edessa', 12387: 'Hisn Kayfa',
    7530: 'Jazirat ibn Umar', 9860: 'Dersim', 876: 'Kharput', 9868: 'Erzincan',
    9932: 'Trebizond', 3979: 'Argyroupolis', 11881: 'Amisos', 6995: 'Sinope',
    3862: 'Tavium', 919: 'Amaseia', 12376: 'Manzikert',
    # Balkans and Greece
    9914: 'Kruja', 619: 'Pétervárad', 9809: 'Doclea', 9894: 'Blagaj', 11899: 'Vrhbosna',
    11905: 'Traianoupolis', 1205: 'Angelokastron', 11597: 'Karvuna',
    # Romania, Moldavia
    9617: 'Câmpulung', 3663: 'Argeș', 3707: 'Orhei', 741: 'Tighina',
    # Rus' and the steppe
    3151: 'Izhora', 3529: 'Itil', 9417: 'Tana', 11437: 'Dnieper Rapids', 11561: 'Ingul',
    6474: 'Sharukan', 9461: 'Sugrov', 11405: 'Khortytsia', 721: 'Oleshye', 11683: 'Olbia',
    11670: 'Khadjibey', 3686: 'Chersonesus', 9680: 'Korchev', 705: 'Soldaia',
    418: 'Donets', 9355: 'Mtsensk', 3520: 'Putivl', 9566: 'Novgorod-Seversky',
    9197: 'Ladoga', 11476: 'Sarkel', 6245: 'Tver', 6338: 'Bilyar', 392: 'Bolgar',
    11225: 'Samara Bend', 11375: 'Gorodets', 6269: 'Suzdal', 9258: 'Burtas',
    9259: 'Cheremis', 11351: 'Meshchera', 487: 'Medveditsa', 3578: 'Uvek',
    11523: 'Tsaritsa', 9432: 'Kamyshin', 11159: 'Onega', 476: 'Bratslav', 488: 'Kaniv',
    3457: 'Podolia', 6557: 'Lutsk', 422: 'Volodymyr', 3350: 'Slutsk',
    # Urals, Volga and Central Asia
    108: 'Vychegda', 7375: 'Great Perm', 6278: 'Votyak', 6124: 'Khlynov', 6502: 'Irgiz',
    3618: 'Saraychik', 11537: 'Yaik', 9292: 'Chelyaba', 10329: 'Ai', 10256: 'Magnit Hill',
    12333: 'Nisa', 4354: 'Bashkort', 1821: 'Iset', 1614: 'Kath', 1493: 'Gurganj',
    9402: 'Cheremis Woods', 11061: 'Ustyug',
    # Poland, Prussia, the Baltic
    9508: 'Łęczyca', 11467: 'Racibórz', 6464: 'Bytom', 9263: 'Puck', 6375: 'Galindia',
    6332: 'Tuwangste', 9304: 'Navahrudak', 406: 'Lahoysk', 11301: 'Drohiczyn',
    3254: 'Yotvingia', 11411: 'Halych', 11479: 'Zvenyhorod', 3152: 'Lindanise',
    9340: 'Ikšķile', 9262: 'Grobiņa', 6222: 'Tērvete', 3255: 'Koknese', 310: 'Jersika',
    3174: 'Soontagana', 185: 'Valjala', 592: 'Otepää', 11312: 'Sudovia', 6229: 'Kernavė',
    # Germany and the Low Countries
    241: 'Jever', 374: 'Stade', 9496: 'Lebus', 3258: 'Demmin', 6389: 'Plön',
    3530: 'Durlach', 6521: 'Brandenburg', 6496: "'s-Hertogenbosch", 3211: 'Leiden',
    9498: 'Dordrecht', 391: 'Haarlem', 9536: 'Thuin',
    # France, Italy, Iberia, Maghreb
    9434: 'Harfleur', 9620: 'Fribourg', 6666: 'Geneva', 3838: 'Aléria', 6973: 'Luni',
    11833: 'Pisa', 12003: 'Mdina', 3790: 'Silves', 13071: 'Canary Islands',
    9793: 'Madina Mayurqa', 7069: 'Anfa', 8038: 'Sakia', 12857: 'Ifni', 7081: 'Buna',
    12034: 'Tobna',
    # British Isles
    11064: 'Kirkwall', 6300: 'Dunfermline', 3379: 'Carrickfergus', 385: 'Derry',
    303: 'Kildare', 9297: 'Worcester', 6384: 'Chester', 9315: 'Pontefract', 9379: 'York',
    9458: 'Winchester', 311: 'Rhuddlan', 540: 'Exeter',
    # Scandinavia
    11151: 'Sarpsborg', 9279: 'Lund', 11215: 'Ronneby', 383: 'Lödöse', 6050: 'Sigtuna',
    9127: 'Borgund', 11380: 'Skänninge', 6310: 'Kungahälla', 11114: 'Tingvalla',
    3136: 'Hamar', 9296: 'Lister', 399: 'Ribe',
}

# state id -> 1187 region name
REGIONS = {
    # Middle East
    455: 'Oultrejordain', 446: 'Eastern Delta', 456: 'Upper Egypt', 680: 'Jazira',
    1010: 'Anbar', 1011: 'Basra', 656: 'Kazima', 658: 'Oman Coast', 859: 'Qatif',
    1014: 'Awal', 266: 'Rayy', 419: 'Urmiya', 1000: 'Azerbaijan', 799: 'Antioch',
    # Anatolia
    797: 'Constantinople', 49: 'Galatia', 339: 'Smyrna', 340: 'Bithynia',
    341: 'Adrianople', 342: 'Pamphylia', 343: 'Phrygia', 344: 'Melitene', 345: 'Cilicia',
    346: 'Iconium', 347: 'Nicomedia', 348: 'Cappadocia', 349: 'Sebasteia',
    350: 'Diyar Bakr', 353: 'Dersim', 354: 'Trebizond', 355: 'Amisos',
    356: 'Paphlagonia', 800: 'Vaspurakan',
    # Caucasus
    229: 'Shirvan', 233: 'Zichia', 234: 'Kuban', 235: 'Majar', 236: 'Saqsin',
    237: 'Caspian Steppe', 238: 'Manych', 821: 'Durdzuketi', 827: 'Kabarda', 828: 'Alania',
    # Rus' and the steppe
    195: 'Ingria', 217: 'Lower Volga', 218: 'Azov Steppe', 226: 'Lower Dnieper',
    227: 'Donets Steppe', 228: 'Polovtsian Steppe', 200: 'Dnieper Rapids', 192: 'Khadjibey',
    221: 'Upper Donets', 222: 'Mtsensk', 225: 'Putivl', 244: 'Ladoga', 245: 'Don Steppe',
    247: 'Tver', 249: 'Volga Bulgaria', 250: 'Suvar', 251: 'Samara Bend', 252: 'Gorodets',
    253: 'Suzdal', 255: 'Burtas', 257: 'Meshchera', 265: 'Medveditsa', 239: 'Uvek',
    829: 'Volga Steppe', 198: 'Bratslav', 199: 'Podolia', 203: 'Kaniv',
    # Urals and Central Asia
    397: 'Komi', 400: 'Vyatka', 401: 'Irgiz', 406: 'Saraychik', 407: 'Yaik', 572: 'Iset',
    573: 'Southern Urals', 582: 'Yaik Steppe', 584: 'Nisa', 652: 'Kipchak Steppe',
    653: 'Yugra', 823: 'Aral', 832: 'Gurganj', 833: 'Cheremis', 880: 'Ustyug',
    # Central Europe
    126: 'Middlesex', 5: 'Prussia', 763: 'Sambia', 188: 'Lamata', 807: 'Pomerelia',
    762: 'Bytom', 87: 'Łęczyca', 89: 'Halych', 91: 'Zvenyhorod', 68: 'Lebus',
    63: 'Pomerania', 72: 'Cieszyn', 74: 'Opava', 69: 'Northern Bohemia',
    972: 'Southern Moravia', 73: 'Ung', 70: 'Nyitra', 71: 'Sáros', 664: 'Abaúj',
    45: 'Bács', 102: 'Styrian March',
}


def main():
    lines = ['l_english:']
    for prov, name in sorted(CITIES.items()):
        lines.append(f' VICTORY_POINTS_{prov}:0 "{name}"')
    for sid, name in sorted(REGIONS.items()):
        lines.append(f' STATE_{sid}:0 "{name}"')
    path = os.path.join(ROOT, 'localisation/english/replace/dv_place_names_l_english.yml')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8-sig', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', len(CITIES), 'cities and', len(REGIONS), 'regions')


if __name__ == '__main__':
    main()

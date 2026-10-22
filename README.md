# Deus Vult

A Hearts of Iron IV mod set during the Third Crusade (1187 to 1192). Jerusalem has fallen to Saladin, and England, France and the Holy Roman Empire take the cross.

## Scope
- Start date 1187, covering Europe, North Africa and the Middle East
- About 15 to 20 playable nations: Kingdom of Jerusalem, Ayyubid Sultanate, England, France, Holy Roman Empire, Byzantine Empire, Sultanate of Rum, County of Tripoli, Principality of Antioch, Kingdom of Sicily, Armenian Cilicia, and others
- Ideologies replaced by religions (Catholic, Orthodox, Sunni, Shia)
- Vanilla units reworked as men-at-arms, knights, archers and siege engines

## Install for testing
Clone this repo straight into the mod folder as `deus_vult` and copy `launcher/deus_vult.mod` next to it (edit its `path` if your Documents folder is elsewhere).

Or manually:
Copy this folder (as `deus_vult/`) and `launcher/deus_vult.mod` into
`Documents/Paradox Interactive/Hearts of Iron IV/mod/`, then enable "Deus Vult" in a playset in the launcher.

## What's in 0.2.0: the 1187 map
- Start date 4 July 1187 (the Battle of Hattin), set in `common/defines/dv_defines.lua`, with a "The Third Crusade" bookmark
- 88 new country tags. All 1,081 vanilla states are given an 1187 owner, so no vanilla country exists at the start
- Detailed realms around the Mediterranean, Europe, the steppe and the Middle East (Jerusalem, Tripoli, Antioch, the Ayyubids, Byzantium, Rum, Angevin England, France, the Holy Roman Empire, Sicily, the Iberian kingdoms, the Almohads, the Rus principalities, Georgia, the Abbasids and others)
- Broad placeholder realms elsewhere (Song, Jin, Khmer, North American Peoples and so on)
- Each country gets a religion as a national spirit (Catholic, Orthodox, Sunni, Shia, Old Gods, Tengrism, Eastern Faiths, Native Faiths). This stands in until religions replace ideologies
- Simple generated placeholder flags for every tag
- Saladin claims Jerusalem, Tripoli and Antioch. France claims the Angevin lands in France

Not done yet: events, proper flags and leader portraits.

## What's in 0.3.0: armies
- Units are renamed for the period: infantry is now **Men-at-Arms**, cavalry is **Knights** and towed artillery is **Siege Engines** (the Trebuchet). Equipment is now **Arms and Armour**. These overrides live in `localisation/english/replace/`
- A new **Archers** sub-unit (`common/units/dv_archers.txt`) hits harder but is more fragile than men-at-arms
- Every nation has a starting army at its capital (`history/units/TAG_1187.txt`), 288 divisions in all:
  - Catholic and Orthodox realms field a *Feudal Host* (men-at-arms, archers, knights) plus *Knights* brigades
  - Muslim and Eastern realms field an *Askar* (more cavalry and archers) plus *Heavy Cavalry*
  - Steppe peoples field a *Horde* (mostly cavalry and archers)
  - Tribes and the placeholder realms field a *Warband*
  - The biggest powers (the Ayyubids, the HRE, Angevin England, France, Byzantium, the Almohads, Sicily, Venice, Jin and Song) also start with a *Siege Train*
- Settled realms start with the siege engine tech, so they can build trebuchets

## What's in 0.4.0: icons and the opening war
- Medieval unit icons replace the WW2 ones: a nasal helm for men-at-arms, a mounted knight with a lance, a trebuchet for siege engines, a bow for archers, and sword-and-shield and trebuchet pictures for the equipment. `tools/draw_icons.py` draws them, and `interface/dv_units.gfx` registers the archer sprite
- The game opens at war, as it was in July 1187: the Ayyubids against the Crusader States faction (Jerusalem, Tripoli and Antioch)
- The 3D models on the map are still vanilla. Turn on "show units as counters" in the game settings to see the medieval icons on the map instead

## What's in 0.5.0: focus trees and religion
- **Religions now have effects.** Each faith's national spirit gives small bonuses: Catholic and Orthodox give stability, Sunni gives morale, Tengrism gives army speed, the Old Gods give defence, and so on
- **Opinions between faiths** are set at game start: +25 for the same faith, -15 between Catholic and Orthodox or Sunni and Shia, and -40 between Christians and Muslims
- **Holy War decisions.** Catholic realms can *Take the Cross* (50 political power): they join the Crusader States, go to war with Saladin and gain the Crusader Vow. Muslim realms can *Answer the Jihad* and join the new Ayyubid Alliance
- **Faith decisions.** Pagan and Tengri peoples can convert to Catholicism, Orthodoxy or Sunni Islam
- **Jerusalem focus tree (14 focuses):** Hattin, Hold Tyre, the Military Orders, Turcopoles, siege engines and Reclaim Jerusalem. *The Third Crusade* (which pulls AI-ruled England, France and the HRE into the war) and *Peace with Saladin* exclude each other. The internal branch ends in *The Kingdom Endures*
- **Ayyubid focus tree (12 focuses):** Mamluk Regiments, Victory at Hattin, Take Jerusalem, Sweep the Coast and *Saladin Takes the Field* (Saladin as a field marshal). *Proclaim the Jihad* (pulls in the Artuqids and the Abbasids) and the *Treaty of Ramla* exclude each other. The internal branch ends in *Sultan of Egypt and Syria*
- `tools/gen_content.py` writes all of this

## What's in 0.6.0: medieval buildings
- The 1936 buildings are replaced on every state:
  - Air bases, radar, rocket sites, reactors, refineries and landmarks are removed
  - Factories are cut back to what a 12th-century realm could support. Each capital has a Market Town and an Armoury, and the great powers (Ayyubids, HRE, England, France, Byzantium, Almohads, Sicily and others) get 3 and 2. Large cities in the theatre get a Market Town
  - Every state in the theatre with a city has a **Castle** (land fort level 2). Capitals get level 3, and the famous strongholds get level 4: Kerak, Krak des Chevaliers, Antioch and Constantinople. Jerusalem, Cairo, Damascus and Aleppo get level 3
  - Shipyards exist only in Venice, Pisa, Constantinople, Sicily and Alexandria. Naval bases are capped at level 3
- Building names are replaced (`localisation/english/replace/dv_buildings_l_english.yml`): Civilian Factory → Market Town, Military Factory → Armoury, Infrastructure → Roads, Land Fort → Castle, Naval Base → Harbour, Dockyard → Shipyard, Coastal Fort → Sea Walls, Supply Hub → Waystation, Railways → Royal Roads
- `gen.py` writes the buildings (see `medieval_buildings()`)

## Focus trees for the other powers
- **England (20 focuses):** the Saladin Tithe, Take the Cross, Richard the Lionheart as a field marshal, the conquest of Cyprus and the Siege of Acre. *Hold the Angevin Empire* or *Crush the Capetians* in France, then Chateau Gaillard. Ireland, Wales, and a choice between enforcing the Treaty of Falaise on Scotland or selling it back
- **France (16):** Take the Cross, then either *Return to France* (white peace with Saladin, leave the crusade, claim Normandy) or *Stay the Course*. Court Henry's rebellious sons, claim the Angevin lands and march to Bouvines. The Walls of Paris, the Louvre, the University and *Rex Franciae*
- **Holy Roman Empire (17):** the Diet of Christ, Take the Cross (Barbarossa as a field marshal), passage through Hungary, *Bargain with Isaac* or *Force the Passage* through Byzantium, the Storm of Iconium and the Teutonic Order. The Sicilian Marriage leads to a war for the crown of Sicily. Ostsiedlung and the Free Imperial Cities
- **Byzantium (17):** *Pact with Saladin* or *Aid the Crusaders*, recover Cyprus, favour Venice or Pisa. Crush the Vlach rebellion in Bulgaria, bring Serbia to heel, reconquer Anatolia from Rum. The Theodosian Walls and *Basileia ton Rhomaion*
- **Sicily (11), the Papacy (9) and Rum (12)** have shorter trees. The Pope can *Preach the Crusade*, which pulls AI-ruled England, France, the HRE, Sicily and Hungary into the war
- **Every other nation** gets a medieval tree instead of the 1936 generic one: levies, knights, archers, siege engines, markets, roads, armouries and castles, plus a faith branch that only shows for its own religion (Take the Cross for Catholics, Answer the Jihad for Muslims, Defenders of Orthodoxy, or the Old Ways)
- The *Take the Cross* focuses do the same as the decision and complete on their own if the country already swore the vow
- `tools/gen_focus.py` writes all of this

## Regenerating the map
`tools/` holds the Python scripts that built the country and state files from the vanilla game files.
`nations.py` lists every tag with its name, colour, capital, religion, leader and states. `assign.py` assigns the remaining states by region, `gen.py` writes the mod files, and `gen_army.py` writes the starting armies (run it before `gen.py`, which reads its `army_summary.json` to link each country to its army). To move a state to a different owner, edit `nations.py`, then rerun `assign.py` and `gen.py`.
The scripts expect the vanilla files (unpacked into `v/`) and a `states.tsv` of state centroids made by `cent.py`.

## Layout
| Folder | Holds |
| --- | --- |
| `common/country_tags`, `common/countries` | Nation definitions |
| `common/bookmarks`, `common/defines` | 1187 start date and bookmark |
| `common/ideas` | Religion national spirits |
| `common/ideologies` | Religions (replacing ideologies) |
| `common/national_focus` | Focus trees |
| `common/decisions` | Decisions such as taking the cross |
| `events` | Event chains |
| `history/countries`, `history/states` | 1187 starting setup and map ownership |
| `localisation/english` | All in-game text (UTF-8 with BOM) |
| `gfx/flags`, `gfx/interface/goals` | Flags and focus icons |

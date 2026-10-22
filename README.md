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

Not done yet: focus trees, events, religion mechanics, proper flags and leader portraits. Vanilla buildings and resources are still on every state.

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

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

## Layout
| Folder | Holds |
| --- | --- |
| `common/country_tags`, `common/countries` | Nation definitions |
| `common/ideologies` | Religions (replacing ideologies) |
| `common/national_focus` | Focus trees |
| `common/decisions` | Decisions such as taking the cross |
| `events` | Event chains |
| `history/countries`, `history/states` | 1187 starting setup and map ownership |
| `localisation/english` | All in-game text (UTF-8 with BOM) |
| `gfx/flags`, `gfx/interface/goals` | Flags and focus icons |

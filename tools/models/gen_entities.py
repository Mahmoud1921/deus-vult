"""Wire the Deus Vult unit models into the game.

    python gen_entities.py <HoI4 install dir> <mod dir>

Writes gfx/entities/dv_units.gfx (mesh definitions) and overrides the vanilla
units_infantry.asset, units_cavalry.asset and units_artillery.asset: they keep every
vanilla entity except the ones the 1187 nations use, which become medieval.
The game looks up "<graphical culture>_<sprite>_entity" first, then "<sprite>_entity".
"""
import os
import re
import sys

GAME, MOD = sys.argv[1:3]
VAN = os.path.join(GAME, "gfx/entities")
OUT = os.path.join(MOD, "gfx/entities")
os.makedirs(OUT, exist_ok=True)

# culture: (foot soldier, archer, rider, rider's weapon)
CULTURES = {
    "": ("footman_west", "archer_levy", "knight_west", "lance"),
    "western_european_gfx": ("footman_west", "archer_levy", "knight_west", "lance"),
    "eastern_european_gfx": ("footman_east", "archer_levy", "knight_east", "lance"),
    "middle_eastern_gfx": ("saracen_saracen", "archer_saracen", "saracen_saracen", "spear"),
    "african_gfx": ("saracen_africa", "archer_saracen", "saracen_africa", "spear"),
    "asian_gfx": ("archer_asia", "archer_asia", "archer_asia", "bow"),
    "southamerican_gfx": ("archer_americas", "archer_americas", "archer_americas", "spear"),
}
BODIES = sorted({m for c in CULTURES.values() for m in c[:3]})


def read(name):
    with open(os.path.join(VAN, name), encoding="utf-8-sig") as f:
        return f.read()


def blocks(text):
    """Yield (start, end, body) for each top-level `entity = { ... }` block."""
    i, depth, start = 0, 0, None
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "#":
            i = text.find("\n", i)
            if i < 0:
                break
            continue
        if ch == '"':
            i = text.find('"', i + 1) + 1
            continue
        if ch == "{":
            if depth == 0:
                m = re.search(r"entity\s*=\s*$", text[max(0, i - 40):i])
                start = i - (len(m.group(0)) if m else 0) if m else None
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                yield start, i + 1, text[start:i + 1]
                start = None
        i += 1


def name_of(block):
    m = re.search(r'\bname\s*=\s*"([^"]+)"', block)
    return m.group(1) if m else None


def find(text, name):
    return next(b for _, _, b in blocks(text) if name_of(b) == name)


def strip_attaches(block):
    return "\n".join(ln for ln in block.split("\n") if not re.match(r"\s*attach\s*=", ln))


def retarget(block, name, mesh, attaches, scale=None):
    block = strip_attaches(block)
    block = re.sub(r'\bname\s*=\s*"[^"]+"', 'name = "%s"' % name, block, count=1)
    block = re.sub(r'\bpdxmesh\s*=\s*"[^"]+"', 'pdxmesh = "%s"' % mesh, block, count=1)
    # no cigarettes in 1187
    block = re.sub(r"propagate_state\s*=\s*\{\s*lighter\s*=\s*\"smoke\"\s*\}", "", block)
    block = re.sub(r"\n\s*event\s*=\s*\{[^\n]*cigarette[^\n]*\}", "", block)
    lines = "".join("\tattach = { name = \"%s\" %s = \"%s\" }\n" % a for a in attaches)
    block = block.rstrip()[:-1].rstrip() + "\n\n" + lines + "}"
    if scale is not None:
        block = re.sub(r"\bscale\s*=\s*[\d.]+", "scale = %s" % scale, block)
    return block


def weapon_attaches(weapon):
    w = "dv_%s_entity" % weapon
    return [("rifle1", "Right_Hand_node", w), ("rifle2", "Left_Hand_node", w), ("rifle3", "mid_back_node", w)]


def override(fname, new_blocks):
    """Vanilla file minus the entities we replace, with ours first so vanilla clones still resolve."""
    text = read(fname)
    names = {name_of(b) for b in new_blocks}
    keep, last = [], 0
    for s, e, b in blocks(text):
        if name_of(b) in names:
            keep.append(text[last:s])
            last = e
    keep.append(text[last:])
    head = "# Deus Vult: medieval unit entities (tools/models/gen_entities.py). Vanilla entities follow.\n\n"
    with open(os.path.join(OUT, fname), "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(head + "\n\n".join(new_blocks) + "\n\n" + "".join(keep))


def main():
    inf = read("units_infantry.asset")
    cav = read("units_cavalry.asset")
    art = read("units_artillery.asset")
    soldier = find(inf, "infantry_rifle_entity")
    rider = find(cav, "infantry_rider_entity")
    combined = find(cav, "generic_cavalry_rifle_combined_entity")
    frame = find(cav, "cavalry_entity")
    gun_frame = find(art, "artillery_entity")

    inf_new = [
        'entity = {\n\tname = "dv_%s_entity"\n\tpdxmesh = "dv_%s_mesh"\n\tscale = 1.0\n}' % (w, w)
        for w in ("spear", "bow", "lance")
    ]
    cav_new, art_new = [], []
    art_new.append(
        'entity = {\n\tname = "dv_trebuchet_entity"\n\tpdxmesh = "dv_trebuchet_mesh"\n\tdefault_state = "idle"\n'
        + "".join('\tstate = { name = "%s" }\n' % s for s in
                  ("idle", "move", "attack", "defend", "support_attack", "retreat", "training", "death"))
        + "\tscale = 0.75\n}")
    for culture, (foot, archer, horseman, weapon) in CULTURES.items():
        p = culture + "_" if culture else ""
        inf_new.append(retarget(soldier, p + "infantry_entity", "dv_%s_mesh" % foot, weapon_attaches("spear")))
        inf_new.append(retarget(soldier, p + "dv_archers_entity", "dv_%s_mesh" % archer, weapon_attaches("bow")))
        rider_name = p + "dv_rider_entity"
        cav_new.append(retarget(rider, rider_name, "dv_%s_mesh" % horseman, weapon_attaches(weapon)))
        cav_new.append(retarget(combined, p + "dv_cavalry_combined_entity", "infantry_cavalry_horse_mesh",
                                [("infantry_unit", "Saddle_Node", rider_name)]))
        cav_new.append(retarget(frame, p + "cavalry_entity", "infantry_cavalry_horse_frame_mesh", [
            ("infantry", "infantry", rider_name),
            ("cavalry", "cavalry", p + "dv_cavalry_combined_entity"),
            ("horse", "horse", "infantry_cavalry_horse_entity"),
        ]))
        art_new.append(retarget(gun_frame, p + "artillery_entity", "frame_artillery_mesh", [
            ("artillery", "artillery", "dv_trebuchet_entity"),
            ("infantry", "infantry", p + "infantry_entity"),
        ]))
    override("units_infantry.asset", inf_new)
    override("units_cavalry.asset", cav_new)
    override("units_artillery.asset", art_new)

    # mesh definitions: soldiers reuse the vanilla rifleman's animation set
    gfx = read("infantry.gfx")
    m = re.search(r'pdxmesh\s*=\s*\{\s*name\s*=\s*"generic_western_european_rifle_infantry_mesh".*?\n\t\}', gfx, re.S)
    anims = "\n".join(ln for ln in m.group(0).split("\n") if "animation" in ln)
    out = ["objectTypes = {"]
    for body in BODIES:
        out.append('\tpdxmesh = {\n\t\tname = "dv_%s_mesh"\n\t\tfile = "gfx/models/units/dv/dv_%s.mesh"\n%s\n\t}'
                   % (body, body, anims))
    for static in ("spear", "bow", "lance", "trebuchet"):
        out.append('\tpdxmesh = {\n\t\tname = "dv_%s_mesh"\n\t\tfile = "gfx/models/units/dv/dv_%s.mesh"\n\t}'
                   % (static, static))
    out.append("}")
    with open(os.path.join(OUT, "dv_units.gfx"), "w", encoding="utf-8-sig", newline="\n") as f:
        f.write("\n\n".join(out) + "\n")


main()

"""Build the Deus Vult 3D unit models.

Run with the `bpy` Python module (pip install bpy==4.2.*) and the io_pdx_mesh
exporter (https://github.com/ross-g/io_pdx_mesh):

    python build_models.py <io_pdx_mesh parent dir> <HoI4 install dir> <mod dir>

Every model is original geometry. The soldiers are skinned to the vanilla infantry
skeleton (read from the game install, not shipped), so they play the vanilla walk,
fight and ride animations. Weapons are static meshes held at the skeleton's hand
nodes. Each model is unwrapped and its textures are baked in Cycles from procedural
materials (chainmail, cloth weave, wood grain, leather, steel), with ambient
occlusion painted into the diffuse map the way the vanilla textures are.
Output goes to <mod>/gfx/models/units/dv/.
"""
import io
import math
import os
import struct
import sys

import bpy  # noqa: I001  (bpy must load before bmesh and mathutils)
import bmesh
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from PIL import Image

EXT, GAME, MOD = sys.argv[-3:]
sys.path.insert(0, EXT)
from io_pdx_mesh.pdx_blender import blender_import_export as bie  # noqa: E402

OUT = os.path.join(MOD, "gfx/models/units/dv")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- materials
# Every face carries one of these material kinds. A palette gives each kind its
# colour for one culture; the kind decides the surface pattern.
(SKIN, MAIL, STEEL, SURCOAT, EMBLEM, LEATHER, WOOD, FIELD, CHARGE, TUNIC, HOSE, TURBAN, HAIR, DARK, GOLD,
 WHITE, QUILT, LIP) = range(18)
KINDS = 18

PALETTES = {
    # Latin Christendom: white surcoat with a red cross, red kite shield
    "west": {SKIN: (206, 160, 128), MAIL: (150, 154, 160), STEEL: (178, 182, 188), SURCOAT: (224, 216, 194),
             EMBLEM: (164, 26, 28), LEATHER: (98, 64, 38), WOOD: (126, 92, 56), FIELD: (164, 30, 32),
             CHARGE: (214, 176, 64), TUNIC: (150, 120, 80), HOSE: (82, 70, 56), TURBAN: (230, 226, 210),
             HAIR: (78, 54, 34), DARK: (26, 24, 24), GOLD: (200, 160, 70), WHITE: (232, 230, 222),
             QUILT: (168, 140, 98), LIP: (150, 96, 84)},
    # Orthodox realms: crimson surcoat with a gold cross, blue shield
    "east": {SKIN: (204, 158, 124), MAIL: (146, 148, 152), STEEL: (174, 176, 180), SURCOAT: (132, 24, 34),
             EMBLEM: (214, 174, 66), LEATHER: (90, 60, 36), WOOD: (120, 86, 52), FIELD: (38, 60, 124),
             CHARGE: (214, 176, 64), TUNIC: (120, 40, 44), HOSE: (66, 58, 50), TURBAN: (226, 222, 206),
             HAIR: (58, 40, 28), DARK: (26, 24, 24), GOLD: (206, 166, 62), WHITE: (232, 230, 222),
             QUILT: (160, 132, 92), LIP: (146, 92, 80)},
    # Islamic realms: white turban, green kaftan, red and white round shield
    "saracen": {SKIN: (176, 128, 92), MAIL: (146, 148, 152), STEEL: (184, 184, 186), SURCOAT: (44, 98, 62),
                EMBLEM: (214, 176, 66), LEATHER: (100, 66, 38), WOOD: (128, 94, 58), FIELD: (168, 32, 32),
                CHARGE: (230, 224, 208), TUNIC: (44, 102, 66), HOSE: (186, 170, 134), TURBAN: (236, 232, 220),
                HAIR: (34, 26, 22), DARK: (26, 24, 24), GOLD: (206, 166, 62), WHITE: (236, 234, 226),
                QUILT: (44, 102, 66), LIP: (130, 84, 70)},
    # Africa: white robes, ochre shield
    "africa": {SKIN: (112, 76, 52), MAIL: (146, 148, 152), STEEL: (176, 176, 178), SURCOAT: (228, 220, 200),
               EMBLEM: (170, 116, 40), LEATHER: (100, 66, 38), WOOD: (128, 94, 58), FIELD: (190, 130, 52),
               CHARGE: (60, 40, 28), TUNIC: (226, 218, 196), HOSE: (196, 180, 146), TURBAN: (236, 232, 220),
               HAIR: (28, 22, 20), DARK: (24, 22, 22), GOLD: (206, 166, 62), WHITE: (236, 234, 226),
               QUILT: (226, 218, 196), LIP: (92, 60, 50)},
    # Plain soldiers in quilted gambesons
    "levy": {SKIN: (204, 158, 126), MAIL: (146, 148, 152), STEEL: (158, 160, 164), SURCOAT: (150, 120, 80),
             EMBLEM: (164, 26, 28), LEATHER: (96, 62, 36), WOOD: (126, 92, 56), FIELD: (90, 110, 60),
             CHARGE: (214, 176, 64), TUNIC: (164, 138, 96), HOSE: (82, 92, 60), TURBAN: (226, 222, 206),
             HAIR: (82, 56, 36), DARK: (26, 24, 24), GOLD: (200, 160, 70), WHITE: (232, 230, 222),
             QUILT: (176, 150, 106), LIP: (150, 96, 84)},
    # East Asia: red lacquered armour and dark helmets
    "asia": {SKIN: (208, 170, 130), MAIL: (70, 64, 60), STEEL: (74, 70, 68), SURCOAT: (146, 32, 28),
             EMBLEM: (206, 166, 62), LEATHER: (72, 48, 30), WOOD: (112, 76, 46), FIELD: (146, 32, 28),
             CHARGE: (206, 166, 62), TUNIC: (146, 32, 28), HOSE: (44, 42, 44), TURBAN: (44, 42, 44),
             HAIR: (24, 20, 20), DARK: (20, 18, 18), GOLD: (206, 166, 62), WHITE: (230, 226, 214),
             QUILT: (146, 32, 28), LIP: (150, 96, 84)},
    # The Americas: undyed cotton armour and bright colours
    "americas": {SKIN: (160, 106, 72), MAIL: (210, 196, 160), STEEL: (190, 166, 108), SURCOAT: (210, 196, 160),
                 EMBLEM: (40, 118, 118), LEATHER: (112, 76, 46), WOOD: (128, 94, 58), FIELD: (40, 118, 118),
                 CHARGE: (206, 58, 40), TUNIC: (214, 200, 162), HOSE: (160, 106, 72), TURBAN: (40, 118, 118),
                 HAIR: (24, 20, 20), DARK: (20, 18, 18), GOLD: (206, 166, 62), WHITE: (232, 226, 210),
                 QUILT: (214, 200, 162), LIP: (120, 72, 60)},
}

# polished metal reads too bright once the spec map adds its highlight
for _pal in PALETTES.values():
    for _k in (MAIL, STEEL):
        _pal[_k] = tuple(int(x * 0.78) for x in _pal[_k])

# (pattern, specular intensity 0-1, gloss 0-1)
SURFACE = {
    SKIN: ("skin", 0.12, 0.25), MAIL: ("mail", 0.75, 0.55), STEEL: ("steel", 0.85, 0.7),
    SURCOAT: ("cloth", 0.06, 0.15), EMBLEM: ("cloth", 0.06, 0.15), LEATHER: ("leather", 0.2, 0.35),
    WOOD: ("wood", 0.1, 0.2), FIELD: ("paint", 0.25, 0.4), CHARGE: ("paint", 0.25, 0.4),
    TUNIC: ("cloth", 0.06, 0.15), HOSE: ("cloth", 0.06, 0.15), TURBAN: ("wrap", 0.06, 0.15),
    HAIR: ("hair", 0.1, 0.2), DARK: ("plain", 0.05, 0.1), GOLD: ("steel", 0.9, 0.7),
    WHITE: ("plain", 0.05, 0.1), QUILT: ("quilt", 0.06, 0.15), LIP: ("skin", 0.12, 0.25),
}


def lin(c):
    """sRGB 0-255 to linear 0-1."""
    out = []
    for x in c:
        x /= 255.0
        out.append(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def make_material(kind):
    """Procedural Cycles material: base colour pattern, bump, and an emission input for the spec bake."""
    pattern, spec, gloss = SURFACE[kind]
    mat = bpy.data.materials.new("k%d" % kind)
    mat.use_nodes = True
    nt = mat.node_tree
    N, L = nt.nodes, nt.links
    bsdf = N["Principled BSDF"]
    coord = N.new("ShaderNodeTexCoord")
    base = N.new("ShaderNodeRGB")
    base.name = "base"
    col = base.outputs[0]
    height = None

    def noise(scale, detail=4.0, vec=None):
        n = N.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        L.new(vec or coord.outputs["Object"], n.inputs["Vector"])
        return n.outputs["Fac"]

    def mix(a, b, fac, mode="MULTIPLY", f=None):
        m = N.new("ShaderNodeMix")
        m.data_type = "RGBA"
        m.blend_type = mode
        if f is not None:
            m.inputs["Factor"].default_value = f
        else:
            L.new(fac, m.inputs["Factor"])
        L.new(a, m.inputs[6])
        if isinstance(b, tuple):
            m.inputs[7].default_value = b
        else:
            L.new(b, m.inputs[7])
        return m.outputs[2]

    def ramp(src, stops):
        r = N.new("ShaderNodeValToRGB")
        r.color_ramp.elements[0].position, r.color_ramp.elements[0].color = stops[0]
        r.color_ramp.elements[1].position, r.color_ramp.elements[1].color = stops[-1]
        for pos, c in stops[1:-1]:
            e = r.color_ramp.elements.new(pos)
            e.color = c
        L.new(src, r.inputs[0])
        return r.outputs[0]

    def scaled(sx, sy, sz):
        m = N.new("ShaderNodeMapping")
        m.inputs["Scale"].default_value = (sx, sy, sz)
        L.new(coord.outputs["Object"], m.inputs["Vector"])
        return m.outputs[0]

    if pattern == "mail":
        v = N.new("ShaderNodeTexVoronoi")
        v.feature = "F1"
        v.inputs["Scale"].default_value = 20.0
        L.new(scaled(1.0, 1.0, 1.6), v.inputs["Vector"])
        # rings: bright metal at mid distance, dark gaps at the centre and between rings
        ring = ramp(v.outputs["Distance"], [(0.0, (0.45, 0.45, 0.45, 1)), (0.18, (1, 1, 1, 1)),
                                            (0.32, (0.9, 0.9, 0.9, 1)), (0.46, (0.5, 0.5, 0.5, 1))])
        col = mix(col, ring, None, f=0.85)
        rust = ramp(noise(3.0), [(0.45, (1, 1, 1, 1)), (0.7, (0.75, 0.6, 0.48, 1))])
        col = mix(col, rust, None, f=0.6)
        height = ring
    elif pattern == "steel":
        scratch = ramp(noise(40.0, 2.0, scaled(1.0, 1.0, 12.0)), [(0.4, (0.82, 0.82, 0.82, 1)), (0.6, (1.08, 1.08, 1.08, 1))])
        col = mix(col, scratch, None, f=0.6)
        grime = ramp(noise(2.5), [(0.4, (1, 1, 1, 1)), (0.75, (0.62, 0.58, 0.52, 1))])
        col = mix(col, grime, None, f=0.7)
        height = noise(30.0, 2.0)
    elif pattern in ("cloth", "wrap", "quilt"):
        weave_a = N.new("ShaderNodeTexWave")
        weave_a.inputs["Scale"].default_value = 60.0
        weave_a.bands_direction = "X"
        L.new(coord.outputs["Object"], weave_a.inputs["Vector"])
        weave_b = N.new("ShaderNodeTexWave")
        weave_b.inputs["Scale"].default_value = 60.0
        weave_b.bands_direction = "Z"
        L.new(coord.outputs["Object"], weave_b.inputs["Vector"])
        weave = mix(weave_a.outputs["Color"], weave_b.outputs["Color"], None, mode="MULTIPLY", f=1.0)
        weave = ramp(weave, [(0.0, (0.88, 0.88, 0.88, 1)), (1.0, (1.05, 1.05, 1.05, 1))])
        col = mix(col, weave, None, f=0.5)
        # stretched noise reads as folds that hang downward
        folds = noise(4.0, 3.0, scaled(3.0, 3.0, 0.35))
        fold_shade = ramp(folds, [(0.3, (0.7, 0.7, 0.7, 1)), (0.7, (1.1, 1.1, 1.1, 1))])
        col = mix(col, fold_shade, None, f=0.8)
        height = folds
        if pattern == "wrap":
            bands = N.new("ShaderNodeTexWave")
            bands.inputs["Scale"].default_value = 7.0
            bands.bands_direction = "Z"
            bands.inputs["Distortion"].default_value = 3.0
            L.new(coord.outputs["Object"], bands.inputs["Vector"])
            col = mix(col, ramp(bands.outputs["Fac"], [(0.0, (0.7, 0.7, 0.7, 1)), (0.5, (1.05, 1.05, 1.05, 1)),
                                                       (1.0, (0.7, 0.7, 0.7, 1))]), None, f=0.9)
            height = bands.outputs["Fac"]
        if pattern == "quilt":
            stitch = N.new("ShaderNodeTexWave")
            stitch.inputs["Scale"].default_value = 9.0
            stitch.bands_direction = "X"
            L.new(coord.outputs["Object"], stitch.inputs["Vector"])
            seams = ramp(stitch.outputs["Fac"], [(0.0, (0.6, 0.6, 0.6, 1)), (0.15, (1.05, 1.05, 1.05, 1)),
                                                 (0.85, (1.05, 1.05, 1.05, 1)), (1.0, (0.6, 0.6, 0.6, 1))])
            col = mix(col, seams, None, f=1.0)
            height = stitch.outputs["Fac"]
        # mud and wear toward the hem
        sep = N.new("ShaderNodeSeparateXYZ")
        L.new(coord.outputs["Object"], sep.inputs[0])
        height_above = N.new("ShaderNodeMapRange")
        height_above.inputs["From Min"].default_value = 0.5
        height_above.inputs["From Max"].default_value = 3.0
        L.new(sep.outputs["Z"], height_above.inputs["Value"])
        col = mix(col, ramp(height_above.outputs[0], [(0.0, (0.55, 0.47, 0.38, 1)), (1.0, (1, 1, 1, 1))]), None,
                  f=0.85)
    elif pattern == "leather":
        mott = ramp(noise(12.0, 6.0), [(0.3, (0.72, 0.72, 0.72, 1)), (0.7, (1.12, 1.12, 1.12, 1))])
        col = mix(col, mott, None, f=0.9)
        height = noise(25.0, 3.0)
    elif pattern == "wood":
        grain = N.new("ShaderNodeTexWave")
        grain.wave_type = "RINGS"
        grain.inputs["Scale"].default_value = 3.0
        grain.inputs["Distortion"].default_value = 6.0
        grain.inputs["Detail"].default_value = 3.0
        L.new(scaled(1.0, 0.15, 1.0), grain.inputs["Vector"])
        col = mix(col, ramp(grain.outputs["Fac"], [(0.0, (0.72, 0.72, 0.72, 1)), (1.0, (1.12, 1.12, 1.12, 1))]),
                  None, f=1.0)
        height = grain.outputs["Fac"]
    elif pattern == "paint":
        chipping = noise(9.0, 6.0)
        chips = ramp(chipping, [(0.62, (1, 1, 1, 1)), (0.68, (0.5, 0.38, 0.28, 1))])
        col = mix(col, chips, None, f=1.0)
        height = chipping
    elif pattern in ("skin", "hair"):
        blot = ramp(noise(14.0 if pattern == "skin" else 40.0, 4.0),
                    [(0.3, (0.9, 0.9, 0.9, 1)), (0.7, (1.06, 1.04, 1.03, 1))])
        col = mix(col, blot, None, f=0.7)
        height = noise(40.0, 2.0)

    L.new(col, bsdf.inputs["Base Color"])
    if height is not None:
        bump = N.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.35 if pattern != "mail" else 0.6
        bump.inputs["Distance"].default_value = 0.02
        L.new(height, bump.inputs["Height"])
        L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    em = N.new("ShaderNodeEmission")
    em.name = "spec"
    em.inputs["Color"].default_value = (spec, gloss, 0.0, 1.0)
    img = N.new("ShaderNodeTexImage")
    img.name = "bake"
    N.active = img
    return mat


def set_palette(mats, pal):
    for kind, mat in enumerate(mats):
        mat.node_tree.nodes["base"].outputs[0].default_value = lin(PALETTES[pal][kind])


# ---------------------------------------------------------------- DDS output
def dds_bytes(img, fmt):
    """DXT1/DXT5 DDS with a full mip chain."""
    levels = []
    im = img
    while True:
        buf = io.BytesIO()
        im.save(buf, "DDS", pixel_format=fmt)
        levels.append(buf.getvalue()[128:])
        if min(im.size) <= 4:
            break
        im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    w, h = img.size
    block = 8 if fmt == "DXT1" else 16
    hdr = struct.pack("<4s7I44s2I4s10I", b"DDS ", 124, 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000,
                      h, w, max(1, (w + 3) // 4) * max(1, (h + 3) // 4) * block, 0, len(levels), b"\0" * 44,
                      32, 0x4, fmt.encode(), 0, 0, 0, 0, 0, 0x1000 | 0x8 | 0x400000, 0, 0, 0, 0)
    return hdr + b"".join(levels)


def save_dds(path, arr, fmt):
    img = Image.fromarray(np.clip(arr * 255 + 0.5, 0, 255).astype(np.uint8), "RGBA")
    with open(path, "wb") as f:
        f.write(dds_bytes(img, fmt))


# ---------------------------------------------------------------- geometry kit
class Builder:
    """Collects parts into one bmesh. Each face carries a material kind; parts can be pinned to one bone."""

    def __init__(self):
        self.bm = bmesh.new()
        self.rigid = self.bm.verts.layers.int.new("rigid")  # 1 + index into self.bones, 0 = skinned
        self.bones = []

    def _finish(self, verts, faces, kind, bone, smooth):
        for f in faces:
            f.material_index = kind
            f.smooth = smooth
        if bone:
            if bone not in self.bones:
                self.bones.append(bone)
            for v in verts:
                if v.is_valid:
                    v[self.rigid] = self.bones.index(bone) + 1

    def loft(self, sections, kind, n=14, bone=None, smooth=True, caps=(True, True), wobble=None):
        """Loft rings through sections [(centre, rx, ry)]. rx runs across, ry along world Y where possible.
        wobble(i, theta) scales the radius for folds."""
        cs = [Vector(s[0]) for s in sections]
        rings = []
        for i, (c, rx, ry) in enumerate((Vector(s[0]), s[1], s[2]) for s in sections):
            a = (cs[min(i + 1, len(cs) - 1)] - cs[max(i - 1, 0)]).normalized()
            ref = Vector((0, 1, 0)) if abs(a.y) < 0.9 else Vector((0, 0, 1))
            u = a.cross(ref).normalized()
            w = a.cross(u).normalized()
            if w.y > 0 and abs(a.y) < 0.9:
                w = -w
            ring = []
            for k in range(n):
                t = 2 * math.pi * k / n
                f = wobble(i, t) if wobble else 1.0
                ring.append(self.bm.verts.new(c + u * math.cos(t) * rx * f + w * math.sin(t) * ry * f))
            rings.append(ring)
        faces = []
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(n):
                j = (k + 1) % n
                faces.append(self.bm.faces.new((r0[k], r0[j], r1[j], r1[k])))
        if caps[0] and sections[0][1] > 1e-4:
            faces.append(self.bm.faces.new(list(reversed(rings[0]))))
        if caps[1] and sections[-1][1] > 1e-4:
            faces.append(self.bm.faces.new(rings[-1]))
        self._finish([v for r in rings for v in r], faces, kind, bone, smooth)

    def tube(self, a, b, ra, rb, kind, n=10, bone=None, smooth=True, ya=None, yb=None, caps=True):
        self.loft([(a, ra, ra if ya is None else ya), (b, rb, rb if yb is None else yb)], kind, n=n, bone=bone,
                  smooth=smooth, caps=(caps, caps))

    def ellipsoid(self, c, r, kind, bone=None, segs=14, rings=8, zcut=None, ycut=None):
        """Ellipsoid at c. zcut keeps the part above that unit height (domes); ycut flattens the front below it."""
        c = Vector(c)
        grid = []
        for k in range(rings + 1):
            phi = math.pi * k / rings
            z = math.cos(phi)
            if zcut is not None and z < zcut:
                z = zcut
            s = math.sqrt(max(0.0, 1 - z * z))
            row = []
            for i in range(segs):
                t = 2 * math.pi * i / segs
                y = s * math.sin(t)
                if ycut is not None and y < ycut:
                    y = ycut
                row.append(self.bm.verts.new(c + Vector((r[0] * s * math.cos(t), r[1] * y, r[2] * z))))
            grid.append(row)
        faces = []
        for k in range(rings):
            for i in range(segs):
                j = (i + 1) % segs
                q = (grid[k][i], grid[k][j], grid[k + 1][j], grid[k + 1][i])
                if len({v.co.to_tuple(5) for v in q}) >= 3:
                    faces.append(self.bm.faces.new(tuple(reversed(q))))
        self._finish([v for row in grid for v in row], faces, kind, bone, True)

    def box(self, c, size, kind, bone=None, rot=None, bevel=0.0):
        c = Vector(c)
        m = rot or Matrix.Identity(3)
        hx, hy, hz = (s / 2 for s in size)
        vs = [self.bm.verts.new(c + m @ Vector((x, y, z))) for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]
        idx = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        faces = [self.bm.faces.new([vs[i] for i in q]) for q in idx]
        if bevel:
            res = bmesh.ops.bevel(self.bm, geom=vs + list({e for f in faces for e in f.edges}), offset=bevel,
                                  segments=1, affect="EDGES")
            faces = list({f for v in res["verts"] for f in v.link_faces})
            vs = list({v for f in faces for v in f.verts})
        self._finish([v for v in vs if v.is_valid], [f for f in faces if f.is_valid], kind, bone, False)

    def plate(self, outline, centre, normal, up, thick, kind, bone=None, bulge=0.0, rim=None):
        """Shield-like plate: 2D outline (x right, y up) at centre facing normal, with an optional rim."""
        centre, normal, up = Vector(centre), Vector(normal).normalized(), Vector(up).normalized()
        right = up.cross(normal).normalized()
        up = normal.cross(right).normalized()

        def place(x, y, off):
            bow = bulge * (1 - min(1.0, (x * x) / 0.55))
            return centre + right * x + up * y + normal * (off + bow)

        # fan from the middle so the bulge reads
        mid_f = self.bm.verts.new(place(0, sum(p[1] for p in outline) / len(outline), thick / 2))
        mid_b = self.bm.verts.new(place(0, sum(p[1] for p in outline) / len(outline), -thick / 2))
        front = [self.bm.verts.new(place(x, y, thick / 2)) for x, y in outline]
        back = [self.bm.verts.new(place(x, y, -thick / 2)) for x, y in outline]
        faces = []
        n = len(outline)
        for i in range(n):
            j = (i + 1) % n
            faces.append(self.bm.faces.new((mid_f, front[i], front[j])))
            faces.append(self.bm.faces.new((mid_b, back[j], back[i])))
            faces.append(self.bm.faces.new((front[j], front[i], back[i], back[j])))
        self._finish(front + back + [mid_f, mid_b], faces, kind, bone, False)
        if rim is not None:
            pts = [place(x, y, thick / 2) for x, y in outline]
            for i in range(n):
                self.tube(pts[i], pts[(i + 1) % n], 0.045, 0.045, rim, n=5, bone=bone)

    def to_object(self, name):
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts[:], dist=1e-5)
        bmesh.ops.dissolve_degenerate(self.bm, edges=self.bm.edges[:], dist=1e-5)
        bmesh.ops.triangulate(self.bm, faces=self.bm.faces[:])
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        me = bpy.data.meshes.new(name)
        self.bm.to_mesh(me)
        obj = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(obj)
        return obj


# ---------------------------------------------------------------- soldier bodies
# Joint positions of the vanilla infantry bind pose (Blender space: Z up, the soldier faces -Y).
J = {}


def side(p, s):
    return Vector((p[0] * s, p[1], p[2]))


def folds(count, depth, start=1):
    return lambda i, t: 1.0 + (depth * math.sin(count * t) * min(1.0, i / 2.0) if i >= start else 0.0)


def legs(b, kind, boot=LEATHER):
    for s in (1, -1):
        up, knee, ankle, toe = (side(J[k], s) for k in ("LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase"))
        calf = knee.lerp(ankle, 0.3) + Vector((0, 0.08, 0))
        b.loft([(up + Vector((s * -0.05, 0, 0.35)), 0.46, 0.44), (up.lerp(knee, 0.45), 0.42, 0.40),
                (knee, 0.31, 0.31), (calf, 0.33, 0.34), (ankle + Vector((0, 0.02, 0.45)), 0.23, 0.23)], kind)
        # boot shaft, then the foot
        b.loft([(ankle + Vector((0, 0.02, 0.85)), 0.27, 0.27), (ankle + Vector((0, 0.04, 0.2)), 0.26, 0.28)],
               boot, caps=(True, False))
        heel = Vector((ankle.x, 0.35, 0.22))
        b.loft([(heel, 0.24, 0.0), (heel.lerp(toe, 0.3) + Vector((0, 0, 0.06)), 0.25, 0.24),
                (Vector((toe.x * 0.97, -0.15, 0.13)), 0.2, 0.12), (Vector((toe.x * 0.96, -0.3, 0.1)), 0.04, 0.04)],
               boot, n=10)


def arms(b, kind, glove=LEATHER, cuff=None):
    for s in (1, -1):
        arm, elbow, roll, wrist, hand = (side(J[k], s) for k in ("LeftArm", "LeftForeArm", "LeftForeArmRoll",
                                                                  "LeftHand", "Left_Hand_node"))
        b.ellipsoid(arm + Vector((s * -0.05, 0, -0.02)), (0.38, 0.38, 0.36), kind, segs=12, rings=7)
        b.loft([(arm, 0.31, 0.31), (arm.lerp(elbow, 0.5), 0.29, 0.28), (elbow, 0.25, 0.25),
                (roll, 0.25, 0.24), (wrist + (wrist - roll).normalized() * 0.08, 0.2, 0.19)], kind)
        if cuff is not None:
            c0 = roll.lerp(wrist, 0.55)
            b.loft([(c0, 0.27, 0.26), (wrist + (wrist - roll).normalized() * 0.02, 0.26, 0.25)], cuff, n=12)
        d = (hand - wrist).normalized()
        b.ellipsoid(wrist.lerp(hand, 0.4), (0.19, 0.15, 0.26), glove, segs=10, rings=6)
        b.ellipsoid(wrist.lerp(hand, 0.35) + Vector((0, -0.14, 0)) + d * 0.05, (0.07, 0.07, 0.14), glove, segs=6,
                    rings=4)


def torso(b, kind, chest=1.0):
    b.loft([((0, 0.1, 3.75), 0.74, 0.52), ((0, 0.09, 4.35), 0.76, 0.54), ((0, 0.06, 5.05), 0.88 * chest, 0.62 * chest),
            ((0, 0.04, 5.6), 0.86, 0.58), ((0, 0.04, 5.95), 0.62, 0.46), ((0, 0.05, 6.1), 0.3, 0.27)], kind, n=16)
    b.loft([((0, 0.05, 6.0), 0.28, 0.26), ((0, 0.03, 6.5), 0.25, 0.24)], SKIN, n=10)


SKIRT = "@skirt"  # skirts hang from the hips and swing partly with the thighs, see skin_from()


def skirt(b, kind, hem, top=4.0, flare=1.0, slit=False, depth=0.07):
    secs = [((0, 0.1, top), 0.8, 0.57), ((0, 0.11, (top + hem) / 2), 0.9 * flare, 0.68 * flare),
            ((0, 0.12, hem), 1.05 * flare, 0.82 * flare)]
    b.loft(secs, kind, n=20, caps=(False, False), wobble=folds(7, depth), bone=SKIRT)


def overcoat(b, kind, hem, sleeveless=True):
    """A surcoat or kaftan worn over the torso: slightly larger, hanging to the hem."""
    b.loft([((0, 0.06, 5.75), 0.82, 0.58), ((0, 0.05, 5.1), 0.92, 0.65), ((0, 0.09, 4.4), 0.8, 0.57),
            ((0, 0.1, 4.0), 0.82, 0.59)], kind, n=16, caps=(True, False))
    skirt(b, kind, hem)


def belt(b, z=4.0, buckle=GOLD):
    b.loft([((0, 0.1, z - 0.1), 0.86, 0.62), ((0, 0.1, z + 0.1), 0.86, 0.62)], LEATHER, n=16, caps=(False, False))
    b.box((0, -0.53, z), (0.2, 0.06, 0.22), buckle, bevel=0.02)
    b.box((-0.62, -0.25, z - 0.25), (0.28, 0.16, 0.32), LEATHER, bone="Hip", bevel=0.03)  # pouch


def head(b, beard=False, hair=True):
    c = Vector((0, 0.02, 6.86))
    b.ellipsoid(c, (0.35, 0.39, 0.46), SKIN, segs=16, rings=10)
    b.ellipsoid((0, -0.13, 6.62), (0.25, 0.22, 0.17), SKIN, segs=10, rings=6)  # jaw
    b.loft([((0, -0.37, 6.95), 0.035, 0.03), ((0, -0.45, 6.78), 0.06, 0.07), ((0, -0.43, 6.73), 0.07, 0.05)], SKIN,
           n=8)  # nose
    for s in (1, -1):
        b.ellipsoid((s * 0.13, -0.33, 6.9), (0.055, 0.035, 0.03), WHITE, segs=8, rings=4)
        b.ellipsoid((s * 0.13, -0.355, 6.9), (0.025, 0.02, 0.025), DARK, segs=6, rings=4)
        b.box((s * 0.13, -0.355, 6.98), (0.15, 0.04, 0.035), HAIR, rot=Matrix.Rotation(s * -0.15, 3, "Y"))
        b.ellipsoid((s * 0.35, 0.05, 6.86), (0.05, 0.1, 0.13), SKIN, segs=8, rings=5)  # ears
    b.box((0, -0.335, 6.62), (0.15, 0.04, 0.03), LIP)
    if beard:
        b.ellipsoid((0, -0.2, 6.55), (0.29, 0.24, 0.2), HAIR, segs=12, rings=6)
        b.ellipsoid((0, -0.3, 6.68), (0.2, 0.08, 0.05), HAIR, segs=8, rings=4)  # moustache
    if hair:
        b.ellipsoid(c + Vector((0, 0.05, 0.05)), (0.37, 0.41, 0.45), HAIR, segs=14, rings=8, ycut=0.2)


def coif(b):
    b.ellipsoid((0, 0.05, 6.84), (0.41, 0.45, 0.52), MAIL, segs=16, rings=8, ycut=-0.15)
    b.loft([((0, 0.06, 5.9), 0.62, 0.5), ((0, 0.04, 6.25), 0.44, 0.42), ((0, 0.02, 6.55), 0.4, 0.42)], MAIL, n=16,
           caps=(False, False))


def rivets(b, z, r, count, ry=None):
    for i in range(count):
        t = 2 * math.pi * (i + 0.5) / count
        b.ellipsoid((r * math.cos(t), 0.02 + (ry or r) * math.sin(t), z), (0.035, 0.035, 0.035), STEEL, segs=6, rings=3)


def nasal_helm(b):
    b.loft([((0, 0.02, 6.86), 0.48, 0.51), ((0, 0.02, 7.12), 0.47, 0.5), ((0, 0.03, 7.36), 0.37, 0.4),
            ((0, 0.04, 7.55), 0.17, 0.19), ((0, 0.04, 7.66), 0.02, 0.02)], STEEL, n=16, caps=(False, False))
    b.loft([((0, 0.02, 6.84), 0.5, 0.53), ((0, 0.02, 6.98), 0.5, 0.53)], STEEL, n=16)  # brow band
    rivets(b, 6.91, 0.51, 10, 0.54)
    b.loft([((0, -0.53, 6.98), 0.06, 0.02), ((0, -0.5, 6.58), 0.05, 0.02)], STEEL, n=6)  # nasal


def great_helm(b):
    b.loft([((0, 0.02, 6.25), 0.48, 0.5), ((0, 0.02, 6.6), 0.49, 0.52), ((0, 0.02, 7.3), 0.48, 0.51),
            ((0, 0.02, 7.42), 0.42, 0.45), ((0, 0.02, 7.45), 0.2, 0.22)], STEEL, n=16)
    for s in (1, -1):
        b.box((s * 0.2, -0.5, 6.98), (0.32, 0.05, 0.065), DARK)  # eye slits
    b.box((0, -0.52, 6.82), (0.1, 0.05, 0.85), GOLD, bevel=0.015)  # brass cross on the face plate
    b.box((0, -0.52, 7.06), (0.66, 0.05, 0.1), GOLD, bevel=0.015)
    for i in range(6):
        for s in (1, -1):
            b.ellipsoid((s * (0.14 + 0.05 * (i % 2)), -0.5, 6.62 - 0.07 * (i // 2)), (0.018, 0.02, 0.018), DARK,
                        segs=6, rings=3)  # breaths
    rivets(b, 7.28, 0.49, 12, 0.52)
    rivets(b, 6.32, 0.49, 12, 0.51)


def turban_helm(b):
    for k, z in enumerate((6.92, 7.04, 7.16)):
        b.loft([((0, 0.02, z - 0.07), 0.5 - 0.03 * k, 0.53 - 0.03 * k), ((0, 0.02, z), 0.56 - 0.04 * k, 0.59 - 0.04 * k),
                ((0, 0.02, z + 0.07), 0.5 - 0.05 * k, 0.53 - 0.05 * k)], TURBAN, n=16, caps=(False, False))
    b.ellipsoid((0, 0.02, 7.15), (0.38, 0.41, 0.4), STEEL, segs=14, rings=7, zcut=0.0)
    b.loft([((0, 0.02, 7.5), 0.08, 0.08), ((0, 0.02, 7.95), 0.0, 0.0)], STEEL, n=6)
    b.ellipsoid((0, 0.02, 7.52), (0.1, 0.1, 0.05), GOLD, segs=8, rings=4)
    b.ellipsoid((0.0, 0.55, 6.9), (0.12, 0.1, 0.25), TURBAN, segs=8, rings=5)  # tail of the wrap


def kettle_hat(b):
    b.ellipsoid((0, 0.02, 6.98), (0.44, 0.47, 0.52), STEEL, segs=16, rings=8, zcut=0.0)
    b.loft([((0, 0.02, 7.04), 0.47, 0.5), ((0, 0.02, 6.98), 0.66, 0.69), ((0, 0.02, 6.9), 0.8, 0.83)], STEEL, n=18,
           caps=(False, False))
    b.loft([((0, 0.02, 7.05), 0.46, 0.49), ((0, 0.02, 7.15), 0.45, 0.48)], LEATHER, n=16, caps=(False, False))


def cross(b, kind, y, z=5.0, scale=1.0, front=True):
    off = -0.02 if front else 0.02
    b.box((0, y + off, z), (0.2 * scale, 0.05, 1.15 * scale), kind)
    b.box((0, y + off, z + 0.18 * scale), (0.8 * scale, 0.05, 0.2 * scale), kind)


def forearm_frame():
    elbow, wrist = Vector(J["LeftForeArm"]), Vector(J["LeftHand"])
    mid = elbow.lerp(wrist, 0.45)
    along = (wrist - elbow).normalized()
    out = along.cross(Vector((0, 1, 0))).normalized()
    if out.x < 0:
        out = -out
    return mid, along, out


def kite_shield(b):
    mid, along, out = forearm_frame()
    outline = []
    for i in range(9):  # rounded top
        t = math.pi * i / 8
        outline.append((0.63 * math.cos(t), 0.72 + 0.4 * math.sin(t)))
    outline = outline[::-1] + [(-0.6, 0.3), (-0.5, -0.25), (-0.3, -0.85), (0.0, -1.4), (0.3, -0.85), (0.5, -0.25),
                                (0.6, 0.3)]
    outline = [outline[-1]] + outline[:-1]
    outline.sort(key=lambda p: math.atan2(p[1] - 0.1, p[0]))
    up = -along
    b.plate(outline, mid + out * 0.33, out, up, 0.08, FIELD, bone="LeftForeArm", bulge=0.14, rim=STEEL)
    right = up.cross(out).normalized()
    rot = Matrix((right, out, up)).transposed()
    c = mid + out * 0.49
    b.box(c + up * 0.0, (0.14, 0.04, 2.0), CHARGE, bone="LeftForeArm", rot=rot)
    b.box(c + up * 0.5, (1.0, 0.04, 0.14), CHARGE, bone="LeftForeArm", rot=rot)
    b.ellipsoid(c + up * 0.5 + out * 0.03, (0.11, 0.11, 0.11), STEEL, bone="LeftForeArm", segs=8, rings=4)


def round_shield(b):
    mid, along, out = forearm_frame()
    ring = [(0.85 * math.cos(2 * math.pi * i / 20), 0.85 * math.sin(2 * math.pi * i / 20)) for i in range(20)]
    b.plate(ring, mid + out * 0.3, out, -along, 0.07, FIELD, bone="LeftForeArm", bulge=0.12, rim=GOLD)
    for r, kind, off in ((0.62, CHARGE, 0.4), (0.42, FIELD, 0.43)):
        inner = [(r * math.cos(2 * math.pi * i / 20), r * math.sin(2 * math.pi * i / 20)) for i in range(20)]
        b.plate(inner, mid + out * off, out, -along, 0.03, kind, bone="LeftForeArm", bulge=0.08)
    b.ellipsoid(mid + out * 0.5, (0.17, 0.17, 0.17), STEEL, bone="LeftForeArm", segs=10, rings=5)


def scabbard(b):
    b.loft([((0.84, -0.08, 3.98), 0.1, 0.06), ((0.94, 0.15, 3.1), 0.09, 0.055), ((1.04, 0.45, 2.2), 0.07, 0.045)],
           LEATHER, n=8, bone="Hip")
    b.box((1.04, 0.45, 2.18), (0.13, 0.09, 0.12), STEEL, bone="Hip")  # chape
    b.box((0.82, -0.12, 4.05), (0.09, 0.5, 0.08), GOLD, bone="Hip", rot=Matrix.Rotation(0.35, 3, "X"))  # cross-guard
    b.tube((0.81, -0.16, 4.08), (0.76, -0.33, 4.5), 0.05, 0.05, LEATHER, n=6, bone="Hip")  # grip
    b.ellipsoid((0.75, -0.36, 4.56), (0.08, 0.08, 0.08), GOLD, bone="Hip", segs=8, rings=4)  # pommel


def quiver(b):
    b.loft([((0.35, 0.74, 4.05), 0.18, 0.15), ((0.05, 0.76, 5.0), 0.2, 0.17), ((-0.25, 0.76, 5.9), 0.22, 0.19)],
           LEATHER, n=10, bone="back_mid")
    for k in range(5):
        dx = (k - 2) * 0.07
        b.tube((-0.25 + dx, 0.76, 5.8), (-0.3 + dx, 0.78 + 0.02 * k, 6.25), 0.015, 0.015, WOOD, n=4, bone="back_mid")
        b.box((-0.31 + dx, 0.78 + 0.02 * k, 6.25), (0.03, 0.09, 0.18), WHITE, bone="back_mid")
    b.tube((0.35, 0.6, 4.1), (-0.55, -0.45, 5.75), 0.04, 0.04, LEATHER, n=5, bone="back_mid")  # strap


BODIES = {
    "footman": ("west", "east"),
    "knight": ("west", "east"),
    "saracen": ("saracen", "africa"),
    "archer": ("levy", "saracen", "asia", "americas"),
}


def build_body(b, kind):
    if kind in ("footman", "knight"):
        legs(b, MAIL)
        arms(b, MAIL)
        torso(b, MAIL)
        overcoat(b, SURCOAT, 2.25 if kind == "footman" else 2.05)
        skirt(b, MAIL, 2.55, top=3.6, flare=0.9, depth=0.02)  # hauberk hem under the surcoat
        belt(b)
        head(b)
        coif(b)
        if kind == "footman":
            nasal_helm(b)
        else:
            great_helm(b)
        cross(b, EMBLEM, -0.66)
        cross(b, EMBLEM, 0.72, front=False)
        kite_shield(b)
        scabbard(b)
    elif kind == "saracen":
        legs(b, HOSE)
        arms(b, TUNIC, cuff=GOLD)
        torso(b, MAIL)
        overcoat(b, TUNIC, 1.85)
        b.loft([((0, 0.1, 4.25), 0.9, 0.66), ((0, 0.1, 4.6), 0.88, 0.64)], EMBLEM, n=16, caps=(False, False))  # sash
        b.ellipsoid((0.55, -0.35, 4.3), (0.15, 0.1, 0.3), EMBLEM, segs=8, rings=5)  # sash knot
        head(b, beard=True)
        turban_helm(b)
        round_shield(b)
        scabbard(b)
    elif kind == "archer":
        legs(b, HOSE)
        arms(b, QUILT)
        torso(b, QUILT, chest=1.05)
        skirt(b, QUILT, 2.8, flare=0.95, depth=0.04)
        belt(b, buckle=STEEL)
        head(b, beard=True)
        kettle_hat(b)
        quiver(b)


# ---------------------------------------------------------------- weapons and siege engine
# Weapons live in hand-node space: the grip is at the origin and the business end
# points along -Y, like the vanilla rifles.
def build_weapon(b, kind):
    if kind == "spear":
        b.tube((0, 2.4, 0), (0, -4.3, 0), 0.065, 0.06, WOOD, n=8)
        b.tube((0, -4.15, 0), (0, -4.5, 0), 0.08, 0.07, STEEL, n=8)  # socket
        b.loft([((0, -4.5, 0), 0.07, 0.03), ((0, -4.75, 0), 0.17, 0.035), ((0, -5.3, 0), 0.0, 0.0)], STEEL, n=6)
        b.tube((0, 0.35, 0), (0, -0.35, 0), 0.08, 0.08, LEATHER, n=8)  # grip wrap
    elif kind == "lance":
        b.loft([((0, 2.6, 0), 0.09, 0.09), ((0, 0.6, 0), 0.12, 0.12), ((0, -3.0, 0), 0.1, 0.1),
                ((0, -7.6, 0), 0.05, 0.05)], FIELD, n=8)
        b.loft([((0, 0.6, 0), 0.32, 0.32), ((0, 0.45, 0), 0.3, 0.3), ((0, -0.3, 0), 0.1, 0.1)], STEEL, n=12)  # vamplate
        b.loft([((0, -7.6, 0), 0.06, 0.06), ((0, -8.2, 0), 0.0, 0.0)], STEEL, n=6)
        b.plate([(0, 0), (0.0, -0.45), (1.2, -0.3), (0.9, -0.22), (1.2, -0.12)], (0, -6.6, 0.12), (1, 0, 0),
                (0, 0, 1), 0.02, CHARGE)  # pennon
    elif kind == "bow":
        pts = []
        for i in range(13):
            t = -1 + i / 6
            curl = 0.12 * t ** 9  # recurved tips
            pts.append(Vector((0, 0.55 * t * t - 0.05 - curl * 3, 2.0 * t)))
        for k, (p, q) in enumerate(zip(pts, pts[1:])):
            r0 = 0.08 - 0.03 * abs(k - 5.5) / 6
            b.tube(p, q, r0, r0, WOOD, n=6)
        b.tube(pts[0], pts[-1], 0.015, 0.015, WHITE, n=4)
        b.tube((0, -0.1, -0.28), (0, -0.1, 0.28), 0.1, 0.1, LEATHER, n=8)


def build_trebuchet(b):
    w = 1.7
    for s in (1, -1):
        b.box((s * w, 0, 0.3), (0.45, 10.0, 0.45), WOOD, bevel=0.04)  # ground rails
        for y in (-2.6, 2.6):
            b.loft([((s * w, y, 0.4), 0.2, 0.2), ((s * (w - 0.2), 0, 7.2), 0.16, 0.16)], WOOD, n=6, smooth=False)
        b.tube((s * w, -4.6, 0.4), (s * w, -2.0, 3.2), 0.13, 0.13, WOOD, n=6, smooth=False)  # braces
        b.tube((s * w, 4.6, 0.4), (s * w, 2.0, 3.2), 0.13, 0.13, WOOD, n=6, smooth=False)
        b.box((s * (w - 0.1), 0, 7.2), (0.5, 0.7, 0.5), STEEL, bevel=0.04)  # axle bearing
        for y in (-4.7, 0.0, 4.7):
            b.box((s * w, y, 0.55), (0.55, 0.55, 0.12), STEEL)  # iron straps
    for y in (-4.7, 0.0, 4.7):
        b.box((0, y, 0.3), (2 * w + 0.4, 0.45, 0.4), WOOD, bevel=0.04)
    b.tube((-w - 0.3, 0, 7.2), (w + 0.3, 0, 7.2), 0.2, 0.2, DARK, n=8)  # axle
    # the throwing arm, cocked: long end down at the back, counterweight up at the front
    pivot = Vector((0, 0, 7.2))
    tip = Vector((0, 7.4, 1.6))
    short = pivot + (pivot - tip).normalized() * 2.4
    b.loft([(short, 0.32, 0.32), (pivot, 0.3, 0.3), (tip, 0.15, 0.15)], WOOD, n=8, smooth=False)
    for k in range(4):
        b.loft([(short.lerp(tip, 0.1 + 0.2 * k), 0.34, 0.34), (short.lerp(tip, 0.12 + 0.2 * k), 0.34, 0.34)], LEATHER,
               n=8)  # rope lashings
    box = short + Vector((0, 0, -1.2))
    b.box(box, (1.9, 1.6, 1.7), WOOD, bevel=0.06)  # counterweight box
    for dz in (0.75, -0.75):
        b.box(box + Vector((0, 0, dz)), (2.0, 1.7, 0.15), STEEL)
    for s in (1, -1):
        b.tube(short + Vector((s * 0.3, 0, 0)), box + Vector((s * 0.7, 0, 0.85)), 0.06, 0.06, LEATHER, n=4)
    b.tube(tip, tip + Vector((0, 1.3, -1.25)), 0.04, 0.04, LEATHER, n=4)  # sling
    b.ellipsoid(tip + Vector((0, 1.35, -1.3)), (0.38, 0.38, 0.34), STEEL, segs=10, rings=6)  # the stone
    b.tube((0, -4.7, 0.6), (0, -4.7, 1.6), 0.25, 0.25, WOOD, n=8)  # winch
    b.tube((-w, -4.7, 1.6), (w, -4.7, 1.6), 0.2, 0.2, WOOD, n=8)
    for k in range(4):
        t = math.pi * k / 2
        b.tube((w + 0.15, -4.7, 1.6), (w + 0.15, -4.7 + 0.8 * math.cos(t), 1.6 + 0.8 * math.sin(t)), 0.05, 0.05,
               WOOD, n=4)  # winch spokes


# ---------------------------------------------------------------- bake and export
def reset_with_vanilla():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bie.import_meshfile(os.path.join(GAME, "gfx/models/units/western_european_infantry.mesh"))
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    body = next(o for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) > 100)
    coll = next(o for o in bpy.data.objects if o.type == "MESH" and o is not body)
    return rig, body, coll


def pdx_material(template, diffuse, stem):
    mat = template.copy()
    mat.name = "dv_" + stem
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image:
            fname = os.path.basename(node.image.filepath)
            if "diffuse" in fname:
                new = diffuse
            elif "spec" in fname:
                new = "%s_spec.dds" % stem
            else:
                new = "%s_normal.dds" % stem
            node.image = bpy.data.images.new(new, 4, 4)
            node.image.filepath = os.path.join(OUT, new)
    return mat


def skin_from(obj, src, rig, bones):
    """Copy skin weights from the nearest point on the vanilla body, then pin rigid parts."""
    rigid = {i: bones[a.value - 1] for i, a in enumerate(obj.data.attributes["rigid"].data) if a.value}
    bm = bmesh.new()
    bm.from_mesh(src.data)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    names = [g.name for g in src.vertex_groups]
    sw = [{names[g.group]: g.weight for g in v.groups if g.weight > 0} for v in src.data.vertices]
    groups = {}
    for v in obj.data.vertices:
        if rigid.get(v.index) == SKIRT:
            # hangs from the hips and swings with both thighs toward the hem, each side more with its own leg
            legs_share = 0.8 * min(1.0, max(0.0, (4.0 - v.co.z) / 2.0))
            left = min(1.0, max(0.0, 0.5 + v.co.x / 0.8))
            w = {"Hip": 1.0 - legs_share, "LeftUpLeg": legs_share * left, "RightUpLeg": legs_share * (1 - left)}
            w = {g: x for g, x in w.items() if x > 0.02}
        elif v.index in rigid:
            w = {rigid[v.index]: 1.0}
        else:
            _, _, fi, _ = tree.find_nearest(v.co)
            w = {}
            for sv in bm.faces[fi].verts:
                k = 1.0 / max(0.05, (sv.co - v.co).length)
                for g, x in sw[sv.index].items():
                    w[g] = w.get(g, 0.0) + x * k
            top = sorted(w.items(), key=lambda kv: -kv[1])[:4]
            tot = sum(x for _, x in top)
            w = {g: x / tot for g, x in top if x / tot > 0.02}
        for g, x in w.items():
            if g not in groups:
                groups[g] = obj.vertex_groups.new(name=g)
            groups[g].add([v.index], x, "REPLACE")
    bm.free()
    mod = obj.modifiers.new("skin", "ARMATURE")
    mod.object = rig
    obj.parent = rig


def unwrap(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.006, area_weight=0.0)
    bpy.ops.object.mode_set(mode="OBJECT")


def bake(obj, mats, size, palettes, stem):
    """Bake albedo per palette plus shared AO, normal and spec maps; write the DDS files."""
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    sc.render.bake.margin = 6
    for o in bpy.data.objects:
        o.select_set(o is obj)
    bpy.context.view_layer.objects.active = obj
    world = bpy.data.worlds.new("bake")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    sc.world = world
    sc.world.light_settings.distance = 0.6

    def target(name, colorspace):
        img = bpy.data.images.new(name, size, size, alpha=False, float_buffer=True)
        img.colorspace_settings.name = colorspace
        for m in mats:
            m.node_tree.nodes["bake"].image = img
            m.node_tree.nodes.active = m.node_tree.nodes["bake"]
        return img

    def pixels(img):
        a = np.array(img.pixels[:], dtype=np.float32).reshape(size, size, 4)
        return a[::-1]  # Blender stores rows bottom-up

    img = target(stem + "_ao", "Non-Color")
    bpy.ops.object.bake(type="AO")
    ao = pixels(img)[..., 0]
    img = target(stem + "_n", "Non-Color")
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")
    nrm = pixels(img)
    # spec: route the emission node holding (intensity, gloss) to the output
    for m in mats:
        nt = m.node_tree
        out = nt.nodes["Material Output"]
        nt.links.new(nt.nodes["spec"].outputs[0], out.inputs["Surface"])
    img = target(stem + "_s", "Non-Color")
    bpy.ops.object.bake(type="EMIT")
    spec = pixels(img)
    for m in mats:
        nt = m.node_tree
        nt.links.new(nt.nodes["Principled BSDF"].outputs[0], nt.nodes["Material Output"].inputs["Surface"])

    # vanilla layout: normal X in R and A, Y in G (DirectX, so flipped), B unused
    n = np.zeros((size, size, 4), np.float32)
    n[..., 0] = nrm[..., 0]
    n[..., 1] = 1.0 - nrm[..., 1]
    n[..., 3] = nrm[..., 0]
    save_dds(os.path.join(OUT, stem + "_normal.dds"), n, "DXT5")
    s = np.zeros((size, size, 4), np.float32)
    s[..., 1] = spec[..., 0] * (0.5 + 0.5 * ao)
    s[..., 3] = spec[..., 1]
    save_dds(os.path.join(OUT, stem + "_spec.dds"), s, "DXT5")

    shade = 0.45 + 0.55 * ao
    names = {}
    for pal in palettes:
        set_palette(mats, pal)
        img = target("%s_%s_d" % (stem, pal), "Linear Rec.709")
        bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"})
        lin_c = pixels(img)[..., :3]
        srgb = np.where(lin_c <= 0.0031308, lin_c * 12.92, 1.055 * np.power(np.clip(lin_c, 0, None), 1 / 2.4) - 0.055)
        d = np.ones((size, size, 4), np.float32)
        d[..., :3] = srgb * shade[..., None]
        name = "%s_%s_diffuse.dds" % (stem, pal)
        save_dds(os.path.join(OUT, name), d, "DXT1")
        names[pal] = name
    return names


def finish_mesh(obj, pdx_mat):
    """Collapse the bake materials into the single PDX material the exporter writes."""
    for p in obj.data.polygons:
        p.material_index = 0
    obj.data.materials.clear()
    obj.data.materials.append(pdx_mat)


def build_static(stem, fill, size, palette, keep_collision=None):
    rig, body, coll = reset_with_vanilla()
    template = body.data.materials[0]
    for o in (rig, body) + (() if keep_collision else (coll,)):
        bpy.data.objects.remove(o)
    if keep_collision:
        coll.data.transform(Matrix.Diagonal((*keep_collision, 1.0)))
        coll.hide_render = True
    b = Builder()
    fill(b)
    obj = b.to_object(stem)
    mats = [make_material(k) for k in range(KINDS)]
    for m in mats:
        obj.data.materials.append(m)
    unwrap(obj)
    names = bake(obj, mats, size, [palette], stem)
    finish_mesh(obj, pdx_material(template, names[palette], stem))
    bie.export_meshfile(os.path.join(OUT, stem + ".mesh"), exp_mesh=True, exp_skel=True, exp_locs=True)


def main():
    for f in os.listdir(OUT):
        if f.endswith((".dds", ".mesh")):
            os.remove(os.path.join(OUT, f))
    rig, body, coll = reset_with_vanilla()
    for bone in rig.data.bones:
        J[bone.name] = tuple(bone.head_local)

    for kind, palettes in BODIES.items():
        stem = "dv_" + kind
        names = None
        for pal in palettes:
            rig, body, coll = reset_with_vanilla()
            template = body.data.materials[0]
            b2 = Builder()
            build_body(b2, kind)
            obj = b2.to_object("%s_%s" % (stem, pal))
            mats = [make_material(k) for k in range(KINDS)]
            for m in mats:
                obj.data.materials.append(m)
            skin_from(obj, body, rig, b2.bones)
            bpy.data.objects.remove(body)
            coll.hide_render = True
            unwrap(obj)
            if names is None:
                names = bake(obj, mats, 512, list(palettes), stem)
            finish_mesh(obj, pdx_material(template, names[pal], stem))
            bie.export_meshfile(os.path.join(OUT, "%s_%s.mesh" % (stem, pal)), exp_mesh=True, exp_skel=True,
                                exp_locs=True)

    for kind in ("spear", "lance", "bow"):
        build_static("dv_" + kind, lambda b, k=kind: build_weapon(b, k), 256, "levy")
    build_static("dv_trebuchet", build_trebuchet, 512, "levy", keep_collision=(2.2, 4.0, 1.4))


main()

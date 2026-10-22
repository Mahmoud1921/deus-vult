"""Build the Deus Vult 3D unit models.

Run with the `bpy` Python module (pip install bpy==4.2.*) and the io_pdx_mesh
exporter (https://github.com/ross-g/io_pdx_mesh):

    python build_models.py <io_pdx_mesh parent dir> <HoI4 install dir> <mod dir>

Every model is original low-poly geometry. The soldiers are skinned to the vanilla
infantry skeleton (read from the game install, not shipped), so they play the
vanilla walk, fight and ride animations. Weapons are static meshes held at the
skeleton's hand nodes. Output goes to <mod>/gfx/models/units/dv/.
"""
import math
import os
import struct
import sys

import bpy  # noqa: I001  (bpy must load before bmesh and mathutils)
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

EXT, GAME, MOD = sys.argv[-3:]
sys.path.insert(0, EXT)
from io_pdx_mesh.pdx_blender import blender_import_export as bie  # noqa: E402

OUT = os.path.join(MOD, "gfx/models/units/dv")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette atlas
# The diffuse texture is a 4x4 grid of flat colour swatches. Each part of a model
# maps into one swatch, so a culture only needs its own swatch colours.
SKIN, MAIL, STEEL, SURCOAT, EMBLEM, LEATHER, WOOD, FIELD, CHARGE, TUNIC, HOSE, TURBAN, HAIR, DARK, GOLD, WHITE = range(16)
METAL = {MAIL, STEEL, GOLD}

PALETTES = {
    # Latin Christendom: white surcoat with a red cross, red kite shield
    "west": {SKIN: (214, 170, 135), MAIL: (128, 132, 138), STEEL: (170, 174, 180), SURCOAT: (226, 220, 200),
             EMBLEM: (170, 28, 30), LEATHER: (92, 60, 36), WOOD: (122, 88, 52), FIELD: (168, 30, 32),
             CHARGE: (222, 186, 70), TUNIC: (150, 120, 80), HOSE: (70, 62, 52), TURBAN: (230, 226, 210),
             HAIR: (82, 56, 36), DARK: (24, 22, 22), GOLD: (206, 168, 72), WHITE: (232, 230, 222)},
    # Orthodox realms: crimson surcoat with a gold cross, blue shield
    "east": {SKIN: (210, 166, 130), MAIL: (124, 126, 130), STEEL: (166, 168, 172), SURCOAT: (140, 26, 36),
             EMBLEM: (220, 180, 70), LEATHER: (84, 56, 34), WOOD: (118, 84, 50), FIELD: (40, 62, 128),
             CHARGE: (222, 186, 70), TUNIC: (120, 40, 44), HOSE: (60, 54, 48), TURBAN: (226, 222, 206),
             HAIR: (60, 42, 30), DARK: (24, 22, 22), GOLD: (214, 172, 64), WHITE: (232, 230, 222)},
    # Islamic realms: white turban, green kaftan, red and white round shield
    "saracen": {SKIN: (186, 138, 98), MAIL: (124, 126, 130), STEEL: (176, 176, 178), SURCOAT: (44, 104, 64),
                EMBLEM: (222, 186, 70), LEATHER: (96, 62, 36), WOOD: (126, 92, 56), FIELD: (176, 34, 34),
                CHARGE: (232, 228, 214), TUNIC: (46, 110, 70), HOSE: (190, 176, 140), TURBAN: (236, 234, 224),
                HAIR: (36, 28, 24), DARK: (24, 22, 22), GOLD: (214, 172, 64), WHITE: (236, 234, 226)},
    # Africa: white robes, ochre shield
    "africa": {SKIN: (120, 82, 56), MAIL: (124, 126, 130), STEEL: (170, 170, 172), SURCOAT: (230, 224, 206),
               EMBLEM: (176, 120, 40), LEATHER: (96, 62, 36), WOOD: (126, 92, 56), FIELD: (196, 134, 54),
               CHARGE: (60, 40, 28), TUNIC: (226, 220, 200), HOSE: (200, 184, 150), TURBAN: (236, 232, 220),
               HAIR: (30, 24, 20), DARK: (24, 22, 22), GOLD: (214, 172, 64), WHITE: (236, 234, 226)},
    # Plain soldiers in quilted gambesons
    "levy": {SKIN: (212, 168, 132), MAIL: (126, 128, 132), STEEL: (150, 152, 156), SURCOAT: (150, 120, 80),
             EMBLEM: (170, 28, 30), LEATHER: (92, 60, 36), WOOD: (122, 88, 52), FIELD: (90, 110, 60),
             CHARGE: (222, 186, 70), TUNIC: (164, 138, 96), HOSE: (78, 90, 58), TURBAN: (226, 222, 206),
             HAIR: (82, 56, 36), DARK: (24, 22, 22), GOLD: (206, 168, 72), WHITE: (232, 230, 222)},
    # East Asia: red lacquered armour and dark helmets
    "asia": {SKIN: (214, 176, 134), MAIL: (60, 56, 52), STEEL: (64, 60, 58), SURCOAT: (150, 34, 30),
             EMBLEM: (214, 172, 64), LEATHER: (70, 46, 30), WOOD: (110, 74, 44), FIELD: (150, 34, 30),
             CHARGE: (214, 172, 64), TUNIC: (150, 34, 30), HOSE: (40, 38, 40), TURBAN: (40, 38, 40),
             HAIR: (24, 20, 20), DARK: (20, 18, 18), GOLD: (214, 172, 64), WHITE: (230, 226, 214)},
    # The Americas: undyed cotton armour and bright feathers
    "americas": {SKIN: (168, 112, 76), MAIL: (210, 196, 160), STEEL: (196, 170, 110), SURCOAT: (210, 196, 160),
                 EMBLEM: (40, 120, 120), LEATHER: (110, 74, 44), WOOD: (126, 92, 56), FIELD: (40, 120, 120),
                 CHARGE: (210, 60, 40), TUNIC: (214, 200, 162), HOSE: (168, 112, 76), TURBAN: (40, 120, 120),
                 HAIR: (24, 20, 20), DARK: (20, 18, 18), GOLD: (214, 172, 64), WHITE: (232, 226, 210)},
}
TEX = 128
CELL = TEX // 4


def swatch_uv(slot):
    return ((slot % 4) + 0.5) / 4.0, ((slot // 4) + 0.5) / 4.0


def write_dds(path, rgba_rows, size):
    """Write an uncompressed 32-bit DDS (A8R8G8B8) with a full mip chain."""
    levels = []
    img = rgba_rows
    s = size
    while True:
        levels.append(img)
        if s == 1:
            break
        ns = s // 2
        img = [[tuple(sum(img[2 * y + dy][2 * x + dx][c] for dy in (0, 1) for dx in (0, 1)) // 4 for c in range(4))
                for x in range(ns)] for y in range(ns)]
        s = ns
    hdr = struct.pack("<4sIIIIIII44sIIIIIIIIIIIII", b"DDS ", 124, 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000, size, size,
                      size * 4, 0, len(levels), b"\0" * 44,
                      32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000,
                      0x1000 | 0x8 | 0x400000, 0, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(hdr)
        for lvl in levels:
            for row in lvl:
                f.write(b"".join(struct.pack("BBBB", b, g, r, a) for r, g, b, a in row))


def build_textures():
    for name, pal in PALETTES.items():
        rows = []
        for y in range(TEX):
            row = []
            for x in range(TEX):
                slot = (x // CELL) + 4 * (3 - y // CELL)  # DDS rows run top-down, UV v runs bottom-up
                r, g, b = pal[slot]
                # a soft vignette inside each swatch reads as shading at map distance
                cx, cy = (x % CELL) / CELL - 0.5, (y % CELL) / CELL - 0.5
                k = 1.0 - 0.18 * (cx * cx + cy * cy) * 4
                row.append((int(r * k), int(g * k), int(b * k), 255))
            rows.append(row)
        write_dds(os.path.join(OUT, "dv_%s_diffuse.dds" % name), rows, TEX)
    # specular: G = intensity, A = gloss (matches the vanilla unit maps)
    rows = []
    for y in range(TEX):
        row = []
        for x in range(TEX):
            slot = (x // CELL) + 4 * (3 - y // CELL)
            row.append((0, 190, 0, 150) if slot in METAL else (0, 26, 0, 40))
        rows.append(row)
    write_dds(os.path.join(OUT, "dv_units_spec.dds"), rows, TEX)
    flat = [[(128, 128, 0, 128)] * 4 for _ in range(4)]
    write_dds(os.path.join(OUT, "dv_units_normal.dds"), flat, 4)


# ---------------------------------------------------------------- geometry kit
class Builder:
    """Collects primitive parts into one bmesh, with a swatch and optional rigid bone per part."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.rigid = self.bm.verts.layers.int.new("rigid")  # 1 + index into self.bones, 0 = skinned
        self.bones = []

    def _finish(self, verts, faces, slot, bone, smooth):
        centre = sum((v.co for v in verts), Vector()) / len(verts)
        cu, cv = swatch_uv(slot)
        for f in faces:
            f.smooth = smooth
            for loop in f.loops:
                d = loop.vert.co - centre
                loop[self.uv].uv = (cu + 0.09 * math.tanh(d.x + 0.5 * d.y), cv + 0.09 * math.tanh(d.z + 0.3 * d.y))
        if bone:
            if bone not in self.bones:
                self.bones.append(bone)
            for v in verts:
                if v.is_valid:
                    v[self.rigid] = self.bones.index(bone) + 1

    def tube(self, a, b, ra, rb, slot, n=8, bone=None, smooth=True, ya=None, yb=None, caps=True):
        """Tapered tube from a to b. ya/yb squash the radius on the axis most aligned with world Y."""
        a, b = Vector(a), Vector(b)
        axis = (b - a).normalized()
        ref = Vector((0, 1, 0)) if abs(axis.y) < 0.9 else Vector((0, 0, 1))
        u = axis.cross(ref).normalized()
        w = axis.cross(u).normalized()
        rings = []
        for c, r, ry in ((a, ra, ra if ya is None else ya), (b, rb, rb if yb is None else yb)):
            ring = []
            for i in range(n):
                t = 2 * math.pi * i / n
                ring.append(self.bm.verts.new(c + u * math.cos(t) * r + w * math.sin(t) * ry))
            rings.append(ring)
        faces = []
        for i in range(n):
            j = (i + 1) % n
            faces.append(self.bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i])))
        if caps:
            faces.append(self.bm.faces.new(list(reversed(rings[0]))))
            faces.append(self.bm.faces.new(rings[1]))
        self._finish(rings[0] + rings[1], faces, slot, bone, smooth)

    def ellipsoid(self, c, r, slot, bone=None, segs=10, rings=6, zcut=None):
        """Ellipsoid at c with radii r. zcut keeps only the part above that local height (domes)."""
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
                row.append(self.bm.verts.new(c + Vector((r[0] * s * math.cos(t), r[1] * s * math.sin(t), r[2] * z))))
            grid.append(row)
        faces = []
        for k in range(rings):
            for i in range(segs):
                j = (i + 1) % segs
                q = (grid[k][i], grid[k][j], grid[k + 1][j], grid[k + 1][i])
                if len({v.co.to_tuple(5) for v in q}) >= 3:
                    faces.append(self.bm.faces.new(tuple(reversed(q))))
        verts = [v for row in grid for v in row]
        self._finish(verts, faces, slot, bone, True)
        bmesh.ops.remove_doubles(self.bm, verts=[v for v in verts if v.is_valid], dist=1e-5)

    def box(self, c, size, slot, bone=None, rot=None):
        c = Vector(c)
        m = rot or Matrix.Identity(3)
        hx, hy, hz = (s / 2 for s in size)
        vs = [self.bm.verts.new(c + m @ Vector((x, y, z)))
              for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]
        idx = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        faces = [self.bm.faces.new([vs[i] for i in q]) for q in idx]
        self._finish(vs, faces, slot, bone, False)

    def plate(self, outline, centre, normal, up, thick, slot, bone=None, bulge=0.0):
        """Flat shield-like plate: 2D outline (x right, y up) placed at centre facing normal."""
        centre, normal, up = Vector(centre), Vector(normal).normalized(), Vector(up).normalized()
        right = up.cross(normal).normalized()
        up = normal.cross(right).normalized()
        front, back = [], []
        for x, y in outline:
            p = centre + right * x + up * y
            bow = bulge * (1 - min(1.0, (x * x) / 0.6))
            front.append(self.bm.verts.new(p + normal * (thick / 2 + bow)))
            back.append(self.bm.verts.new(p - normal * (thick / 2 - bow)))
        faces = [self.bm.faces.new(front), self.bm.faces.new(list(reversed(back)))]
        n = len(outline)
        for i in range(n):
            j = (i + 1) % n
            faces.append(self.bm.faces.new((front[j], front[i], back[i], back[j])))
        self._finish(front + back, faces, slot, bone, False)
        bmesh.ops.recalc_face_normals(self.bm, faces=faces)

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


def body_base(b, cloth, legs, arms, boots=LEATHER, skirt_to=2.35, skirt_slot=None):
    for s in (1, -1):
        up, knee, ankle, toe = (side(J[k], s) for k in ("LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase"))
        b.tube(up + Vector((0, 0, 0.25)), knee, 0.44, 0.33, legs)
        b.tube(knee, ankle + Vector((0, 0, 0.25)), 0.33, 0.25, legs)
        b.tube(ankle + Vector((0, 0.15, 0.55)), side((1.0, -0.15, 0.12), s), 0.28, 0.2, boots, n=6)
        sh, arm, elbow, wrist, hand = (side(J[k], s) for k in ("LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand", "Left_Hand_node"))
        b.tube(arm + Vector((0, 0, 0.05)), elbow, 0.3, 0.25, arms)
        b.tube(elbow, wrist, 0.25, 0.2, arms)
        b.ellipsoid(wrist.lerp(hand, 0.5), (0.2, 0.2, 0.2), LEATHER, segs=6, rings=4)
        b.ellipsoid(arm + Vector((0, 0, -0.05)), (0.36, 0.36, 0.34), cloth, segs=8, rings=5)
    # torso and the skirt of the coat
    b.tube((0, 0.08, 3.75), (0, 0.06, 5.95), 0.8, 0.92, cloth, n=10, ya=0.55, yb=0.62)
    b.tube((0, 0.08, 3.95), (0, 0.1, skirt_to), 0.82, 1.08, skirt_slot if skirt_slot is not None else cloth,
           n=10, ya=0.58, yb=0.82, smooth=False)
    b.tube((0, 0.06, 5.9), (0, 0.04, 6.45), 0.3, 0.27, SKIN, n=8)
    b.tube((0, 0.08, 3.85), (0, 0.08, 4.1), 0.85, 0.85, LEATHER, n=10, ya=0.6, yb=0.6)  # belt


def head(b, beard=False):
    b.ellipsoid((0, 0.02, 6.86), (0.36, 0.4, 0.47), SKIN, segs=10, rings=6)
    b.ellipsoid((0, -0.36, 6.82), (0.07, 0.08, 0.1), SKIN, segs=6, rings=4)  # nose
    if beard:
        b.ellipsoid((0, -0.18, 6.52), (0.3, 0.26, 0.24), HAIR, segs=8, rings=5)


def cross(b, slot, y, z=5.05, scale=1.0):
    b.box((0, y, z), (0.2 * scale, 0.05, 1.15 * scale), slot)
    b.box((0, y, z + 0.18 * scale), (0.8 * scale, 0.05, 0.2 * scale), slot)


def kite_shield(b):
    elbow, wrist = Vector(J["LeftForeArm"]), Vector(J["LeftHand"])
    mid = elbow.lerp(wrist, 0.45)
    along = (wrist - elbow).normalized()
    out = along.cross(Vector((0, 1, 0))).normalized()
    if out.x < 0:
        out = -out
    outline = [(0.0, 1.1), (0.45, 1.0), (0.62, 0.7), (0.6, 0.1), (0.38, -0.6), (0.0, -1.35),
               (-0.38, -0.6), (-0.6, 0.1), (-0.62, 0.7), (-0.45, 1.0)]
    up = -along
    b.plate(outline, mid + out * 0.32, out, up, 0.08, FIELD, bone="LeftForeArm", bulge=0.12)
    c = mid + out * 0.41
    right = up.cross(out).normalized()
    b.box(c + up * 0.05, (0.12, 0.05, 1.9), CHARGE, bone="LeftForeArm",
          rot=Matrix((right, out, up)).transposed())
    b.box(c + up * 0.55, (0.95, 0.05, 0.12), CHARGE, bone="LeftForeArm",
          rot=Matrix((right, out, up)).transposed())


def round_shield(b):
    elbow, wrist = Vector(J["LeftForeArm"]), Vector(J["LeftHand"])
    mid = elbow.lerp(wrist, 0.45)
    along = (wrist - elbow).normalized()
    out = along.cross(Vector((0, 1, 0))).normalized()
    if out.x < 0:
        out = -out
    ring = [(0.85 * math.cos(2 * math.pi * i / 14), 0.85 * math.sin(2 * math.pi * i / 14)) for i in range(14)]
    b.plate(ring, mid + out * 0.3, out, -along, 0.07, FIELD, bone="LeftForeArm", bulge=0.1)
    inner = [(0.5 * x / 0.85, 0.5 * y / 0.85) for x, y in ring]
    b.plate(inner, mid + out * 0.38, out, -along, 0.04, CHARGE, bone="LeftForeArm", bulge=0.06)
    b.ellipsoid(mid + out * 0.44, (0.16, 0.16, 0.16), STEEL, bone="LeftForeArm", segs=8, rings=4)


def scabbard(b):
    b.tube((0.82, -0.05, 3.95), (1.02, 0.45, 2.2), 0.09, 0.07, LEATHER, n=6, bone="Hip", smooth=False)
    b.tube((0.8, -0.1, 4.0), (0.72, -0.25, 4.45), 0.06, 0.06, DARK, n=6, bone="Hip")  # hilt
    b.box((0.81, -0.08, 4.0), (0.08, 0.45, 0.08), GOLD, bone="Hip")


def nasal_helm(b):
    b.tube((0, 0.02, 6.86), (0, 0.02, 7.0), 0.47, 0.47, STEEL, n=10, ya=0.5, yb=0.5)
    b.tube((0, 0.02, 7.0), (0, 0.04, 7.62), 0.47, 0.03, STEEL, n=10, ya=0.5, yb=0.04)
    b.box((0, -0.47, 6.74), (0.08, 0.05, 0.42), STEEL)
    b.tube((0, 0.04, 6.2), (0, 0.03, 6.8), 0.42, 0.42, MAIL, n=10, ya=0.46, yb=0.46, caps=False)  # coif


def great_helm(b):
    b.tube((0, 0.02, 6.3), (0, 0.02, 7.38), 0.47, 0.47, STEEL, n=10, ya=0.5, yb=0.5)
    b.tube((0, 0.02, 7.38), (0, 0.02, 7.45), 0.47, 0.4, STEEL, n=10, ya=0.5, yb=0.43)
    b.box((0, -0.5, 6.98), (0.72, 0.05, 0.07), DARK)  # eye slit
    b.box((0, -0.5, 6.82), (0.1, 0.06, 0.55), GOLD)  # brow cross
    b.box((0, -0.5, 7.06), (0.6, 0.06, 0.08), GOLD)


def turban_helm(b):
    b.ellipsoid((0, 0.02, 7.02), (0.52, 0.55, 0.24), TURBAN, segs=10, rings=5)
    b.ellipsoid((0, 0.02, 7.1), (0.4, 0.43, 0.42), STEEL, segs=10, rings=5, zcut=0.0)
    b.tube((0, 0.02, 7.45), (0, 0.02, 7.85), 0.06, 0.0, STEEL, n=6)


def kettle_hat(b):
    b.ellipsoid((0, 0.02, 6.98), (0.44, 0.47, 0.5), STEEL, segs=10, rings=5, zcut=0.0)
    b.tube((0, 0.02, 6.98), (0, 0.02, 7.03), 0.8, 0.5, STEEL, n=12, ya=0.83, yb=0.53)


def quiver(b):
    b.tube((0.35, 0.72, 4.1), (-0.25, 0.72, 5.9), 0.17, 0.2, LEATHER, n=6, bone="back_mid", smooth=False)
    b.ellipsoid((-0.27, 0.72, 6.0), (0.18, 0.18, 0.16), WHITE, bone="back_mid", segs=6, rings=4)


BODIES = {
    # name: (builder, palettes it is exported in)
    "footman": ("west", "east"),
    "knight": ("west", "east"),
    "saracen": ("saracen", "africa"),
    "archer": ("levy", "saracen", "asia", "americas"),
}


def build_body(b, kind):
    if kind == "footman":
        body_base(b, SURCOAT, MAIL, MAIL)
        head(b)
        nasal_helm(b)
        cross(b, EMBLEM, -0.6)
        cross(b, EMBLEM, 0.66)
        kite_shield(b)
        scabbard(b)
    elif kind == "knight":
        body_base(b, SURCOAT, MAIL, MAIL, skirt_to=2.15)
        head(b)
        great_helm(b)
        cross(b, EMBLEM, -0.6)
        cross(b, EMBLEM, 0.66)
        kite_shield(b)
        scabbard(b)
    elif kind == "saracen":
        body_base(b, TUNIC, HOSE, MAIL, skirt_to=1.95)
        b.tube((0, 0.08, 4.35), (0, 0.08, 4.55), 0.86, 0.86, EMBLEM, n=10, ya=0.62, yb=0.62)  # sash
        head(b, beard=True)
        turban_helm(b)
        round_shield(b)
        scabbard(b)
    elif kind == "archer":
        body_base(b, TUNIC, HOSE, TUNIC, skirt_to=2.85)
        head(b, beard=True)
        kettle_hat(b)
        quiver(b)


# ---------------------------------------------------------------- weapons and siege engine
# Weapons live in hand-node space: the grip is at the origin and the business end
# points along -Y, like the vanilla rifles.
def build_weapon(b, kind):
    if kind == "spear":
        b.tube((0, 2.4, 0), (0, -4.4, 0), 0.06, 0.06, WOOD, n=6)
        b.tube((0, -4.4, 0), (0, -5.15, 0), 0.14, 0.0, STEEL, n=4, yb=0.0, ya=0.05)
    elif kind == "lance":
        b.tube((0, 2.6, 0), (0, -7.6, 0), 0.11, 0.05, FIELD, n=6)
        b.tube((0, 0.55, 0), (0, -0.25, 0), 0.3, 0.08, STEEL, n=8)
        b.tube((0, -7.6, 0), (0, -8.1, 0), 0.07, 0.0, STEEL, n=4)
        b.plate([(0, 0), (0.0, -0.45), (1.1, -0.22)], (0, -6.6, 0.12), (1, 0, 0), (0, 0, 1), 0.02, CHARGE)
    elif kind == "bow":
        pts = []
        for i in range(9):
            t = -1 + i / 4
            pts.append(Vector((0, 0.55 * t * t - 0.05, 2.0 * t)))
        for p, q in zip(pts, pts[1:]):
            b.tube(p, q, 0.07, 0.07, WOOD, n=5)
        b.tube(pts[0], pts[-1], 0.015, 0.015, WHITE, n=3)
        b.tube((0, -0.1, -0.25), (0, -0.1, 0.25), 0.1, 0.1, LEATHER, n=6)


def build_trebuchet(b):
    w = 1.7
    for s in (1, -1):
        b.box((s * w, 0, 0.3), (0.45, 10.0, 0.45), WOOD)  # ground rails
        for y in (-2.6, 2.6):
            a, c = Vector((s * w, y, 0.4)), Vector((s * (w - 0.2), 0, 7.2))
            b.tube(a, c, 0.18, 0.15, WOOD, n=4, smooth=False)
        b.tube((s * w, -4.6, 0.4), (s * w, -2.0, 3.2), 0.12, 0.12, WOOD, n=4, smooth=False)  # braces
        b.tube((s * w, 4.6, 0.4), (s * w, 2.0, 3.2), 0.12, 0.12, WOOD, n=4, smooth=False)
    for y in (-4.7, 0.0, 4.7):
        b.box((0, y, 0.3), (2 * w + 0.4, 0.45, 0.4), WOOD)
    b.tube((-w - 0.2, 0, 7.2), (w + 0.2, 0, 7.2), 0.2, 0.2, DARK, n=6)  # axle
    # the throwing arm, cocked: long end down at the back, counterweight up at the front
    pivot = Vector((0, 0, 7.2))
    tip = Vector((0, 7.4, 1.6))
    short = pivot + (pivot - tip).normalized() * 2.4
    b.tube(short, tip, 0.3, 0.14, WOOD, n=6, smooth=False)
    b.box(short + Vector((0, 0, -1.2)), (1.9, 1.6, 1.7), WOOD)  # counterweight box
    b.box(short + Vector((0, 0, -0.4)), (2.0, 1.7, 0.18), STEEL)
    b.box(short + Vector((0, 0, -1.9)), (2.0, 1.7, 0.18), STEEL)
    b.tube(short, short + Vector((0, 0, -0.4)), 0.07, 0.07, LEATHER, n=4)
    b.tube(tip, tip + Vector((0, 1.3, -1.25)), 0.04, 0.04, LEATHER, n=3)  # sling
    b.ellipsoid(tip + Vector((0, 1.35, -1.3)), (0.38, 0.38, 0.34), STEEL, segs=8, rings=5)  # the stone
    b.tube((0, -4.7, 0.6), (0, -4.7, 1.6), 0.25, 0.25, WOOD, n=6)  # winch
    b.tube((-w, -4.7, 1.6), (w, -4.7, 1.6), 0.18, 0.18, WOOD, n=6)


# ---------------------------------------------------------------- export helpers
def reset_with_vanilla():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bie.import_meshfile(os.path.join(GAME, "gfx/models/units/western_european_infantry.mesh"))
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    body = next(o for o in bpy.data.objects if o.type == "MESH" and len(o.data.vertices) > 100)
    coll = next(o for o in bpy.data.objects if o.type == "MESH" and o is not body)
    return rig, body, coll


def pdx_material(template, palette):
    mat = template.copy()
    mat.name = "dv_%s" % palette
    for node in mat.node_tree.nodes:
        if node.type == "TEX_IMAGE" and node.image:
            img = node.image
            fname = os.path.basename(img.filepath)
            if "diffuse" in fname:
                new = "dv_%s_diffuse.dds" % palette
            elif "spec" in fname:
                new = "dv_units_spec.dds"
            else:
                new = "dv_units_normal.dds"
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
    sw = []
    for v in src.data.vertices:
        sw.append({names[g.group]: g.weight for g in v.groups if g.weight > 0})
    groups = {}
    for v in obj.data.vertices:
        if v.index in rigid:
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


def export(path):
    bie.export_meshfile(path, exp_mesh=True, exp_skel=True, exp_locs=True)


def main():
    build_textures()
    rig, body, coll = reset_with_vanilla()
    for bone in rig.data.bones:
        J[bone.name] = tuple(bone.head_local)

    for kind, palettes in BODIES.items():
        for pal in palettes:
            rig, body, coll = reset_with_vanilla()
            template = body.data.materials[0]
            b = Builder()
            build_body(b, kind)
            obj = b.to_object("dv_%s_%s" % (kind, pal))
            obj.data.materials.append(pdx_material(template, pal))
            skin_from(obj, body, rig, b.bones)
            bpy.data.objects.remove(body)
            export(os.path.join(OUT, "dv_%s_%s.mesh" % (kind, pal)))

    for kind in ("spear", "lance", "bow"):
        rig, body, coll = reset_with_vanilla()
        template = body.data.materials[0]
        for o in (rig, body, coll):
            bpy.data.objects.remove(o)
        b = Builder()
        build_weapon(b, kind)
        obj = b.to_object("dv_%s" % kind)
        obj.data.materials.append(pdx_material(template, "levy"))
        export(os.path.join(OUT, "dv_%s.mesh" % kind))

    rig, body, coll = reset_with_vanilla()
    template = body.data.materials[0]
    for o in (rig, body):
        bpy.data.objects.remove(o)
    coll.data.transform(Matrix.Diagonal((2.2, 4.0, 1.4, 1.0)))  # selection box around the engine
    b = Builder()
    build_trebuchet(b)
    obj = b.to_object("dv_trebuchet")
    obj.data.materials.append(pdx_material(template, "levy"))
    export(os.path.join(OUT, "dv_trebuchet.mesh"))


main()

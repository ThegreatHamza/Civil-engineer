"""Low-level drafting engine.

Every sheet is drawn twice at the same time:
  * on a matplotlib figure in paper millimetres (-> PDF / PNG), with frame and title block;
  * in a DXF model space in real metres (-> AutoCAD / any CAD), one DXF per sheet.

A `View` maps model coordinates (metres) to the paper at a given scale (1:50, 1:20 ...).
"""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path  # noqa: E402
import ezdxf  # noqa: E402
from ezdxf.enums import TextEntityAlignment  # noqa: E402
from shapely.geometry.polygon import orient  # noqa: E402

MM2PT = 72.0 / 25.4
LW = {"xthick": 0.70, "thick": 0.50, "med": 0.35, "thin": 0.25, "fine": 0.18, "hair": 0.13}

INK = "#111111"
GREY = "#5c5c5c"
LIGHT = "#9a9a9a"
POCHE = "#cfcfcf"
CONC = "#e6e6e6"
GLASS = "#dcebf5"
AXIS = "#9b2c2c"
REBAR = "#b3261e"
ACCENT = "#1f3b57"

LS = {
    "-": "-",
    "dash": (0, (4, 2.2)),
    "hidden": (0, (3, 1.8)),
    "axis": (0, (14, 3, 2, 3)),
    "dot": (0, (1, 2)),
}
DXF_LT = {"-": "CONTINUOUS", "dash": "DASHED", "hidden": "HIDDEN", "axis": "CENTER", "dot": "DOT"}
DXF_COLOR = {INK: 7, GREY: 8, LIGHT: 9, AXIS: 1, REBAR: 1, ACCENT: 5, POCHE: 9, CONC: 9, GLASS: 4}

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["hatch.linewidth"] = 0.3
plt.rcParams["pdf.fonttype"] = 42

PAPER = {"A2": (594.0, 420.0), "A3": (420.0, 297.0)}
DXF_REF = 0.1  # paper mm -> metres offset of each view inside the sheet's DXF

_ALIGN = {
    ("left", "bottom"): "BOTTOM_LEFT", ("center", "bottom"): "BOTTOM_CENTER", ("right", "bottom"): "BOTTOM_RIGHT",
    ("left", "center"): "MIDDLE_LEFT", ("center", "center"): "MIDDLE_CENTER", ("right", "center"): "MIDDLE_RIGHT",
    ("left", "top"): "TOP_LEFT", ("center", "top"): "TOP_CENTER", ("right", "top"): "TOP_RIGHT",
}


def _pt(mm):
    return mm * MM2PT


def rings_of(geom):
    """Exterior + interior rings of a (Multi)Polygon, correctly oriented for even fill."""
    if geom.is_empty:
        return []
    polys = [geom] if geom.geom_type == "Polygon" else [g for g in geom.geoms if g.geom_type == "Polygon"]
    rings = []
    for p in polys:
        p = orient(p, 1.0)
        rings.append(list(p.exterior.coords))
        rings += [list(r.coords) for r in p.interiors]
    return rings


def _path(rings):
    verts, codes = [], []
    for r in rings:
        if len(r) < 2:
            continue
        verts += list(r) + [r[0]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(r) - 1) + [Path.CLOSEPOLY]
    return Path(verts, codes)


class Sheet:
    def __init__(self, fmt, number, total, title, lot, scale_txt, phase="EXE", date="21/11/2026"):
        self.W, self.H = PAPER[fmt]
        self.fmt = fmt
        self.fig = plt.figure(figsize=(self.W / 25.4, self.H / 25.4))
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, self.W)
        ax.set_ylim(0, self.H)
        ax.set_aspect("equal")
        ax.axis("off")
        self.ax = ax
        self.doc = ezdxf.new("R2010", setup=True)
        self.doc.units = ezdxf.units.M
        self.doc.header["$LTSCALE"] = 0.025
        self.msp = self.doc.modelspace()
        self.number, self.total, self.title, self.lot = number, total, title, lot
        self.scale_txt, self.phase, self.date = scale_txt, phase, date
        self.frame()
        self.title_block()

    # ---------------- paper primitives (mm) ----------------
    def line(self, pts, lw="thin", color=INK, ls="-", z=5, cap="butt"):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=color, lw=_pt(LW.get(lw, lw) if isinstance(lw, str) else lw),
                     linestyle=LS.get(ls, ls), zorder=z, solid_capstyle=cap, dash_capstyle="butt",
                     solid_joinstyle="miter")

    def rings(self, rings, fc="none", ec=INK, lw="thin", hatch=None, hcolor=GREY, z=4, ls="-"):
        if not rings:
            return
        path = _path(rings)
        if fc != "none" or hatch:
            self.ax.add_patch(PathPatch(path, facecolor=fc, edgecolor=hcolor if hatch else "none", lw=0,
                                        hatch=hatch, zorder=z))
        if ec != "none":
            self.ax.add_patch(PathPatch(path, facecolor="none", edgecolor=ec, linestyle=LS.get(ls, ls),
                                        lw=_pt(LW.get(lw, lw) if isinstance(lw, str) else lw), zorder=z + 0.1,
                                        joinstyle="miter"))

    def rect(self, x0, y0, x1, y1, **kw):
        self.rings([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]], **kw)

    def text(self, x, y, s, h=2.5, ha="left", va="bottom", rot=0, weight="normal", color=INK, z=8,
             style="normal", family=None):
        kw = {}
        if family:
            kw["family"] = family
        self.ax.text(x, y, s, fontsize=_pt(h), ha=ha, va=va, rotation=rot, rotation_mode="anchor",
                     fontweight=weight, color=color, zorder=z, fontstyle=style, linespacing=1.25, **kw)

    def circle(self, x, y, r, fc="white", ec=INK, lw="thin", z=6):
        self.ax.add_patch(matplotlib.patches.Circle((x, y), r, facecolor=fc, edgecolor=ec,
                                                    lw=_pt(LW.get(lw, lw) if isinstance(lw, str) else lw),
                                                    zorder=z))

    def view_title(self, x, y, title, scale=None, h=4.2, ha="left"):
        self.text(x, y, title, h=h, weight="bold", ha=ha, color=ACCENT)
        w = len(title) * h * 0.74
        x0 = x if ha == "left" else x - w / 2
        self.line([(x0, y - 1.4), (x0 + w, y - 1.4)], lw="thick", color=ACCENT)
        self.line([(x0, y - 2.4), (x0 + w, y - 2.4)], lw="fine", color=ACCENT)
        if scale:
            self.text(x0 + w + 3, y, f"Éch. {scale}", h=h * 0.7, color=GREY)

    def table(self, x, y, cols, rows, h=2.3, row_h=5.5, header_fill="#e9eef3", title=None, bold_last=False):
        """cols = [(header, width, align)]; rows = list of lists. (x, y) = top-left corner."""
        if title:
            self.text(x, y + 2.5, title, h=3.0, weight="bold", color=ACCENT)
        W = sum(c[1] for c in cols)
        n = len(rows) + 1
        self.rect(x, y - row_h, x + W, y, fc=header_fill, ec="none")
        for i in range(n + 1):
            yy = y - i * row_h
            self.line([(x, yy), (x + W, yy)], lw="thin" if i in (0, 1, n) else "hair")
        cx = x
        for c in cols:
            self.line([(cx, y), (cx, y - n * row_h)], lw="hair")
            cx += c[1]
        self.line([(cx, y), (cx, y - n * row_h)], lw="thin")
        self.line([(x, y), (x, y - n * row_h)], lw="thin")
        for r in range(n):
            vals = [c[0] for c in cols] if r == 0 else rows[r - 1]
            cx = x
            for c, v in zip(cols, vals):
                al = c[2] if len(c) > 2 else "center"
                tx = cx + 1.5 if al == "left" else (cx + c[1] / 2 if al == "center" else cx + c[1] - 1.5)
                bold = r == 0 or (bold_last and r == n - 1)
                self.text(tx, y - r * row_h - row_h / 2, str(v), h=h, ha=al, va="center",
                          weight="bold" if bold else "normal")
                cx += c[1]
        return y - n * row_h

    def notes(self, x, y, title, lines, h=2.4, width=None, lh=1.55):
        self.text(x, y, title, h=3.0, weight="bold", color=ACCENT)
        yy = y - 5
        for ln in lines:
            self.text(x, yy, ln, h=h, va="top")
            yy -= h * lh * (ln.count("\n") + 1)
        return yy

    # ---------------- frame & title block ----------------
    def frame(self):
        W, H = self.W, self.H
        self.rect(20, 10, W - 10, H - 10, lw="xthick")
        self.rect(5, 5, W - 5, H - 5, lw="hair", ec=LIGHT)
        # reference grid marks
        nx, ny = 8, 6
        for i in range(1, nx):
            x = 20 + (W - 30) * i / nx
            self.line([(x, H - 10), (x, H - 5)], lw="hair")
            self.line([(x, 5), (x, 10)], lw="hair")
        for i in range(nx):
            x = 20 + (W - 30) * (i + 0.5) / nx
            self.text(x, H - 7.5, str(i + 1), h=2, ha="center", va="center", color=GREY)
            self.text(x, 7.5, str(i + 1), h=2, ha="center", va="center", color=GREY)
        for j in range(1, ny):
            y = 10 + (H - 20) * j / ny
            self.line([(5, y), (20, y)], lw="hair")
            self.line([(W - 10, y), (W - 5, y)], lw="hair")
        for j in range(ny):
            y = 10 + (H - 20) * (j + 0.5) / ny
            self.text(12.5, y, "ABCDEF"[ny - 1 - j], h=2, ha="center", va="center", color=GREY)
            self.text(W - 7.5, y, "ABCDEF"[ny - 1 - j], h=2, ha="center", va="center", color=GREY)

    def title_block(self):
        W = self.W
        w, x1, y0 = 175.0, W - 10, 10.0
        x0 = x1 - w
        rows = [0, 9, 23, 38, 47, 60, 68]  # cumulative heights from bottom
        top = y0 + rows[-1]
        self.rect(x0, y0, x1, top, fc="white", ec="none", z=3)
        self.rect(x0, y0, x1, top, lw="thick", z=7)
        for r in rows[1:-1]:
            self.line([(x0, y0 + r), (x1, y0 + r)], lw="thin", z=7)
        # header band
        self.rect(x0, y0 + rows[5], x1, top, fc=ACCENT, ec="none", z=6)
        self.text(x0 + 3, y0 + rows[5] + 4, "BUREAU D'ÉTUDES  ·  ARCHITECTURE & GÉNIE CIVIL", h=2.6,
                  va="center", weight="bold", color="white")
        self.text(x1 - 3, y0 + rows[5] + 4, "DOSSIER D'EXÉCUTION", h=2.3, va="center", ha="right",
                  color="white")
        # project
        self.text(x0 + 3, y0 + rows[4] + 10.0, "PROJET :", h=2.0, color=GREY)
        self.text(x0 + 3, y0 + rows[4] + 6.6, "CONSTRUCTION D'UNE HABITATION INDIVIDUELLE EN R.D.C", h=2.9,
                  weight="bold", va="center")
        self.text(x0 + 3, y0 + rows[4] + 1.2, "3 chambres · salon · cuisine · WC · hall — Emprise 15.00 × 8.00 m",
                  h=2.0, color=GREY)
        # lot / phase
        self.line([(x0 + 115, y0 + rows[3]), (x0 + 115, y0 + rows[4])], lw="thin", z=7)
        self.text(x0 + 3, y0 + rows[3] + 4.5, f"LOT :  {self.lot}", h=2.6, weight="bold", va="center")
        self.text(x0 + 118, y0 + rows[3] + 4.5, f"PHASE :  {self.phase}", h=2.6, weight="bold", va="center")
        # title
        self.text(x0 + 3, y0 + rows[2] + 12.2, "DÉSIGNATION DE LA PLANCHE :", h=2.0, color=GREY)
        self.text(x0 + w / 2, y0 + rows[2] + 6.0, self.title, h=4.4, weight="bold", ha="center", va="center",
                  color=ACCENT)
        # scale / date / index / sheet
        cells = [(0, 45, "ÉCHELLE", self.scale_txt), (45, 85, "DATE", self.date), (85, 115, "INDICE", "A"),
                 (115, 175, "PLANCHE N°", f"{self.number:02d} / {self.total:02d}")]
        for a, b, lab, val in cells:
            if a:
                self.line([(x0 + a, y0 + rows[1]), (x0 + a, y0 + rows[2])], lw="thin", z=7)
            self.text(x0 + a + 2, y0 + rows[2] - 3, lab, h=1.9, color=GREY, va="center")
            big = lab == "PLANCHE N°"
            self.text(x0 + (a + b) / 2, y0 + rows[1] + 5, val, h=5.0 if big else 3.2, ha="center",
                      va="center", weight="bold")
        # signatures
        for i, lab in enumerate(["Dessiné par :", "Vérifié par :", "Approuvé par :"]):
            xa = x0 + i * w / 3
            if i:
                self.line([(xa, y0), (xa, y0 + rows[1])], lw="thin", z=7)
            self.text(xa + 2, y0 + 4.5, lab, h=2.0, color=GREY, va="center")

    def north_arrow(self, x, y, r=9):
        self.circle(x, y, r, fc="white", lw="thin")
        self.ax.add_patch(matplotlib.patches.Polygon([(x, y + r * 0.95), (x - r * 0.38, y - r * 0.6), (x, y - r * 0.3)],
                                                     closed=True, fc=INK, ec=INK, lw=0.4, zorder=7))
        self.ax.add_patch(matplotlib.patches.Polygon([(x, y + r * 0.95), (x + r * 0.38, y - r * 0.6), (x, y - r * 0.3)],
                                                     closed=True, fc="white", ec=INK, lw=0.4, zorder=7))
        self.text(x, y + r + 1.5, "N", h=4, ha="center", weight="bold")

    def save(self, pdf, png_path=None, dxf_path=None, dpi=110):
        pdf.savefig(self.fig)
        if png_path:
            self.fig.savefig(png_path, dpi=dpi, facecolor="white")
        if dxf_path:
            self.doc.saveas(dxf_path)
        plt.close(self.fig)


class View:
    """Model (metres) -> paper (mm) mapping, mirrored into the sheet's DXF in metres."""

    def __init__(self, sheet, ox, oy, scale):
        self.s, self.ox, self.oy, self.scale = sheet, ox, oy, scale
        self.k = 1000.0 / scale
        self.dx, self.dy = ox * DXF_REF, oy * DXF_REF

    def P(self, x, y):
        return (self.ox + x * self.k, self.oy + y * self.k)

    def m(self, mm):
        """paper millimetres -> model metres"""
        return mm / self.k

    def _d(self, pts):
        return [(x + self.dx, y + self.dy) for x, y in pts]

    def _attr(self, layer, color=INK, ls="-"):
        return {"layer": layer, "color": DXF_COLOR.get(color, 7), "linetype": DXF_LT.get(ls, "CONTINUOUS")}

    # ---- primitives ----
    def line(self, pts, lw="thin", color=INK, ls="-", layer="0", z=5, dxf=True, cap="butt"):
        self.s.line([self.P(*p) for p in pts], lw=lw, color=color, ls=ls, z=z, cap=cap)
        if dxf:
            self.s.msp.add_lwpolyline(self._d(pts), dxfattribs=self._attr(layer, color, ls))

    def seg(self, x0, y0, x1, y1, **kw):
        self.line([(x0, y0), (x1, y1)], **kw)

    def rings(self, rings, fc="none", ec=INK, lw="thin", hatch=None, hcolor=GREY, layer="0", z=4, ls="-",
              dxf=True, dxf_pattern=None):
        self.s.rings([[self.P(*p) for p in r] for r in rings], fc=fc, ec=ec, lw=lw, hatch=hatch, hcolor=hcolor,
                     z=z, ls=ls)
        if not dxf:
            return
        if ec != "none":
            for r in rings:
                self.s.msp.add_lwpolyline(self._d(r), close=True, dxfattribs=self._attr(layer, ec, ls))
        if fc != "none" or hatch:
            h = self.s.msp.add_hatch(color=DXF_COLOR.get(fc, 8), dxfattribs={"layer": layer + "-HATCH"})
            if hatch:
                h.set_pattern_fill(dxf_pattern or "ANSI31", scale=0.02 * self.scale / 50, color=8)
            for r in rings:
                h.paths.add_polyline_path(self._d(r), is_closed=True)

    def geom(self, g, **kw):
        self.rings(rings_of(g), **kw)

    def rect(self, x0, y0, x1, y1, **kw):
        self.rings([[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]], **kw)

    def poly(self, pts, **kw):
        self.rings([pts], **kw)

    def arcpts(self, cx, cy, r, a0, a1, n=24):
        return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                 cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

    def circle(self, cx, cy, r, fc="none", ec=INK, lw="thin", layer="0", z=5, n=36):
        pts = self.arcpts(cx, cy, r, 0, 360, n)[:-1]
        self.rings([pts], fc=fc, ec=ec, lw=lw, layer=layer, z=z)

    def dot(self, cx, cy, r, color=REBAR, layer="S-REBAR", z=9):
        """filled bar section (r in model metres)"""
        self.circle(cx, cy, r, fc=color, ec=color, lw="hair", layer=layer, z=z, n=16)

    def text(self, x, y, s, h=2.5, ha="left", va="bottom", rot=0, weight="normal", color=INK, layer="A-TEXT",
             z=8, dxf=True, style="normal"):
        px, py = self.P(x, y)
        self.s.text(px, py, s, h=h, ha=ha, va=va, rot=rot, weight=weight, color=color, z=z, style=style)
        if dxf:
            for i, ln in enumerate(s.split("\n")):
                t = self.s.msp.add_text(ln, height=self.m(h) * 0.72,
                                        dxfattribs={"layer": layer, "rotation": rot,
                                                    "color": DXF_COLOR.get(color, 7)})
                yy = y - i * self.m(h) * 1.25
                t.set_placement((x + self.dx, yy + self.dy), align=TextEntityAlignment[_ALIGN[(ha, va if va in ("bottom", "center", "top") else "bottom")]])

    def label_box(self, x, y, s, h=2.3, pad=1.0, fc="white", ec=INK, layer="A-TEXT", weight="normal"):
        """Text centred in a framed box (paper-sized)."""
        w = len(s) * h * 0.62 + 2 * pad
        hh = h + 2 * pad
        px, py = self.P(x, y)
        self.s.rect(px - w / 2, py - hh / 2, px + w / 2, py + hh / 2, fc=fc, ec=ec, lw="fine", z=7.5)
        self.text(x, y, s, h=h, ha="center", va="center", layer=layer, weight=weight)

    # ---- dimensions ----
    def dim(self, vals, at, orient="h", ext_from=None, side=1, h=2.2, layer="A-DIMS", fmt="{:.2f}",
            labels=None, color=INK):
        """Chain dimension. vals: coordinates along the measured axis. at: position of dimension line.
        ext_from: coordinate where extension lines start (object side). side: text side (+1 above/right)."""
        vals = list(vals)
        g = self.m(1.2)    # gap between object and extension line
        ov = self.m(1.6)   # overshoot
        tk = self.m(1.3)   # tick half-length

        def T(a, b):  # (along, across) -> (x, y)
            return (a, b) if orient == "h" else (b, a)

        a0, a1 = vals[0] - ov, vals[-1] + ov
        self.line([T(a0, at), T(a1, at)], lw="fine", layer=layer, color=color)
        for v in vals:
            if ext_from is not None:
                d = 1 if at > ext_from else -1
                self.line([T(v, ext_from + d * g), T(v, at + d * ov)], lw="hair", layer=layer, color=color)
            else:
                self.line([T(v, at - ov), T(v, at + ov)], lw="hair", layer=layer, color=color)
            # architectural tick (45 deg)
            self.line([T(v - tk, at - tk), T(v + tk, at + tk)] if orient == "h" else
                      [T(v + tk, at - tk), T(v - tk, at + tk)], lw="med", layer=layer, color=color)
        stagger = 0
        for i in range(len(vals) - 1):
            a, b = vals[i], vals[i + 1]
            txt = labels[i] if labels else fmt.format(b - a)
            seglen = (b - a) * self.k
            need = len(txt) * h * 0.6 + 1.5
            off = self.m(0.9 + (h + 0.6) * stagger) * side
            if seglen < need:
                stagger = 1 - stagger if stagger in (0, 1) else 0
            else:
                stagger = 0
            mid = (a + b) / 2
            va = "bottom" if side > 0 else "top"
            if orient == "h":
                self.text(mid, at + off, txt, h=h, ha="center", va=va, layer=layer, color=color)
            else:
                self.text(at - off, mid, txt, h=h, ha="center", va=va, rot=90, layer=layer, color=color)

    # ---- symbols ----
    def axis(self, p0, p1, label, r_mm=4.2, ends=(True, True), layer="A-AXES"):
        """Grid axis with bubbles at the chosen ends."""
        self.line([p0, p1], lw="fine", color=AXIS, ls="axis", layer=layer, z=2)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        r = self.m(r_mm)
        for use, (px, py), sgn in ((ends[0], p0, -1), (ends[1], p1, 1)):
            if not use:
                continue
            cx, cy = px + sgn * ux * r, py + sgn * uy * r
            self.circle(cx, cy, r, fc="white", ec=AXIS, lw="thin", layer=layer, z=6)
            self.text(cx, cy, label, h=3.4, ha="center", va="center", weight="bold", color=AXIS, layer=layer)

    def level(self, x, z, txt, side=1, length_mm=16, h=2.3, layer="A-TEXT", color=INK, under=False):
        """Elevation level mark: triangle on the level line + leader + text."""
        t = self.m(1.6)
        self.poly([(x, z), (x - t, z + t * 1.6), (x + t, z + t * 1.6)], fc=color if not under else "white",
                  ec=color, lw="fine", layer=layer, z=7)
        L = self.m(length_mm) * side
        self.line([(x, z), (x + L, z)], lw="fine", layer=layer, color=color)
        self.text(x + self.m(2.6) * side, z + self.m(0.8), txt, h=h, ha="left" if side > 0 else "right",
                  layer=layer, color=color)

    def plan_level(self, x, y, txt, h=2.1):
        px, py = self.P(x, y)
        w = len(txt) * h * 0.62 + 5
        self.s.rect(px - 2, py - 2, px - 2 + w, py + 2.4, fc="white", ec=INK, lw="fine", z=7.5)
        self.s.ax.add_patch(matplotlib.patches.Polygon([(px, py - 1.2), (px + 1.4, py + 1.2), (px - 1.4, py + 1.2)],
                                                       closed=True, fc=INK, lw=0, zorder=8))
        self.s.text(px + 2.4, py + 0.2, txt, h=h, va="center", z=8)

    def break_line(self, p0, p1, layer="0"):
        (x0, y0), (x1, y1) = p0, p1
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        a = self.m(2.2)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        pts = [(x0 - ux * a, y0 - uy * a), (mx - ux * a, my - uy * a), (mx - ux * a * 0.4 + nx * a * 1.4, my - uy * a * 0.4 + ny * a * 1.4),
               (mx + ux * a * 0.4 - nx * a * 1.4, my + uy * a * 0.4 - ny * a * 1.4), (mx + ux * a, my + uy * a),
               (x1 + ux * a, y1 + uy * a)]
        self.line(pts, lw="fine", layer=layer)

    def leader(self, pts, txt, h=2.2, ha="left", layer="A-TEXT", color=INK, va="center"):
        self.line(pts, lw="fine", layer=layer, color=color)
        x, y = pts[0]
        r = self.m(0.5)
        self.circle(x, y, r, fc=color, ec=color, lw="hair", layer=layer, n=8)
        ex, ey = pts[-1]
        self.text(ex + (self.m(1) if ha == "left" else -self.m(1)), ey, txt, h=h, ha=ha, va=va, layer=layer,
                  color=color)

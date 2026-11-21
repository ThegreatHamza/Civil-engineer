"""Structural calculations (BAEL 91 mod. 99 / CBA 93, RPA 99 v.2003, DTR B.C 2.2).

All results used by the calculation note (note_calcul.py) and checked against the
reinforcement shown on the drawings. Units: kN, m, kN·m, MPa (= MN/m²), cm² for steel areas.
"""
import math

import model as M

# ------------------------------------------------------------------ materials
FC28 = 25.0
FT28 = 0.6 + 0.06 * FC28                  # 2.1 MPa
GB, GS = 1.5, 1.15
FBU = 0.85 * FC28 / GB                    # 14.17 MPa
SBC = 0.6 * FC28                          # 15 MPa
FE = 400.0
FSU = FE / GS                             # 347.8 MPa
ETA = 1.6
SS_PREJ = min(2 / 3 * FE, max(0.5 * FE, 110 * math.sqrt(ETA * FT28)))   # 201.6 MPa (fissuration préjudiciable)
MU_L = 0.392                              # FeE400
EIJ = 11000 * FC28 ** (1 / 3)             # 32 164 MPa
SIGMA_SOL = 200.0                         # kPa = 2.0 bars (hypothèse)
GAMMA_SOIL = 18.0
GAMMA_BA = 25.0

AREA = {6: 0.283, 8: 0.503, 10: 0.785, 12: 1.131, 14: 1.539, 16: 2.011}   # cm² per bar


def As(n, phi):
    return n * AREA[phi]


# ------------------------------------------------------------------ loads
TERRACE = [  # (layer, thickness m or None, unit weight kN/m3 or None, G kN/m2)
    ("Protection en gravillons roulés", 0.05, 20.0, None),
    ("Étanchéité multicouche", None, None, 0.12),
    ("Isolation thermique en liège", 0.04, 4.0, None),
    ("Forme de pente en béton maigre (ép. moyenne)", 0.08, 22.0, None),
    ("Plancher à corps creux (20 + 4)", None, None, 3.20),
    ("Enduit plâtre sous plafond", 0.02, 10.0, None),
]


def terrace_loads():
    rows, tot = [], 0.0
    for lab, e, g, G in TERRACE:
        val = G if G is not None else e * g
        rows.append((lab, e, g, round(val, 2)))
        tot += val
    return rows, round(tot, 2)


G_T_CALC = terrace_loads()[1]       # 6.44
G_T = 6.50                          # retained (rounded up)
Q_T = 1.00                          # terrasse inaccessible (DTR B.C 2.2)
PU_S = 1.35 * G_T + 1.5 * Q_T       # 10.275 kN/m2
PS_S = G_T + Q_T                    # 7.50

EXT_WALL = [("Brique creuse 15 cm", 1.30), ("Brique creuse 10 cm", 0.90),
            ("Enduit ciment extérieur 2 cm (18 kN/m³)", 0.36), ("Enduit plâtre intérieur 1.5 cm", 0.15)]
INT_WALL = [("Brique creuse 10 cm", 0.90), ("Enduit plâtre 1.5 cm × 2 faces", 0.30)]
G_EXT = round(sum(v for _, v in EXT_WALL), 2)      # 2.71 kN/m2
G_INT = round(sum(v for _, v in INT_WALL), 2)      # 1.20 kN/m2
ACRO_G = 0.10 * 0.60 * GAMMA_BA + 0.10             # 1.60 kN/m (with coping)
H_WALL_X = M.Z_PP_SOF - M.Z_LONG_TOP               # 2.84 under PP
H_WALL_Y = M.Z_PS_SOF - M.Z_LONG_TOP               # 2.94 under PS


# ------------------------------------------------------------------ helpers
def flex(Mu, b, d):
    """Simple bending ELU, rectangular section. Mu kN·m, b,d m -> dict (As cm²)."""
    mu = Mu / 1000 / (b * d * d * FBU)
    assert mu < MU_L, "compression steel needed"
    alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
    z = d * (1 - 0.4 * alpha)
    A = Mu / 1000 / (z * FSU) * 1e4
    return dict(mu=mu, alpha=alpha, z=z, As=A)


def amin_bael(b, d):
    return 0.23 * b * d * FT28 / FE * 1e4


def sigma_bc(Mser, b, d, A_cm2, n=15):
    """Concrete stress at SLS, rectangular cracked section (tension steel only)."""
    A = A_cm2 * 1e-4
    # b y²/2 + n A y - n A d = 0
    y = (-n * A + math.sqrt((n * A) ** 2 + 2 * b * n * A * d)) / b
    I = b * y ** 3 / 3 + n * A * (d - y) ** 2
    return Mser / 1000 * y / I, y, I


def shear(Vu, b0, d, st, At_cm2, k=1.0):
    tau = Vu / 1000 / (b0 * d)
    tau_lim = min(0.2 * FC28 / GB, 5.0)
    need = (tau - 0.3 * k * FT28) / (0.9 * FSU) * b0 * st * 1e4    # cm²
    need_min = 0.4 * b0 * st / FE * 1e4
    return dict(tau=tau, tau_lim=tau_lim, At_need=max(need, need_min), At=At_cm2, st_max=min(0.9 * d, 0.40))


# ------------------------------------------------------------------ 1. joists (poutrelles)
def poutrelles():
    b, b0, h, h0 = 0.65, 0.12, 0.24, 0.04
    d = 0.9 * h
    qu, qs = PU_S * b, PS_S * b
    lw, le = 5.0 - 0.30, 3.0 - 0.30                 # clear spans (nus)
    # Caquot (2 spans, intermediate support B)
    Ma = (qu * lw ** 3 + qu * le ** 3) / (8.5 * (lw + le))
    Mas = Ma * qs / qu
    M0 = qu * lw ** 2 / 8
    x0 = lw / 2 - Ma / (qu * lw)
    Mt = qu * x0 * (lw - x0) / 2 - Ma * x0 / lw
    Mts = Mt * qs / qu
    Vw = qu * lw / 2 - Ma / lw
    Vb1 = qu * lw / 2 + Ma / lw
    Vb2 = qu * le / 2 + Ma / le
    Ve = qu * le / 2 - Ma / le
    Mtu_table = FBU * 1000 * b * h0 * (d - h0 / 2)
    ft = flex(Mt, b, d)
    fa = flex(Ma, b0, d)
    A_t = As(2, 12)
    A_a = As(2, 12)
    sh = shear(max(Vb1, Vb2), b0, d, 0.15, 2 * AREA[6])
    sig = sigma_bc(Mts, b, d, A_t)[0]
    # deflection conditions (BAEL B.6.5.1)
    fl = [("h / L ≥ 1 / 22.5", h / lw, 1 / 22.5), ("h / L ≥ Mt / (15·M0)", h / lw, Mt / (15 * M0)),
          ("A / (b0·d) ≤ 3.6 / fe", A_t / 1e4 / (b0 * d), 3.6 / FE)]
    # compression slab mesh
    A_perp = 4 * b * 100 / 520      # cm²/ml (l in cm, fe = 520 MPa)
    return dict(b=b, b0=b0, h=h, h0=h0, d=d, qu=qu, qs=qs, lw=lw, le=le, Ma=Ma, Mas=Mas, M0=M0, x0=x0, Mt=Mt,
                Mts=Mts, Vw=Vw, Vb1=Vb1, Vb2=Vb2, Ve=Ve, Mtu_table=Mtu_table, ft=ft, fa=fa, A_t=A_t, A_a=A_a,
                Amin=amin_bael(b0, d), sh=sh, sig=sig, fl=fl, A_perp=A_perp, A_par=A_perp / 2, A_ts=5 * AREA[6])


P = poutrelles()


# ------------------------------------------------------------------ 2. main beams PP (forfaitaire)
def beam_PP():
    b, h = 0.30, 0.45
    d = h - 0.06                    # two layers
    L = 5.0 - 0.30
    g_self = b * h * GAMMA_BA + b * (G_T - 3.20)        # 3.375 + 0.99
    res = {}
    for axis, name in ((5.0, "B"), (0.0, "A"), (8.0, "C")):
        if name == "B":
            ru = (P["Vb1"] + P["Vb2"]) / P["b"]
            rs = ru * P["qs"] / P["qu"]
            Gbeam = G_T * 4.0 + g_self
            Qbeam = Q_T * 4.0
            acro = 0
        elif name == "A":
            ru = P["Vw"] / P["b"]
            rs = ru * P["qs"] / P["qu"]
            Gbeam, Qbeam, acro = G_T * 2.5 + g_self, Q_T * 2.5, ACRO_G
        else:
            ru = P["Ve"] / P["b"]
            rs = ru * P["qs"] / P["qu"]
            Gbeam, Qbeam, acro = G_T * 1.5 + g_self, Q_T * 1.5, ACRO_G
        pu = ru + 1.35 * (g_self + acro)
        ps = rs + g_self + acro
        alpha = Qbeam / (Gbeam + Qbeam)
        M0 = pu * L ** 2 / 8
        M0s = ps * L ** 2 / 8
        Ma_int, Ma_rive = 0.5 * M0, 0.15 * M0
        Mt_rive = max(max(1 + 0.3 * alpha, 1.05) * M0 - (0 + Ma_int) / 2, (1.2 + 0.3 * alpha) / 2 * M0)
        Mt_int = max(max(1 + 0.3 * alpha, 1.05) * M0 - Ma_int, (1 + 0.3 * alpha) / 2 * M0)
        Mts = Mt_rive * M0s / M0
        Vu = 1.15 * pu * L / 2
        res[name] = dict(pu=pu, ps=ps, alpha=alpha, M0=M0, M0s=M0s, Ma_int=Ma_int, Ma_rive=Ma_rive, Mt_rive=Mt_rive,
                         Mt_int=Mt_int, Mts=Mts, Vu=Vu, ru=ru)
    B = res["B"]
    ft = flex(B["Mt_rive"], b, d)
    fa = flex(B["Ma_int"], b, h - 0.045)
    A_bot = As(6, 16)
    A_top_sup = As(6, 14)
    sig = sigma_bc(B["Mts"], b, d, A_bot)[0]
    sh = shear(B["Vu"], b, h - 0.045, 0.15, 4 * AREA[8])
    fl = [("h / L ≥ 1 / 16", h / L, 1 / 16), ("h / L ≥ Mt / (10·M0)", h / L, B["Mt_rive"] / (10 * B["M0"])),
          ("A / (b·d) ≤ 4.2 / fe", A_bot / 1e4 / (b * d), 4.2 / FE)]
    rpa = dict(Amin=0.005 * b * h * 1e4, A_tot=As(3, 16) + As(3, 14), st_nod=min(h / 4, 12 * 1.4 / 100),
               st_cour=h / 2, At_min=0.003 * 0.15 * b * 1e4)
    return dict(b=b, h=h, d=d, L=L, g_self=g_self, axes=res, ft=ft, fa=fa, A_bot=A_bot, A_top_sup=A_top_sup,
                sig=sig, sh=sh, fl=fl, rpa=rpa, Amin=amin_bael(b, d), A_A=flex(res["A"]["Mt_rive"], b, h - 0.045))


PP = beam_PP()


# ------------------------------------------------------------------ 3. secondary beams PS (Caquot)
def beam_PS():
    b, h = 0.30, 0.35
    d = h - 0.035
    g_self = b * h * GAMMA_BA
    strip = P["b"]                       # slab strip carried (one joist spacing)
    G = g_self + G_T * strip + ACRO_G
    Q = Q_T * strip
    pu, ps = 1.35 * G + 1.5 * Q, G + Q
    lw, le = 4.70, 2.70
    Ma = pu * (lw ** 3 + le ** 3) / (8.5 * (lw + le))
    x0 = lw / 2 - Ma / (pu * lw)
    Mt = pu * x0 * (lw - x0) / 2 - Ma * x0 / lw
    V = pu * lw / 2 + Ma / lw
    ft, fa = flex(Mt, b, d), flex(Ma, b, d)
    sh = shear(V, b, d, 0.15, 3 * AREA[8])
    rpa = dict(Amin=0.005 * b * h * 1e4, A_tot=As(3, 14) + As(3, 12), st_nod=min(h / 4, 12 * 1.2 / 100),
               st_cour=h / 2, At_min=0.003 * 0.15 * b * 1e4)
    return dict(b=b, h=h, d=d, G=G, Q=Q, pu=pu, ps=ps, Ma=Ma, Mt=Mt, x0=x0, V=V, ft=ft, fa=fa, sh=sh, rpa=rpa,
                A_bot=As(3, 14), A_top=As(3, 12) + As(2, 12), sig=sigma_bc(Mt * ps / pu, b, d, As(3, 14))[0])


PS = beam_PS()


# ------------------------------------------------------------------ 4. load descent (columns + footings)
def _trib(v, axes):
    i = axes.index(v)
    lo = (axes[i] - axes[i - 1]) / 2 if i > 0 else 0.0
    hi = (axes[i + 1] - axes[i]) / 2 if i < len(axes) - 1 else 0.0
    return lo, hi


def _overlap(a0, a1, segs):
    return sum(max(0.0, min(a1, s1) - max(a0, s0)) for s0, s1 in segs)


WALLS_ON_X = {0.0: [("ext", 0, 15)], 8.0: [("ext", 0, 15)], 5.0: [("int", 0, 15)]}       # walls along y = const
WALLS_ON_Y = {0.0: [("ext", 0, 8)], 15.0: [("ext", 0, 8)], 5.0: [("int", 5, 8)], 10.0: [("int", 5, 8)]}


def descent(x, y):
    xl, xh = _trib(x, M.XA)
    yl, yh = _trib(y, M.YA)
    area = (xl + xh) * (yl + yh)
    kx = 1.10 if x in (5.0, 10.0) else 1.0        # 3-span PP: first interior supports
    ky = 1.15 if y == 5.0 else 1.0                # 2-span joists: interior support
    k = max(kx, ky)
    rows = []
    rows.append(("Plancher terrasse G", G_T * area * k, 0))
    rows.append(("Plancher terrasse Q", 0, Q_T * area * k))
    per = 0.0
    if y in (0.0, 8.0):
        per += xl + xh
    if x in (0.0, 15.0):
        per += yl + yh
    if per:
        rows.append(("Acrotère", ACRO_G * per, 0))
    rows.append(("Poutres PP (retombée 30×21)", 0.30 * 0.21 * GAMMA_BA * (xl + xh), 0))
    rows.append(("Poutres PS (retombée 30×11)", 0.30 * 0.11 * GAMMA_BA * (yl + yh), 0))
    rows.append(("Poteau 30×30 (h = 2.84 m)", 0.09 * GAMMA_BA * H_WALL_X, 0))
    Ncol_G = sum(r[1] for r in rows)
    Ncol_Q = sum(r[2] for r in rows)
    # loads brought by tie beams to the footing
    rows2 = []
    Ltb = (xl + xh) + (yl + yh)
    rows2.append(("Longrines 30×40", 0.30 * 0.40 * GAMMA_BA * Ltb, 0))
    wall = 0.0
    for kind, a, b in WALLS_ON_X.get(y, []):
        L = _overlap(x - xl, x + xh, [(a, b)])
        wall += L * (G_EXT if kind == "ext" else G_INT) * H_WALL_X
    for kind, a, b in WALLS_ON_Y.get(x, []):
        L = _overlap(y - yl, y + yh, [(a, b)])
        wall += L * (G_EXT if kind == "ext" else G_INT) * H_WALL_Y
    if wall:
        rows2.append(("Murs sur longrines", wall, 0))
    t = M.footing_type(x, y)
    a, hs = M.FOOTINGS[t]
    ztop = M.footing_top(x, y)
    rows2.append(("Amorce de poteau", 0.09 * GAMMA_BA * (M.Z_LONG_TOP - ztop), 0))
    Nf_G = Ncol_G + sum(r[1] for r in rows2)
    Nf_Q = Ncol_Q
    self_f = a * a * hs * GAMMA_BA
    soil = (a * a - 0.09) * (M.Z_TN - ztop) * GAMMA_SOIL
    Nser_tot = Nf_G + Nf_Q + self_f + soil
    sigma = Nser_tot / (a * a)
    return dict(x=x, y=y, name=f"{M.YL[M.YA.index(y)]}{M.XL[M.XA.index(x)]}", area=area, k=k, rows=rows, rows2=rows2,
                Ncol_s=Ncol_G + Ncol_Q, Ncol_u=1.35 * Ncol_G + 1.5 * Ncol_Q, Nf_s=Nf_G + Nf_Q,
                Nf_u=1.35 * Nf_G + 1.5 * Nf_Q, type=t, a=a, hs=hs, self_f=self_f, soil=soil, Nser_tot=Nser_tot,
                sigma=sigma)


DESC = [descent(x, y) for (x, y) in M.COLUMNS]


def columns():
    a = 0.30
    worst = max(DESC, key=lambda r: r["Ncol_u"])
    l0 = M.Z_SLAB - M.Z_LONG_TOP           # 3.29 m
    lf = 0.7 * l0
    lam = lf * math.sqrt(12) / a
    alpha = 0.85 / (1 + 0.2 * (lam / 35) ** 2)
    Br = (a - 0.02) ** 2
    A = As(8, 12)
    Nlim = alpha * (Br * FC28 * 1000 / (0.9 * GB) + A / 1e4 * FE * 1000 / GS)
    nu = worst["Ncol_s"] / 1000 / (a * a * FC28)
    rpa = dict(Amin=0.008 * a * a * 1e4, Amax=0.04 * a * a * 1e4, A=A, min_dim=25, he20=(M.Z_PP_SOF - M.Z_LONG_TOP) / 20,
               t_nod=min(10 * 1.2, 15), t_cour=15 * 1.2, lam_g=lf / a)
    At_min = 0.003 * 0.15 * a * 1e4
    At = 2 * AREA[8] + 2 * AREA[8] * math.cos(math.radians(45))
    return dict(a=a, worst=worst, l0=l0, lf=lf, lam=lam, alpha=alpha, Br=Br, A=A, Nlim=Nlim, nu=nu, rpa=rpa,
                At_min=At_min, At=At)


COL = columns()


# ------------------------------------------------------------------ 5. seismic (RPA 99 v2003, méthode statique équivalente)
def seismic():
    A_z = 0.15          # zone IIa, groupe d'usage 2
    R = 3.5             # portiques autostables en BA avec remplissage en maçonnerie rigide
    Q = 1.20            # facteur de qualité (hypothèse : 1 + Σ Pq)
    xi = 7.0            # %
    eta = math.sqrt(7 / (2 + xi))
    T2 = 0.50           # site S3 (meuble) supposé
    hN = M.Z_SLAB
    CT = 0.050
    T = CT * hN ** 0.75
    D = 2.5 * eta if T <= T2 else 2.5 * eta * (T2 / T) ** (2 / 3)
    Wrows = []
    Sroof = (M.LX + 0.30) * (M.LY + 0.30)
    Wrows.append(("Plancher terrasse (G = 6.50 kN/m²)", G_T * Sroof))
    Wrows.append(("Retombées poutres PP", 0.30 * 0.21 * GAMMA_BA * 3 * 14.10))
    Wrows.append(("Retombées poutres PS", 0.30 * 0.11 * GAMMA_BA * 4 * 7.40))
    Wrows.append(("Acrotère", ACRO_G * 46.80))
    Wrows.append(("Poteaux (demi-hauteur)", 12 * 0.09 * GAMMA_BA * H_WALL_X / 2))
    Wrows.append(("Murs extérieurs (demi-hauteur)", G_EXT * (2 * 14.10 + 2 * 7.40) * H_WALL_X / 2))
    Wrows.append(("Cloisons intérieures (demi-hauteur)", G_INT * 33.80 * 3.0 / 2))
    WG = sum(v for _, v in Wrows)
    beta = 0.20
    WQ = beta * Q_T * Sroof
    W = WG + WQ
    V = A_z * D * Q * W / R
    # column checks
    ncol = 12
    Vc = V / ncol
    he = M.Z_PP_SOF - M.Z_LONG_TOP
    Mc = Vc * he / 2
    I = 0.30 ** 4 / 12
    kcol = 12 * EIJ * 1000 * I / he ** 3
    delta_e = V / (ncol * kcol)
    delta_k = R * delta_e
    theta = W * delta_k / (V * he)
    return dict(A=A_z, R=R, Q=Q, xi=xi, eta=eta, T2=T2, hN=hN, CT=CT, T=T, D=D, Wrows=Wrows, WG=WG, WQ=WQ, W=W, V=V,
                Vc=Vc, he=he, Mc=Mc, kcol=kcol, delta_e=delta_e, delta_k=delta_k, theta=theta, Sroof=Sroof)


SEI = seismic()


def column_NM(N, Mreq):
    """Resisting moment of the 30×30 column (3T12 per face) under N, accidental combination."""
    b, d, dp = 0.30, 0.26, 0.04
    fbu = 0.85 * FC28 / 1.15
    A1 = As(3, 12) / 1e4
    fs = FE
    # solve 0.8 y b fbu + A' σs'(y) - A fs = N
    lo, hi = 0.041, 0.26
    for _ in range(80):
        y = (lo + hi) / 2
        ss = min(fs, 200000 * 0.0035 * (y - dp) / y)
        f = 0.8 * y * b * fbu * 1000 + A1 * ss * 1000 - A1 * fs * 1000 - N
        lo, hi = (y, hi) if f < 0 else (lo, y)
    ss = min(fs, 200000 * 0.0035 * (y - dp) / y)
    MR = 0.8 * y * b * fbu * 1000 * (0.15 - 0.4 * y) + A1 * ss * 1000 * (0.15 - dp) + A1 * fs * 1000 * (d - 0.15)
    return dict(y=y, ss=ss, MR=MR, Mreq=Mreq)


# ------------------------------------------------------------------ 6. footings & tie beams
def footings():
    out = {}
    for t, (a, hs) in M.FOOTINGS.items():
        cols = [r for r in DESC if r["type"] == t]
        w = max(cols, key=lambda r: r["sigma"])
        d = hs - 0.05
        A_need = w["Nf_s"] * (a - 0.30) / (8 * d * SS_PREJ * 1000) * 1e4
        n = math.ceil((a - 0.10) / 0.15 - 1e-9) + 1
        out[t] = dict(a=a, hs=hs, d=d, cols=[c["name"] for c in cols], worst=w, rigid=(a - 0.30) / 4,
                      A_need=A_need, n=n, A=As(n, 12), A_min_area=w["Nser_tot"] / SIGMA_SOL)
    return out


FOOT = footings()


def longrines():
    b, h = 0.30, 0.40
    Nmax = max(r["Ncol_u"] for r in DESC)
    F = max(Nmax / 15, 20.0)                 # RPA 10.1.1 : α = 15 (zone IIa, site S3)
    A_trac = F / 1000 / FSU * 1e4
    Amin = 0.006 * b * h * 1e4
    q = 1.35 * (G_EXT * H_WALL_X + b * h * GAMMA_BA)
    L = max(Lc for _, Lc in M.longrine_spans())
    Mu = q * L ** 2 / 10
    f = flex(Mu, b, h - 0.04)
    return dict(b=b, h=h, Nmax=Nmax, F=F, A_trac=A_trac, Amin=Amin, q=q, L=L, Mu=Mu, f=f, A=As(6, 14),
                st=min(0.20, 15 * 1.4 / 100), Ltot=M.longrine_length())


LONG = longrines()


# ------------------------------------------------------------------ 7. parapet
def acrotere():
    h, e = 0.60, 0.10
    Wp = e * h * GAMMA_BA
    Fp = 4 * 0.15 * 0.80 * Wp
    Fh = max(Fp, 1.0)
    Mu, Ms = 1.5 * Fh * h, Fh * h
    Nu = 1.35 * Wp
    d = 0.08
    f = flex(Mu, 1.0, d)
    Amin = amin_bael(1.0, d)
    A = 5 * AREA[8]
    ss = Ms / 1000 / (A / 1e4 * 0.9 * d)
    return dict(h=h, e=e, Wp=Wp, Fp=Fp, Fh=Fh, Mu=Mu, Ms=Ms, Nu=Nu, d=d, f=f, Amin=Amin, A=A, Arep=A / 4,
                A_rep=4 * AREA[8], ss=ss)


ACRO = acrotere()


def checks():
    """Every verification as (label, value, limit, ok)."""
    c = []
    c.append(("Poutrelle travée : A prévue ≥ A calculée (cm²)", P["A_t"], P["ft"]["As"], P["A_t"] >= P["ft"]["As"]))
    c.append(("Poutrelle appui : chapeau ≥ A calculée (cm²)", P["A_a"], P["fa"]["As"], P["A_a"] >= P["fa"]["As"]))
    c.append(("Poutrelle : τu ≤ τ̄u (MPa)", P["sh"]["tau"], P["sh"]["tau_lim"], P["sh"]["tau"] <= P["sh"]["tau_lim"]))
    c.append(("PP travée : A prévue ≥ A calculée (cm²)", PP["A_bot"], PP["ft"]["As"], PP["A_bot"] >= PP["ft"]["As"]))
    c.append(("PP appui : A prévue ≥ A calculée (cm²)", PP["A_top_sup"], PP["fa"]["As"], PP["A_top_sup"] >= PP["fa"]["As"]))
    c.append(("PP : σbc ≤ 15 MPa", PP["sig"], SBC, PP["sig"] <= SBC))
    c.append(("PP : τu ≤ τ̄u (MPa)", PP["sh"]["tau"], PP["sh"]["tau_lim"], PP["sh"]["tau"] <= PP["sh"]["tau_lim"]))
    c.append(("PS : A prévue ≥ A calculée (cm²)", PS["A_bot"], PS["ft"]["As"], PS["A_bot"] >= PS["ft"]["As"]))
    c.append(("Poteau : Nu ≤ Nu lim (kN)", COL["worst"]["Ncol_u"], COL["Nlim"], COL["worst"]["Ncol_u"] <= COL["Nlim"]))
    c.append(("Poteau : effort normal réduit ν ≤ 0.30", COL["nu"], 0.30, COL["nu"] <= 0.30))
    for t, f in FOOT.items():
        c.append((f"Semelle {t} : σ ≤ σ sol (kPa)", f["worst"]["sigma"], SIGMA_SOL, f["worst"]["sigma"] <= SIGMA_SOL))
        c.append((f"Semelle {t} : A prévue ≥ A calculée (cm²)", f["A"], f["A_need"], f["A"] >= f["A_need"]))
    c.append(("Longrine : A ≥ A min RPA (cm²)", LONG["A"], LONG["Amin"], LONG["A"] >= LONG["Amin"]))
    c.append(("Déplacement relatif Δk ≤ 1 % he (mm)", SEI["delta_k"] * 1000, SEI["he"] * 10, SEI["delta_k"] <= SEI["he"] / 100))
    nm = column_NM(0.8 * min(r["Ncol_s"] for r in DESC), SEI["Mc"])
    c.append(("Poteau sous séisme : M ≤ M résistant (kN·m)", SEI["Mc"], nm["MR"], SEI["Mc"] <= nm["MR"]))
    c.append(("Acrotère : A ≥ A min (cm²/ml)", ACRO["A"], ACRO["Amin"], ACRO["A"] >= ACRO["Amin"]))
    return c


if __name__ == "__main__":
    print("G terrasse", G_T_CALC, "pu", PU_S)
    print("Poutrelle Ma %.2f Mt %.2f V %.2f As_t %.2f As_a %.2f" % (P["Ma"], P["Mt"], P["Vb1"], P["ft"]["As"], P["fa"]["As"]))
    for k, v in PP["axes"].items():
        print("PP", k, "pu %.2f M0 %.1f Mt %.1f Ma %.1f V %.1f" % (v["pu"], v["M0"], v["Mt_rive"], v["Ma_int"], v["Vu"]))
    print("PP As_t %.2f As_a %.2f sig %.1f" % (PP["ft"]["As"], PP["fa"]["As"], PP["sig"]))
    print("PS pu %.2f Mt %.2f Ma %.2f As %.2f" % (PS["pu"], PS["Mt"], PS["Ma"], PS["ft"]["As"]))
    for r in DESC:
        print(r["name"], r["type"], "Ncol_u %.1f Nf_s %.1f Ntot %.1f sigma %.1f" % (r["Ncol_u"], r["Nf_s"], r["Nser_tot"], r["sigma"]))
    print("col Nlim %.0f nu %.3f" % (COL["Nlim"], COL["nu"]))
    print("seismic T %.3f D %.3f W %.0f V %.1f dk %.2fmm" % (SEI["T"], SEI["D"], SEI["W"], SEI["V"], SEI["delta_k"] * 1000))
    for t, f in FOOT.items():
        print(t, f["worst"]["name"], "%.1f kPa As %.2f / %.2f" % (f["worst"]["sigma"], f["A_need"], f["A"]))
    print("long", LONG)
    for c in checks():
        print(("OK " if c[3] else "NOK"), c[0], "%.3f / %.3f" % (c[1], c[2]))

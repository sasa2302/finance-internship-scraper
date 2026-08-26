"""Generation du classeur Excel : un onglet Off-Cycle, un onglet Summer.

Structure du fichier data/stages_finance_marche_YYYY-MM-DD.xlsx :
  - Resume     : compteurs par type, zone, categorie d'employeur, top societes
  - Off-Cycle  : stages longs / cesure
  - Summer     : summer analyst / programmes d'ete
  - A trier    : calendrier non identifie (rien n'est perdu)
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

logger = logging.getLogger(__name__)

# (en-tete, largeur, attribut de JobOffer)
COLUMNS = [
    ("Poste", 52, "title"),
    ("Entreprise", 26, "company"),
    ("Type employeur", 24, "employer_category"),
    ("Lieu", 28, "location"),
    ("Zone", 16, "zone_label"),
    ("Duree", 14, "duration"),
    ("Periode visee", 16, "_period"),
    ("Type de stage", 14, "_type_label"),
    ("Pourquoi ce type", 30, "type_reason"),
    ("Score", 8, "relevance_score"),
    ("Publiee le", 14, "date_posted"),
    ("Source", 14, "source"),
    ("Lien", 16, "url"),
    ("Description", 70, "description_snippet"),
]

HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
TITLE_FONT = Font(bold=True, size=14, color="1F3864")
LINK_FONT = Font(color="0563C1", underline="single")

SCORE_FILLS = [
    (0.75, PatternFill("solid", fgColor="C6EFCE")),   # vert   - tres pertinent
    (0.50, PatternFill("solid", fgColor="FFEB9C")),   # orange - a regarder
    (0.00, PatternFill("solid", fgColor="FFC7CE")),   # rouge  - faible
]

ZONE_ORDER = {"CORE": 0, "EUROPE": 1, "GLOBAL": 2, "INCONNU": 3}

THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def _score_fill(score):
    for threshold, fill in SCORE_FILLS:
        if score >= threshold:
            return fill
    return SCORE_FILLS[-1][1]


def _value(offer, attr, type_label):
    if attr == "_type_label":
        return type_label
    if attr == "_period":
        label = getattr(offer, "period_label", "") or ""
        note = getattr(offer, "period_note", "") or ""
        return label or ("a confirmer" if note else "")
    val = getattr(offer, attr, "")
    if val is None:
        return ""
    if attr == "relevance_score":
        return round(float(val), 2)
    if attr == "description_snippet":
        return str(val)[:400]
    return str(val)


def _write_sheet(ws, offers, type_label, sheet_title):
    ws.freeze_panes = "A3"

    # Ligne 1 : titre de l'onglet
    ws.cell(row=1, column=1, value=sheet_title).font = TITLE_FONT
    ws.cell(row=1, column=len(COLUMNS), value=f"{len(offers)} offre(s)").alignment = (
        Alignment(horizontal="right")
    )

    # Ligne 2 : en-tetes
    for idx, (header, width, _) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=2, column=idx, value=header)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(idx)].width = width
    ws.row_dimensions[2].height = 28

    # Tri : zone prioritaire d'abord, puis score decroissant
    ordered = sorted(
        offers,
        key=lambda o: (ZONE_ORDER.get(o.zone, 9), -float(o.relevance_score or 0), o.company or ""),
    )

    for r, offer in enumerate(ordered, start=3):
        for c, (_, _, attr) in enumerate(COLUMNS, start=1):
            cell = ws.cell(row=r, column=c, value=_value(offer, attr, type_label))
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=(attr in ("title", "description_snippet")))

            if attr == "url" and offer.url:
                cell.value = "Voir l'offre"
                cell.hyperlink = offer.url
                cell.font = LINK_FONT
                cell.alignment = Alignment(horizontal="center", vertical="top")
            elif attr == "relevance_score":
                cell.fill = _score_fill(float(offer.relevance_score or 0))
                cell.number_format = "0.00"
                cell.alignment = Alignment(horizontal="center", vertical="top")

    # Filtre automatique sur les colonnes
    if ordered:
        last_col = get_column_letter(len(COLUMNS))
        ws.auto_filter.ref = f"A2:{last_col}{len(ordered) + 2}"
    else:
        ws.cell(row=3, column=1, value="Aucune offre pour ce type lors de ce run.")


def _write_summary(ws, buckets, run_stats):
    ws.column_dimensions["A"].width = 38
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 38
    ws.column_dimensions["D"].width = 16

    row = 1
    ws.cell(row=row, column=1, value="Stages Finance de Marche - Rapport quotidien").font = TITLE_FONT
    row += 1
    ws.cell(row=row, column=1,
            value=f"Genere le {datetime.now(timezone.utc).strftime('%d/%m/%Y a %H:%M UTC')}")
    row += 2

    def section(title, pairs):
        nonlocal row
        c = ws.cell(row=row, column=1, value=title)
        c.fill, c.font = HEADER_FILL, HEADER_FONT
        ws.cell(row=row, column=2).fill = HEADER_FILL
        row += 1
        for label, value in pairs:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value).alignment = Alignment(horizontal="right")
            row += 1
        row += 1

    section("Repartition par type de stage", [
        ("Off-Cycle (stage long / cesure)", len(buckets["off_cycle"])),
        ("Summer (programme d'ete)", len(buckets["summer"])),
        ("A trier (calendrier inconnu)", len(buckets["unknown"])),
        ("TOTAL retenu", sum(len(v) for v in buckets.values())),
    ])

    all_offers = [o for v in buckets.values() for o in v]

    zones = {}
    for o in all_offers:
        zones[o.zone_label or "Non precise"] = zones.get(o.zone_label or "Non precise", 0) + 1
    section("Repartition geographique",
            sorted(zones.items(), key=lambda kv: -kv[1]))

    cats = {}
    for o in all_offers:
        cats[o.employer_category or "Non classe"] = cats.get(o.employer_category or "Non classe", 0) + 1
    section("Type d'employeur", sorted(cats.items(), key=lambda kv: -kv[1]))

    firms = {}
    for o in all_offers:
        if o.company:
            firms[o.company] = firms.get(o.company, 0) + 1
    section("Top 15 entreprises",
            sorted(firms.items(), key=lambda kv: -kv[1])[:15])

    if run_stats:
        section("Statistiques du run", list(run_stats.items()))


def build_workbook(buckets, output_path, run_stats=None):
    """Ecrit le classeur Excel et renvoie son chemin."""
    wb = Workbook()

    ws_summary = wb.active
    ws_summary.title = "Resume"
    _write_summary(ws_summary, buckets, run_stats)

    _write_sheet(wb.create_sheet("Off-Cycle"), buckets["off_cycle"], "Off-Cycle",
                 "OFF-CYCLE - stages longs (4-6 mois), cesure, stage de fin d'etudes")
    _write_sheet(wb.create_sheet("Summer"), buckets["summer"], "Summer",
                 "SUMMER - programmes d'ete (Summer Analyst, 8-12 semaines)")
    _write_sheet(wb.create_sheet("A trier"), buckets["unknown"], "A trier",
                 "A TRIER - calendrier non identifie automatiquement")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    logger.info(f"Classeur Excel ecrit : {output_path}")
    return output_path

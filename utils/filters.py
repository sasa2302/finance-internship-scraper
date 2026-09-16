"""Chaine de filtrage des offres.

Ordre des controles (du moins couteux / plus discriminant au plus fin) :
  1. Est-ce un stage ?                       (rejet CDI, CDD, alternance, VIE)
  2. Employeur de finance de marche ?        (whitelist, cf. utils.employer_match)
  3. Intitule hors finance de marche ?       (M&A, gestion privee, ESG, marketing...)
  4. Localisation ciblee ?                   (cf. utils.location_match)
  5. Metier de finance de marche ?           (mots-cles roles)
  6. Classification Off-Cycle / Summer + score
"""

import logging
import re
from collections import Counter
from datetime import date, datetime, timedelta

from config.keywords import (
    ROLE_KEYWORDS,
    INTERNSHIP_PREFIXES_FR,
    INTERNSHIP_PREFIXES_EN,
    EXCLUDE_KEYWORDS,
    EXCLUDE_TITLE_KEYWORDS,
    EXCLUDE_DURATION_PATTERNS,
    NON_STAGE_TYPES,
    DIVISION_LABELS,
    MARKETS_TITLE_TERMS,
    SUPPORT_LABELS_CONDITIONAL,
    STRONG_MARKETS_TITLE_TERMS,
)
from utils.textnorm import norm_text, has_any, has_phrase
from utils.employer_match import classify_employer
from utils.location_match import evaluate as evaluate_location, zone_bonus
from utils.classify import classify as classify_period, extract_duration, LABELS
from utils.period import detect_period, format_period, summer_ok, off_cycle_ok
from utils.metier import is_quant_or_tech, classify_metier
from config.settings import (
    TARGET_SUMMER_YEARS, OFF_CYCLE_START_MIN, MAX_OFFER_AGE_DAYS,
    EXCLUDE_QUANT_ROLES,
)

logger = logging.getLogger(__name__)

_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y")


def parse_posted_date(value):
    """Date de publication, ou None si illisible."""
    if not value:
        return None
    text = str(value).strip()[:10]
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None



_ALL_PREFIXES = INTERNSHIP_PREFIXES_FR + INTERNSHIP_PREFIXES_EN


class JobFilter:
    def __init__(self):
        self.rejections = Counter()

    # --- etapes unitaires -------------------------------------------------
    def is_internship(self, offer) -> bool:
        """Le marqueur de stage doit etre dans l'INTITULE ou le type de contrat.

        Se fier a la description laissait passer des postes temps plein : les
        annonces mentionnent souvent les programmes de stage de la maison en
        texte generique. Mesure sur 1 512 offres Greenhouse : 14 offres etaient
        retenues sur ce seul critere, et les 14 etaient des faux positifs
        ("Linux Engineer", "Campus Recruiter", "Graduate Trader").
        """
        text = norm_text(f"{offer.title} {offer.job_type or ''}")
        return has_any(text, _ALL_PREFIXES)

    def matches_role(self, offer) -> bool:
        """Le metier de marche doit figurer dans l'INTITULE.

        La description ne suffit pas : celle d'une prop firm ou d'une banque
        parle toujours de trading, ce qui laissait passer "IT Intern", "Asset
        Servicing", "Client Support" ou "Company Secretarial Assistant".
        """
        return has_any(norm_text(offer.title), ROLE_KEYWORDS)

    def is_non_stage(self, offer) -> bool:
        """Rejette ce qui n'est manifestement pas un stage."""
        job_type = norm_text(offer.job_type or "")
        title = norm_text(offer.title)

        if has_any(job_type, NON_STAGE_TYPES):
            return True

        # Un intitule de poste permanent, sauf s'il precise "stage"
        if has_any(title, ["cdi", "cdd", "full time", "temps plein", "permanent position",
                           "emploi", "recrutement", "embauche"]):
            return not has_any(title, ["stage", "stagiaire", "internship", "intern"])

        return has_any(title, ["alternance", "alternant", "apprenti", "vie",
                               "volontariat international"])

    def is_stale(self, offer) -> bool:
        """Offre trop ancienne.

        Une offre sans date de publication lisible est CONSERVEE : beaucoup de
        sites carriere ne publient pas cette information, et la deduplication
        ecarte de toute facon ce qui a deja ete vu.
        """
        if MAX_OFFER_AGE_DAYS <= 0:
            return False
        posted = parse_posted_date(offer.date_posted)
        if posted is None:
            return False
        return posted < date.today() - timedelta(days=MAX_OFFER_AGE_DAYS)

    def is_excluded_title(self, offer) -> bool:
        title = norm_text(offer.title)
        text = norm_text(f"{offer.title} {offer.description_snippet}")

        if has_any(title, EXCLUDE_KEYWORDS):
            return True
        if has_any(title, EXCLUDE_TITLE_KEYWORDS):
            return True
        # Libelle de division banque d'affaires sans aucun metier de marche
        if has_any(title, DIVISION_LABELS) and not has_any(title, MARKETS_TITLE_TERMS):
            return True
        if (has_any(title, SUPPORT_LABELS_CONDITIONAL)
                and not has_any(title, STRONG_MARKETS_TITLE_TERMS)):
            return True
        return False

    def has_excluded_duration(self, offer) -> bool:
        text = norm_text(f"{offer.title} {offer.description_snippet}")
        return any(re.search(p, text, re.IGNORECASE) for p in EXCLUDE_DURATION_PATTERNS)

    # --- score ------------------------------------------------------------
    def compute_relevance_score(self, offer) -> float:
        score = 0.0
        title = norm_text(offer.title)
        text = norm_text(f"{offer.title} {offer.description_snippet}")

        # Metier present dans l'intitule (poids fort)
        if has_any(title, ROLE_KEYWORDS):
            score += 0.30

        # Densite de mots-cles metier dans le texte
        hits = sum(1 for kw in ROLE_KEYWORDS if has_phrase(text, kw))
        score += min(hits * 0.05, 0.20)

        # Confirmation "stage"
        if self.is_internship(offer):
            score += 0.15

        # Duree identifiee
        if offer.duration:
            score += 0.10

        # Calendrier identifie (off-cycle ou summer, pas "a trier")
        if offer.internship_type in ("off_cycle", "summer"):
            score += 0.05

        # Priorite geographique
        score += zone_bonus(offer.zone)

        # Employeur formellement identifie
        if offer.employer_category and not offer.employer_category.startswith("A verifier"):
            score += 0.05

        return min(round(score, 2), 1.0)

    # --- pipeline ---------------------------------------------------------
    def filter_and_score(self, offers) -> list:
        self.rejections = Counter()
        results = []

        for offer in offers:
            if self.is_non_stage(offer):
                self.rejections["pas un stage (CDI/CDD/alternance/VIE)"] += 1
                continue

            if self.is_stale(offer):
                self.rejections[f"publiee il y a plus de {MAX_OFFER_AGE_DAYS} jours"] += 1
                continue

            ok, category, why = classify_employer(offer)
            if not ok:
                self.rejections[why] += 1
                continue
            offer.employer_category = category

            if self.is_excluded_title(offer):
                self.rejections["intitule hors finance de marche"] += 1
                continue

            if self.has_excluded_duration(offer):
                self.rejections["duree exclue (12 mois et plus, alternance)"] += 1
                continue

            if EXCLUDE_QUANT_ROLES and is_quant_or_tech(offer.title):
                self.rejections["poste quant / tech (profil non vise)"] += 1
                continue

            loc_ok, zone, zone_label, loc_why = evaluate_location(offer.location or "")
            if not loc_ok and loc_why == "hors places financieres ciblees":
                # Le lieu est parfois un simple pays ("Mainland China") et la
                # ville n'apparait que dans l'intitule ("... - Shanghai").
                t_ok, t_zone, t_label, _ = evaluate_location(offer.title)
                if t_ok and t_zone != "INCONNU":
                    loc_ok, zone, zone_label = True, t_zone, t_label
            if not loc_ok:
                self.rejections[loc_why] += 1
                continue
            offer.zone = zone
            offer.zone_label = zone_label

            # Stage ET metier de marche : le "ou" laissait passer des postes
            # temps plein (ex. "Commodities Volatility Trader").
            if not self.is_internship(offer):
                self.rejections["pas identifie comme stage"] += 1
                continue
            if not self.matches_role(offer):
                self.rejections["metier hors finance de marche"] += 1
                continue

            offer.duration = extract_duration(
                norm_text(f"{offer.description_snippet} {offer.duration or ''} {offer.title}")
            ) or (offer.duration or "")
            offer.internship_type, offer.type_reason = classify_period(offer)
            offer.metier = classify_metier(offer.title)

            # Campagne visee : ete 2027 pour les summer, demarrage >= janvier
            # 2027 pour les off-cycle. Une offre sans date reste dans le
            # rapport, signalee dans la colonne "Periode".
            period = detect_period(offer)
            offer.period_label = format_period(period)
            if offer.internship_type == "summer":
                ok_period, note = summer_ok(period, TARGET_SUMMER_YEARS)
            else:
                ok_period, note = off_cycle_ok(period, OFF_CYCLE_START_MIN)
            if not ok_period:
                self.rejections[f"hors campagne visee ({note})"] += 1
                continue
            offer.period_note = note

            offer.relevance_score = self.compute_relevance_score(offer)
            results.append(offer)

        results.sort(key=lambda o: (-o.relevance_score, o.company or "", o.title))
        return self._collapse_near_duplicates(results)

    def _collapse_near_duplicates(self, offers) -> list:
        """Fusionne les doublons intra-run.

        Une meme offre remontee par plusieurs sources (site carriere + LinkedIn,
        ou deux jours d'archives) a des URL differentes mais le meme couple
        societe/intitule. On garde la mieux notee. La zone fait partie de la cle :
        un meme programme ouvert a Paris, Londres et Zurich reste 3 lignes.
        """
        best = {}
        order = []
        for offer in offers:
            key = (norm_text(offer.company or ""), norm_text(offer.title), offer.zone_label)
            current = best.get(key)
            if current is None:
                best[key] = offer
                order.append(key)
            elif offer.relevance_score > current.relevance_score:
                best[key] = offer
            else:
                self.rejections["doublon (meme societe/intitule/zone)"] += 1
                continue
            if current is not None:
                self.rejections["doublon (meme societe/intitule/zone)"] += 1
        return [best[k] for k in order]

    def split_by_period(self, offers) -> dict:
        """Separe les offres retenues en off_cycle / summer / unknown."""
        buckets = {"off_cycle": [], "summer": [], "unknown": []}
        for offer in offers:
            buckets.get(offer.internship_type, buckets["unknown"]).append(offer)
        return buckets

    def log_rejections(self):
        if not self.rejections:
            return
        logger.info("    Motifs de rejet :")
        for reason, count in self.rejections.most_common():
            logger.info(f"      - {reason}: {count}")

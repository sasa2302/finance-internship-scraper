# Finance Internship Scraper

Scraper quotidien de **stages en finance de marché**. Il interroge les sites
carrière des acteurs de marché et les agrégateurs, filtre sur l'univers finance
de marché, puis produit un **classeur Excel avec un onglet Off-Cycle et un
onglet Summer**.

## Ce que produit le scraper

**Un seul fichier** : `data/stages_finance_marche.xlsx`, mis à jour à chaque run.

| Onglet | Contenu |
|---|---|
| **Résumé** | Nouveautés du run, totaux, répartition géographique et par type d'employeur |
| **Off-Cycle** | Stages longs / césure |
| **Summer** | Programmes d'été |
| **À trier** | Calendrier non identifié — rien n'est jeté |
| `_donnees` | Feuille technique masquée, relue au run suivant |

Les offres du jour sont **en tête de chaque onglet, marquées NOUVEAU**. Les
précédentes restent visibles pendant `REPORT_WINDOW_DAYS` (60 jours par défaut)
puis sortent automatiquement : à ~2,5 offres/jour, le fichier se stabilise
autour de 150 lignes et ne dérive pas.

`data/seen_hashes.json` et `data/run_log.json` sont des fichiers techniques
(mémoire de déduplication et journal du run), pas des livrables.

### Off-Cycle vs Summer

| | Signaux retenus |
|---|---|
| **Off-Cycle** | `off-cycle`, césure, gap year, placement year, stage de fin d'études, durée ≥ 4 mois, `long term internship`, et tout intitulé français en « Stage / Stagiaire » sans mention d'été |
| **Summer** | `summer analyst`, `summer associate`, `summer internship`, `spring week`, stage d'été, durée ≤ 12 semaines |
| **À trier** | Aucun signal calendaire fiable — rien n'est jeté, tout atterrit dans le 4ᵉ onglet |

Un stage français annoncé « Juillet 2026 » est classé **Off-Cycle** : en France
un stage démarrant en juillet est un 6 mois, pas un programme d'été.

## Sources scrapées

Le scraper n'interroge que des **API JSON**, mesurées comme productives :

| Type | Sources | Exemples |
|---|---|---|
| Greenhouse | 17 | Jane Street, Point72, DRW, IMC, Jump Trading, Man Group, AQR, Virtu, Flow Traders, WorldQuant, Squarepoint, Tower Research, Schonfeld |
| Workday | 8 | Barclays, Morgan Stanley, Citi, Nomura, Macquarie, UBS, Bank of America |
| Oracle HCM | 2 | JP Morgan, Schroders |
| Agrégateurs | 4 | LinkedIn, Indeed, Glassdoor, Welcome to the Jungle |

Les 84 sites carrière restants (Société Générale, BNP, Goldman, Deutsche…)
sont dans `PENDING_ATS` et **ne sont pas scrapés** : ce sont des applications
JavaScript dont le parsing HTML rendait 0 offre sur 10 sites testés, tout en
consommant la totalité du budget de temps. Leur couverture passe par les
agrégateurs, et ces employeurs restent dans la whitelist.

### Banques non scrapables en direct

Certaines banques ne peuvent pas être interrogées directement : BNP Paribas
est derrière un pare-feu anti-bot (Akamai, HTTP 403), Goldman et Natixis sont
des applications JavaScript sans API accessible, UBS / Nomura / Macquarie ont
changé de chemin Workday.

**Insister sur leurs serveurs ferait risquer un blocage sans rien rapporter.**
Elles sont donc cherchées **nommément sur les agrégateurs**, où elles publient
de toute façon — voir `AGGREGATOR_TARGETED_EMPLOYERS` dans
`config/companies.py`. Ces requêtes passent **en premier** dans le plan, pour
qu'une interruption par le budget de temps ne les sacrifie pas.

### Charge envoyée

86 requêtes par run au total, espacées de 1,5 à 3 s : 1 requête par jour et
par board Greenhouse, 1 pour Société Générale, 4 par site Oracle, 12 par site
Workday. Volontairement en dessous d'un usage humain normal.

## Périmètre

**Employeurs** — whitelist de ~390 noms (`config/employers.py`), organisée en
banques / BFI, hedge funds, prop trading & market makers, brokers, asset
managers, bourses & infrastructure, institutions. Une société absente de la
liste n'est retenue que si son intitulé porte un signal marché fort
(« sales trader », « equity derivatives », « structuring »…) ; elle est alors
marquée *À vérifier* dans le rapport.

> C'est le changement de fond par rapport à la version précédente, qui
> fonctionnait par liste noire : chaque nouvelle enseigne non listée passait au
> travers (supermarchés, hôtels, agences immobilières, retail…).

**Métiers retenus** : trading, sales, structuration, dérivés, fixed income,
taux, crédit, FX, matières premières, market making, delta one, quant
(recherche / trading / pricing / XVA), risque de marché, gestion de
portefeuille, prime brokerage, repo, recherche marché.

**Métiers exclus** : M&A, private equity, corporate finance, DCM/ECM et
origination, gestion privée / patrimoine, ESG/ISR, audit, compliance, juridique,
comptabilité, marketing, RH, IT généraliste, retail et vente.

**Contrats exclus** : CDI, CDD, alternance, apprentissage, VIE, stages de 12 mois
et plus.

### Géographie

| Zone | Localisations | Bonus de score |
|---|---|---|
| **Cœur de cible** | Paris / Île-de-France, Londres, Suisse (Zurich, Genève, Lausanne, Zoug, Bâle, Lugano), Luxembourg | +0,15 |
| **Europe** | Allemagne, Irlande, Pays-Bas, Belgique, Nordiques, Autriche, Monaco | +0,08 |
| **Mondial** | Hong Kong, Singapour, New York, Chicago, Boston, Tokyo, Shanghai, Sydney, Melbourne, Dubaï, Toronto | +0,05 |

**Exclus** : Espagne, Italie, Portugal. Également exclus : les villes françaises
hors Île-de-France, le Royaume-Uni hors Londres (et Dublin), et les sites
back-office indiens des banques (Mumbai, Pune, Chennai, Noida, Gurugram).

## Utilisation

```bash
pip install -r requirements.txt
python main.py
```

Options :

```bash
python main.py --skip-aggregators   # sites carrière uniquement
python main.py --skip-companies     # agrégateurs uniquement
python main.py --no-dedup           # rapport complet, sans tenir compte de l'historique
```

`--no-dedup` ne modifie pas `data/seen_hashes.json`.

## Automatisation

GitHub Actions (`.github/workflows/scrape.yml`) lance le scraper chaque jour à
09:00 heure de Paris, commite les fichiers produits, et publie le classeur Excel
en artefact téléchargeable (conservé 90 jours).

## Architecture

```
config/
  companies.py    sites carrière à scraper
  employers.py    whitelist finance de marché + signaux marché forts
  keywords.py     métiers retenus / intitulés exclus / types de contrat
  locations.py    zones géographiques et exclusions
  settings.py     réglages HTTP et scraping
scrapers/
  base.py         JobOffer + classe de base
  workday.py      API Workday
  custom_html.py  parsing HTML des autres sites
  aggregators.py  LinkedIn, Indeed, Glassdoor (jobspy) + Welcome to the Jungle
utils/
  textnorm.py       normalisation accents/casse, recherche par mots entiers
  employer_match.py whitelist employeur
  location_match.py filtrage géographique
  classify.py       Off-Cycle vs Summer
  filters.py        chaîne de filtrage complète + score
  csv_manager.py    écriture CSV
  excel_export.py   génération du classeur Excel
  dedup.py          déduplication SHA-256 entre runs
```

Toutes les comparaisons de texte passent par `utils/textnorm.has_phrase`, qui
compare des **mots entiers** sur du texte sans accents. La version précédente
utilisait des sous-chaînes brutes, ce qui écartait par exemple toutes les offres
« Quantitative Re**sea**rch » via le mot-clé `sea`.

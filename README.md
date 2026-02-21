# Finance Internship Scraper

Scraper autonome qui recherche chaque jour les meilleures offres de stage de 6 mois en finance de marché.

## Ce que fait le programme

- **Scrape 54 banques/institutions** : sites carrières de Barclays, Morgan Stanley, Citi, Goldman Sachs, JP Morgan, HSBC, BNP Paribas, Societe Generale, Natixis, CACIB, Deutsche Bank, UBS, Nomura, Citadel, Jane Street, Optiver, etc.
- **Scrape 4 agrégateurs** : LinkedIn, Indeed, Glassdoor et Welcome to the Jungle
- **Filtre intelligent** : garde uniquement les postes en trading, sales, structuration, risk et quant en finance de marché
- **Exclut automatiquement** : M&A, Private Equity, corporate finance, alternances, stages de 12 mois, postes seniors, et les entreprises non-finance (retail, luxe, consulting)
- **Filtre géographique** : Paris et alentours, Londres, Suisse, Luxembourg, Allemagne uniquement (exclut les villes secondaires françaises)
- **Scoring de pertinence** : chaque offre reçoit un score de 0 à 1 basé sur les mots-clés, la durée, la localisation et le département
- **Déduplication** : évite les doublons via un système de hash SHA-256
- **Exécution automatique** : tourne tous les jours à 9h (Paris) via GitHub Actions et commit les résultats dans un CSV

## Stack technique

Python 3.11 | requests | BeautifulSoup4 | pandas | python-jobspy | GitHub Actions

## Structure

- `config/` : entreprises, mots-clés, filtres, paramètres
- `scrapers/` : Workday API, HTML générique, agrégateurs
- `utils/` : filtres, déduplication, gestion CSV, client HTTP
- `data/` : CSV des offres, historique des hashs, logs

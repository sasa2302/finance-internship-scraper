"""Sources scrapees directement.

COMPANIES ne contient que les sources a API JSON, mesurees comme productives.
Le parsing HTML generique rendait 0 offre sur 10 sites testes (ce sont des
applications JavaScript) tout en consommant la totalite du budget de temps :
ces sites sont donc listes dans PENDING_ATS, non scrapes, en attendant un
scraper adapte a leur ATS reel.

Leur couverture n'est pas perdue pour autant : ces employeurs restent dans la
whitelist config/employers.py, donc leurs offres remontees par LinkedIn,
Indeed ou Glassdoor sont bien retenues.
"""

COMPANIES = [
    # === Oracle Cloud Recruiting (API REST publique) ===
    {
        "name": "JP Morgan",
        "scraper_type": "oracle_hcm",
        "host": "jpmc.fa.oraclecloud.com",
        "site_number": "CX_1001",
    },
    {
        "name": "Schroders",
        "scraper_type": "oracle_hcm",
        "host": "ekbq.fa.em2.oraclecloud.com",
        "site_number": "CX_1",
    },

    # === Workday (API CXS) ===
    {
        "name": "Barclays",
        "scraper_type": "workday",
        "base_url": "https://barclays.wd3.myworkdayjobs.com/en-US/external_career_site_barclays",
        "wday_path": "barclays/external_career_site_barclays",
    },
    {
        "name": "Morgan Stanley",
        "scraper_type": "workday",
        "base_url": "https://ms.wd5.myworkdayjobs.com/External",
        "wday_path": "ms/External",
    },
    {
        "name": "Citi",
        "scraper_type": "workday",
        "base_url": "https://citi.wd5.myworkdayjobs.com/2",
        "wday_path": "citi/2",
    },
    {
        "name": "Fidelity International",
        "scraper_type": "workday",
        "base_url": "https://fil.wd3.myworkdayjobs.com/001",
        "wday_path": "fil/001",
    },
    {
        "name": "Nomura",
        "scraper_type": "workday",
        "base_url": "https://nomuracareers.wd1.myworkdayjobs.com/en-US/NomuraExternalCareers",
        "wday_path": "nomuracareers/NomuraExternalCareers",
    },
    {
        "name": "Macquarie",
        "scraper_type": "workday",
        "base_url": "https://macquarie.wd3.myworkdayjobs.com/en-US/Macquarie_Careers",
        "wday_path": "macquarie/Macquarie_Careers",
    },
    {
        "name": "Credit Suisse (UBS)",
        "scraper_type": "workday",
        "base_url": "https://ubs.wd3.myworkdayjobs.com/en-US/Find_a_job_at_UBS",
        "wday_path": "ubs/Find_a_job_at_UBS",
    },
    {
        "name": "Bank of America",
        "scraper_type": "workday",
        "base_url": "https://ghr.wd1.myworkdayjobs.com/en-us/lateral-us",
        "wday_path": "ghr/lateral-us",
    },

    # === Greenhouse (API JSON des job boards) ===
    {
        "name": "Jane Street",
        "scraper_type": "greenhouse",
        "board_token": "janestreet",
    },
    {
        "name": "Point72",
        "scraper_type": "greenhouse",
        "board_token": "point72",
    },
    {
        "name": "IMC Trading",
        "scraper_type": "greenhouse",
        "board_token": "imc",
    },
    {
        "name": "Man Group",
        "scraper_type": "greenhouse",
        "board_token": "mangroup",
    },
    {
        "name": "AQR Capital Management",
        "scraper_type": "greenhouse",
        "board_token": "aqr",
    },
    {
        "name": "Virtu Financial",
        "scraper_type": "greenhouse",
        "board_token": "virtu",
    },
    {
        "name": "Flow Traders",
        "scraper_type": "greenhouse",
        "board_token": "flowtraders",
    },
    {
        "name": "Jump Trading",
        "scraper_type": "greenhouse",
        "board_token": "jumptrading",
    },
    {
        "name": "ExodusPoint Capital",
        "scraper_type": "greenhouse",
        "board_token": "exoduspoint",
    },
    {
        "name": "Schonfeld",
        "scraper_type": "greenhouse",
        "board_token": "schonfeld",
    },
    {
        "name": "Quadrature Capital",
        "scraper_type": "greenhouse",
        "board_token": "quadraturecapital",
    },
    {
        "name": "WorldQuant",
        "scraper_type": "greenhouse",
        "board_token": "worldquant",
    },
    {
        "name": "DRW",
        "scraper_type": "greenhouse",
        "board_token": "drweng",
    },
    {
        "name": "Squarepoint Capital",
        "scraper_type": "greenhouse",
        "board_token": "squarepointcapital",
    },
    {
        "name": "Tower Research Capital",
        "scraper_type": "greenhouse",
        "board_token": "towerresearchcapital",
    },
    {
        "name": "Akuna Capital",
        "scraper_type": "greenhouse",
        "board_token": "akunacapital",
    },
    {
        "name": "Old Mission Capital",
        "scraper_type": "greenhouse",
        "board_token": "oldmissioncapital",
    },
]


# Sites carriere sans scraper adapte : applications JavaScript dont le
# parsing HTML ne tire rien. A migrer vers leur ATS reel (Avature pour HSBC
# et Goldman, SuccessFactors pour Standard Chartered, etc.).
PENDING_ATS = [
    "Societe Generale",
    "BNP Paribas",
    "Natixis",
    "CACIB",
    "Goldman Sachs",
    "JP Morgan",
    "Lazard",
    "Deutsche Bank",
    "Murex",
    "Kepler Cheuvreux",
    "Rothschild & Co",
    "HSBC",
    "UBS",
    "Bank of America",
    "Cantor Fitzgerald",
    "Jefferies",
    "Standard Chartered",
    "Credit Mutuel CIC",
    "Commerzbank",
    "ING",
    "ABN AMRO",
    "Exane (BNP Paribas)",
    "Millennium Management",
    "Citadel Securities",
    "Jane Street",
    "Optiver",
    "Qube Research & Technologies",
    "Euronext",
    "Amundi",
    "AXA Investment Managers",
    "Ostrum Asset Management (Natixis)",
    "Mediobanca",
    "Unicredit",
    "Oddo BHF",
    "Berenberg",
    "BRED Banque Populaire",
    "La Banque Postale",
    "Banque de France",
    "Coface",
    "SILEX Investment Partners",
    "Feefty",
    "Market Securities",
    "Magen Financial",
    "Generali Investments",
    "Deutsche Pfandbriefbank",
    "China Merchants Securities",
    "Groupe BPCE",
    "Tradition Securities (TSAF)",
    "ICAP (TP ICAP)",
    "BGC Partners",
    "Lombard Odier",
    "Pictet",
    "Julius Baer",
    "Vontobel",
    "CIC Market Solutions",
    "Tikehau Capital",
    "Sycomore AM",
    "CPR Asset Management",
    "Rothschild Martin Maurel",
    "Schroders",
    "Aviva Investors",
    "Man Group",
    "Two Sigma",
    "DE Shaw",
    "Virtu Financial",
    "Flow Traders",
    "IMC Trading",
    "DRW",
    "Susquehanna (SIG)",
    "Brevan Howard",
    "Capula Investment Management",
    "Marshall Wace",
    "Eisler Capital",
    "Squarepoint Capital",
    "Winton Group",
    "Capital Fund Management (CFM)",
    "Point72",
    "Balyasny Asset Management",
    "WorldQuant",
    "AQR Capital Management",
    "ExodusPoint Capital",
    "Aspect Capital",
    "Bridgewater Associates",
    "Citadel LLC",
]

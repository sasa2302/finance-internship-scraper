COMPANIES = [
    # === Workday API (confirmed working) ===
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

    # === Custom HTML / SPA scrapers ===
    # These sites are JS-rendered SPAs - the scraper will attempt HTML parsing
    # but most results will come from the aggregators (LinkedIn, Indeed)
    {
        "name": "Societe Generale",
        "scraper_type": "custom_html",
        "base_url": "https://careers.societegenerale.com/en/job-offers",
        "search_url": "https://careers.societegenerale.com/en/job-offers",
    },
    {
        "name": "BNP Paribas",
        "scraper_type": "custom_html",
        "base_url": "https://group.bnpparibas/emploi-carriere/toutes-offres-emploi",
        "search_url": "https://group.bnpparibas/emploi-carriere/toutes-offres-emploi",
    },
    {
        "name": "Natixis",
        "scraper_type": "custom_html",
        "base_url": "https://recrutement.natixis.com",
        "search_url": "https://recrutement.natixis.com",
    },
    {
        "name": "Goldman Sachs",
        "scraper_type": "custom_html",
        "base_url": "https://higher.gs.com/results",
        "search_url": "https://higher.gs.com/results",
    },
    {
        "name": "JP Morgan",
        "scraper_type": "custom_html",
        "base_url": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs",
        "search_url": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs",
    },
    {
        "name": "Lazard",
        "scraper_type": "custom_html",
        "base_url": "https://lazard-careers.tal.net/vx/lang-en-GB/appcentre-ext/brand-4/candidate/jobboard/vacancy/2/adv/",
        "search_url": "https://lazard-careers.tal.net/vx/lang-en-GB/appcentre-ext/brand-4/candidate/jobboard/vacancy/2/adv/",
    },
    {
        "name": "Deutsche Bank",
        "scraper_type": "custom_html",
        "base_url": "https://careers.db.com/professionals/search-roles",
        "search_url": "https://careers.db.com/professionals/search-roles",
    },
    {
        "name": "Murex",
        "scraper_type": "custom_html",
        "base_url": "https://www.murex.com/careers",
        "search_url": "https://www.murex.com/careers",
    },
    {
        "name": "Kepler Cheuvreux",
        "scraper_type": "custom_html",
        "base_url": "https://www.keplercheuvreux.com/en/careers",
        "search_url": "https://www.keplercheuvreux.com/en/careers",
    },
    {
        "name": "Credit Agricole CIB",
        "scraper_type": "custom_html",
        "base_url": "https://careers.ca-cib.com/offres-emploi",
        "search_url": "https://careers.ca-cib.com/offres-emploi",
    },
    {
        "name": "Rothschild & Co",
        "scraper_type": "custom_html",
        "base_url": "https://www.rothschildandco.com/en/careers/",
        "search_url": "https://www.rothschildandco.com/en/careers/",
    },
    {
        "name": "HSBC",
        "scraper_type": "custom_html",
        "base_url": "https://www.hsbc.com/careers/students-and-graduates",
        "search_url": "https://www.hsbc.com/careers/students-and-graduates",
    },
    {
        "name": "UBS",
        "scraper_type": "custom_html",
        "base_url": "https://www.ubs.com/global/en/careers/students.html",
        "search_url": "https://www.ubs.com/global/en/careers/students.html",
    },
    {
        "name": "Bank of America",
        "scraper_type": "custom_html",
        "base_url": "https://campus.bankofamerica.com/careers",
        "search_url": "https://campus.bankofamerica.com/careers",
    },
]

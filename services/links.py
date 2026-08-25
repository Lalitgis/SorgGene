"""
SorghumPost - External Link Builders
=======================================
Centralizes URL construction for SorghumBase and Phytozome gene pages so
every tab links out the same way.
"""

SORGHUMBASE_BASE_URL = "https://ensembl.sorghumbase.org/"
PHYTOZOME_GENE_URL = "https://phytozome-next.jgi.doe.gov/report/gene/Sbicolor_v3_1_1/"

GENOTYPE_SPECIES_SLUG = {
    "BTx623": "Sorghum_bicolor",
    "Tx2783": "Sorghum_tx2783pac",
    "Rio": "Sorghum_rio",
}


def sorghumbase_url(gene_id: str, genotype: str = "BTx623") -> str:
    slug = GENOTYPE_SPECIES_SLUG.get(genotype, "Sorghum_bicolor")
    return f"{SORGHUMBASE_BASE_URL}{slug}/Gene/Summary?g={gene_id}"


def phytozome_url(phytozome_id: str) -> str:
    return f"{PHYTOZOME_GENE_URL}{phytozome_id}"

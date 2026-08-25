# Data Credits

## Sorghumbase
Gene annotation for all three genotypes in this app (BTx623, Tx2783, Rio) was
downloaded from Sorghumbase's public FTP site (ftp.sorghumbase.org), which
mirrors Ensembl Plants-format GFF3 files for the sorghum pangenome.

SorghumBase: a web-based portal for sorghum genetic information and community
advancement. Cannon EKS, Birkett AS, Braun BL, et al. *Planta*. 2022.
doi:10.1007/s00425-022-03821-6

## Phytozome
The BTx623 reference gene models (`Sorghum_bicolor_NCBIv3` on Sorghumbase)
are the same v3.1.1 annotation hosted on Phytozome as `Sbicolor_v3_1_1`,
produced by the DOE Joint Genome Institute (JGI).

Source: https://phytozome-next.jgi.doe.gov

## Reference Genome Assemblies
- **BTx623** (Sorghum bicolor NCBIv3) — Paterson AH, et al. "The Sorghum
  bicolor genome and the diversification of grasses." *Nature*. 2009.
- **Tx2783** (CSHL-USDA-1.0) — chromosome-scale assembly, Cold Spring Harbor
  Laboratory / USDA.
- **Rio** (JGI-v2.0) — chromosome-scale assembly, DOE Joint Genome Institute.

## Tool Development
SorghumPost was built as a Sorghum-focused counterpart to
[WheatPost](https://github.com/neupanebpn63/WheatPost) by Bipin Neupane,
following the same tab-based, locally-run design for post-genomics
lookups -- gene proximity search, gene ID cross-reference, and (in place
of wheat's multi-assembly-version liftover) cross-genotype pangenome
comparison, reflecting what Sorghumbase and Phytozome actually provide
for *Sorghum bicolor*.

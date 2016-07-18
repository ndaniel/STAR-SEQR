# STAR-SEQR
Breakpoint and Fusion Detection. More description to follow.

### Generate STAR index as follows:
* RNA
  * STAR --runMode genomeGenerate --genomeFastaFiles /mounts/datah/indexes/DNA/h_sapiens/hg19_scaffolds.fa --genomeDir STAR_SEQR_hg19gencodeV24lift37_S1_RNA --sjdbGTFfile /mounts/isilon/data/indexes/GFFs/gencodeV24lift37.gtf --runThreadN 18 --genomeSAsparseD 1

* DNA
  * STAR --runMode genomeGenerate --genomeFastaFiles /mounts/datah/indexes/DNA/h_sapiens/hg19_scaffolds.fa --genomeDir ./ --runThreadN 18 --genomeSAsparseD 2


### Dependencies:
* Python2.7
  * intervaltree_bio
  * pandas >0.18.0
  * pysam >0.9.0
  * primer3-py

* Tools that need to be on path
  * biobambam2
  * STAR
  * Velvet
  * Spades
  * samtools




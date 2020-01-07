
# <i class="fa fa-search"></i> Sequence search

The RNAcentral [sequence similarity search](/sequence-search) enables searches against a comprehensive collection of non-coding RNA sequences from a consortium of [RNA databases](/expert-databases). The search is powered by the [nhmmer](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3777106/) software which is more sensitive than *blastn* but is comparable in speed.

### Sequence search versions <a style="cursor: pointer" id="legacy-search" ng-click="scrollTo('legacy-search')" name="legacy-search" class="text-muted smaller"><i class="fa fa-link"></i></a>

The original sequence search was [implemented in 2015](https://blog.rnacentral.org/2015/06/rnacentral-release-3.html) when RNAcentral was much smaller than it is today. As the database grew, some searches were taking too long, so a new sequence search was developed in 2019.

<i class="fa fa-cloud fa-3x pull-left" style="margin-right: 20px;"></i>

The new version runs on a [cloud infrastructure](https://www.embassycloud.org), where each search can be **parallelised** making it much faster. The new user interface allows filtering the results using the same **facets** as the RNAcentral [text search](/help/text-search).

⚠️ The original sequence search is [still available](/legacy-sequence-search) but will be shut down in early 2020.

### What is different about the new sequence search? <a style="cursor: pointer" id="differences" ng-click="scrollTo('differences')" name="differences" class="text-muted smaller"><i class="fa fa-link"></i></a>

Please be aware that results now show **species-specific identifiers** which include NCBI taxonomy ids (for example [URS00000478B7_9606](/rna/URS00000478B7_9606), human 7SL RNA) while the old search results included only the unique RNA sequence identifiers (for example [URS00000478B7](/rna/URS00000478B7), SRP RNA from 5 species). This can increase the total number of results (in this example, the old search showed only 1 entry but the new one shows 5). This change enables the user to clearly see which species the sequence results are coming from.

### Exact sequence matches <a style="cursor: pointer" id="exact-matches" ng-click="scrollTo('exact-matches')" name="exact-matches" class="text-muted smaller"><i class="fa fa-link"></i></a>

Whenever a sequence is entered in the search input box, the query is compared with all RNAcentral sequences and if there is an **exact match**, the links to the entries matching the query are displayed in a green box. This is very quick because only identical matches are considered. To see all similar sequences, just click Submit.

### Rfam classification <a style="cursor: pointer" id="rfam" ng-click="scrollTo('rfam')" name="rfam" class="text-muted smaller"><i class="fa fa-link"></i></a>

<img src="/static/img/expert-db-logos/rfam.png" class="img-responsive pull-left" style="width: 140px; margin-right: 20px;">

In addition to nhmmer searches against RNAcentral, every query is automatically compared with the [Rfam](https://rfam.org) library of RNA families. The searches are done using the [Infernal](http://eddylab.org/infernal) cmscan program coupled with a [post-processing step](https://github.com/nawrockie/cmsearch_tblout_deoverlap). The post-processing removes any hits that overlap Rfam families from the same clan (a clan is a set of homologous families, for example LSU_rRNA_archaea, LSU_rRNA_bacteria and LSU_rRNA_eukarya). This is a unique functionality not available on the [Rfam website](https://rfam.org) or the [EBI cmscan service](https://www.ebi.ac.uk/Tools/rna/infernal_cmscan/) that report all matching families, including the redundant overlapping hits from the same clan.

### Searching for ribosomal RNAs <a style="cursor: pointer" id="rrna" ng-click="scrollTo('rrna')" name="rrna" class="text-muted smaller"><i class="fa fa-link"></i></a>

Over 50% of RNAcentral sequences are ribosomal RNAs (rRNAs). The abundance and high conservation of rRNA sequences makes it difficult to perform sequence similarity searches, as such searches are expected to match a large number of sequences and can take a long time to complete.

To get around this, the sequence similarity searches are performed against a subset of ~100,000 rRNA sequences from Ensembl, FlyBase, HGNC, MGI, PDBe, PomBase, RDP, RefSeq, RGD, SGD, TAIR, and WormBase.

### How long are the search results available for? <a style="cursor: pointer" id="stable-links" ng-click="scrollTo('stable-links')" name="stable-links" class="text-muted smaller"><i class="fa fa-link"></i></a>

The results will be available at the same URL for **at least one month**.

## Feedback

Please feel free to [contact us](/contact) or [raise a GitHub issue](https://github.com/rnacentral/rnacentral-sequence-search/issues).

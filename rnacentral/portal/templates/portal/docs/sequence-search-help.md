
# <i class="fa fa-search"></i> Sequence search

The RNAcentral [sequence similarity search](/sequence-search) enables searches against a comprehensive collection of non-coding RNA sequences from a consortium of [RNA databases](/expert-databases).

<iframe width="560" height="315" src="https://www.youtube.com/embed/2H4--NfjIsI" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

### Powered by nhmmer <a style="cursor: pointer" id="nhmmer" ng-click="scrollTo('nhmmer')" name="nhmmer" class="text-muted smaller"><i class="fa fa-link"></i></a>

The search is powered by the [nhmmer](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3777106/) software which is more sensitive than *blastn* but is comparable in speed. The command executed by the sequence search is as follows:

`nhmmer --qfasta --tformat fasta -o <output_file> -T 0 --F3 0.02 --rna --watson --cpu 4 -Z <number> <query> <database.fasta>`

Where:

* **--F3 0.02** is only used when the sequence length is less than 50 nucleotides
* **-Z &lt;number&gt;** is calculated according to the size of the database

A description of what each parameter does can be seen on the software [*man page*](http://eddylab.org/software/hmmer/Userguide.pdf) (manual page).

### Searching for ribosomal RNAs <a style="cursor: pointer" id="rrna" ng-click="scrollTo('rrna')" name="rrna" class="text-muted smaller"><i class="fa fa-link"></i></a>

Over 50% of RNAcentral sequences are ribosomal RNAs (rRNAs). The abundance and high conservation of rRNA sequences makes it difficult to perform sequence similarity searches, as such searches are expected to match a large number of sequences and can take a long time to complete.

To get around this, the sequence similarity searches are performed against a subset of ~100,000 rRNA sequences from Ensembl, FlyBase, HGNC, MGI, PDBe, PomBase, RDP, RefSeq, RGD, SGD, TAIR, and WormBase.

### Exact sequence matches <a style="cursor: pointer" id="exact-matches" ng-click="scrollTo('exact-matches')" name="exact-matches" class="text-muted smaller"><i class="fa fa-link"></i></a>

Whenever a sequence is entered in the search input box, the query is compared with all RNAcentral sequences and if there is an **exact match**, the links to the entries matching the query are displayed in a green box. This is very quick because only identical matches are considered. To see all similar sequences, just click Submit.

### Rfam classification <a style="cursor: pointer" id="rfam" ng-click="scrollTo('rfam')" name="rfam" class="text-muted smaller"><i class="fa fa-link"></i></a>

<img src="/static/img/expert-db-logos/rfam.png" class="img-responsive pull-left" style="width: 140px; margin-right: 20px;">

In addition to nhmmer searches against RNAcentral, every query is automatically compared with the [Rfam](https://rfam.org) library of RNA families. The searches are done using the [Infernal](http://eddylab.org/infernal) cmscan program coupled with a [post-processing step](https://github.com/nawrockie/cmsearch_tblout_deoverlap). The post-processing removes any hits that overlap Rfam families from the same clan (a clan is a set of homologous families, for example LSU_rRNA_archaea, LSU_rRNA_bacteria and LSU_rRNA_eukarya). This is a unique functionality not available on the [Rfam website](https://rfam.org) or the [EBI cmscan service](https://www.ebi.ac.uk/Tools/rna/infernal_cmscan/) that report all matching families, including the redundant overlapping hits from the same clan.

### Secondary structure <a style="cursor: pointer" id="r2dt" ng-click="scrollTo('r2dt')" name="r2dt" class="text-muted smaller"><i class="fa fa-link"></i></a>

The RNAcentral sequence similarity search also generates secondary structure (2D) diagrams using the [R2DT](https://github.com/RNAcentral/R2DT) software that visualises RNA structure using standard layouts or templates. Learn more about this new feature in the [R2DT paper](https://www.nature.com/articles/s41467-021-23555-5).

### Number of similar sequences <a style="cursor: pointer" id="number" ng-click="scrollTo('number')" name="number" class="text-muted smaller"><i class="fa fa-link"></i></a>

Although the number of similar sequences can reach tens of thousands, for performance reasons, only the top 1000 results will be shown in each search.

### Download search results <a style="cursor: pointer" id="download" ng-click="scrollTo('download')" name="download" class="text-muted smaller"><i class="fa fa-link"></i></a>

The search results are available for download in a compressed folder. This folder contains the *datapackage.json* file with the search metadata and a directory with three different files. The *similar-sequence.json* and *similar-sequence.txt* files contain the search results. The *similar-sequences.fasta* file contains a list of fasta sequences.

### API documentation <a style="cursor: pointer" id="sequence-search-api" ng-click="scrollTo('sequence-search-api')" name="sequence-search-api" class="text-muted smaller"><i class="fa fa-link"></i></a>

See the [API documentation](/sequence-search/api) to learn how to start an asynchronous job using our REST based API.

### How long are the search results available for? <a style="cursor: pointer" id="stable-links" ng-click="scrollTo('stable-links')" name="stable-links" class="text-muted smaller"><i class="fa fa-link"></i></a>

The results will be available at the same URL for **up to 7 days**. After this period, **all data and metadata are deleted**.

## Feedback

Please feel free to [contact us](/contact) or [raise a GitHub issue](https://github.com/rnacentral/rnacentral-sequence-search/issues).

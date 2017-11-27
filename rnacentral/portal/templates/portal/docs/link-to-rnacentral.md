
## Linking to RNAcentral <a style="cursor: pointer" id="link-to-rnacentral" ng-click="scrollTo('link-to-rnacentral')" name="link-to-rnacentral" class="text-muted smaller"><i class="fa fa-link"></i></a>

 * <a href="" ng-click="scrollTo('link-to-sequence')">how to create a badge on RNAcentral member database website</a>
 * <a href="" ng-click="scrollTo('link-to-genome-location')">how to link to a specific sequence</a>
 * <a href="" ng-click="scrollTo('expert-database-badge')">how to link to a specific genome location</a>
 * <a href="" ng-click="scrollTo('expert-database-badge')">how to cite RNAcentral</a>
 * <a href="" ng-click="scrollTo('expert-database-badge')">how to refer to our Twitter account</a>
 * <a href="rnacentral.org/contact">how to contact us</a>

## RNAcentral member database badge <a style="cursor: pointer" id="expert-database-badge" ng-click="scrollTo('expert-database-badge')" name="expert-database-badge" class="text-muted smaller"><i class="fa fa-link"></i></a>

If you maintain a database that has been [integrated in RNAcentral](/expert-databases),
please include the **RNAcentral Expert Database logo** on your website:

#### How to create a badge

Here's how the badge can look like:

<img src="http://localhost:8000/static/img/logo/RNAcentral_expert_database_logo.png" style="width: 80px">

Code:

```
<img src="http://localhost:8000/static/img/embed-logo/rnacentral.png" style="width: 80px">
```

#### Download badge image

You can download the logo and serve it from your website or retrieve it directly from RNAcentral.

#### What should the logo link to?

The logo should link to the RNAcentral homepage or to the landing page of the member database within RNAcentral.

For example, this is the FlyBase landing page in RNAcentral: [http://rnacentral.org/expert-database/flybase](http://rnacentral.org/expert-database/flybase).

#### What should I do if my database is not in RNAcentral yet?

If you maintain an ncRNA database and would like to join RNAcentral,
please <a href="http://rnacentral.org/contact">contact us</a>.

## Linking to RNAcentral sequences <a style="cursor: pointer" id="link-to-sequence" ng-click="scrollTo('link-to-sequence')" name="link-to-sequence" class="text-muted smaller"><i class="fa fa-link"></i></a>

#### What RNAcentral identifier should I link to?

You can find RNAcentral accessions using [text search](/help/text-search). If you need to perform a large-scale mapping,
please use the mapping files found in FTP archive:

* For all RNAcentral sequences:
  [ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/)

* Database-specific mapping files:
  [ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/)

#### Link format

Please use the following format to link to RNAcentral sequences:

* `http://rnacentral.org/rna/<rnacentral identifier>`

If you would like to link to information about a specific species,
we encourage you to append [NCBI taxonomy identifier](https://www.ncbi.nlm.nih.gov/taxonomy)
to the RNAcentral accession (e.g. *9606* for a *Homo sapiens* sequence):

* http://rnacentral.org/rna/URS000075A546/9606
* http://rnacentral.org/rna/URS000075A546_9606

Example of link appearance:

<p>
<p><img src="http://localhost:8000/static/img/logo/RNAcentral_icon.png" style="width: 16px; height: 16px; vertical-align: middle;"> <a href="http://localhost:8000/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">http://localhost:8000/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333</a></p>
</p>

Code:

```
<p>
<p><img src="http://localhost:8000/static/img/logo/RNAcentral_icon.png" style="width: 16px; height: 16px; vertical-align: middle;"> <a href="http://localhost:8000/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">http://localhost:8000/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333</a></p>
</p>
```

## Linking to genome locations <a style="cursor: pointer" id="link-to-genome-location" ng-click="scrollTo('link-to-genome-location')" name="link-to-genome-location" class="text-muted smaller"><i class="fa fa-link"></i></a>

#### Link format

To link to a specific genome location of interest, please use links to our genome browser page. Its structure is as follows:

* `http://rnacentral.org/genome-browser?species=<species>&chromosome=<chromosome>&start=<start>&end=<end>`

Here:
* species is species name with underscore and lowercase letter as in Ensembl (e.g. homo_sapiens or canis_lupus_familiaris)
* chromosome is Ensembl-style (not UCSC-style) chromosome name
* start and end coordinates are also Ensembl coordinates

Example of link appearance:

<p><img src="http://localhost:8000/static/img/logo/RNAcentral_icon.png" style="width: 16px; height: 16px; vertical-align: middle;"> <a href="http://rnacentral.org/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">Human XIST gene</a></p>

Code:

```
<p>
  <img src="http://localhost:8000/static/img/logo/RNAcentral_icon.png" style="width: 16px; height: 16px; vertical-align: middle;"> <a href="http://localhost:8000/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">Human XIST gene</a>
</p>
```

## Citing RNAcentral

If your website links to RNAcentral, consider citing the most recent
RNAcentral publication:

<blockquote class="callout-info">
  <p>RNAcentral: a comprehensive database of non-coding RNA sequences</p>
  <footer>The RNAcentral Consortium, 2017</footer>
  <footer><em>Nucleic Acids Research (Database issue)</em></footer>
  <a href="http://nar.oxfordjournals.org/content/45/D1/D128.full">NAR</a> |
  <a href="http://europepmc.org/abstract/MED/27794554">EuropePMC</a> |
  <a href="http://www.ncbi.nlm.nih.gov/pubmed/27794554">Pubmed</a>
</blockquote>

## RNAcentral on Twitter

You could also follow or mention us on Twitter: <a href="https://twitter.com/RNAcentral">@RNAcentral</a>

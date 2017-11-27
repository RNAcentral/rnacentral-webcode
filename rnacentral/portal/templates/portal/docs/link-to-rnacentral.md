
## Linking to RNAcentral <a style="cursor: pointer" id="link-to-rnacentral" ng-click="scrollTo('link-to-rnacentral')" name="link-to-rnacentral" class="text-muted smaller"><i class="fa fa-link"></i></a>

 * <a href="" ng-click="scrollTo('link-to-sequence')">How to create a badge on RNAcentral member database website</a>
 * <a href="" ng-click="scrollTo('link-to-genome-location')">How to link to a specific sequence</a>
 * <a href="" ng-click="scrollTo('expert-database-badge')">How to link to a specific genome location</a>
 * <a href="" ng-click="scrollTo('downloads')">Downloads
 * <a href="" ng-click="scrollTo('citing-rnacentral')">Citing RNAcentral</a>

---

## RNAcentral Expert Database badge <a style="cursor: pointer" id="expert-database-badge" ng-click="scrollTo('expert-database-badge')" name="expert-database-badge" class="text-muted smaller"><i class="fa fa-link"></i></a>

If you maintain a database that has been [integrated in RNAcentral](/expert-databases),
please include the **RNAcentral Expert Database badge** on your website:

<img src="/static/img/logo/RNAcentral_expert_database.svg" style="width: 120px">

Example code:

```
<img src="http://rnacentral.org/static/img/logo/RNAcentral_expert_database.svg" style="width: 120px">
```

The badge should link to the [RNAcentral homepage](http://rnacentral.org)
or to the **landing page** of the member database within RNAcentral,
such as [http://rnacentral.org/expert-database/flybase](http://rnacentral.org/expert-database/flybase) or
[http://rnacentral.org/expert-database/gtrnadb](http://rnacentral.org/expert-database/gtrnadb).

The image is available for download in <a href="" ng-click="scrollTo('downloads')">Downloads</a> section.

If you maintain an RNA database and would like to join RNAcentral,
please <a href="http://rnacentral.org/contact">contact us</a>.

---

## Linking to RNAcentral sequences <a style="cursor: pointer" id="link-to-sequence" ng-click="scrollTo('link-to-sequence')" name="link-to-sequence" class="text-muted smaller"><i class="fa fa-link"></i></a>

### Link format

Please use the following format to link to RNAcentral sequences:

`http://rnacentral.org/rna/<RNAcentral identifier>/<NCBI taxonomy identifier>`

These links show information about a specific species using
[NCBI taxonomy identifiers](https://www.ncbi.nlm.nih.gov/taxonomy), for example
*9606* for *Homo sapiens*.

You can use slash `/` or underscore `_` before the NCBI taxonomy identifier:

* <a href="http://rnacentral.org/rna/URS000075A546/9606">URS000075A546/9606</a>
* <a href="http://rnacentral.org/rna/URS000075A546_9606">URS000075A546_9606</a>

Links without NCBI taxonomy identifiers show information from all species
where the sequence was found.

You can optionally add RNAcentral logo before the link, for example:

<p>
  <img src="/static/img/logo/RNAcentral_icon.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="http://rnacentral.org/rna/URS000075A546/9606">URS000075A546/9606</a>
</p>

Example code:

```
<p>
  <img src="http://rnacentral.org/static/img/logo/RNAcentral_icon.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="http://rnacentral.org/rna/URS000075A546/9606">URS000075A546/9606</a>
</p>
```

RNAcentral logo icons are available for download in <a href="" ng-click="scrollTo('downloads')">Downloads</a> section.

### What RNAcentral identifier should I link to?

For a **small number of sequences**, you can find RNAcentral accessions using [text search](/help/text-search).

If you need to perform a **large-scale mapping** between RNAcentral identifiers and Expert Database accessions,
please use the mapping files found in FTP archive:

* Mapping between RNAcentral sequences and all Expert Databases in a **single file**:
  [ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/)

* Mapping between RNAcentral sequences and each Expert Databases in **separate files**:
  [ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/)

---

## Linking to genome locations <a style="cursor: pointer" id="link-to-genome-location" ng-click="scrollTo('link-to-genome-location')" name="link-to-genome-location" class="text-muted smaller"><i class="fa fa-link"></i></a>

### Link format

You can link to a genome location of interest within the RNAcentral genome browser using links like this:

`http://rnacentral.org/genome-browser?species=<species>&chromosome=<chromosome>&start=<start>&end=<end>`

where:

* `<species>` is the species name (lowercase, spaces replaced with underscores as in [Ensembl](https://ensembl.org), for example: *homo_sapiens* or *canis_lupus_familiaris*)
* `<chromosome>` is Ensembl-style (not UCSC-style) chromosome name
* `<start>` and `<end>` coordinates are also Ensembl coordinates

Example:

<p>
  <img src="http://rnacentral.org/static/img/logo/RNAcentral_icon.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="http://rnacentral.org/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">Human XIST gene</a>
</p>

Code:

```
<span>
  <img src="http://rnacentral.org/static/img/logo/RNAcentral_icon.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="http://rnacentral.org/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">Human XIST gene</a>
</span>
```

RNAcentral logo icons are available for download in <a href="" ng-click="scrollTo('downloads')">Downloads</a> section.

---

## Downloads <a style="cursor: pointer" id="downloads" ng-click="scrollTo('downloads')" name="downloads" class="text-muted smaller"><i class="fa fa-link"></i></a>

### RNAcentral logo icons

Here are RNAcentral logo icons in different resolutions:

* <a target="_blank" href="http://rnacentral.org/static/img/logo/logo16x16.png">16x16.png</a>
* <a target="_blank" href="http://rnacentral.org/static/img/logo/logo24x24.png">24x24.png</a>
* <a target="_blank" href="http://rnacentral.org/static/img/logo/logo32x32.png">32x32.png</a>
* <a target="_blank" href="http://rnacentral.org/static/img/logo/logo64x64.png">64x64.png</a>
* <a target="_blank" href="http://rnacentral.org/static/img/logo/logo128x128.png">128x128.png</a>
* <a target="_blank" href="http://rnacentral.org/static/img/logo/RNAcentral_icon.png">full_size.png</a>

### RNAcentral Expert Database badge

* <a target="_blank" href="http://rnacentral.org/static/img/logo/RNAcentral_expert_database.svg">RNAcentral_expert_database.svg</a>

---

## Citing RNAcentral <a style="cursor: pointer" id="citing-rnacentral" ng-click="scrollTo('citing-rnacentral')" name="citing-rnacentral" class="text-muted smaller"><i class="fa fa-link"></i></a>

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

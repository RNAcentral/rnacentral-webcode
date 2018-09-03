
# Linking to RNAcentral <a style="cursor: pointer" id="link-to-rnacentral" ng-click="scrollTo('link-to-rnacentral')" name="link-to-rnacentral" class="text-muted smaller"><i class="fa fa-link"></i></a>

On this page:

 * <a href="" ng-click="scrollTo('link-to-sequence')">RNAcentral Expert Database badge</a>
 * <a href="" ng-click="scrollTo('link-to-genome-location')">Linking to RNAcentral sequences</a>
 * <a href="" ng-click="scrollTo('expert-database-badge')">Linking to genome locations</a>
 * <a href="" ng-click="scrollTo('downloads')">Downloads
 * <a href="" ng-click="scrollTo('citing-rnacentral')">Citing RNAcentral</a>

---

## RNAcentral Expert Database badge <a style="cursor: pointer" id="expert-database-badge" ng-click="scrollTo('expert-database-badge')" name="expert-database-badge" class="text-muted smaller"><i class="fa fa-link"></i></a>

Databases [integrated in RNAcentral](/expert-databases) can display
an **RNAcentral Expert Database badge**:

<a href="https://rnacentral.org" style="text-decoration: none;">
  <img src="/static/img/logo/rnacentral-expert-database.svg"
  style="width: 140px;">
</a>
<a class="btn btn-default" style="margin-left: 20px;" target="_blank" href="https://rnacentral.org/static/img/logo/rnacentral-expert-database.svg">Download (svg)</a>

Example code:

```
<a href="https://rnacentral.org">
  <img src="https://rnacentral.org/static/img/logo/rnacentral-expert-database.svg" style="width: 140px">
</a>
```

The badge should link to the [RNAcentral homepage](https://rnacentral.org)
or to the **landing page** of the member database within RNAcentral,
such as [https://rnacentral.org/expert-database/flybase](https://rnacentral.org/expert-database/flybase) or
[https://rnacentral.org/expert-database/gtrnadb](https://rnacentral.org/expert-database/gtrnadb).

---

## Linking to RNAcentral sequences <a style="cursor: pointer" id="link-to-sequence" ng-click="scrollTo('link-to-sequence')" name="link-to-sequence" class="text-muted smaller"><i class="fa fa-link"></i></a>

### Link format

Please use the following format to link to RNAcentral sequences:

`https://rnacentral.org/rna/<RNAcentral identifier>/<NCBI taxonomy identifier>`

The URL includes
[NCBI taxonomy identifiers](https://www.ncbi.nlm.nih.gov/taxonomy), for example
*9606* for *Homo sapiens*.

Either slash `/` or underscore `_` can be used as a separator:

* <a href="/rna/URS000075A546/9606">URS000075A546/9606</a>
* <a href="/rna/URS000075A546_9606">URS000075A546_9606</a>

Links without NCBI taxonomy identifiers show annotations from all species
where the sequence was found.

You can optionally add RNAcentral logo before the link, for example:

<p>
  <img src="/static/img/logo/rnacentral-logo.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="/rna/URS000075A546/9606">URS000075A546/9606</a>
</p>

Example code:

```
<p>
  <img src="https://rnacentral.org/static/img/logo/rnacentral-logo.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="https://rnacentral.org/rna/URS000075A546/9606">URS000075A546/9606</a>
</p>
```

RNAcentral logos are available in the <a href="" ng-click="scrollTo('downloads')">Downloads</a> section.

### Mapping between third-party identifiers and RNAcentral IDs

For a **small number of sequences**, you can find RNAcentral accessions using [text search](/help/text-search).

If you need to perform a **large-scale mapping** between RNAcentral identifiers and Expert Database accessions,
please use the mapping files found in FTP archive:

* Mapping between RNAcentral sequences and all Expert Databases in a **single file**:
  [ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/)

* Mapping between RNAcentral sequences and each Expert Databases in **separate files**:
  [ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/](ftp://ftp.ebi.ac.uk/pub/databases/RNAcentral/current_release/id_mapping/database_mappings/)

---

## Linking to genome locations <a style="cursor: pointer" id="link-to-genome-location" ng-click="scrollTo('link-to-genome-location')" name="link-to-genome-location" class="text-muted smaller"><i class="fa fa-link"></i></a>

## Link format <a style="cursor: pointer" id="link-format" ng-click="scrollTo('link-format')" name="link-format" class="text-muted smaller"><i class="fa fa-link"></i></a>

You can link to a genome location of interest within the RNAcentral genome browser using links like this:

`https://rnacentral.org/genome-browser?species=<species>&chromosome=<chromosome>&start=<start>&end=<end>`

where:

* `<species>` - organism name (lowercase, spaces replaced with underscores as in [Ensembl](https://ensembl.org), for example: *homo_sapiens* or *canis_lupus_familiaris*)
* `<chromosome>` - chromosome name in Ensembl format, for example `1` (not `chr1`)
* `<start>` and `<end>` - genome coordinates

Example:

<p>
  <img src="/static/img/logo/rnacentral-logo.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="https://rnacentral.org/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">Human XIST gene</a>
</p>

Example code:

```
<p>
  <img src="https://rnacentral.org/static/img/logo/rnacentral-logo.png" style="width: 16px; height: 16px; vertical-align: middle;">
  <a href="https://rnacentral.org/genome-browser?species=homo_sapiens&chromosome=X&start=73819307&end=73856333">Human XIST gene</a>
</p>
```

---

## Downloads <a style="cursor: pointer" id="downloads" ng-click="scrollTo('downloads')" name="downloads" class="text-muted smaller"><i class="fa fa-link"></i></a>

<h3> RNAcentral icons <img src="/static/img/logo/rnacentral-logo-32x32.png"></h3>

Here are RNAcentral logo icons in different resolutions:

* <a target="_blank" href="https://rnacentral.org/static/img/logo/rnacentral-logo-16x16.png">16x16</a>
* <a target="_blank" href="https://rnacentral.org/static/img/logo/rnacentral-logo-24x24.png">24x24</a>
* <a target="_blank" href="https://rnacentral.org/static/img/logo/rnacentral-logo-32x32.png">32x32</a>
* <a target="_blank" href="https://rnacentral.org/static/img/logo/rnacentral-logo-64x64.png">64x64</a>
* <a target="_blank" href="https://rnacentral.org/static/img/logo/rnacentral-logo-128x128.png">128x128</a>
* <a target="_blank" href="https://rnacentral.org/static/img/logo/rnacentral-logo.png">530x530</a>

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

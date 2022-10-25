
# Secondary structure

RNAcentral generates secondary structure (2D) diagrams using
the [R2DT](https://github.com/RNAcentral/R2DT) software that
visualises RNA structure using standard layouts or templates.
Learn more about the method in the [R2DT paper](https://www.nature.com/articles/s41467-021-23555-5)
or check out the code on [GitHub](http://github.com/rnacentral/r2dt).

## R2DT overview

RNAcentral stores RNA secondary structures computed using R2DT for [millions of non-coding RNAs](https://rnacentral.org/search?q=has_secondary_structure:%22True%22).
The structures are displayed using a library of ~4,000 templates, including:

1. Small rRNA subunit (SSU) and 5S rRNA templates from the [Comparative RNA Website](http://www.rna.ccbb.utexas.edu) (CRW);
2. Small and large rRNA subunit (LSU) templates from [RiboVision](http://apollo.chemistry.gatech.edu/RiboVision/);
3. Isotype-specific tRNA templates from [GtRNAdb](http://gtrnadb.ucsc.edu).
4. RNAse P templates from the RNAse P database;
5. [Rfam](http://rfam.org) consensus secondary structures for all other RNA types;

For each sequence the **R2DT pipeline** automatically selects the template using [ribovore](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-021-04316-z),
folds the sequence into the template structure using [Infernal](http://eddylab.org/infernal),
and visualises it using [Traveler](https://github.com/davidhoksza/traveler).

<img src="https://github.com/RNAcentral/R2DT/raw/master/examples/method-overview.png">

## RNA secondary structure in RNAcentral

The secondary structures are displayed in text search results, on RNA sequence pages,
and in sequence similarity search results. For example, text search results include
simplified outlines of the structures:

<a class="thumbnail" href="/search?q=RNA">
  <img src="/static/img/2d-in-text-search.png">
</a>

Clicking on any thumbnail shows a detailed diagram, such as the following fly RNAse
P structure:

<a class="thumbnail" href="/rna/URS00001AD746/7227?tab=2d">
  <img src="/static/img/2d-example.png">
</a>

### What do colours mean?

The differences between the template and the sequence are highlighted in colour.
The nucleotides shown in black are identical to the template while the nucleotides
that differ from the template are shown in several colours depending on whether
it's an insertion (magenta) or modification (green).

## R2DT web application

A secondary structure can be generated for an RNA sequence using the [R2DT web application](https://rnacentral.org/r2dt).

<a class="thumbnail" href="/r2dt">
  <img src="/static/img/r2dt.png">
</a>

### Template used <a style="cursor: pointer" id="template" ng-click="scrollTo('template')" name="template" class="text-muted smaller"><i class="fa fa-link"></i></a>

By default R2DT chooses a template automatically but it is possible to choose a
template manually by clicking **Show advanced** and browsing the templates.
This option could be useful to highlight species-specific regions. For example,
one could display the human small SSU rRNA using a bacterial template.

<img src="/static/img/r2dt-advanced-options.png">

### Constrained folding <a style="cursor: pointer" id="constrained_folding" ng-click="scrollTo('constrained_folding')" name="constrained_folding" class="text-muted smaller"><i class="fa fa-link"></i></a>

The advanced options also enable constrained folding, which uses [RNAfold](http://rna.tbi.univie.ac.at/cgi-bin/RNAWebSuite/RNAfold.cgi)
from the [Vienna RNA package](https://www.tbi.univie.ac.at/RNA/) to add base pairs
for the single-stranded regions that are not modelled by the templates.
For example, this method can improve microRNA diagrams where the Rfam consensus
structure has long dangling ends or large hairpin loops. It can also fold
species-specific insertions found in many rRNAs:

<img src="/static/img/r2dt-constrained-folding.png">

There are four ways of using constrained folding:

- **Auto:** by default the best mode is chosen automatically based on RNA type and insertion size;
- **Full molecule:** the entire molecule is folded using RNAfold with the template structure provided as a constraint;
- **Insertions only:** the secondary structure of the insertion relative to the template is predicted with RNAfold and added to the diagram;
- **All constraints enforced:** same as above except for the nucleotides that align to single-stranded regions of the template are kept unpaired when predicting the new structure using RNAfold

To use constrained folding, choose one of the modes in the advanced options:

<img src="/static/img/r2dt-constrained-folding-options.png">

## Embeddable widget

It is possible to embed an R2DT secondary structure into any website, and it has
already been added to [FlyBase](http://flybase.org/), [SGD](http://yeastgenome.org/),
and [Rfam](http://rfam.org/).

Find out more about [how to integrate this widget into your website](https://github.com/RNAcentral/r2dt-web).

## Find out more

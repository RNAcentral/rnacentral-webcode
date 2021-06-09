
# Secondary structure

RNAcentral generates secondary structure (2D) diagrams using
the [R2DT](https://github.com/RNAcentral/R2DT) software that
visualises RNA structure using standard layouts or templates.
Learn more in the [R2DT paper](https://www.nature.com/articles/s41467-021-23555-5)

<iframe width="560" height="315" src="https://www.youtube.com/embed/La7HA8i_h5I" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## 2D templates

Four types of secondary structure templates are used:

1. Small rRNA subunit (SSU) and 5S rRNA templates from the [Comparative RNA Website](http://www.rna.ccbb.utexas.edu) (CRW);
2. [Rfam](http://rfam.org) consensus secondary structures for all other RNA types;
3. Small and large rRNA subunit (LSU) templates from [RiboVision](http://apollo.chemistry.gatech.edu/RiboVision/);
4. Isotype-specific tRNA templates from [GtRNAdb](http://gtrnadb.ucsc.edu).

For each sequence the **R2DT pipeline** automatically selects the template using a custom set of covariance models,
folds the sequence into the template structure using [Infernal](http://eddylab.org/infernal),
and visualises it using [Traveler](https://github.com/davidhoksza/traveler).

<a href='/search?q=has_secondary_structure:"True"' class="btn btn-primary">Browse all RNAs with secondary structures</a>

## What do colours mean?

The differences between the template and the sequence are highlighted in colour.
For example, in the following *Thermus thermophilus*
[SSU structure](/rna/URS000080E226/274)
nucleotides shown in black are identical to the CRW template
while the nucleotides that differ from the template are shown in several colours
depending on whether it's an insertion (red) or modification (green):

<a class="thumbnail" href="/rna/URS000080E226/274">
  <img src="/static/img/2d-example.png">
</a>

## Acknowledgements

We would like to thank [David Hoksza](https://github.com/davidhoksza)
for help with the [Traveler](https://github.com/davidhoksza/traveler) software, [Robin Gutell](http://www.rna.ccbb.utexas.edu) for providing the rRNA templates, [Eric Nawrocki](https://github.com/nawrockie) for help with the ribotyper software, [Anton S. Petrov](http://cool.gatech.edu/people/petrov-anton) for the LSU templates, as well as [Patricia Chan](https://www.soe.ucsc.edu/people/pchan) and [Todd Lowe](https://www.soe.ucsc.edu/people/lowe) for providing the tRNA templates.

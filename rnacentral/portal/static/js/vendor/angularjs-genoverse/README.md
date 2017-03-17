AngularJS - Genoverse
=====================

[![Build Status](https://travis-ci.org/RNAcentral/angularjs-genoverse.svg?branch=master)](https://travis-ci.org/RNAcentral/angularjs-genoverse)
[![npm version](https://badge.fury.io/js/angularjs-genoverse.svg)](https://badge.fury.io/js/angularjs-genoverse)
[![Bower version](https://badge.fury.io/bo/angularjs-genoverse.svg)](https://badge.fury.io/bo/angularjs-genoverse)

An AngularJS (1.x) directive, wrapping the [Genoverse genome browser](https://github.com/wtsi-web/Genoverse) version 3.

Read more about how to use the browser here: http://wtsi-web.github.io/Genoverse/.

Example
=======

A complete example is available at: https://RNAcentral.github.io/angularjs-genoverse/

Use this directive as a "web component" in your HTML:

```HTML
<genoverse genome="genome" chromosome="chromosome" start="start" end="end">
    <genoverse-track name="'Sequence'" model="Genoverse.Track.Model.Sequence.Ensembl" view="Genoverse.Track.View.Sequence" controller="Genoverse.Track.Controller.Sequence" url="urls.sequence" resizable="'auto'" auto-height="true" extra="{100000: false}"></genoverse-track>
    <genoverse-track name="'Genes'" labels="true" info="'Ensembl API genes'" model="Genoverse.Track.Model.Gene.Ensembl" view="Genoverse.Track.View.Gene.Ensembl" url="urls.genes" resizable="'auto'" auto-height="true"></genoverse-track>
    <genoverse-track name="'Transcripts'" labels="true" info="'Ensembl API transcripts'" model="Genoverse.Track.Model.Transcript.Ensembl" view="Genoverse.Track.View.Transcript.Ensembl" url="urls.transcripts" resizable="'auto'" auto-height="true"></genoverse-track>
</genoverse>
```


Installation and requirements
=============================

This package is available at [NPM](https://www.npmjs.com/package/angularjs-genoverse) and [Bower](https://github.com/RNAcentral/angularjs-genoverse).

We don't provide wrappers for AMD, CommonJS or ECMA6 modules, so you might need a shim for Webpack, Browserify, SystemJS or RequireJS.

To include the script with this directive in your HTML, use:

```HTML
<!-- Uglified version -->
<script src=".../angularjs-genoverse/dist/angularjs-genoverse.min.js"></script>

<!-- Concatenated, but non-obfuscated source -->
<script src=".../angularjs-genoverse/dist/angularjs-genoverse.all.js"></script>
```


You'll also need the Genoverse browser itself (both JS and CSS). You can either download it
directly from [github](https://github.com/wtsi-web/Genoverse), or use the version, included in this repository's `lib` folder:

```HTML
<!-- CSS -->
<link rel="stylesheet" href="/lib/Genoverse/css/genoverse.css">
<link rel="stylesheet" href="/lib/Genoverse/css/controlPanel.css">
<link rel="stylesheet" href="/lib/Genoverse/css/fileDrop.css">
<link rel="stylesheet" href="/lib/Genoverse/css/karyotype.css">
<link rel="stylesheet" href="/lib/Genoverse/css/resizer.css">
<link rel="stylesheet" href="/lib/Genoverse/css/trackControls.css">
<link rel="stylesheet" href="/lib/Genoverse/css/tooltips.css">

<!-- Javascript -->
<script src=".../angularjs-genoverse/lib/Genoverse/js/genoverse.combined.js"></script>
<script src=".../angularjs-genoverse/lib/Genoverse/js/genomes/grch38.js"></script>

```


To use it in your AngularJS module, you need to specify `Genoverse` module as a dependency, e.g.

```javascript
angular.module("Example", ["Genoverse"]);
```

AngularJS-Genoverse depends on `angular.js` and `jquery`. Don't forget to include them as well.

Configuration
=============

We have 2 directives in this package: `<genoverse>` and `<genoverse-track>`.

Below is the full description of their attributes that you can use to configure them.

Note that all attributes are interpolated, i.e. use 2-way data-binding. So if you try passing an attribute as
`<genoverse attr="val">`, angular will look for variable, called "val", not a string "val". If you want just to pass
a literal, use another pair of quotes like: `<genoverse attr="'literal'"`.

genoverse
---------

Global configuration of the browser. To specify tracks, use nested `<genoverse-track>` tags within `genoverse`.

Attribute  | Type   | Required | Description
---------- | ------ | -------- | -----------
genome     | Object | true     | {<br>   'species': 'Homo sapiens',<br>   'synonyms': ['human'],<br>   'assembly': 'GRCh38',<br>   'assembly_ucsc': 'hg38',<br>   'taxid': 9606,<br>   'division': 'Ensembl',<br>   'example_location': {<br>     'chromosome': 'X',<br>     'start': 73792205,<br>     'end': 73829231<br> }
chromosome | String | true     | Ensembl-style chromosome name, e.g. 'X' or '1' or '3R' or 'III'
start      | Number | true     | Current genome location, where viewport starts
end        | Number | true     | Current genome location, where viewport ends


genoverseTrack
--------------

Configuration of a single track. Note that you don't have to create Scalebar track - it's present by default.


Attribute        | Type               | Required | Default | Description
---------------- | ------------------ | -------- | ------- | -----------
name             | String             | true     |         | Track id
labels           | Boolean            | false    | true    | Display labels
id               | String             | false    |         |
model            | Object             | true     |         | `Genoverse.Track.Model` subclass
model-extra      | Object             | false    |         | Extra parameters to extend your model with: `model.extend(modelExtra)`
url              | String OR Function | true     |         | String template or function that returns string template that track uses to download features data to display.<br><br> E.g. 'https://rest.ensemblgenomes.org/sequence/region/homo_sapiens/__CHR__:__START__-__END__?content-type=text/plain'.<br><br>Note that it uses `__CHR__`, `__START__` and `__END__` variables, but doesn't support a variable for species/genome.
view             | Object             | true     |         | `Genoverse.Track.View` subclass
view-extra       | Object             | false    |         | Extra parameters to extend your view with: `view.extend(viewExtra)`
controller       | Object             | false    |         | `Genoverse.Track.Controller` subclass
controller-extra | Object             | false    |         | Extra parameters to extend your controller with: `controller.extend(controllerExtra)`
resizable        | String             | false    | 'auto'  | Allow user to resize tracks by dragging a handle?
auto-height      | Boolean            | false    | false   | Automatically resize tracks upon load to take as much space as is required to display all features
extra            | Object             | false    |         | Extra parameters to extend your track's configuration, e.g. `track.extend(extra)`


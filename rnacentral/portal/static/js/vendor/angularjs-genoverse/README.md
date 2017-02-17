AngularJS - Genoverse
=====================

An AngularJS (1.x) directive, wrapping the [Genoverse genome browser](https://github.com/wtsi-web/Genoverse).

Read more about how to use the browser here: http://wtsi-web.github.io/Genoverse/

Example
=======

A complete example is available at: https://RNAcentral.github.io/angularjs-genoverse/

Use this directive as a "web component" in your HTML:

```HTML
<genoverse genome={} chromosome="X" start="1" stop="1000000">
   <genoverse-track id="" name="Sequence" info="" label="true"
    url-template="{{protocol}}//{{endpoint}}/overlap/region/{{species}}/{{chromosome}}:{{start}}-{{end}}?feature=gene;content-type=application/json"
    url-variables="{protocol: 'https', endpoint: 'rest.ensembl.org'">
   </genoverse-track>
</genoverse>
```


Installation and requirements
=============================

This package is available at [NPM]() and [Bower]().

We don't provide wrappers for AMD, CommonJS or ECMA6 modules, so you might need a shim for Webpack, Browserify, SystemJS or RequireJS.

To include the script with this directive in your HTML, use:

```HTML
<!-- Uglified version -->
<script src=".../angularjs-genoverse/dist/angularjs-genoverse.min.js"></script>

<!-- Concatenated, but non-obfuscated source -->
<script src=".../angularjs-genoverse/dist/angularjs-genoverse.all.js"></script>
```



You'll also need the Genoverse browser itself (both JS and CSS). You can either download it
directly from [github](https://github.com/wtsi-web/Genoverse), or use the verion, included in this repository's `lib` folder:

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

AngularJS-Genoverse also depends on `angular.js` and `jquery`. Don't forget to include them as well.

Configuration
=============

We have 2 directives in this package: genoverse and genoverse-track. Here is the full description of their attributes
that you can use to configure them.

genoverse
---------

Attribute | Description
--------- | -----------
genome    | {Object}
chromosome | {String} Ensembl-style chromosome name
start     | {Number}
end       | {Number}


genoverseTrack
--------------

Attribute | Description
--------- | -----------
id            |
name          |
info          |
label         |
url-template  |
url-variables |


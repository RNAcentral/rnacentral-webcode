angular.module("textSearch", ['ngResource', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'Genoverse'])
    .config(sceWhitelist)
    .controller("rnaSequenceController", rnaSequenceController);

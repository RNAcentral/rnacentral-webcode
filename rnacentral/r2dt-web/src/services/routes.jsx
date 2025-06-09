let ebiDevOrProd = process.env.REACT_APP_BRANCH === 'dev' ? 'wwwdev' : 'www';
let server =  `https://${ebiDevOrProd}.ebi.ac.uk/Tools/services/rest/r2dt`;
let firebaseServer = process.env.REACT_APP_FIREBASE;
let rnacentralServer = process.env.REACT_APP_BRANCH === 'dev' ? 'test.rnacentral' : 'rnacentral';
let rnaCanvasServer = process.env.REACT_APP_BRANCH === 'dev' ? 'https://rna2drawer2-dev.uk.r.appspot.com' : 'https://rnacanvas.app';

module.exports = {
  submitJob:  () => `${server}/run`,
  jobStatus:  (jobId) => `${server}/status/${jobId}`,
  fetchFasta: (jobId) => `${server}/result/${jobId}/fasta`,
  fetchJson:  (jobId) => `${server}/result/${jobId}/json`,
  fetchSvg:   (jobId) => `${server}/result/${jobId}/svg`,
  fetchSvgAn: (jobId) => `${server}/result/${jobId}/svg_annotated`,
  fetchThumb: (jobId) => `${server}/result/${jobId}/thumbnail`,
  fetchTsv:   (jobId) => `${server}/result/${jobId}/tsv`,
  firebase:   () => `${firebaseServer}/data.json`,
  firebaseId: (id) => `${firebaseServer}/data/${id}.json`,
  fetchUrs:   (urs) => `https://${rnacentralServer}.org/api/v1/rna/${urs}/2d/`,
  rnaCanvas:  (jobId) => `${rnaCanvasServer}?rna_2d_schema_url=${server}/result/${jobId}/json`,
  canvasCode: (jobId) => `https://code.rnacanvas.app/?schema=${server}/result/${jobId}/json`,
  xRNA:       (jobId) => `https://ldwlab.github.io/XRNA-React/?source_url=${server}/result/${jobId}/json`
};

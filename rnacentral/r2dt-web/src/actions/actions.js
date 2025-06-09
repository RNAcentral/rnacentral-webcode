import * as types from './actionTypes';
import routes from 'services/routes.jsx';
import {store} from 'app.jsx';

//
// submission form
//
export function firebaseFetchData(sequence, templateId) {
  let foundR2DT = false;
  let currentDate = new Date();

  return function(dispatch) {
    fetch(routes.firebase(), {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    })
    .then(function (response) {
      if (response.ok) { return response.json() }
      else { throw response }
    })
    .then(data => {
      data && Object.entries(data).map(([key,value]) => {
        if (sequence === value.sequence && templateId === value.templateId){
          let submitted = new Date(value.date)
          submitted.setDate(submitted.getDate()+7);
          submitted.setHours(submitted.getHours() - 1);

          if (currentDate < submitted && (value.status === "RUNNING" || value.status === "FINISHED")) {
            dispatch({type: types.SET_FIREBASE_ID, data: key})
            dispatch(fetchStatus(value.r2dt_id));
            foundR2DT = true;
          } else {
            dispatch({type: types.SET_FIREBASE_ID, data: key})
          }
        }
      });
      if (!foundR2DT) { dispatch(onSubmit(sequence, true)) }
    })
    .catch(error => dispatch({type: types.FIREBASE_STATUS, status: 'fetchError'}));
  }
}

export function firebasePost(r2dt_id, sequence, templateId) {
  const currentDate = new Date();

  return function(dispatch) {
    fetch(routes.firebase(), {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        r2dt_id: r2dt_id,
        sequence: sequence,
        templateId: templateId,
        date: currentDate
      })
    })
    .then(function (response) {
      if (response.ok) { return response.json() }
      else { throw response }
    })
    .then(data => {dispatch({type: types.SET_FIREBASE_ID, data: data.name})})
    .catch(error => dispatch({type: types.FIREBASE_STATUS, status: 'postError'}));
  }
}

export function firebasePatch(r2dt_id, svg, status) {
  let state = store.getState();

  if (state.firebaseId) {
    const currentDate = new Date();
    let data = {};

    if (r2dt_id) {
      data = { r2dt_id: r2dt_id, date: currentDate }
    } else if (svg){
      data = { svg: svg }
    } else if (status){
      data = { status: status }
    }

    return function(dispatch) {
      fetch(routes.firebaseId(state.firebaseId), {
        method: 'PATCH',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })
      .catch(error => dispatch({type: types.FIREBASE_STATUS, status: 'patchError'}));
    }
  }
}

export function onSubmit(sequence, example=false, dotBracket=false) {
  let state = store.getState();
  let templateId = dotBracket ? "" : state.templateId;
  let body = `email=rnacentral%40gmail.com&sequence=${sequence}&template_id=${templateId}`;
  if (!dotBracket && state.constrainedFolding && state.foldType.length > 0) {
    body = body + `&constraint=${state.constrainedFolding}&fold_type=${state.foldType}`
  } else if (!dotBracket && state.constrainedFolding) {
    body = body + `&constraint=${state.constrainedFolding}`
  }

  return function(dispatch) {
    dispatch({type: types.UPDATE_STATUS});
    fetch(routes.submitJob(), {
      method: 'POST',
      headers: {
        'Accept': 'text/plain',
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body
    })
    .then(function (response) {
      if (response.ok) { return response.text() }
      else { throw response }
    })
    .then(data => {
        dispatch({type: types.SUBMIT_JOB, status: 'success', data: data});
        if (example && state.firebaseId) { dispatch(firebasePatch(data, "", "")) }
        if (example && !state.firebaseId) { dispatch(firebasePost(data, sequence, state.templateId)) }
        if (!example) { dispatch({type: types.SET_FIREBASE_ID, data: ""}) }
        dispatch(fetchStatus(data));
    })
    .catch(error => dispatch({type: types.SUBMIT_JOB, status: 'error', response: error}));
  }
}

export function onSubmitUrs(urs) {
  let state = store.getState();

  return function(dispatch) {
    if (state.status === "notSubmitted") { dispatch({type: types.UPDATE_STATUS}) }
    fetch(routes.fetchUrs(urs), {
      method: 'GET'
    })
    .then(function (response) {
      if (response.ok) { return response.json() }
      else { throw response }
    })
    .then(response => {
      let width = (response.data.layout.match(/width="(.*?)"/)[1]);
      let height = (response.data.layout.match(/height="(.*?)"/)[1]);
      dispatch({
        type: types.URS_RESULTS,
        status: 'success',
        width: width,
        height: height,
        svg: response.data.layout,
        notation: response.data.secondary_structure,
        template: response.data.model_id,
        source: response.data.source,
        jobId: urs
      })
    })
    .catch(error => dispatch({type: types.URS_RESULTS, status: 'error'}));
  }
}

export function onExampleSequence(sequence) {
  return {type: types.EXAMPLE_SEQUENCE, sequence: sequence};
}

export function onClearSequence() {
  return {type: types.CLEAR_SEQUENCE}
}

export function onSequenceTextAreaChange(event) {
  let state = store.getState();
  let sequence = event.target.value;

  return function(dispatch) {
    if (state.advancedSearchCollapsed) { dispatch({type: types.TEMPLATE_CHANGE, templateId: ""}) }
    dispatch({type: types.TEXTAREA_CHANGE, sequence: sequence});
  }
}

export function onChangeTemplateId(event) {
  let state = store.getState();
  let templateId = ""

  if (state.searchMethod === "option1") {
    templateId = event ? event.target.value : ""
  } else {
    templateId = event[0] && event[0].model_id ? event[0].model_id : "";
  }

  return {type: types.TEMPLATE_CHANGE, templateId: templateId ? templateId : ""};
}

export function onChangeConstrainedFolding() {
  return function(dispatch) {
    dispatch({type: types.TOGGLE_CONSTRAINED_FOLDING})
    dispatch({type: types.FOLD_TYPE, foldType: ""})
  }
}

export function onChangeFoldType(event) {
  return {type: types.FOLD_TYPE, foldType: event.target.value}
}

export function clearTemplateId() {
  return {type: types.TEMPLATE_CHANGE, templateId: ""}
}

export function handleOptionChange(event) {
  return {type: types.SEARCH_METHOD, searchMethod: event.target.value};
}

export function invalidSequence() {
  return {type: types.INVALID_SEQUENCE}
}

export function invalidDotBracket() {
  return {type: types.INVALID_DOT_BRACKET}
}

export function onToggleAdvancedSearch() {
  let state = store.getState();
  return function(dispatch) {
    if (!state.advancedSearchCollapsed && !state.jobId) {
      dispatch({type: types.TEMPLATE_CHANGE, templateId: "" })
    }
    if (!state.advancedSearchCollapsed && state.constrainedFolding) {
      dispatch({type: types.TOGGLE_CONSTRAINED_FOLDING})
    }
    if (!state.advancedSearchCollapsed && state.foldType) {
      dispatch({type: types.FOLD_TYPE, foldType: ""})
    }
    dispatch({type: types.TOGGLE_ADVANCED_SEARCH });
  }
}

//
// status
//
export function fetchStatus(jobId) {
  let state = store.getState();

  return function(dispatch) {
    if (state.status === "notSubmitted") { dispatch({type: types.UPDATE_STATUS}) }
    if (!state.jobId) { dispatch({type: types.SET_JOB_ID, jobId: jobId}) }
    fetch(routes.jobStatus(jobId), {
      method: 'GET',
      headers: { 'Accept': 'text/plain' }
    })
    .then(function(response) {
      if (response.ok) { return response.text() }
      else { throw response }
    })
    .then((data) => {
      if (data === 'RUNNING' || data === 'QUEUED') {
        let statusTimeout = setTimeout(() => store.dispatch(fetchStatus(jobId)), 2000);
        dispatch({type: types.SET_STATUS_TIMEOUT, timeout: statusTimeout});
      } else if (data === 'FINISHED') {
        // Wait another second to change the status. This will allow the SVG resultType to work correctly.
        let statusTimeout = setTimeout(() => dispatch({type: types.FETCH_RESULTS}), 1000);
        dispatch({type: types.SET_STATUS_TIMEOUT, timeout: statusTimeout});
        dispatch(getSvg(jobId));
        dispatch(getFasta(jobId));
        dispatch(getTsv(jobId));
      } else if (data === 'NOT_FOUND') {
        dispatch({type: types.FETCH_STATUS, status: 'NOT_FOUND'})
      } else if (data === 'FAILURE') {
        dispatch({type: types.FETCH_STATUS, status: 'FAILURE'})
      } else if (data === 'ERROR') {
        dispatch({type: types.FETCH_STATUS, status: 'ERROR'})
      }
      if (state.firebaseId){ dispatch(firebasePatch("", "", data))}
    })
    .catch(error => {
      if (store.getState().hasOwnProperty('statusTimeout')) {
        clearTimeout(store.getState().statusTimeout); // clear status timeout
      }
      dispatch({type: types.FETCH_STATUS, status: 'error'})
    });
  }
}

//
// results
//
export function getSvg(jobId) {
  let state = store.getState();
  let svg = "";

  return function(dispatch) {
    fetch(routes.fetchSvg(jobId), {
      method: 'GET',
      headers: { 'Accept': 'text/plain' },
    })
    .then(function (response) {
      if (response.ok) { return response.text() }
      else { throw response }
    })
    .then(data => {
      let width = (data.match(/width="(.*?)"/)[1]);
      let height = (data.match(/height="(.*?)"/)[1]);
      let replaceSVGColor = data.replace("rgb(255, 0, 0)", "rgb(255,0,255)")
      dispatch({type: types.GET_SVG, status: 'success', width: width, height: height, svg: replaceSVGColor});
      svg = true;
    })
    .catch(error => {
      svg = false;
      dispatch({type: types.GET_SVG, status: 'error'});
    })
    .finally(() => {
      if (state.firebaseId){ dispatch(firebasePatch("", svg, "")) }
    });
  }
}

export function onToggleColors(svg) {
  let state = store.getState();
  const colourOn = ['class="green"', 'class="red"', 'class="blue"'];
  const colourOff = ['class="ex-green"', 'class="ex-red"', 'class="ex-blue"'];

  if(state.svgColor){
    colourOn.forEach( (tag, i) => svg = svg.replace(new RegExp(tag, "g"), colourOff[i]) )
  } else {
    colourOff.forEach( (tag, i) => svg = svg.replace(new RegExp(tag, "g"), colourOn[i]) )
  }

  return {type: types.SVG_COLORS, svg: svg};
}

export function onToggleNumbers(svg) {
  let state = store.getState();
  const numberOn = [
    'class="numbering-label"',
    'class="numbering-line"',
    'class="numbering-label sequential"',
    'class="numbering-line sequential"'
  ];
  const numberOff = [
    'class="numbering-label" visibility="hidden"',
    'class="numbering-line" visibility="hidden"',
    'class="numbering-label sequential" visibility="hidden"',
    'class="numbering-line sequential" visibility="hidden"'
  ];

  if(state.svgNumber){
    numberOn.forEach( (tag, i) => svg = svg.replace(new RegExp(tag, "g"), numberOff[i]) )
  } else {
    numberOff.forEach( (tag, i) => svg = svg.replace(new RegExp(tag, "g"), numberOn[i]) )
  }

  return {type: types.SVG_NUMBERS, svg: svg};
}

export function getFasta(jobId) {
  let state = store.getState();

  return function(dispatch) {
    fetch(routes.fetchFasta(jobId), {
      method: 'GET',
      headers: { 'Accept': 'text/plain' },
    })
    .then(function (response) {
      if (response.ok) { return response.text() }
      else { throw response }
    })
    .then(data => {
      let lines = (data.match(/[^\r\n]+/g));
      let description = lines[0];
      let sequence = lines[1];
      let notation = lines[2];
      if (description && sequence && !/^[>]/.test(state.sequence)){
        dispatch({type: types.UPDATE_SEQUENCE, sequence: description + '\n' + sequence})
      }
      dispatch({type: types.FASTA, status: 'success', notation: notation})
    })
    .catch(error => dispatch({type: types.FASTA, status: 'error'}));
  }
}

export function getTsv(jobId) {
  let state = store.getState();

  return function(dispatch) {
    fetch(routes.fetchTsv(jobId), {
      method: 'GET',
      headers: { 'Accept': 'text/plain' },
    })
    .then(function (response) {
      if (response.ok) { return response.text() }
      else { throw response }
    })
    .then(data => {
      let lines = (data.match(/[^\t]+/g));
      let template = lines[1];
      let source = lines[2].trimEnd();
      dispatch({type: types.TSV, status: 'success', template: template, source: source});
      if (!state.templateId) { dispatch({type: types.TEMPLATE_CHANGE, templateId: template}) }
    })
    .catch(error => dispatch({type: types.TSV, status: 'error'}));
  }
}
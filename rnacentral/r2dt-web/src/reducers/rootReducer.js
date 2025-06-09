import * as actions from "../actions/actionTypes";
import initialState from "../store/initialState";


const rootReducer = function (state = initialState, action) {
  let newState;

  switch (action.type) {
    //
    // submission form
    //
    case actions.FIREBASE_STATUS:
      switch (action.status) {
        case 'fetchError':
          return Object.assign({}, state, { firebaseStatus: "fetchError" });
        case 'postError':
          return Object.assign({}, state, { firebaseStatus: "postError" });
        case 'patchError':
          return Object.assign({}, state, { firebaseStatus: "patchError" });
        default:
          return newState;
      }

    case actions.SUBMIT_JOB:
      switch (action.status) {
        case 'success':
          return Object.assign({}, state, {
            jobId: action.data,
            status: "RUNNING",
            submissionError: ""
          });
        case 'error':
          return Object.assign({}, state, {status: "error", submissionError: action.response.statusText});
        default:
          return newState;
      }

    case actions.SET_FIREBASE_ID:
      return Object.assign({}, state, {firebaseId: action.data});

    case actions.UPDATE_STATUS:
      return Object.assign({}, state, {status: "RUNNING"});

    case actions.EXAMPLE_SEQUENCE:
      return Object.assign({}, state, {
        jobId: null,
        status: "notSubmitted",
        submissionError: null,
        sequence: action.sequence,
        width: 900,
        height: 600,
        svg: null,
        svgColor: true,
        svgNumber: true,
        notation: "",
        template: "",
        source: "",
        firebaseId: null,
        firebaseStatus: "",
      });

    case actions.CLEAR_SEQUENCE:
      return Object.assign({}, state, {
        jobId: null,
        status: "notSubmitted",
        submissionError: null,
        sequence: "",
        width: 900,
        height: 600,
        svg: null,
        svgColor: true,
        svgNumber: true,
        notation: "",
        template: "",
        source: "",
        firebaseId: null,
        firebaseStatus: "",
        advancedSearchCollapsed: true,
        templateId: "",
        searchMethod: "option1",
        constrainedFolding: false,
        foldType: ""
      });

    case actions.TEXTAREA_CHANGE:
      return Object.assign({}, state, {
        jobId: null,
        status: "notSubmitted",
        submissionError: null,
        sequence: action.sequence,
        width: 900,
        height: 600,
        svg: null,
        svgColor: true,
        svgNumber: true,
        notation: "",
        template: "",
        source: "",
        firebaseId: null,
        firebaseStatus: "",
      });

    case actions.TEMPLATE_CHANGE:
      return Object.assign({}, state, {templateId: action.templateId});

    case actions.SEARCH_METHOD:
      return Object.assign({}, state, {searchMethod: action.searchMethod});

    case actions.INVALID_SEQUENCE:
      return Object.assign({}, state, {status: "invalidSequence"});

    case actions.INVALID_DOT_BRACKET:
      return Object.assign({}, state, {status: "invalidDotBracket"});

    case actions.TOGGLE_ADVANCED_SEARCH:
      return Object.assign({}, state, { advancedSearchCollapsed: !state.advancedSearchCollapsed });

    case actions.TOGGLE_CONSTRAINED_FOLDING:
      return Object.assign({}, state, { constrainedFolding: !state.constrainedFolding });

    case actions.FOLD_TYPE:
      return Object.assign({}, state, { foldType: action.foldType });

    //
    // status
    //
    case actions.FETCH_STATUS:
      if (action.status === 'error') {
        return Object.assign({}, state, {status: "error"});
      } else if (action.status === 'NOT_FOUND') {
        return Object.assign({}, state, {status: "NOT_FOUND"});
      } else if (action.status === 'FAILURE') {
        return Object.assign({}, state, {status: "FAILURE"});
      } else {
        return Object.assign({}, state, {status: action})
      }

    case actions.SET_JOB_ID:
      return Object.assign({}, state, {jobId: action.jobId});

    case actions.SET_STATUS_TIMEOUT:
      return Object.assign({}, state, {statusTimeout: action.statusTimeout});

    //
    // results
    //
    case actions.FETCH_RESULTS:
      return Object.assign({}, state, {status: "FINISHED"});

    case actions.URS_RESULTS:
      switch (action.status) {
        case 'success':
          return Object.assign({}, state, {
            status: "FINISHED",
            width: action.width,
            height: action.height,
            svg: action.svg,
            notation: action.notation,
            template: action.template,
            source: action.source,
            jobId: action.jobId
          });
        case 'error':
          return Object.assign({}, state, {status: "ERROR"});
        default:
          return newState;
      }

    case actions.GET_SVG:
      switch (action.status) {
        case 'success':
          return Object.assign({}, state, {width: action.width, height: action.height, svg: action.svg});
        case 'error':
          return Object.assign({}, state, {svg: "SVG not available"});
        default:
          return newState;
      }

    case actions.SVG_COLORS:
      return Object.assign({}, state, {svg: action.svg, svgColor: !state.svgColor});

    case actions.SVG_NUMBERS:
      return Object.assign({}, state, {svg: action.svg, svgNumber: !state.svgNumber});

    case actions.UPDATE_SEQUENCE:
      return Object.assign({}, state, {sequence: action.sequence});

    case actions.FASTA:
      switch (action.status) {
        case 'success':
          return Object.assign({}, state, {notation: action.notation});
        case 'error':
          return Object.assign({}, state, {notation: "error"});
        default:
          return newState;
      }

    case actions.TSV:
      switch (action.status) {
        case 'success':
          return Object.assign({}, state, {template: action.template, source: action.source});
        case 'error':
          return Object.assign({}, state, {template: "error", source: "error"});
        default:
          return newState;
      }

    default:
      return state;
  }
};

export default rootReducer;
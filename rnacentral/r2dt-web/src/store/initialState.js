let initialState = {
  jobId: null,
  status: "notSubmitted",  // options: error, RUNNING, FINISHED, NOT_FOUND and FAILURE
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
};

export default initialState;

import React from 'react';
import { connect } from 'react-redux';
import * as actionCreators from 'actions/actions';
import { store } from 'app.jsx';
import { FaSearch } from 'react-icons/fa';
import { FiTrash2 } from 'react-icons/fi';
import ReactGA from 'react-ga4';
import Advanced from 'containers/R2DT/components/SearchForm/components/Advanced/index.jsx'


class SearchForm extends React.Component {
  showExamples(linkColor){
    const examples = this.props.examples;
    return examples.map(example =>
      <li key={example.description} className="mr-2">
        <a className="custom-link" style={{color: linkColor}} onClick={() => this.exampleSequence('>' + example.description + '\n' + example.sequence)}>{example.descriptionNote ? <>{example.descriptionNote} (<small>{example.description}</small>)</> : example.description}</a>
      </li>)
  }

  exampleSequence(sequence) {
    const state = store.getState();
    store.dispatch(actionCreators.onExampleSequence(sequence));
    if (state.advancedSearchCollapsed) {
      store.dispatch(actionCreators.clearTemplateId());
      store.dispatch(actionCreators.firebaseFetchData(sequence, ""));
    }
  }

  searchUrs(urs) {
    // register full page URLs in GA4
    // ref: https://www.optimizesmart.com/how-to-view-full-page-urls-in-ga4/
    ReactGA.initialize('G-HEBH0L4399');
    ReactGA.send({ hitType: "pageview", page: window.location.href });
    store.dispatch(actionCreators.onSubmitUrs(urs));
  }

  onSubmit(event) {
    event.preventDefault();
    const state = store.getState();
    const userInput = state.sequence.split("\n");
    const isDotBracket = /[.()]/;
    let fastaHeader, sequence, dotBracket

    if (/^>/.test(userInput[0])) {
      fastaHeader = userInput[0];
      if (userInput[2] && isDotBracket.test(userInput[2])) {
        sequence = userInput[1].replace(/\s+/g, "");
        dotBracket = userInput[2].replace(/\s+/g, "");
      } else {
        sequence = userInput.slice(1).join("");
      }
    } else {
      fastaHeader = '>description';
      sequence = state.sequence.replace(/\s+/g, "");
    }

    if (/^r2dt/.test(state.sequence)){
      store.dispatch(actionCreators.fetchStatus(state.sequence))
    } else if (sequence.length < 4 || sequence.length > 8000) {
      store.dispatch(actionCreators.invalidSequence());
    } else if (dotBracket){
      if (sequence.length !== dotBracket.length) {
        store.dispatch(actionCreators.invalidDotBracket());
      } else {
        store.dispatch(actionCreators.onSubmit(fastaHeader + '\n' + sequence + '\n' + dotBracket, false, true));
      }
    } else {
      store.dispatch(actionCreators.onSubmit(fastaHeader + '\n' + sequence));
    }
  }

  render() {
    const urs = this.props.search ? this.props.search["urs"] : null;
    const searchButtonColor = this.props.customStyle && this.props.customStyle.searchButtonColor ? this.props.customStyle.searchButtonColor : "";
    const clearButtonColor = this.props.customStyle && this.props.customStyle.clearButtonColor ? this.props.customStyle.clearButtonColor : "#6c757d";
    const fixCss = this.props.customStyle && this.props.customStyle.fixCss && this.props.customStyle.fixCss === "true" ? "1.5rem" : "";
    const fixCssBtn = this.props.customStyle && this.props.customStyle.fixCss && this.props.customStyle.fixCss === "true" ? "38px" : "";
    const hideRnacentral = this.props.customStyle && this.props.customStyle.hideRnacentral && this.props.customStyle.hideRnacentral === "true" ? "none" : "initial";
    const linkColor = this.props.customStyle && this.props.customStyle.linkColor ? this.props.customStyle.linkColor : "#337ab7";
    const firebaseStatus = this.props.firebaseStatus;
    return (
      <div className="rna">
        {
          !urs ? <div>
            <div className="row">
              <div className="col-12">
                <small className="text-muted" style={{display: hideRnacentral}}><img src={'https://rnacentral.org/static/img/logo/rnacentral-logo.png'} alt="RNAcentral logo" style={{width: "1em", verticalAlign: "text-top"}}/> Powered by <a className="custom-link mr-2" style={{color: linkColor}} target='_blank' href='https://rnacentral.org/'>RNAcentral</a></small>
              </div>
            </div>
            <form onSubmit={(e) => this.onSubmit(e)}>
              <div className="row mt-1">
                <div className="col-12 col-sm-9 mb-2">
                  <textarea style={{fontSize: fixCss}} className="form-control" id="sequence" name="sequence" rows="7" value={this.props.sequence} disabled={this.props.status === "RUNNING" ? "disabled" : ""} onChange={(e) => this.props.onSequenceTextareaChange(e)} placeholder={this.props.status === "RUNNING" ? "Please wait..." : "Enter RNA/DNA sequence or job ID (FASTA format with optional description). Include secondary structure in dot-bracket notation, if available"} />
                </div>
                <div className="col-12 col-sm-3">
                  {
                    this.props.status === "RUNNING" ?
                      <button className="btn btn-primary mb-2" style={{background: searchButtonColor, borderColor: searchButtonColor, fontSize: fixCss, height: fixCssBtn}} type="button" disabled>
                        <span className={`spinner-border ${fixCss ? '' : 'spinner-border-sm'}`} role="status" aria-hidden="true"></span>
                        &nbsp;Running...
                      </button> :
                      <button className="btn btn-primary mb-2" style={{background: searchButtonColor, borderColor: searchButtonColor, fontSize: fixCss, height: fixCssBtn}} type="submit" disabled={!this.props.sequence ? "disabled" : ""}>
                        <span className="btn-icon"><FaSearch /></span> Run
                      </button>
                  }
                  <br />
                  <button className="btn btn-secondary mb-2" style={{background: clearButtonColor, borderColor: clearButtonColor, fontSize: fixCss, height: fixCssBtn}} type="submit" onClick={ this.props.onClearSequence } disabled={!this.props.sequence ? "disabled" : ""}>
                    <span className="btn-icon"><FiTrash2 /></span> Clear
                  </button><br />
                  {
                    this.props.status === "RUNNING" ?
                      <a>
                        { this.props.advancedSearchCollapsed ? <span style={{color: linkColor, fontSize: fixCss}}>Show advanced</span> : <span style={{color: linkColor, fontSize: fixCss}}>Hide advanced</span> }
                      </a> :
                      <a className="custom-link" onClick={ this.props.onToggleAdvancedSearch }>
                        { this.props.advancedSearchCollapsed ? <span style={{color: linkColor, fontSize: fixCss}}>Show advanced</span> : <span style={{color: linkColor, fontSize: fixCss}}>Hide advanced</span> }
                      </a>
                  }
                </div>
              </div>
              <div className="row">
                <div className="col-12 col-sm-9">
                  { this.props.advancedSearchCollapsed ? "" : <Advanced customStyle={ this.props.customStyle } /> }
                </div>
              </div>
              <div className="row">
                <div className="col-12 col-sm-9">
                  {this.props.examples ? <div id="examples"><ul className="text-muted">Examples: {this.showExamples(linkColor)}</ul></div> : ""}
                </div>
              </div>
            </form>
          </div> : this.props.status === "notSubmitted" ? this.searchUrs(urs) : ""
        }
        {
          this.props.submissionError && (
            <div className="row">
              <div className="col-12 col-sm-9">
                <div className="alert alert-danger">
                  { this.props.submissionError }
                </div>
              </div>
            </div>
          )
        }
        {
          this.props.status === "invalidSequence" && (
            <div className="row">
              <div className="col-12 col-sm-9">
                <div className="alert alert-warning">
                  Please check your sequence, it cannot be shorter than 4 or longer than 8000 nucleotides
                </div>
              </div>
            </div>
          )
        }
        {
          this.props.status === "invalidDotBracket" && (
            <div className="row">
              <div className="col-12 col-sm-9">
                <div className="alert alert-warning">
                  The secondary structure in dot-bracket notation must be the same length as the fasta sequence
                </div>
              </div>
            </div>
          )
        }
        {
          this.props.status === "NOT_FOUND" && (
            <div className="row">
              <div className="col-12 col-sm-9">
                <div className="alert alert-warning">
                  Job not found. The results might have expired.
                  If you think this is an error, please let us know by raising an issue on <a href="https://github.com/RNAcentral/r2dt-web/issues" target="_blank">GitHub</a>
                </div>
              </div>
            </div>
          )
        }
        {
          (this.props.status === "FAILURE" || this.props.status === "ERROR") && (
            <div className="row">
              <div className="col-12 col-sm-9">
                <div className="alert alert-danger">
                  There was an error. Let us know if the problem persists by raising an issue on <a href="https://github.com/RNAcentral/r2dt-web/issues" target="_blank">GitHub</a>.
                </div>
              </div>
            </div>
          )
        }
        {
          (firebaseStatus === "fetchError" || firebaseStatus === "postError" || firebaseStatus === "patchError") && (
            <div className="row">
              <div className="col-12 col-sm-9">
                <div className="alert alert-warning">
                  <p><strong>There was an error with Firebase</strong></p>
                  <span>Let us know if the problem persists by raising an issue on <a href="https://github.com/RNAcentral/r2dt-web/issues" target="_blank">GitHub</a></span>
                </div>
              </div>
            </div>
          )
        }
      </div>
    )
  }
}

const mapStateToProps = (state) => ({
  jobId: state.jobId,
  status: state.status,
  submissionError: state.submissionError,
  sequence: state.sequence,
  firebaseStatus: state.firebaseStatus,
  advancedSearchCollapsed: state.advancedSearchCollapsed,
});

const mapDispatchToProps = (dispatch) => ({
  onSequenceTextareaChange: (event) => dispatch(actionCreators.onSequenceTextAreaChange(event)),
  onClearSequence: () => dispatch(actionCreators.onClearSequence()),
  onToggleAdvancedSearch: () => dispatch(actionCreators.onToggleAdvancedSearch()),
});


export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SearchForm);

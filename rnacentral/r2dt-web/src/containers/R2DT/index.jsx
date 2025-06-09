import React from 'react';
import * as actionCreators from 'actions/actions';
import {store} from "app.jsx";
import {connect} from "react-redux";

import Results from 'containers/R2DT/components/Results/index.jsx';
import SearchForm from 'containers/R2DT/components/SearchForm/index.jsx';


class SequenceSearch extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    // check if a jobId was passed as a parameter to search for results
    let url = window.location.href;
    url = url.split("?jobid=");
    let jobId = url[url.length - 1]
    if (/^r2dt/.test(jobId)) {
      store.dispatch(actionCreators.fetchStatus(jobId))
    }
  }

  componentDidUpdate() {
    // show the jobId in the URL
    let url = window.location.href;
    let splitUrl = url.split("?jobid=");
    let domain = splitUrl[0]
    if (this.props.jobId && /^r2dt/.test(this.props.jobId)){
      window.history.replaceState("", "", domain + "?jobid=" + this.props.jobId);
    } else {
      window.history.replaceState("", "", domain);
    }
  }

  render() {
    return [
      <SearchForm
          key ={`searchForm`}
          customStyle={this.props.customStyle}
          examples={this.props.examples}
          search={this.props.search}
      />,
      <Results
          key={`results`}
          customStyle={this.props.customStyle}
          search={this.props.search}
      />
    ]
  }
}

function mapStateToProps(state) {
  return {
    jobId: state.jobId,
  };
}

function mapDispatchToProps(dispatch) {
  return {};
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(SequenceSearch);

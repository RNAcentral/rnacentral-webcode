import React from 'react';
import { connect } from 'react-redux';
import * as actionCreators from 'actions/actions';
import routes from 'services/routes.jsx';
import {ALIGN_CENTER, POSITION_LEFT, UncontrolledReactSVGPanZoom, TOOL_NONE} from 'react-svg-pan-zoom';
import { SvgLoader } from 'react-svgmt';
import { saveSvgAsPng } from 'save-svg-as-png';
import { BsToggles } from "react-icons/bs";
import { FaEdit } from "react-icons/fa";
import { MdColorLens } from 'react-icons/md';
import { RiDownload2Fill, RiFileCopy2Line } from "react-icons/ri";

const miniatureProps = { position: TOOL_NONE };
const toolbarProps = { position: POSITION_LEFT, SVGAlignY: ALIGN_CENTER, SVGAlignX: ALIGN_CENTER };

class Results extends React.Component {
  constructor(props) {
    super(props);
    this.viewerRef = React.createRef();
    this.divRef = React.createRef();
    this.downloadMenuRef = React.createRef();
    this.editMenuRef = React.createRef();
    this.doFirstFit = true;
    this.handleClickOutside = this.handleClickOutside.bind(this);
    this.state = { divWidth: window.innerWidth };
  }

  componentDidMount() {
    window.addEventListener("resize", () => this.handleResize());
    window.addEventListener("click", this.handleClickOutside);  // close dropdown on outside click
  }

  componentWillUnmount() {
    window.removeEventListener("resize", () => this.handleResize());
    window.removeEventListener("click", this.handleClickOutside);
  }

  componentDidUpdate() {
    if (this.doFirstFit && this.viewerRef.current) {
      this.viewerRef.current.fitToViewer("center", "center");
      this.doFirstFit = false;
    }
    if (!this.props.jobId && !this.doFirstFit) {
      this.doFirstFit = true;
    }
  }

  // border responsive
  handleResize() {
    const { current } = this.divRef;
    current && this.setState({ divWidth: current.offsetWidth });
  }

  // close dropdowns when clicking outside
  handleClickOutside = (event) => {
    const downloadMenu = this.downloadMenuRef.current;
    const editMenu = this.editMenuRef.current;

    // close the download dropdown if clicked outside
    if (downloadMenu && !downloadMenu.contains(event.target) && event.target.id !== "downloadDropdownButton") {
      downloadMenu.classList.remove("show");
    }

    // close the edit dropdown if clicked outside
    if (editMenu && !editMenu.contains(event.target) && event.target.id !== "editDropdownButton") {
      editMenu.classList.remove("show");
    }
  }

  // toggle the download dropdown menu
  toggleDownloadDropdown = (event) => {
    event.stopPropagation();
    const downloadMenu = this.downloadMenuRef.current;
    const editMenu = this.editMenuRef.current;

    // close the edit dropdown if it's open
    if (editMenu && editMenu.classList.contains("show")) {
      editMenu.classList.remove("show");
    }

    if (downloadMenu) {
      downloadMenu.classList.toggle("show");
    }
  }

  // toggle the edit dropdown menu
  toggleEditDropdown = (event) => {
    event.stopPropagation();
    const editMenu = this.editMenuRef.current;
    const downloadMenu = this.downloadMenuRef.current;

    // close the download dropdown if it's open
    if (downloadMenu && downloadMenu.classList.contains("show")) {
      downloadMenu.classList.remove("show");
    }

    if (editMenu) {
      editMenu.classList.toggle("show");
    }
  }

  downloadFile = async (event, url, filename) => {
    event.preventDefault();

    try {
      const response = await fetch(url, { mode: "cors" });
      if (!response.ok) {
        console.error(`Failed to fetch ${filename}`);
        return;
      }

      const blob = await response.blob();
      const downloadLink = document.createElement("a");
      const objectUrl = URL.createObjectURL(blob);

      downloadLink.href = objectUrl;
      downloadLink.download = filename;

      document.body.appendChild(downloadLink);
      downloadLink.click();

      URL.revokeObjectURL(objectUrl);
      document.body.removeChild(downloadLink);
    } catch (error) {
      console.error(`Error downloading ${filename}:`, error);
    }
  };

  downloadPNG() {
    let div = document.createElement('div');
    div.innerHTML = this.props.svg;
    saveSvgAsPng(div.firstChild, this.props.jobId + ".png", {backgroundColor: 'white', scale: 3});
  }

  downloadSVG() {
    let svgBlob = new Blob([this.props.svg], {type:"image/svg+xml;charset=utf-8"});
    let svgUrl = URL.createObjectURL(svgBlob);
    let downloadLink = document.createElement("a");
    downloadLink.href = svgUrl;
    downloadLink.download = this.props.jobId + ".svg";
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
  }

  downloadJson = (event) => {
    const url = routes.fetchJson(this.props.jobId);
    const filename = `${this.props.jobId}.json`;
    this.downloadFile(event, url, filename);
  }

  downloadSVGAnnotated = (event) => {
    const url = routes.fetchSvgAn(this.props.jobId);
    const filename = `${this.props.jobId}_annotated.svg`;
    this.downloadFile(event, url, filename);
  }

  downloadThumbnail = (event) => {
    const url = routes.fetchThumb(this.props.jobId);
    const filename = `${this.props.jobId}_thumbnail.svg`;
    this.downloadFile(event, url, filename);
  }

  sourceLink(source, linkColor){
    let link = "#";
    let name = "";
    if (source.toLowerCase() === "crw") {
      link = "https://crw2-comparative-rna-web.org/";
      name = "CRW";
    } else if (source.toLowerCase() === "rfam") {
      link = "https://rfam.org/";
      name = "Rfam";
    } else if (source.toLowerCase() === "ribovision") {
      link = "http://apollo.chemistry.gatech.edu/RiboVision/";
      name = "RiboVision";
    } else if (source.toLowerCase() === "gtrnadb") {
      link = "http://gtrnadb.ucsc.edu/";
      name = "GtRNAdb"
    }
    return <a className="custom-link" style={{color: linkColor}} href={link} target="_blank">{name}</a>
  }

  render() {
    const hideTitle = this.props.customStyle && this.props.customStyle.hideTitle && this.props.customStyle.hideTitle === "true" ? "none" : "initial";
    let title = {
      color: this.props.customStyle && this.props.customStyle.titleColor ? this.props.customStyle.titleColor : "#007c82",
      fontSize: this.props.customStyle && this.props.customStyle.titleSize ? this.props.customStyle.titleSize : "28px",
    };
    const fixCss = this.props.customStyle && this.props.customStyle.fixCss && this.props.customStyle.fixCss === "true" ? "1.5rem" : "";
    const linkColor = this.props.customStyle && this.props.customStyle.linkColor ? this.props.customStyle.linkColor : "#337ab7";
    const legendLocation = this.props.customStyle && this.props.customStyle.legendLocation ? this.props.customStyle.legendLocation : "";
    const width = document.getElementsByTagName('r2dt-web')[0] && document.getElementsByTagName('r2dt-web')[0].offsetWidth ? document.getElementsByTagName('r2dt-web')[0].offsetWidth - 40 : 1100;  // using - 40 to display the right side border
    const height = parseFloat(this.props.height) > 600 ? parseFloat(this.props.height) : 600;
    const hasDotBracket = /[.()]/.test(this.props.sequence);

    const renderLegend = () => (
      <div className="mt-3" style={{ fontSize: fixCss }}>
        <strong>Colour legend</strong>
        <ul className="list-unstyled">
          <li className="mt-1"><span className="traveler-black traveler-key"></span> Same as the template</li>
          <li className="mt-1"><span className="traveler-green traveler-key"></span> Modified compared to the template</li>
          <li className="mt-1"><span className="traveler-magenta traveler-key"></span> Inserted nucleotides</li>
          <li className="mt-1"><span className="traveler-blue traveler-key"></span> Repositioned compared to the template</li>
          <li className="mt-2"><strong>Tip:</strong> Hover over nucleotides for more details</li>
        </ul>
      </div>
    );

    const renderSVGComponent = () => (
      <UncontrolledReactSVGPanZoom
        width={legendLocation ? width * 0.7 : width}  // 70% of the total width if legend is on the right or left
        height={height}
        ref={this.viewerRef}
        toolbarProps={toolbarProps}
        miniatureProps={miniatureProps}
        detectAutoPan={false}
        background={"#fff"}
        scaleFactorMin={0.5}
        scaleFactorMax={5}
      >
        <svg width={parseFloat(this.props.width)} height={parseFloat(this.props.height)}>
          <SvgLoader svgXML={this.props.svg} />
        </svg>
      </UncontrolledReactSVGPanZoom>
    );

    return (
      <div className="rna" ref={this.divRef}>
        {
          this.props.jobId && this.props.status === "error" && (
            <div className="row" key={`error-div`}>
              <div className="col-12 col-sm-9">
                <div className="alert alert-danger">
                  There was an error. Let us know if the problem persists by raising an issue on <a href="https://github.com/RNAcentral/r2dt-web/issues" target="_blank">GitHub</a>.
                </div>
              </div>
            </div>
          )
        }
        {
          this.props.jobId && this.props.svg === "SVG not available" && this.props.status === "FINISHED" && (
            <div className="row" key={`error-div`}>
              <div className="col-12 col-sm-9">
                <div className="alert alert-warning">
                  { this.props.advancedSearchCollapsed ? "The sequence did not match any of the templates." : "The sequence did not match the selected template." } If you think it's an error, please <a href="https://github.com/RNAcentral/r2dt-web/issues" target="_blank">get in touch</a>.
                </div>
              </div>
            </div>
          )
        }
        {
          this.props.jobId && this.props.svg !== "SVG not available" && this.props.status === "FINISHED" && [
            <div className="row" key={`results-div`}>
              <div className="col-12">
                <div style={{display: hideTitle}}>
                  <span style={title}>Secondary structure </span>
                </div>
                {
                  (this.props.template === "error" || this.props.source === "error") ? <p className="text-muted mt-3" style={{fontSize: fixCss}}>
                    Generated by <a className="custom-link" style={{color: linkColor}} href="https://github.com/RNAcentral/r2dt" target="_blank">R2DT</a>. <a className="custom-link" style={{color: linkColor}} href="https://rnacentral.org/help/secondary-structure" target="_blank">Learn more →</a>
                  </p> : this.props.template === "R2R" ? <p className="text-muted mt-3" style={{fontSize: fixCss}}>
                    Generated by <a className="custom-link" style={{color: linkColor}} href="https://github.com/RNAcentral/r2dt" target="_blank">R2DT</a> using the <i>{this.props.template}</i> software. <a className="custom-link" style={{color: linkColor}} href="https://rnacentral.org/help/secondary-structure" target="_blank">Learn more →</a>
                  </p> : <p className="text-muted mt-3" style={{fontSize: fixCss}}>
                    Generated by <a className="custom-link" style={{color: linkColor}} href="https://github.com/RNAcentral/r2dt" target="_blank">R2DT</a> using the <i>{this.props.template}</i> template provided by {this.sourceLink(this.props.source, linkColor)}. <a className="custom-link" style={{color: linkColor}} href="https://rnacentral.org/help/secondary-structure" target="_blank">Learn more →</a>
                  </p>
                }
                <div className="btn-group mb-3" role="group" aria-label="button options" style={{display: "flow"}}>
                  <button className="btn btn-outline-secondary" style={{fontSize: fixCss}} onClick={() => this.props.toggleColors(this.props.svg)}><span className="btn-icon"><MdColorLens size="1.2em"/></span> Toggle colours</button>
                  <button className="btn btn-outline-secondary" style={{fontSize: fixCss}} onClick={() => this.props.toggleNumbers(this.props.svg)}><span className="btn-icon"><BsToggles size="1.2em"/></span> Toggle numbers</button>
                  {this.props.notation ? <button className="btn btn-outline-secondary" style={{fontSize: fixCss}} onClick={() => navigator.clipboard.writeText(this.props.notation)}><span className="btn-icon"><RiFileCopy2Line size="1.2em"/></span> Copy dot-bracket notation</button> : ""}
                  {
                    this.props.search ? "" : <>
                      <div className="btn-group" role="group">
                        <button className="btn btn-outline-secondary dropdown-toggle" style={{fontSize: fixCss}} type="button" id="editDropdownButton" onClick={this.toggleEditDropdown}><span className="btn-icon"><FaEdit size="1.2em"/></span> Edit image</button>
                        <ul className="dropdown-menu" style={{fontSize: fixCss}} id="editDropdownMenu" ref={this.editMenuRef}>
                          <li><a className="dropdown-item" href={routes.rnaCanvas(this.props.jobId)} target="_blank">Edit in RNAcanvas</a></li>
                          <li><a className="dropdown-item" href={routes.xRNA(this.props.jobId)} target="_blank">Edit in XRNA-React</a></li>
                          <li><a className="dropdown-item beta" href={routes.canvasCode(this.props.jobId)} target="_blank">Edit in RNAcanvas Code </a></li>
                        </ul>
                      </div>
                    </>
                  }
                  <div className="btn-group" role="group">
                    <button className="btn btn-outline-secondary dropdown-toggle" style={{fontSize: fixCss}} type="button" id="dropdownMenuButton" onClick={this.toggleDownloadDropdown}><span className="btn-icon"><RiDownload2Fill size="1.2em"/></span> Download</button>
                    <ul className="dropdown-menu" id="dropdownMenu" ref={this.downloadMenuRef}>
                      {
                        this.props.search ? "" : <li>
                          <a className="btn dropdown-item" style={{fontSize: fixCss}}  href={routes.fetchJson(this.props.jobId)} onClick={this.downloadJson}>JSON</a>
                        </li>
                      }
                      <li><button className="dropdown-item" style={{fontSize: fixCss}} onClick={() => this.downloadPNG()}>PNG</button></li>
                      <li><button className="dropdown-item" style={{fontSize: fixCss}} onClick={() => this.downloadSVG()}>SVG</button></li>
                      {
                        hasDotBracket || this.props.search ? "" : <li>
                          <a className="btn dropdown-item" style={{fontSize: fixCss}} href={routes.fetchSvgAn(this.props.jobId)} onClick={this.downloadSVGAnnotated}>SVG annotated</a>
                        </li>
                      }
                      {
                        this.props.search ? "" : <li>
                          <a className="btn dropdown-item" style={{fontSize: fixCss}} href={routes.fetchThumb(this.props.jobId)} onClick={this.downloadThumbnail}>Thumbnail</a>
                        </li>
                      }
                    </ul>
                  </div>
                </div>
                {
                  legendLocation === "right" || legendLocation === "left" ? (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      {
                        legendLocation === "left" && (
                          <div style={{ flex: '1 1 30%', marginRight: '1rem' }}>
                            { renderLegend() }
                          </div>
                        )
                      }
                      <div style={{ flex: '1 1 70%' }} className="border border-secondary">
                        { renderSVGComponent() }
                      </div>
                      {
                        legendLocation === "right" && (
                          <div style={{ flex: '1 1 30%', marginLeft: '1rem' }}>
                            { renderLegend() }
                          </div>
                        )
                      }
                    </div>
                  ) : (
                    <div className="border border-secondary">
                      { renderSVGComponent() }
                    </div>
                  )
                }
                { legendLocation !== "right" && legendLocation !== "left" && renderLegend() }
              </div>
            </div>
          ]
        }
        {
          this.props.jobId && this.props.svg !== "SVG not available" && this.props.status === "FINISHED" && this.props.notation && [
            <div className="row" key={`notation-div`}>
              <div className={`col-12 ${legendLocation ? 'mt-3' : ''}`}>
                <span><strong>Dot-bracket notation</strong></span>
                {
                  this.props.notation === "error" ? <div className="alert alert-danger">
                    There was an error loading the dot-bracket notation. Let us know if the problem persists by raising an issue on <a href="https://github.com/RNAcentral/r2dt-web/issues" target="_blank">GitHub</a>.
                  </div> : <pre className="mt-1 notation">
                    <span className="notation-font">{this.props.notation}</span>
                  </pre>
                }
              </div>
            </div>
          ]
        }
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    jobId: state.jobId,
    status: state.status,
    submissionError: state.submissionError,
    sequence: state.sequence,
    width: state.width,
    height: state.height,
    svg: state.svg,
    notation: state.notation,
    template: state.template,
    source: state.source,
    advancedSearchCollapsed: state.advancedSearchCollapsed,
  };
}

function mapDispatchToProps(dispatch) {
  return {
    toggleColors: (svg) => dispatch(actionCreators.onToggleColors(svg)),
    toggleNumbers: (svg) => dispatch(actionCreators.onToggleNumbers(svg))
  }
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Results);

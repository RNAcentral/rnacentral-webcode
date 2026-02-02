(function() {
  const { useState, useEffect } = React;
  
  const TrainingPanel = () => {
    const [liveData, setLiveData] = useState(null);
    const [onDemandData, setOnDemandData] = useState(null);

    useEffect(() => {
      const getData = async () => {
        fetch(
          "https://www.ebi.ac.uk/ebisearch/ws/rest/ebiweb_training_events?format=json&query=domain_source:ebiweb_training_events%20AND%20timeframe:upcoming&start=0&size=2&fieldurl=true&fields=title,description,start_date,end_date,date_time_clean,resource_training_page,type,training_type,url,venue,materials,status,timeframe,resource_training_page,course_image&facetcount=50&sort=start_date&facets=resource_training_page:RNAcentral"
        )
          .then((Response) => Response.json())
          .then((findresponse) => {
            setLiveData(findresponse);
          })
          .catch((error) => {
            console.error("Error fetching live training data:", error);
          });

        fetch(
          "https://www.ebi.ac.uk/ebisearch/ws/rest/ebiweb_training_online?format=json&query=domain_source:ebiweb_training_online&start=0&size=2&fields=title,subtitle,description,type,url&sort=title&facets=resource_training_page:RNAcentral"
        )
          .then((Response) => Response.json())
          .then((findresponse) => {
            setOnDemandData(findresponse);
          })
          .catch((error) => {
            console.error("Error fetching on-demand training data:", error);
          });
      };
      getData();
    }, []);

    useEffect(() => {
      // Initialize vfTabs after component renders
      setTimeout(() => {
        if (window.vfTabs) {
          window.vfTabs();
        }
      }, 100);
    }, [liveData, onDemandData]);

    const stripHtml = (html) => {
      const div = document.createElement('div');
      div.innerHTML = html.replace(/&nbsp;/g, ' ');
      return div.textContent || div.innerText || '';
    };

    const formatDesc = (content) => {
      if (content) {
        let safeContent = stripHtml(content);
        let slicedContent =
          safeContent.length > 200
            ? safeContent.slice(0, 200).split(" ").slice(0, -1).join(" ") + "..."
            : safeContent;
        return slicedContent;
      }
    };

    return React.createElement(
      React.Fragment,
      null,
      React.createElement("h2", {
        className: "text-center",
        style: { marginTop: '10px', marginBottom: '2px' }
      }, "Training"),
      React.createElement("div", { className: "row" },
        React.createElement("p", {
          className: "text-center col-md-8 col-md-offset-2"
        }, "Learn how to use RNAcentral's features")
      ),
      React.createElement("div", { style: { backgroundColor: 'white', padding: '15px', marginLeft: '-10px', marginRight: '-10px', marginBottom: '-10px', borderTop: '1px solid #e3e3e3' } },
        React.createElement("div", { className: "vf-tabs" },
          React.createElement("ul", { className: "vf-tabs__list", "data-vf-js-tabs": true },
            React.createElement("li", { className: "vf-tabs__item" },
              React.createElement("a", { className: "vf-tabs__link", href: "#vf-tabs__section--2" },
                "On-demand training"
              )
            ),
            React.createElement("li", { className: "vf-tabs__item" },
              React.createElement("a", { className: "vf-tabs__link", href: "#vf-tabs__section--1" },
                "Live training"
              )
            )
          )
        ),
        React.createElement("div", { className: "vf-tabs-content", "data-vf-js-tabs-content": true },
          React.createElement("section", { className: "vf-tabs__section", id: "vf-tabs__section--2" },
            React.createElement("div", { className: "vf-grid vf-grid__col-2" },
              onDemandData && onDemandData.entries && onDemandData.entries.length > 0
                ? onDemandData.entries.map((item, index) =>
                    React.createElement("div", {
                      key: index,
                      className: "vf-summary vf-summary--event"
                    },
                      React.createElement("p", { className: "vf-summary__date" }, item.fields.type),
                      React.createElement("h3", { className: "vf-summary__title" },
                        React.createElement("a", {
                          href: item.fields.url ? item.fields.url[0] : '#',
                          target: "_blank",
                          rel: "noopener noreferrer",
                          className: "vf-summary__link"
                        },
                          item.fields.title,
                          item.fields.subtitle && item.fields.subtitle[0] && item.fields.subtitle[0].length > 0
                            ? ": " + item.fields.subtitle[0]
                            : ""
                        )
                      ),
                      React.createElement("div", null,
                        React.createElement("div", { className: "vf-summary__text" },
                          formatDesc(item.fields.description ? item.fields.description[0] : '')
                        )
                      )
                    )
                  )
                : React.createElement("p", { className: "text-center" }, "No on-demand training materials available.")
            )
          ),
          React.createElement("section", { className: "vf-tabs__section", id: "vf-tabs__section--1" },
            React.createElement("div", { className: "vf-grid vf-grid__col-2" },
              liveData && liveData.entries && liveData.entries.length > 0
                ? liveData.entries.map((item, index) =>
                    React.createElement("div", {
                      key: index,
                      className: "vf-summary vf-summary--event"
                    },
                      React.createElement("p", { className: "vf-summary__date" }, item.fields.type),
                      React.createElement("h3", { className: "vf-summary__title" },
                        React.createElement("a", {
                          href: item.fields.url ? item.fields.url[0] : '#',
                          target: "_blank",
                          rel: "noopener noreferrer",
                          className: "vf-summary__link"
                        }, item.fields.title)
                      ),
                      React.createElement("div", null,
                        React.createElement("div", { className: "vf-summary__text" },
                          formatDesc(item.fields.description ? item.fields.description[0] : '')
                        ),
                        React.createElement("div", { className: "vf-summary__location" },
                          React.createElement("div", { className: "vf-u-margin__top--400" }),
                          React.createElement("span", null, item.fields.status),
                          " | ",
                          React.createElement("span", null,
                            React.createElement("i", { className: "icon icon-common icon-calendar-alt" }),
                            " ",
                            item.fields.date_time_clean
                          ),
                          React.createElement("span", null,
                            " | ",
                            React.createElement("i", { className: "icon icon-common icon-location" }),
                            " ",
                            item.fields.venue === "null" || !item.fields.venue ? "Online" : item.fields.venue
                          )
                        )
                      )
                    )
                  )
                : React.createElement("p", { className: "text-center" }, "No upcoming live training events available.")
            )
          )
        )
      )
    );
  };

  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      const rootElement = document.getElementById("training-widget-root");
      if (rootElement && window.ReactDOM) {
        ReactDOM.render(React.createElement(TrainingPanel), rootElement);
      }
    });
  } else {
    const rootElement = document.getElementById("training-widget-root");
    if (rootElement && window.ReactDOM) {
      ReactDOM.render(React.createElement(TrainingPanel), rootElement);
    }
  }
})();
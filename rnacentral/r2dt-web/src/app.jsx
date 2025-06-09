import React from 'react';
import ReactDOM from 'react-dom';
import {Provider} from 'react-redux';

import R2DTWebContainer from 'containers/R2DT/index.jsx';
import configureStore from 'store/configureStore.js';

import bootstrap from 'styles/bootstrap.scss';
import R2DTWebStyles from 'styles/index.scss';

// Prepare data
export const store = configureStore();


class R2DTWeb extends HTMLElement {
  constructor() {
    super();

    // prepare DOM and shadow DOM
    // workaround found at https://github.com/facebook/react/issues/9242 to avoid re-renders
    const shadowRoot = this.attachShadow({mode: 'open'});
    const mountPoint = document.createElement('html');
    shadowRoot.appendChild(mountPoint);
    Object.defineProperty(mountPoint, "ownerDocument", { value: shadowRoot });
    shadowRoot.createElement = (...args) => document.createElement(...args);
    shadowRoot.createElementNS = (...args) => document.createElementNS(...args);
    shadowRoot.createTextNode = (...args) => document.createTextNode(...args);

    // parse arguments
    const customStyle = JSON.parse(this.attributes.customStyle ? this.attributes.customStyle.nodeValue : null);
    const examples = JSON.parse(this.attributes.examples ? this.attributes.examples.nodeValue : null);
    const search = JSON.parse(this.attributes.search ? this.attributes.search.nodeValue : null);

    // render React
    ReactDOM.render([
      <style key={bootstrap} dangerouslySetInnerHTML={{__html: bootstrap}}/>,
      <style key={R2DTWebStyles} dangerouslySetInnerHTML={{__html: R2DTWebStyles}}/>,
      <body key='body'>
        <Provider key='provider' store={store}>
          <R2DTWebContainer
              customStyle={customStyle}
              examples={examples}
              search={search}
          />
        </Provider>
      </body>
      ],
      mountPoint
    );
  }

  disconnectedCallback() {
    let state = store.getState();
    if (state.statusTimeout) {
      clearTimeout(state.statusTimeout);
    }
  }
}

customElements.define('r2dt-web', R2DTWeb);

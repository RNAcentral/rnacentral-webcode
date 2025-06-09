# R2DT-Web

This is an embeddable component that you can include into your website to visualise RNA secondary structures.

## How to use

To use the latest stable version without worrying about updates, use the component's javascript package available at 
GitHub:

`<script type="text/javascript" src="https://rnacentral.github.io/r2dt-web/dist/r2dt-web.js"></script>`

If you prefer to install this package and perform the updates manually, see the [Installation](#Installation) section. 

This tool can be used in two ways:

**1- Allow the user to enter a sequence and search for the secondary structure**. 

For that, you just need to insert this html tag somewhere in your html:

```
<r2dt-web />
```

To show some examples, use:

```
<r2dt-web 
    examples='[
        {"description": "RNA5S1-8", "sequence": "GUCUACGGCCAUACCACCCUGAACGCGCCCGAUCUCGUCUGAUCUCGGAAGCUAAGCAGGGUCGGGCCUGGUUAGUACUUGGAUGGGAGACCGCCUGGGAAUACCGGGUGCUGUAGGCUUU"},
        {"description": "TRT-TGT2-1", "sequence": "GGCTCCATAGCTCAGTGGTTAGAGCACTGGTCTTGTAAACCAGGGGTCGCGAGTTCGATCCTCGCTGGGGCCT"}
    ]'
/>
```

You can also customise some elements of this embeddable component. See what you can change [here](#layout).
The example below changes the color of the buttons:

```
<r2dt-web
    customStyle='{
      "searchButtonColor": "#007c82",
      "clearButtonColor": "#6c757d"
    }'
/>
```

For a minimal example, see [index.html](./index.html).

**2- Given a specific URS, show the secondary structure**

To show the secondary structure for a specific sequence, you need to pass the **U**nique **R**NA **S**equence 
identifier (URS), for example: 

```
<r2dt-web search='{"urs": "URS000044DFF6"}' />
```

Click [here](https://rnacentral.org/help#how-to-find-rnacentral-id) to see how you can find an RNAcentral identifier 
for an RNA sequence.

Obviously, you can automate this process by passing the URS as a variable, for example:

```
<r2dt-web search='{"urs": "{{ variable }}"}' />
```

For a minimal example, see [urs-example.html](./urs-example.html).

## Installation

Download this package directly from GitHub.

`git clone https://github.com/RNAcentral/r2dt-web.git`

Now you can add the component's javascript bundle (it contains all the styles and fonts) to your web page either 
directly or through an import with Webpack:

`<script type="text/javascript" src="/r2dt-web/dist/r2dt-web.js"></script>`

You will need to run the `git pull` command whenever there are updates.

## Attributes/parameters

This component accepts a number of attributes. You pass them as html attributes and their values are strings 
(this is a requirement of Web Components):

#### layout

Parameters that you can use to customise some elements of this embeddable component

| parameter         | description                                                                              |
|-------------------|------------------------------------------------------------------------------------------|
| fixCss            | fix the CSS. Use *"fixCss": "true"* if the button sizes are different                    |
| linkColor         | change the color of the links                                                            |
| searchButtonColor | change the color of the `Search` button                                                  |
| clearButtonColor  | change the color of the `Clear` button                                                   |
| titleColor        | change the color of the `Secondary structure` text                                       |
| titleSize         | change the size of the `Secondary structure` text                                        |
| hideTitle         | Use *"hideTitle": "true"* to hide the title                                              |
| legendLocation    | Use *"legendLocation": "right"* to show the legend side by side with secondary structure |

## Developer details

When integrating the r2dt-web component into your webpage, please be aware that its styles might conflict 
with the existing styles of your page. To prevent such CSS conflicts and ensure proper isolation of the 
component's styles, you can add the following lines to your webpage's CSS file:

```
r2dt-web {
    all: initial;
}
```

This will reset all inherited styles for the r2dt-web component, minimizing the chances of unintended 
style interference.

### Local development

1. `npm install`

2. `npm run serve` to start a server on http://localhost:8080/

3. `npm run clean` to clean the dist folder of old assets

4. `npm run build` to generate a new distribution.

### Notes

This embed is implemented as a Web Component, wrapping a piece of code in React/Redux. 
The CSS styles and fonts are bundled into the javascript inline via Webpack build system, see webpack.config.js file. 
Upon load of r2dt-web.js, the component registers itself in the custom elements registry.

Web Components accept input parameters as strings. That means that we have to parse parameters in Web Component 
initialization code and pass the resulting objects as props to React. Here are some examples of passing the 
parameters to the Web Component or from Web Component to React:

* https://hackernoon.com/how-to-turn-react-component-into-native-web-component-84834315cb24
* https://stackoverflow.com/questions/50404970/web-components-pass-data-to-and-from/50416836

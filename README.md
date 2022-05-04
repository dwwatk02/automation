# mdjs component example

> This is an example for a component - also see [mdjs basics](https://webcomponents.dev/edit/tS7JYfymt6yeshma8Gn1)

This example loads the web component and direclty shows it

```js script
import "./my-card.js";
import { html } from "lit-html";
```

<my-card header="from attribute"></my-card>

## Show it with properties

Rendering via a template function with lit-html allows to use for example properties.

```js story
const headlineText = "Headline Text";
export const myCard = () => html`
  <my-card .header=${headlineText}>Main content text</my-card>
`;
```

## Show it within a frame

Show it within a frame and

```js preview-story
export const cardWithFrame = () => html`
  <my-card .header=${"My Headline Nr: " + 2 * 2}>Main content text</my-card>
`;
```

## Have a component with a fixed headlineText

You can provide a header as a property or attribute.

```js preview-story
export const myFixedCard = () => html`
  <my-card header="Fixed Header">Main content text</my-card>
`;
```

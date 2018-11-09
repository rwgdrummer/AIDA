/**
 *
 * Panel
 *
 */

import React from 'react';
import PropTypes from 'prop-types';
// import styled from 'styled-components';
import { Input, Button, Segment, Label } from 'semantic-ui-react';
import { Element } from 'react-scroll';
import { Container, Row, Col } from 'react-grid-system';

/* eslint-disable react/prefer-stateless-function */
const hide = { display: 'none' };
const inputStyle = {
  width: '25%',
  padding: '5px',
};
const inputStyle2 = {
  width: '49.2%',
  padding: '5px',
};

const inline = { padding: '2px' };
class Panel extends React.Component {
  constructor(props) {
    super(props);
    this.canvasImage = React.createRef();
    this.base = React.createRef();
    this.state = {
      x: 0,
      y: 0,
      height: 0,
      width: 0,
      url:
        'http://2.bp.blogspot.com/-CmBgofK7QzU/TVj3u3N1h2I/AAAAAAAADN8/OszBhGvvXRU/s640/tumblr_lg7h9gpbtP1qap9qio1_500.jpeg',
      canonical:
      {
        entity: props.items.entity,
        MD5: props.items.MD5,
        REF: props.items.REF,
        SegmentId: props.items.SegmentId,
        Frame: props.items.Frame,
        canonicalMentions: props.items.canonicalMentions,
      }
    };
    this.handleChange = this.handleChange.bind(this);
    this.reloadBoundingBox = this.reloadBoundingBox.bind(this);
    this.createCanonicalMention = this.createCanonicalMention.bind(this);
  }

  handleChange(event) {
    console.log(event.target.name);
    console.log(event.target.value);
    this.setState({ [event.target.name]: parseInt(event.target.value, 10) });
  }

  componentDidMount() {
    const canvas = this.canvasImage.current;
    const ctx = canvas.getContext('2d');
    const img = this.base.current;
    img.onload = () => {
      ctx.drawImage(img, 0, 0);
      ctx.moveTo(this.state.x, this.state.y);
      ctx.lineTo(this.state.x + this.state.width, this.state.y);
      ctx.stroke();
      ctx.lineTo(this.state.x + this.state.width, this.state.y + this.state.height);
      ctx.stroke();
      ctx.lineTo(this.state.x, this.state.height + this.state.y);
      ctx.stroke();
      ctx.lineTo(this.state.x, this.state.y);
      ctx.stroke();
      ctx.strokeStyle = '#FF0000';
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.restore();
    };
  }
  reloadBoundingBox() {
    console.log(this.state);
    const canvas = this.canvasImage.current;
    const ctx = canvas.getContext('2d');
    const img = this.base.current;
    img.src = this.state.url;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);
    ctx.moveTo(this.state.x, this.state.y);
    ctx.beginPath();
    ctx.lineTo(this.state.x + this.state.width, this.state.y);
    ctx.lineTo(this.state.x + this.state.width, this.state.y + this.state.height);
    ctx.lineTo(this.state.x, this.state.height + this.state.y);
    ctx.lineTo(this.state.x, this.state.y);
    ctx.stroke();
  }

  createCanonicalMention() {
    console.log("State: ");
    console.log(this.state);
    const canonical = {
      boundingBox: `${this.state.x},${this.state.y},${this.state.height},${this.state.width}`
    }
    console.log(canonical);

  }

  render() {
    return (
      <div>
        <Container>
          <Row>
            <Col sm={8}>
              <Element
                name="entities"
                className="element"
                id="containerElement"
                style={{
                  position: 'relative',
                  height: '75vh',
                  overflow: 'scroll',
                }}
              >
                <canvas ref={this.canvasImage} width="1000" height="500" onClick={this.tagPerson} />
                <img
                  ref={this.base}
                  src="http://2.bp.blogspot.com/-CmBgofK7QzU/TVj3u3N1h2I/AAAAAAAADN8/OszBhGvvXRU/s640/tumblr_lg7h9gpbtP1qap9qio1_500.jpeg"
                  style={hide}
                  alt="Media goes here"
                />
              </Element>
              <Segment inverted color="blue">
                <Input style={inputStyle} type="number" name="x" placeholder="X" onChange={this.handleChange} />
                <Input style={inputStyle} type="number" name="y" placeholder="Y" onChange={this.handleChange} />
                <Input style={inputStyle} type="number" name="height" placeholder="Height" onChange={this.handleChange} />
                <Input style={inputStyle} type="number" name="width" placeholder="Width" onChange={this.handleChange} />
                <Button style={inputStyle2} onClick={this.reloadBoundingBox}>Box It!</Button>
                <Button style={inputStyle2} onClick={this.createCanonicalMention}>Add It!</Button>
              </Segment>
            </Col>
            <Col sm={4}>
              <Row style={inline}>
                <Label color="black">Entity: {this.props.items.entity}</Label>
              </Row>
              <Row style={inline}>
                <Label color="black">MD5: {this.props.items.MD5}</Label>
              </Row>
              <Row style={inline}>
                <Label color="black">REF: {this.props.items.REF}</Label>
              </Row>
              <Row style={inline}>
                <Label color="black">Segment ID: {this.props.items.SegmentId}</Label>
              </Row>
              <Row style={inline}>
                <Label color="black">Frame No: {this.props.items.Frame}</Label>
              </Row>
              <Row style={inline}>
                <Label color="green">
                  Canonical Mentions:
              <Element
                    name="entities"
                    className="element"
                    id="containerElement"
                    style={{
                      position: 'relative',
                      height: '15vh',
                      overflow: 'scroll',
                    }}
                  >
                    <ul>
                      {this.props.items.canonicalMentions.map(m => (
                        <li>{m} <a href="#">Replace</a>, <a href="#">Remove</a></li>
                      ))}
                    </ul>
                  </Element>
                </Label>
              </Row>
              <Row style={inline}>
                <Button>Prev</Button>
                <Button>Next</Button>
              </Row>
            </Col>
          </Row>
        </Container>

      </div>
    );
  }
}

Panel.propTypes = {
  items: PropTypes.object,
};

export default Panel;

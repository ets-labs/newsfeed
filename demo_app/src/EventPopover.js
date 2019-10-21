import React from "react";
import { Button, Form, Icon, Input, Popover, Select } from "antd";

export class SubmitEventPopover extends React.Component {
  state = {
    inputData: "",
    visible: false
  };

  hide = () => {
    this.setState({
      visible: false
    });
  };

  handleVisibleChange = visible => {
    this.setState({ visible });
  };

  handleInputChange = event => {
    const target = event.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;
    this.setState({
      [name]: value
    });
  };

  handleInputDataFormSubmit = event => {
    this.props.handleSendEvent(event, this.state.inputData);
    this.hide();
    this.setState(() => {
      return {
        inputData: ""
      };
    });
  };

  render() {
    const content = (
      <Form
        layout="inline"
        onSubmit={event => this.handleInputDataFormSubmit(event)}
      >
        <Form.Item>
          <Input
            placeholder="New event"
            name="inputData"
            onChange={this.handleInputChange}
            value={this.state.inputData}
          />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Send event
          </Button>
        </Form.Item>
      </Form>
    );
    return (
      <Popover
        content={content}
        title="New event"
        trigger="click"
        visible={this.state.visible}
        onVisibleChange={this.handleVisibleChange}
      >
        <Icon type="edit" key="edit" />
      </Popover>
    );
  }
}

export class SubscribeEventPopover extends React.Component {
  state = {
    inputData: "",
    visible: false
  };

  hide = () => {
    this.setState({
      visible: false
    });
  };

  handleVisibleChange = visible => {
    this.setState({ visible });
  };

  handleInputChange = value => {
    this.setState({
      inputData: value
    });
  };

  handleInputDataFormSubmit = event => {
    this.props.handleSubscribe(event, this.state.inputData);
    this.hide();
    this.setState(() => {
      return {
        inputData: ""
      };
    });
  };

  render() {
    const content = (
      <Form
        layout="inline"
        onSubmit={event => this.handleInputDataFormSubmit(event)}
      >
        <Form.Item label="Select">
          <Select
            style={{ width: 200 }}
            placeholder="Select a newsfeed"
            value={this.state.inputData}
            onChange={this.handleInputChange}
          >
            {Object.entries(this.props.newsFeeds).map(([key, value]) => {
              return (
                <Select.Option key={key} value={key}>
                  {value.name}
                </Select.Option>
              );
            })}
          </Select>
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Subscribe
          </Button>
        </Form.Item>
      </Form>
    );
    return (
      <Popover
        content={content}
        trigger="click"
        visible={this.state.visible}
        onVisibleChange={this.handleVisibleChange}
      >
        <Icon type="ellipsis" key="ellipsis" />
      </Popover>
    );
  }
}

export class OptionsEventPopover extends React.Component {
  state = {
    inputData: "",
    visible: false
  };

  hide = () => {
    this.setState({
      visible: false
    });
  };

  handleVisibleChange = visible => {
    this.setState({ visible });
  };

  handleInputChange = value => {
    this.setState({
      inputData: value
    });
  };

  handleInputDataFormSubmit = event => {
    this.props.handleUnsubscribe(event, this.state.inputData);
    this.hide();
    this.setState(() => {
      return {
        inputData: ""
      };
    });
  };

  render() {
    const content = (
      <Form
        layout="inline"
        onSubmit={event => this.handleInputDataFormSubmit(event)}
      >
        <Form.Item label="Select">
          <Select
            style={{ width: 200 }}
            placeholder="Select a newsfeed"
            value={this.state.inputData}
            onChange={this.handleInputChange}
          >
            {this.props.subscriptions.map((item) => {
              if (this.props.newsFeeds[item.to_newsfeed_id]) {
                return (
                  <Select.Option key={item.id} value={item.id}>
                    {this.props.newsFeeds[item.to_newsfeed_id].name}
                  </Select.Option>
                );
              }
            })}
          </Select>
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            Unsubscribe
          </Button>
        </Form.Item>
      </Form>
    );
    return (
      <Popover
        content={content}
        trigger="click"
        visible={this.state.visible}
        onVisibleChange={this.handleVisibleChange}
        onClick={this.props.getSubscriptions}
      >
        <Icon type="setting" key="setting" />
      </Popover>
    );
  }
}
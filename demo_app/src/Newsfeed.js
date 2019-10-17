import React from "react";
import { Card, Icon } from "antd";
import axios from 'axios';
import {
  SubmitEventPopover,
  SubscribeEventPopover,
  OptionsEventPopover
} from "./EventPopover";

export class NewsFeed extends React.Component {
  state = {
    events: [],
    subscriptions: []
  };

  componentDidMount() {
    fetch(`http://127.0.0.1:8000/api/newsfeed/${this.props.index}/events/`)
      .then(response => response.json())
      .then(dataJson => {
        this.setState(() => {
          return {
            events: dataJson.results
          };
        });
      });
    fetch(
      `http://127.0.0.1:8000/api/newsfeed/${this.props.index}/subscriptions/`
    )
      .then(response => response.json())
      .then(dataJson => {
        this.setState(() => {
          return {
            subscriptions: dataJson.results
          };
        });
      });
  }

  getEvents = () => {
    const url = `http://127.0.0.1:8000/api/newsfeed/${this.props.index}/events/`;
    fetch(url)
      .then(response => response.json())
      .then(dataJson => {
        this.setState(() => {
          return {
            events: dataJson.results
          };
        });
      })
      .catch(error => console.error("Bad request:", error));
  };

  getSubscriptions = () => {
    const url = `http://127.0.0.1:8000/api/newsfeed/${this.props.index}/subscriptions/`;
    fetch(url)
      .then(response => response.json())
      .then(dataJson => {
        this.setState(() => {
          return {
            subscriptions: dataJson.results
          };
        });
      })
      .catch(error => console.error("Bad request:", error));
  };

  handleSendEvent = (event, eventData) => {
    event.preventDefault();
    if (!eventData) {
      return false;
    }
    const url = `http://127.0.0.1:8000/api/newsfeed/${this.props.index}/events/`;
    const data = { data: { field_1: eventData } };

    fetch(url, {
      method: "POST",
      mode: "no-cors",
      body: JSON.stringify(data),
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      }
    }).catch(error => console.error("Bad request:", error));

    setTimeout(
      () =>
        fetch(url)
          .then(response => response.json())
          .then(dataJson => {
            this.setState(() => {
              return {
                events: dataJson.results
              };
            });
          })
          .catch(error => console.error("Bad request:", error)),
      1000
    );
  };

  handleSubscribe = (event, eventData) => {
    event.preventDefault();
    if (!eventData) {
      return false;
    }
    const url = `http://127.0.0.1:8000/api/newsfeed/${this.props.index}/subscriptions/`;
    const data = { to_newsfeed_id: eventData };

    fetch(url, {
      method: "POST",
      mode: "no-cors",
      body: JSON.stringify(data),
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      }
    }).catch(error => console.error("Bad request:", error));
  };

  handleUnsubscribe = (event, eventData) => {
    event.preventDefault();
    if (!eventData) {
      return false;
    }
    const url = `http://127.0.0.1:8000/api/newsfeed/${this.props.index}/subscriptions/${eventData}/`;
    axios.delete(url)
      .catch(error => console.error("Bad request:", error));
  };

  render() {
    return (
      <Card
        key={this.props.index}
        title={this.props.value.name}
        extra={<Icon type="sync" onClick={this.getEvents} />}
        hoverable={true}
        style={{ width: 250 }}
        actions={[
          <OptionsEventPopover
            handleSubscribe={this.handleSubscribe}
            subscriptions={this.state.subscriptions}
            getSubscriptions={this.getSubscriptions}
            newsFeeds={this.props.newsFeeds}
            handleUnsubscribe={this.handleUnsubscribe}
          />,
          <SubmitEventPopover handleSendEvent={this.handleSendEvent} />,
          <SubscribeEventPopover
            handleSubscribe={this.handleSubscribe}
            newsFeeds={this.props.newsFeeds}
          />
        ]}
      >
        <div style={{ overflow: "auto", height: 250 }}>
          {this.state.events.map(event => {
            return (
              <Card
                key={event.id}
                style={{ marginTop: 16 }}
                type="inner"
                title="Inner Card title"
                extra={<p>More</p>}
              >
                {event.data.field_1}
              </Card>
            );
          })}
        </div>
      </Card>
    );
  }
}

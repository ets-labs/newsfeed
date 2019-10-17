import React from "react";
import { NewsFeed } from "./Newsfeed";
import { generateId } from "./utils";
import "antd/dist/antd.css";
import "./App.css";

export class App extends React.Component {
  state = {
    newsFeeds: {
      "4yrb2ocd25bk17c9n5w": {
        name: "NF-BBC"
      },
      f2iw3ssb4hik1c38ni4: {
        name: "NF-WP"
      }
    }
  };

  createNewsFeed = () => {
    this.setState(prevState => {
      const newsFeeds = prevState.newsFeeds;
      const id = generateId();
      newsFeeds[id] = {
        name: `NF-${id.substring(0, 3)}`
      };
      localStorage.setItem("myNewsFeeds", JSON.stringify(newsFeeds));
      return {
        newsFeeds: newsFeeds
      };
    });
  };

  clearNewsFeedsStorage = () => {
    localStorage.clear();
    this.setState(() => {
      return {
        newsFeeds: {
          "4yrb2ocd25bk17c9n5w": {
            name: "NF-BBC"
          },
          f2iw3ssb4hik1c38ni4: {
            name: "NF-WP"
          }
        }
      };
    });
  };

  render() {
    const newsFeeds = localStorage.getItem("myNewsFeeds")
      ? Object.entries(JSON.parse(localStorage.getItem("myNewsFeeds")))
      : [];
    return (
      <div className="App">
        <div className="row text-center">
          <div className="col-md-4">
            <button className="btn-minimal" onClick={this.createNewsFeed}>
              Create NewsFeed
            </button>
          </div>
          <div className="col-md-4">
            <button
              className="btn-minimal"
              onClick={this.clearNewsFeedsStorage}
            >
              Clear Storage
            </button>
          </div>
        </div>
        <div className="row newsfeeds-card">
          {newsFeeds.map(([key, value]) => {
            return (
              <div key={key} className="col-md-4">
                <NewsFeed
                  index={key}
                  key={key}
                  value={value}
                  newsFeeds={this.state.newsFeeds}
                />
              </div>
            );
          })}
        </div>
      </div>
    );
  }
}

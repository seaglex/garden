
const App = React.createClass({
  render() {
    return (
      <div>
        <h1>App</h1>
        <ul>
          <li><ReactRouter.Link to="/react_router/about">About</ReactRouter.Link></li>
          <li><ReactRouter.Link to="/react_router/inbox">Inbox</ReactRouter.Link></li>
          <li><ReactRouter.Link to="/react_router/inbox/messages/8">Inbox8</ReactRouter.Link></li>
        </ul>
        {this.props.children}
      </div>
    )
  }
})
const About = React.createClass({
  render() {
    return (
      <div>
        About
      </div>
    )
  }
})
// etc.

const Inbox = React.createClass({
  render() {
    if (!this.props.children) {
        ReactRouter.browserHistory.push("/react_router/inbox/messages/0")
    }
    return (
      <div>
        <h2>Inbox</h2>
        {this.props.children || "Welcome to your Inbox"}
      </div>
    )
  }
})

const Message = React.createClass({
  render() {
    return <h3>Message {this.props.params.id}</h3>
  }
})

ReactDOM.render((
  <ReactRouter.Router history={ReactRouter.browserHistory}>
    <ReactRouter.Route path="/react_router" component={App}>
      <ReactRouter.Route path="about" component={About}/>
      <ReactRouter.Route path="inbox" component={Inbox}>
        <ReactRouter.Route path="messages/:id" component={Message}/>
      </ReactRouter.Route>
      <ReactRouter.Route path="*" component={ReactRouter.NoMatch}/>
    </ReactRouter.Route>
  </ReactRouter.Router>
), document.body)
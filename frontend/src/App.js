import React, { useContext } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import { GlobalStateProvider } from './context/GlobalState';
import Login from './components/Login';
import PageManagement from './components/PageManagement';
import LinkManagement from './components/LinkManagement';
import UserManagement from './components/UserManagement';
import DataBackup from './components/DataBackup';

const PrivateRoute = ({ component: Component, ...rest }) => {
  const { isAuthenticated } = useContext(AuthContext);
  return (
    <Route
      {...rest}
      render={props =>
        isAuthenticated ? (
          <Component {...props} />
        ) : (
          <Redirect to="/login" />
        )
      }
    />
  );
};

const App = () => {
  return (
    <AuthProvider>
      <GlobalStateProvider>
        <Router>
          <Switch>
            <Route path="/login" component={Login} />
            <PrivateRoute path="/pages" component={PageManagement} />
            <PrivateRoute path="/links" component={LinkManagement} />
            <PrivateRoute path="/users" component={UserManagement} />
            <PrivateRoute path="/backup" component={DataBackup} />
            <Redirect from="/" to="/login" />
          </Switch>
        </Router>
      </GlobalStateProvider>
    </AuthProvider>
  );
};

export default App;

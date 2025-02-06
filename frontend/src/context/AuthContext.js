import React, { createContext, useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { authStatus } from '../utils/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const history = useHistory();

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await authStatus();
        if (response.authenticated) {
          setIsAuthenticated(true);
          setUser(response.user);
        } else {
          setIsAuthenticated(false);
          setUser(null);
          history.push('/login');
        }
      } catch (error) {
        setIsAuthenticated(false);
        setUser(null);
        history.push('/login');
      }
    };

    checkAuthStatus();
  }, [history]);

  return (
    <AuthContext.Provider value={{ isAuthenticated, setIsAuthenticated, user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

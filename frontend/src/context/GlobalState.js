import React, { createContext, useReducer } from 'react';

const initialState = {
  pages: [],
  links: [],
  users: [],
  backup: null,
};

const GlobalStateContext = createContext(initialState);
const DispatchContext = createContext(() => {});

const globalStateReducer = (state, action) => {
  switch (action.type) {
    case 'SET_PAGES':
      return { ...state, pages: action.payload };
    case 'SET_LINKS':
      return { ...state, links: action.payload };
    case 'SET_USERS':
      return { ...state, users: action.payload };
    case 'SET_BACKUP':
      return { ...state, backup: action.payload };
    default:
      return state;
  }
};

const GlobalStateProvider = ({ children }) => {
  const [state, dispatch] = useReducer(globalStateReducer, initialState);

  return (
    <GlobalStateContext.Provider value={state}>
      <DispatchContext.Provider value={dispatch}>
        {children}
      </DispatchContext.Provider>
    </GlobalStateContext.Provider>
  );
};

export { GlobalStateContext, DispatchContext, GlobalStateProvider };

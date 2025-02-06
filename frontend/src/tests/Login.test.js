import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import Login from '../components/Login';
import { AuthProvider } from '../context/AuthContext';
import { login } from '../utils/api';

jest.mock('../utils/api');

describe('Login Component', () => {
  test('renders login form', () => {
    const { getByLabelText, getByText } = render(
      <AuthProvider>
        <Router>
          <Login />
        </Router>
      </AuthProvider>
    );

    expect(getByLabelText(/用户名/i)).toBeInTheDocument();
    expect(getByLabelText(/密码/i)).toBeInTheDocument();
    expect(getByText(/登录/i)).toBeInTheDocument();
  });

  test('displays error message on failed login', async () => {
    login.mockResolvedValueOnce({ success: false, message: '登录失败' });

    const { getByLabelText, getByText, findByText } = render(
      <AuthProvider>
        <Router>
          <Login />
        </Router>
      </AuthProvider>
    );

    fireEvent.change(getByLabelText(/用户名/i), { target: { value: 'wronguser' } });
    fireEvent.change(getByLabelText(/密码/i), { target: { value: 'wrongpassword' } });
    fireEvent.click(getByText(/登录/i));

    const errorMessage = await findByText(/登录失败/i);
    expect(errorMessage).toBeInTheDocument();
  });

  test('redirects to pages on successful login', async () => {
    login.mockResolvedValueOnce({ success: true });

    const { getByLabelText, getByText, history } = render(
      <AuthProvider>
        <Router>
          <Login />
        </Router>
      </AuthProvider>
    );

    fireEvent.change(getByLabelText(/用户名/i), { target: { value: 'correctuser' } });
    fireEvent.change(getByLabelText(/密码/i), { target: { value: 'correctpassword' } });
    fireEvent.click(getByText(/登录/i));

    await waitFor(() => {
      expect(history.location.pathname).toBe('/pages');
    });
  });
});

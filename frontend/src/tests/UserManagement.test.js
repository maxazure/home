import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import UserManagement from '../components/UserManagement';
import { getUsers, addUser, updateUser, deleteUser } from '../utils/api';

jest.mock('../utils/api');

describe('UserManagement Component', () => {
  const mockUsers = [
    { id: 1, username: 'user1' },
    { id: 2, username: 'user2' },
  ];

  beforeEach(() => {
    getUsers.mockResolvedValue(mockUsers);
  });

  test('renders user list', async () => {
    render(<UserManagement />);
    const user1 = await screen.findByText('user1');
    const user2 = await screen.findByText('user2');
    expect(user1).toBeInTheDocument();
    expect(user2).toBeInTheDocument();
  });

  test('adds a new user', async () => {
    const newUser = { id: 3, username: 'user3' };
    addUser.mockResolvedValue(newUser);

    render(<UserManagement />);
    fireEvent.change(screen.getByLabelText('用户名'), { target: { value: 'user3' } });
    fireEvent.change(screen.getByLabelText('密码'), { target: { value: 'password' } });
    fireEvent.click(screen.getByText('添加用户'));

    const user3 = await screen.findByText('user3');
    expect(user3).toBeInTheDocument();
  });

  test('updates an existing user', async () => {
    const updatedUser = { id: 1, username: 'updatedUser1' };
    updateUser.mockResolvedValue(updatedUser);

    render(<UserManagement />);
    fireEvent.click(screen.getByText('编辑', { selector: 'button' }));
    fireEvent.change(screen.getByLabelText('用户名'), { target: { value: 'updatedUser1' } });
    fireEvent.change(screen.getByLabelText('密码'), { target: { value: 'newpassword' } });
    fireEvent.click(screen.getByText('更新用户'));

    const updatedUser1 = await screen.findByText('updatedUser1');
    expect(updatedUser1).toBeInTheDocument();
  });

  test('deletes a user', async () => {
    deleteUser.mockResolvedValue({ message: 'User deleted successfully' });

    render(<UserManagement />);
    fireEvent.click(screen.getByText('删除', { selector: 'button' }));

    const user1 = screen.queryByText('user1');
    expect(user1).not.toBeInTheDocument();
  });
});

import React, { useState, useEffect } from 'react';
import { getUsers, addUser, updateUser, deleteUser } from '../utils/api';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [editingUser, setEditingUser] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    const response = await getUsers();
    setUsers(response);
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    const newUser = await addUser({ username, password });
    setUsers([...users, newUser]);
    setUsername('');
    setPassword('');
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();
    const updatedUser = await updateUser(editingUser.id, { username, password });
    setUsers(users.map(user => (user.id === editingUser.id ? updatedUser : user)));
    setEditingUser(null);
    setUsername('');
    setPassword('');
  };

  const handleDeleteUser = async (id) => {
    await deleteUser(id);
    setUsers(users.filter(user => user.id !== id));
  };

  const startEditing = (user) => {
    setEditingUser(user);
    setUsername(user.username);
    setPassword('');
  };

  const cancelEditing = () => {
    setEditingUser(null);
    setUsername('');
    setPassword('');
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">用户管理</h2>
      <form onSubmit={editingUser ? handleUpdateUser : handleAddUser} className="mb-4">
        <div className="mb-2">
          <label className="block text-sm font-medium text-gray-700">用户名</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            required
          />
        </div>
        <div className="mb-2">
          <label className="block text-sm font-medium text-gray-700">密码</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
            required
          />
        </div>
        <div className="flex items-center justify-between">
          <button
            type="submit"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            {editingUser ? '更新用户' : '添加用户'}
          </button>
          {editingUser && (
            <button
              type="button"
              onClick={cancelEditing}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              取消
            </button>
          )}
        </div>
      </form>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {users.map((user) => (
            <tr key={user.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.username}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  onClick={() => startEditing(user)}
                  className="text-indigo-600 hover:text-indigo-900"
                >
                  编辑
                </button>
                <button
                  onClick={() => handleDeleteUser(user.id)}
                  className="text-red-600 hover:text-red-900 ml-4"
                >
                  删除
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserManagement;

// 全局变量
let currentCategoryId = null;
let currentLinkId = null;
let currentUserId = null;

// 页面加载完成后显示分类管理
document.addEventListener('DOMContentLoaded', () => {
    showCategories();
});

// 显示分类管理页面
async function showCategories() {
    document.getElementById('categories-section').classList.remove('hidden');
    document.getElementById('links-section').classList.add('hidden');
    document.getElementById('users-section').classList.add('hidden');
    await loadCategories();
}

// 显示链接管理页面
async function showLinks() {
    document.getElementById('categories-section').classList.add('hidden');
    document.getElementById('links-section').classList.remove('hidden');
    document.getElementById('users-section').classList.add('hidden');
    await Promise.all([loadLinks(), loadCategoriesForSelect()]);
}

// 显示用户管理页面
async function showUsers() {
    document.getElementById('categories-section').classList.add('hidden');
    document.getElementById('links-section').classList.add('hidden');
    document.getElementById('users-section').classList.remove('hidden');
    await loadUsers();
}

// 加载分类列表
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();
        
        const tbody = document.getElementById('categories-table-body');
        tbody.innerHTML = categories.map(category => `
            <tr>
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900">${category.id}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-900">${category.title}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-900">${category.section_name}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    <button onclick="editCategory(${category.id}, '${category.title}', '${category.section_name}')"
                            class="text-primary-600 hover:text-primary-900 mr-3">编辑</button>
                    <button onclick="deleteCategory(${category.id})"
                            class="text-red-600 hover:text-red-900">删除</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// 加载链接列表
async function loadLinks() {
    try {
        const [categoriesResponse, linksResponse] = await Promise.all([
            fetch('/api/categories'),
            fetch('/api/links')
        ]);
        
        const categories = await categoriesResponse.json();
        const links = await linksResponse.json();
        
        // 按分类组织链接
        const linksByCategory = {};
        links.forEach(link => {
            if (!linksByCategory[link.category_id]) {
                linksByCategory[link.category_id] = [];
            }
            linksByCategory[link.category_id].push(link);
        });
        
        const container = document.getElementById('links-container');
        container.innerHTML = categories.map(category => `
            <div class="bg-white shadow rounded-lg overflow-hidden">
                <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
                    <div>
                        <h3 class="text-lg font-medium text-gray-900">${category.title}</h3>
                        <p class="mt-1 text-sm text-gray-500">${category.section_name}</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="editCategory(${category.id}, '${category.title}', '${category.section_name}')" 
                                class="btn btn-secondary flex items-center">
                            <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                            </svg>
                            修改分类
                        </button>
                        <button onclick="deleteCategoryWithConfirm(${category.id}, '${category.title}')" 
                                class="btn btn-danger flex items-center">
                            <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                            </svg>
                            删除分类
                        </button>
                        <button onclick="showAddLinkModal(${category.id})" class="btn btn-primary flex items-center">
                            <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M12 4v16m8-8H4"/>
                            </svg>
                            添加链接
                        </button>
                    </div>
                </div>
                <div class="px-4 py-5 sm:p-6">
                    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        ${(linksByCategory[category.id] || []).map(link => `
                            <div class="bg-gray-50 rounded-lg p-4 hover:shadow transition-shadow">
                                <div class="flex justify-between items-start">
                                    <div class="flex-1">
                                        <h4 class="text-base font-medium text-gray-900">${link.name}</h4>
                                        <a href="${link.url}" target="_blank" rel="noopener noreferrer" 
                                           class="mt-1 text-sm text-primary-600 hover:text-primary-900 break-all">
                                            ${link.url}
                                        </a>
                                    </div>
                                    <div class="ml-4 flex-shrink-0">
                                        <button onclick="editLink(${link.id}, '${link.name}', '${link.url}', ${link.category_id})"
                                                class="text-primary-600 hover:text-primary-900">
                                            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                                            </svg>
                                        </button>
                                        <button onclick="deleteLink(${link.id})"
                                                class="ml-2 text-red-600 hover:text-red-900">
                                            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading links:', error);
    }
}

// 加载分类下拉选择框
async function loadCategoriesForSelect() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();
        
        const select = document.getElementById('link-category');
        select.innerHTML = categories.map(category =>
            `<option value="${category.id}">${category.title}</option>`
        ).join('');
    } catch (error) {
        console.error('Error loading categories for select:', error);
    }
}

// 显示添加分类模态框
function showAddCategoryModal() {
    currentCategoryId = null;
    document.getElementById('category-modal-title').textContent = '添加分类';
    document.getElementById('category-title').value = '';
    document.getElementById('section-name').value = '';
    document.getElementById('category-modal').classList.remove('hidden');
}

// 显示编辑分类模态框
function editCategory(id, title, sectionName) {
    currentCategoryId = id;
    document.getElementById('category-modal-title').textContent = '编辑分类';
    document.getElementById('category-title').value = title;
    document.getElementById('section-name').value = sectionName;
    document.getElementById('category-modal').classList.remove('hidden');
}

// 显示添加链接模态框
function showAddLinkModal(categoryId = null) {
    currentLinkId = null;
    document.getElementById('link-modal-title').textContent = '添加链接';
    document.getElementById('link-name').value = '';
    document.getElementById('link-url').value = '';
    if (categoryId) {
        document.getElementById('link-category').value = categoryId;
    }
    document.getElementById('link-modal').classList.remove('hidden');
}

// 显示编辑链接模态框
function editLink(id, name, url, categoryId) {
    currentLinkId = id;
    document.getElementById('link-modal-title').textContent = '编辑链接';
    document.getElementById('link-name').value = name;
    document.getElementById('link-url').value = url;
    document.getElementById('link-category').value = categoryId;
    document.getElementById('link-modal').classList.remove('hidden');
}

// 关闭模态框
function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// 处理分类表单提交
document.getElementById('category-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('category-title').value;
    const section_name = document.getElementById('section-name').value;
    
    try {
        const url = currentCategoryId 
            ? `/api/admin/categories/${currentCategoryId}`
            : '/api/admin/categories';
            
        const method = currentCategoryId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, section_name }),
        });
        
        if (response.ok) {
            closeModal('category-modal');
            await loadCategories();
        } else {
            const error = await response.json();
            alert(error.message || '操作失败');
        }
    } catch (error) {
        console.error('Error saving category:', error);
        alert('保存失败，请重试');
    }
});

// 处理链接表单提交
document.getElementById('link-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('link-name').value;
    const url = document.getElementById('link-url').value;
    const category_id = document.getElementById('link-category').value;
    
    try {
        const apiUrl = currentLinkId 
            ? `/api/admin/links/${currentLinkId}`
            : '/api/admin/links';
            
        const method = currentLinkId ? 'PUT' : 'POST';
        
        const response = await fetch(apiUrl, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, url, category_id }),
        });
        
        if (response.ok) {
            closeModal('link-modal');
            await loadLinks();
        } else {
            const error = await response.json();
            alert(error.message || '操作失败');
        }
    } catch (error) {
        console.error('Error saving link:', error);
        alert('保存失败，请重试');
    }
});

// 删除分类
async function deleteCategory(id) {
    if (!confirm('确定要删除这个分类吗？相关的链接也会被删除。')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/categories/${id}`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
            await loadCategories();
        } else {
            const error = await response.json();
            alert(error.message || '删除失败');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        alert('删除失败，请重试');
    }
}

// 删除链接
async function deleteLink(id) {
    if (!confirm('确定要删除这个链接吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/links/${id}`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
            await loadLinks();
        } else {
            const error = await response.json();
            alert(error.message || '删除失败');
        }
    } catch (error) {
        console.error('Error deleting link:', error);
        alert('删除失败，请重试');
    }
}

// 加载用户列表
async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users');
        const users = await response.json();
        
        const tbody = document.getElementById('users-table-body');
        tbody.innerHTML = users.map(user => `
            <tr>
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-900">${user.id}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-900">${user.username}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-900">${new Date(user.created_at).toLocaleString()}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    <button onclick="editUser(${user.id}, '${user.username}')"
                            class="text-primary-600 hover:text-primary-900 mr-3">编辑</button>
                    <button onclick="deleteUser(${user.id})"
                            class="text-red-600 hover:text-red-900">删除</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// 显示添加用户模态框
function showAddUserModal() {
    currentUserId = null;
    document.getElementById('user-modal-title').textContent = '添加用户';
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    document.getElementById('user-modal').classList.remove('hidden');
}

// 显示编辑用户模态框
function editUser(id, username) {
    currentUserId = id;
    document.getElementById('user-modal-title').textContent = '编辑用户';
    document.getElementById('username').value = username;
    document.getElementById('password').value = '';
    document.getElementById('user-modal').classList.remove('hidden');
}

// 删除用户
async function deleteUser(id) {
    if (!confirm('确定要删除这个用户吗？')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/users/${id}`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
            await loadUsers();
        } else {
            const error = await response.json();
            alert(error.message || '删除失败');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('删除失败，请重试');
    }
}

// 处理用户表单提交
document.getElementById('user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        const url = currentUserId 
            ? `/api/admin/users/${currentUserId}`
            : '/api/admin/users';
            
        const method = currentUserId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        if (response.ok) {
            closeModal('user-modal');
            await loadUsers();
        } else {
            const error = await response.json();
            alert(error.message || '操作失败');
        }
    } catch (error) {
        console.error('Error saving user:', error);
        alert('保存失败，请重试');
    }
});

// 添加新的删除分类确认函数
async function deleteCategoryWithConfirm(id, title) {
    if (!confirm(`确定要删除分类"${title}"吗？\n注意：该分类下的所有链接都将被删除！`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/categories/${id}`, {
            method: 'DELETE',
        });
        
        if (response.ok) {
            await loadLinks();
        } else {
            const error = await response.json();
            alert(error.message || '删除失败');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        alert('删除失败，请重试');
    }
} 
// 全局变量
let currentCategoryId = null;
let currentLinkId = null;
let currentUserId = null;

// 页面加载完成后显示分类管理
document.addEventListener('DOMContentLoaded', () => {
    showCategories();
});

// 更新页面标题
function updatePageTitle(title) {
    document.getElementById('main-title').textContent = title;
}

// 显示分类管理页面
async function showCategories() {
    updatePageTitle('分类管理');
    document.getElementById('categories-section').classList.remove('hidden');
    document.getElementById('links-section').classList.add('hidden');
    document.getElementById('users-section').classList.add('hidden');
    await loadCategories();
}

// 显示链接管理页面
async function showLinks() {
    updatePageTitle('链接管理');
    document.getElementById('categories-section').classList.add('hidden');
    document.getElementById('links-section').classList.remove('hidden');
    document.getElementById('users-section').classList.add('hidden');
    await Promise.all([loadLinks(), loadCategoriesForSelect()]);
}

// 显示用户管理页面
async function showUsers() {
    updatePageTitle('用户管理');
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
        
        // 按区域分组
        const sectionGroups = {};
        categories.forEach(category => {
            if (!sectionGroups[category.section_name]) {
                sectionGroups[category.section_name] = [];
            }
            sectionGroups[category.section_name].push(category);
        });
        
        const container = document.getElementById('categories-container');
        container.innerHTML = ''; // 清空现有内容
        
        // 渲染每个区域的卡片
        Object.entries(sectionGroups).forEach(([sectionName, categories]) => {
            const sectionCard = document.createElement('div');
            sectionCard.className = 'bg-white shadow rounded-lg overflow-hidden mb-6';
            sectionCard.innerHTML = `
                <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
                    <div class="flex items-center space-x-4">
                        <h3 class="text-lg font-medium text-gray-900">${sectionName}</h3>
                        <div class="flex items-center space-x-2">
                            <button onclick="showSectionModal('${sectionName}')" class="text-sm text-blue-600 hover:text-blue-800">
                                修改区域名称
                            </button>
                            <button onclick="deleteSection('${sectionName}')" class="text-sm text-red-600 hover:text-red-800">
                                删除区域
                            </button>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="showAddCategoryModal('${sectionName}')" class="btn btn-primary">
                            添加分类
                        </button>
                        <button onclick="moveSectionUp('${sectionName}')" class="btn btn-secondary">
                            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                            </svg>
                        </button>
                        <button onclick="moveSectionDown('${sectionName}')" class="btn btn-secondary">
                            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="px-4 py-5 sm:p-6">
                    <div class="space-y-4" id="categories-${sectionName.replace(/\s+/g, '-')}">
                        ${categories.map((category, index) => `
                            <div class="flex items-center justify-between bg-gray-50 p-4 rounded-lg" 
                                 draggable="true" 
                                 ondragstart="dragStart(event, ${category.id})"
                                 ondragend="dragEnd(event)"
                                 ondragover="dragOver(event)"
                                 ondragleave="dragLeave(event)"
                                 ondrop="drop(event, ${category.id})"
                                 data-category-id="${category.id}">
                                <div class="flex-1">
                                    <h4 class="text-base font-medium text-gray-900">${category.title}</h4>
                                </div>
                                <div class="flex items-center space-x-2">
                                    <button onclick="editCategory(${category.id}, '${category.title}', '${category.section_name}')"
                                            class="text-blue-600 hover:text-blue-800">编辑</button>
                                    <button onclick="deleteCategory(${category.id})"
                                            class="text-red-600 hover:text-red-900">删除</button>
                                    <button onclick="moveCategoryUp(${category.id})" class="text-gray-600 hover:text-gray-800">
                                        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                                        </svg>
                                    </button>
                                    <button onclick="moveCategoryDown(${category.id})" class="text-gray-600 hover:text-gray-800">
                                        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            container.appendChild(sectionCard);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
        alert('加载分类失败，请重试');
    }
}

// 拖拽相关函数
function dragStart(event, categoryId) {
    event.dataTransfer.setData('text/plain', categoryId);
    const draggedElement = event.target;
    draggedElement.classList.add('opacity-50');
}

function dragEnd(event) {
    event.target.classList.remove('opacity-50');
}

function dragOver(event) {
    event.preventDefault();
    const dropZone = event.target.closest('[data-category-id]');
    if (dropZone) {
        dropZone.classList.add('bg-gray-100');
    }
}

function dragLeave(event) {
    const dropZone = event.target.closest('[data-category-id]');
    if (dropZone) {
        dropZone.classList.remove('bg-gray-100');
    }
}

function drop(event, targetCategoryId) {
    event.preventDefault();
    const dropZone = event.target.closest('[data-category-id]');
    if (dropZone) {
        dropZone.classList.remove('bg-gray-100');
    }
    
    const sourceCategoryId = event.dataTransfer.getData('text/plain');
    if (sourceCategoryId !== targetCategoryId.toString()) {
        reorderCategories(parseInt(sourceCategoryId), targetCategoryId);
    }
}

// 重新排序分类
async function reorderCategories(sourceCategoryId, targetCategoryId) {
    try {
        const response = await fetch('/api/admin/categories/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                source_id: sourceCategoryId,
                target_id: targetCategoryId
            }),
        });
        
        if (response.ok) {
            await loadCategories();
        } else {
            const error = await response.json();
            alert(error.message || '重新排序失败');
        }
    } catch (error) {
        console.error('Error reordering categories:', error);
        alert('重新排序失败，请重试');
    }
}

// 显示区域管理模态框
function showSectionModal(sectionName = '') {
    document.getElementById('section-modal-title').textContent = sectionName ? '修改区域名称' : '添加新区域';
    document.getElementById('section-name-input').value = sectionName;
    document.getElementById('old-section-name').value = sectionName;
    document.getElementById('section-modal').classList.remove('hidden');
    
    // 确保表单重置
    const form = document.getElementById('section-form');
    form.reset();
    if (sectionName) {
        document.getElementById('section-name-input').value = sectionName;
    }
}

// 处理区域表单提交
async function handleSectionSubmit(event) {
    event.preventDefault();
    const sectionNameInput = document.getElementById('section-name-input');
    const oldSectionName = document.getElementById('old-section-name').value;
    const newSectionName = sectionNameInput.value.trim();

    if (!newSectionName) {
        alert('请输入区域名称');
        return;
    }

    try {
        const url = oldSectionName ? '/api/admin/sections/update' : '/api/admin/sections';
        const data = {
            section_name: newSectionName,
            old_section_name: oldSectionName
        };
        
        console.log('发送请求到:', url);
        console.log('发送数据:', data);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const responseData = await response.json();
        console.log('服务器响应:', responseData);
        
        if (response.ok) {
            closeModal('section-modal');
            await loadCategories();
        } else {
            alert(responseData.message || '操作失败');
        }
    } catch (error) {
        console.error('Error handling section:', error);
        alert('操作失败，请重试');
    }
}

// 移动区域位置
async function moveSectionUp(sectionName) {
    await moveSection(sectionName, 'up');
}

async function moveSectionDown(sectionName) {
    await moveSection(sectionName, 'down');
}

async function moveSection(sectionName, direction) {
    try {
        const response = await fetch('/api/admin/sections/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                section_name: sectionName,
                direction: direction
            }),
        });
        
        if (response.ok) {
            await loadCategories();
        } else {
            const error = await response.json();
            alert(error.message || '移动失败');
        }
    } catch (error) {
        console.error('Error moving section:', error);
        alert('移动失败，请重试');
    }
}

// 移动分类位置
async function moveCategoryUp(categoryId) {
    await moveCategory(categoryId, 'up');
}

async function moveCategoryDown(categoryId) {
    await moveCategory(categoryId, 'down');
}

async function moveCategory(categoryId, direction) {
    try {
        const response = await fetch('/api/admin/categories/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                category_id: categoryId,
                direction: direction
            }),
        });
        
        if (response.ok) {
            await loadCategories();
        } else {
            const error = await response.json();
            alert(error.message || '移动失败');
        }
    } catch (error) {
        console.error('Error moving category:', error);
        alert('移动失败，请重试');
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

// 加载区域下拉框
async function loadSectionsForSelect() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();
        
        // 获取唯一的区域名称
        const sections = [...new Set(categories.map(c => c.section_name))];
        
        const select = document.getElementById('section-name');
        select.innerHTML = sections.map(section =>
            `<option value="${section}">${section}</option>`
        ).join('');
    } catch (error) {
        console.error('Error loading sections for select:', error);
    }
}

// 显示添加分类模态框
function showAddCategoryModal(sectionName = null) {
    currentCategoryId = null;
    document.getElementById('category-modal-title').textContent = '添加分类';
    document.getElementById('category-title').value = '';
    if (sectionName) {
        document.getElementById('section-name').value = sectionName;
    }
    loadSectionsForSelect();
    document.getElementById('category-modal').classList.remove('hidden');
}

// 显示编辑分类模态框
function editCategory(id, title, sectionName) {
    currentCategoryId = id;
    document.getElementById('category-modal-title').textContent = '编辑分类';
    document.getElementById('category-title').value = title;
    loadSectionsForSelect().then(() => {
        document.getElementById('section-name').value = sectionName;
    });
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
            alert('删除成功！');
        } else {
            const error = await response.json();
            alert(error.message || '删除失败，请重试');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        alert('删除失败，请重试');
    }
}

function updateUserSection(data) {
    const userSection = document.getElementById('userSection');
    if (data.authenticated) {
        userSection.innerHTML = `
            <div class="flex items-center space-x-4">
                <span class="text-gray-700">${data.username}</span>
                <a href="/" class="text-blue-600 hover:text-blue-800">查看首页</a>
                <a href="/admin" class="text-blue-600 hover:text-blue-800">进入后台</a>
                <button onclick="logout()" class="text-red-600 hover:text-red-800">退出</button>
            </div>
        `;
    } else {
        userSection.innerHTML = `
            <a href="/admin/login.html" class="text-blue-600 hover:text-blue-800">登录</a>
        `;
    }
}

// 删除区域
async function deleteSection(sectionName) {
    if (!confirm(`确定要删除区域 "${sectionName}" 吗？\n注意：这将同时删除该区域下的所有分类和链接！`)) {
        return;
    }

    try {
        const response = await fetch('/api/admin/sections/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                section_name: sectionName
            })
        });

        const data = await response.json();
        
        if (response.ok) {
            await loadCategories();
        } else {
            alert(data.message || '删除失败');
        }
    } catch (error) {
        console.error('Error deleting section:', error);
        alert('删除失败，请重试');
    }
} 
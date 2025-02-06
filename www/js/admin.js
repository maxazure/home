let currentCategoryId = null;
let currentLinkId = null;
let currentUserId = null;
let currentPageId = null;
let currentRegionId = null;

document.addEventListener('DOMContentLoaded', () => {
    showCategories();
});

function updatePageTitle(title) {
    document.getElementById('main-title').textContent = title;
}

async function showCategories() {
    updatePageTitle('分类管理');
    document.getElementById('categories-section').classList.remove('hidden');
    document.getElementById('links-section').classList.add('hidden');
    document.getElementById('users-section').classList.add('hidden');
    document.getElementById('backup-section').classList.add('hidden');
    document.getElementById('pages-section').classList.add('hidden');
    updateActiveMenu('categories');
    await loadCategories();
}

async function showLinks() {
    updatePageTitle('链接管理');
    document.getElementById('categories-section').classList.add('hidden');
    document.getElementById('links-section').classList.remove('hidden');
    document.getElementById('users-section').classList.add('hidden');
    document.getElementById('backup-section').classList.add('hidden');
    document.getElementById('pages-section').classList.add('hidden');
    updateActiveMenu('links');
    await Promise.all([loadLinks(), loadCategoriesForSelect()]);
}

async function showUsers() {
    updatePageTitle('用户管理');
    document.getElementById('categories-section').classList.add('hidden');
    document.getElementById('links-section').classList.add('hidden');
    document.getElementById('users-section').classList.remove('hidden');
    document.getElementById('backup-section').classList.add('hidden');
    document.getElementById('pages-section').classList.add('hidden');
    updateActiveMenu('users');
    await loadUsers();
}

async function showPages() {
    updatePageTitle('页面管理');
    document.getElementById('categories-section').classList.add('hidden');
    document.getElementById('links-section').classList.add('hidden');
    document.getElementById('users-section').classList.add('hidden');
    document.getElementById('backup-section').classList.add('hidden');
    document.getElementById('pages-section').classList.remove('hidden');
    updateActiveMenu('pages');
    await loadPages();
}

async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();
        const sectionGroups = {};
        categories.forEach(category => {
            if (!sectionGroups[category.section_name]) {
                sectionGroups[category.section_name] = [];
            }
            sectionGroups[category.section_name].push(category);
        });
        const container = document.getElementById('categories-container');
        container.innerHTML = '';
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

function showSectionModal(sectionName = '') {
    document.getElementById('section-modal-title').textContent = sectionName ? '修改区域名称' : '添加新区域';
    document.getElementById('section-name-input').value = sectionName;
    document.getElementById('old-section-name').value = sectionName;
    document.getElementById('section-modal').classList.remove('hidden');
    const form = document.getElementById('section-form');
    form.reset();
    if (sectionName) {
        document.getElementById('section-name-input').value = sectionName;
    }
}

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
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        const responseData = await response.json();
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

async function loadSectionsForSelect() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();
        const sections = [...new Set(categories.map(c => c.section_name))];
        const select = document.getElementById('category-section');
        select.innerHTML = sections.map(section =>
            `<option value="${section}">${section}</option>`
        ).join('');
    } catch (error) {
        console.error('Error loading sections for select:', error);
    }
}

async function showAddCategoryModal(sectionName = null) {
    currentCategoryId = null;
    document.getElementById('category-modal-title').textContent = '添加分类';
    document.getElementById('category-title').value = '';
    await loadSectionsForSelect();
    if (sectionName) {
        document.getElementById('category-section').value = sectionName;
    }
    document.getElementById('category-modal').classList.remove('hidden');
}

async function editCategory(categoryId, currentName, sectionName) {
    currentCategoryId = categoryId;
    document.getElementById('category-modal-title').textContent = '编辑分类';
    document.getElementById('category-title').value = currentName;
    await loadSectionsForSelect();
    document.getElementById('category-section').value = sectionName;
    document.getElementById('category-modal').classList.remove('hidden');
}

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

function editLink(id, name, url, categoryId) {
    currentLinkId = id;
    document.getElementById('link-modal-title').textContent = '编辑链接';
    document.getElementById('link-name').value = name;
    document.getElementById('link-url').value = url;
    document.getElementById('link-category').value = categoryId;
    document.getElementById('link-modal').classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

document.getElementById('category-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('category-title').value;
    const section_name = document.getElementById('category-section').value;
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
            await loadLinks();
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

async function loadUsers() {
    try {
        const response = await fetch('/api/admin/users');
        const users = await response.json();
        const tbody = document.getElementById('users-table-body');
        tbody.innerHTML = users.map(user => `
            <tr class="hover:bg-gray-50">
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900">${user.id}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-900">${user.username}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">${new Date(user.created_at).toLocaleString()}</td>
                <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <div class="flex items-center space-x-4">
                        <button onclick="editUser(${user.id}, '${user.username}')"
                                class="text-blue-600 hover:text-blue-900">编辑</button>
                        <button onclick="deleteUser(${user.id})"
                                class="text-red-600 hover:text-red-900">删除</button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function showAddUserModal() {
    currentUserId = null;
    document.getElementById('user-modal-title').textContent = '添加用户';
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
    document.getElementById('user-modal').classList.remove('hidden');
}

function editUser(id, username) {
    currentUserId = id;
    document.getElementById('user-modal-title').textContent = '编辑用户';
    document.getElementById('username').value = username;
    document.getElementById('password').value = '';
    document.getElementById('user-modal').classList.remove('hidden');
}

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

async function loadLinks() {
    try {
        const response = await fetch('/api/links');
        const links = await response.json();
        const categoryGroups = {};
        links.forEach(link => {
            if (!categoryGroups[link.category_id]) {
                categoryGroups[link.category_id] = {
                    id: link.category_id,
                    name: link.category.title,
                    links: []
                };
            }
            categoryGroups[link.category_id].links.push(link);
        });
        const linksContainer = document.getElementById('links-container');
        linksContainer.innerHTML = '';
        Object.values(categoryGroups).forEach(({id: categoryId, name, links}) => {
            const categoryCard = document.createElement('div');
            categoryCard.className = 'bg-white shadow rounded-lg overflow-hidden mb-6';
            categoryCard.innerHTML = `
                <div class="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
                    <h3 class="text-lg font-medium text-gray-900">${name}</h3>
                    <div class="flex items-center space-x-2">
                        <button onclick="editCategory(${categoryId}, '${name}')" class="text-sm text-blue-600 hover:text-blue-800">修改分类名</button>
                        <button onclick="deleteCategoryWithConfirm(${categoryId}, '${name}')" class="text-sm text-red-600 hover:text-red-800">删除分类</button>
                    </div>
                </div>
                <div class="px-4 py-5 sm:p-6">
                    <div class="space-y-4">
                        ${links.map(link => `
                            <div class="flex items-center justify-between">
                                <div>
                                    <a href="${link.url}" target="_blank" class="text-blue-600 hover:text-blue-800">${link.name}</a>
                                </div>
                                <div class="flex items-center space-x-2">
                                    <button onclick="editLink(${link.id}, '${link.name}', '${link.url}', ${link.category_id})" class="text-sm text-blue-600 hover:text-blue-800">编辑</button>
                                    <button onclick="deleteLink(${link.id})" class="text-sm text-red-600 hover:text-red-800">删除</button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            linksContainer.appendChild(categoryCard);
        });
    } catch (error) {
        console.error('Error loading links:', error);
        alert('加载链接失败，请重试');
    }
}

function showBackup() {
    updatePageTitle('数据备份');
    document.getElementById('categories-section').classList.add('hidden');
    document.getElementById('links-section').classList.add('hidden');
    document.getElementById('users-section').classList.add('hidden');
    document.getElementById('backup-section').classList.remove('hidden');
    document.getElementById('pages-section').classList.add('hidden');
    updateActiveMenu('backup');
}

async function exportData() {
    try {
        const response = await fetch('/api/admin/export');
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || '导出失败');
        }
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'links_backup.json';
        if (contentDisposition) {
            const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        console.error('Error exporting data:', error);
        alert(error.message || '导出失败，请重试');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const importForm = document.getElementById('import-form');
    if (importForm) {
        importForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const fileInput = document.getElementById('import-file');
            const file = fileInput.files[0];
            if (!file) {
                alert('请选择要导入的文件');
                return;
            }
            if (!file.name.endsWith('.json')) {
                alert('请选择JSON格式的文件');
                return;
            }
            if (!confirm('导入数据将覆盖现有的所有数据，确定要继续吗？')) {
                return;
            }
            const formData = new FormData();
            formData.append('file', file);
            try {
                const response = await fetch('/api/admin/import', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (!response.ok) {
                    throw new Error(result.message || '导入失败');
                }
                alert('数据导入成功');
                fileInput.value = '';
                await loadCategories();
            } catch (error) {
                console.error('Error importing data:', error);
                alert(error.message || '导入失败，请重试');
            }
        });
    }
});

function updateActiveMenu(section) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`[data-section="${section}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

async function loadPages() {
    try {
        const response = await fetch('/api/pages');
        if (!response.ok) {
            throw new Error('加载页面失败');
        }
        const pages = await response.json();
        const container = document.getElementById('pages-container');
        container.innerHTML = pages.map(page => `
            <div class="bg-white shadow rounded-lg overflow-hidden">
                <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
                    <div>
                        <h3 class="text-lg font-medium text-gray-900">${page.name}</h3>
                        <p class="mt-1 text-sm text-gray-500">访问地址: /${page.slug}</p>
                    </div>
                    <div class="flex items-center space-x-4">
                        <button onclick="showAddRegionModal(${page.id})" class="btn btn-secondary">添加区域</button>
                        <button onclick="editPage(${page.id}, '${page.name}')" class="btn btn-secondary">编辑</button>
                        <button onclick="deletePage(${page.id})" class="btn btn-danger">删除</button>
                    </div>
                </div>
                ${page.regions && page.regions.length > 0 ? `
                    <div class="px-4 py-5 sm:p-6 border-t border-gray-200">
                        <h4 class="text-base font-medium text-gray-900 mb-4">区域列表</h4>
                        <div class="space-y-4">
                            ${page.regions.map(region => `
                                <div class="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
                                    <div class="flex-1">
                                        <h5 class="text-sm font-medium text-gray-900">${region.name}</h5>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <button onclick="editRegion(${region.id}, '${region.name}', ${page.id})" class="text-blue-600 hover:text-blue-800">编辑</button>
                                        <button onclick="deleteRegion(${region.id})" class="text-red-600 hover:text-red-900">删除</button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading pages:', error);
        alert('加载页面失败，请重试');
    }
}

async function showAddPageModal() {
    currentPageId = null;
    document.getElementById('page-modal-title').textContent = '添加页面';
    document.getElementById('page-name').value = '';
    document.getElementById('page-modal').classList.remove('hidden');
}

function editPage(id, name) {
    currentPageId = id;
    document.getElementById('page-modal-title').textContent = '编辑页面';
    document.getElementById('page-name').value = name;
    document.getElementById('page-modal').classList.remove('hidden');
}

document.getElementById('page-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('page-name').value;
    
    try {
        const url = currentPageId ? `/api/pages/${currentPageId}` : '/api/pages/';
        const method = currentPageId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name })
        });
        
        if (!response.ok) {
            throw new Error('操作失败');
        }
        
        closeModal('page-modal');
        await loadPages();
    } catch (error) {
        console.error('Error saving page:', error);
        alert('保存失败，请重试');
    }
});

async function deletePage(id) {
    if (!confirm('确定要删除这个页面吗？相关的区域也会被删除。')) {
        return;
    }
    try {
        const response = await fetch(`/api/admin/pages/${id}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            await loadPages();
        } else {
            const error = await response.json();
            alert(error.message || '删除失败');
        }
    } catch (error) {
        console.error('Error deleting page:', error);
        alert('删除失败，请重试');
    }
}

async function loadPagesForSelect() {
    try {
        const response = await fetch('/api/pages');
        if (!response.ok) {
            throw new Error('加载页面失败');
        }
        const pages = await response.json();
        const select = document.getElementById('region-page');
        select.innerHTML = pages.map(page =>
            `<option value="${page.id}">${page.name}</option>`
        ).join('');
    } catch (error) {
        console.error('Error loading pages for select:', error);
        alert('加载页面列表失败，请重试');
    }
}

async function showAddRegionModal(pageId) {
    currentRegionId = null;
    document.getElementById('region-modal-title').textContent = '添加区域';
    document.getElementById('region-name').value = '';
    await loadPagesForSelect();
    if (pageId) {
        document.getElementById('region-page').value = pageId;
    }
    document.getElementById('region-modal').classList.remove('hidden');
}

async function editRegion(id, name, pageId) {
    currentRegionId = id;
    document.getElementById('region-modal-title').textContent = '编辑区域';
    document.getElementById('region-name').value = name;
    await loadPagesForSelect();
    document.getElementById('region-page').value = pageId;
    document.getElementById('region-modal').classList.remove('hidden');
}

document.getElementById('region-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('region-name').value;
    const page_id = document.getElementById('region-page').value;
    try {
        const url = currentRegionId 
            ? `/api/regions/${currentRegionId}`
            : '/api/regions';
        const method = currentRegionId ? 'PUT' : 'POST';
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, page_id }),
        });
        if (response.ok) {
            closeModal('region-modal');
            await loadPages();
        } else {
            const error = await response.json();
            alert(error.message || '操作失败');
        }
    } catch (error) {
        console.error('Error saving region:', error);
        alert('保存失败，请重试');
    }
});

async function deleteRegion(id) {
    if (!confirm('确定要删除这个区域吗？')) {
        return;
    }
    try {
        const response = await fetch(`/api/regions/${id}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            await loadPages();
        } else {
            const error = await response.json();
            alert(error.message || '删除失败');
        }
    } catch (error) {
        console.error('Error deleting region:', error);
        alert('删除失败，请重试');
    }
}

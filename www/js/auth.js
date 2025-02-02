// 检查用户登录状态
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        updateUserSection(data);
    } catch (error) {
        console.error('Error checking auth status:', error);
        updateUserSection({ authenticated: false });
    }
}

// 更新用户状态显示
function updateUserSection(data) {
    const userSection = document.getElementById('userSection');
    if (data.authenticated) {
        userSection.innerHTML = `
            <div class="flex items-center space-x-4">
                <span class="text-gray-700">${data.username}</span>
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

// 退出登录
async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.reload();
    } catch (error) {
        console.error('Error logging out:', error);
    }
}

// 页面加载时检查登录状态
document.addEventListener('DOMContentLoaded', checkAuthStatus); 
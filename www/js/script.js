document.addEventListener('DOMContentLoaded', async () => {
    try {
        // 获取当前页面的 slug
        const slug = window.location.pathname.substring(1) || 'home';
        console.log('当前页面 slug:', slug);
        
        // 先获取页面信息
        console.log('开始获取页面信息...');
        const pageResponse = await fetch(`/api/pages`);
        console.log('页面信息响应状态:', pageResponse.status);
        
        if (!pageResponse.ok) {
            throw new Error(`获取页面信息失败: ${pageResponse.status}, ${pageResponse.statusText}`);
        }
        
        const pages = await pageResponse.json();
        console.log('获取到的页面信息:', pages);
        
        const currentPage = pages.find(p => p.slug === slug);
        if (!currentPage) {
            throw new Error('页面不存在');
        }
        
        // 获取页面的区域
        const app = document.getElementById('app');
        if (!app) {
            throw new Error('找不到app元素');
        }
        
        app.innerHTML = ''; // 清空现有内容
        
        // 遍历页面的区域
        for (const region of currentPage.regions) {
            console.log(`开始处理区域: ${region.name}`);
            
            // 获取分类数据
            console.log('获取分类数据...');
            const categoriesResponse = await fetch(`/api/categories`);
            console.log('分类数据响应状态:', categoriesResponse.status);
            
            if (!categoriesResponse.ok) {
                throw new Error(`获取分类数据失败: ${categoriesResponse.status}, ${categoriesResponse.statusText}`);
            }
            
            const allCategories = await categoriesResponse.json();
            console.log('获取到的所有分类:', allCategories);
            
            const categories = allCategories.filter(c => c.region_id === region.id);
            console.log(`区域 ${region.name} 的分类:`, categories);
            
            const sections = {};
            categories.forEach(category => {
                if (!sections[category.section_name]) {
                    sections[category.section_name] = [];
                }
                sections[category.section_name].push(category);
            });
            
            // 为每个区域创建一个容器
            const regionHtml = `
                <div class="region mb-8">
                    <h2 class="text-2xl font-bold mb-6">${region.name}</h2>
                    ${Object.entries(sections).map(([sectionName, sectionCategories]) => `
                        <div class="section bg-white shadow rounded-lg overflow-hidden mb-6">
                            <div class="px-4 py-5 sm:px-6">
                                <h3 class="text-xl font-semibold text-gray-900">${sectionName}</h3>
                            </div>
                            <div class="border-t border-gray-200">
                                <div class="px-4 py-5 sm:p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                                    ${sectionCategories.map(category => `
                                        <div class="category">
                                            <h4 class="text-lg font-medium text-gray-900 mb-4">${category.title}</h4>
                                            <div class="grid gap-3" id="links-${category.id}">
                                                <!-- 链接将通过 JavaScript 动态加载 -->
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            app.insertAdjacentHTML('beforeend', regionHtml);
            
            // 加载每个分类的链接
            for (const category of categories) {
                try {
                    console.log(`获取分类 ${category.id} 的链接...`);
                    const linksResponse = await fetch(`/api/categories/${category.id}/links`);
                    console.log(`分类 ${category.id} 的链接响应状态:`, linksResponse.status);
                    
                    if (!linksResponse.ok) {
                        throw new Error(`获取链接失败: ${linksResponse.status}, ${linksResponse.statusText}`);
                    }
                    
                    const links = await linksResponse.json();
                    console.log(`分类 ${category.id} 的链接数据:`, links);
                    
                    const linksContainer = document.getElementById(`links-${category.id}`);
                    if (linksContainer) {
                        linksContainer.innerHTML = links.map(link => `
                            <a href="${link.url}" 
                               target="_blank" 
                               rel="noopener noreferrer"
                               class="flex items-center p-3 text-base font-medium text-gray-900 rounded-lg bg-gray-50 hover:bg-gray-100 group hover:shadow">
                                <span class="flex-1 ml-3 whitespace-nowrap">${link.name}</span>
                                <span class="inline-flex items-center justify-center px-2 py-0.5 ml-3 text-xs font-medium text-gray-500 bg-gray-200 rounded">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                    </svg>
                                </span>
                            </a>
                        `).join('');
                    }
                } catch (error) {
                    console.error(`Error loading links for category ${category.id}:`, error);
                    const linksContainer = document.getElementById(`links-${category.id}`);
                    if (linksContainer) {
                        linksContainer.innerHTML = `
                            <div class="error">
                                <p>加载链接失败: ${error.message}</p>
                                <p>请刷新页面重试</p>
                            </div>
                        `;
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error loading data:', error);
        const errorMessage = error.message || '未知错误';
        document.getElementById('app').innerHTML = `
            <div class="error">
                <p>加载数据时出错：${errorMessage}</p>
                <p>请检查网络连接并刷新页面重试。如果问题持续存在，请联系管理员。</p>
                <p>错误详情：${error.stack || error}</p>
            </div>
        `;
    }
}); 
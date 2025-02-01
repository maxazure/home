document.addEventListener('DOMContentLoaded', async () => {
    try {
        // 获取所有分类
        const response = await fetch('/api/categories');
        const categories = await response.json();
        
        // 按 section_name 分组
        const sections = {};
        categories.forEach(category => {
            if (!sections[category.section_name]) {
                sections[category.section_name] = [];
            }
            sections[category.section_name].push(category);
        });
        
        // 生成 HTML
        const app = document.getElementById('app');
        for (const [sectionName, categories] of Object.entries(sections)) {
            const sectionHtml = `
                <div class="section">
                    <h2 class="section-title">${sectionName}</h2>
                    <div class="categories">
                        ${await Promise.all(categories.map(async category => {
                            // 获取该分类下的所有链接
                            const linksResponse = await fetch(`/api/categories/${category.id}/links`);
                            const links = await linksResponse.json();
                            
                            return `
                                <div class="category">
                                    <h3 class="category-title">${category.title}</h3>
                                    <div class="links-grid">
                                        ${links.map(link => `
                                            <div class="link-item">
                                                <a href="${link.url}" target="_blank" rel="noopener noreferrer">
                                                    ${link.name}
                                                </a>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            `;
                        })).then(categoriesHtml => categoriesHtml.join(''))}
                    </div>
                </div>
            `;
            app.insertAdjacentHTML('beforeend', sectionHtml);
        }
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('app').innerHTML = `
            <div class="error">
                加载数据时出错。请刷新页面重试。
            </div>
        `;
    }
}); 
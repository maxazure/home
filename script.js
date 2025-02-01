$(document).ready(function() {
    $.ajax({
        url: 'link.json', // 确认您的JSON文件的正确路径
        type: "GET",
        dataType: "json",
        success: function(data) {
            $.each(data, function(index, section) {
                var sectionDiv = $('<div/>', { 'class': 'section my-4' });
                var sectionTitle = $('<h2/>', { 'class': 'section-title text-center mb-3', text: section.sectionName });
                sectionDiv.append(sectionTitle);

                // 遍历行
                $.each(section.rows, function(index, row) {
                    var rowDiv = $('<div/>', { 'class': 'row' });

                    // 遍历列
                    $.each(row.columns, function(index, column) {
                        var columnDiv = $('<div/>', { 'class': 'col-md-4' });
                        var columnContentDiv = $('<div/>', { 'class': 'p-3 border bg-light' });
                        var columnTitle = $('<h3/>', { text: column.title, 'class': 'column-title' });
                        columnContentDiv.append(columnTitle);
                        var columnList = $('<ul/>', { 'class': 'list-unstyled' });

                        // 遍历链接
                        $.each(column.links, function(index, link) {
                            var listItem = $('<li/>');
                            var anchor = $('<a/>', { href: link.url, text: link.name, target: '_blank' });
                            if (link.url === "" || link.url === "#") {
                                // 如果是，就创建一个文本节点
                                listItem.text(link.name);
                              }else{
                                listItem.append(anchor);
                              }
                            
                            columnList.append(listItem);
                        });

                        columnContentDiv.append(columnList);
                        columnDiv.append(columnContentDiv);
                        rowDiv.append(columnDiv);
                    });

                    sectionDiv.append(rowDiv);
                });

                $('#content').append(sectionDiv);
            });
        },
        error: function(error) {
            console.error('加载数据时出错:', error);
        }
    });
});

$(document).ready(function(){
    // 由于 Google 搜索框的加载可能会延迟，我们使用定时器确保更改能够应用
    var checkExist = setInterval(function() {
       var searchText = $('input[type="text"]'); 
       if (searchText.length) {
           searchText.attr('placeholder', 'Google Search...');
          clearInterval(checkExist);
       }
    }, 1000); // 检查每 100 毫秒
});


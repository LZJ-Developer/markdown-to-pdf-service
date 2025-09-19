/**
 * 动态表格布局系统 - 智能列宽分配算法
 * 基于内容分析的自适应表格布局解决方案
 * 
 * @author ZJL
 * @version 1.0.0
 * @description 为科研报告表格提供智能的动态列宽分配，支持任意列数的自适应布局
 */

class DynamicTableLayout {
    /**
     * 构造函数
     * @param {Object} options - 配置选项
     * @param {number} options.minColumnWidth - 最小列宽（px）
     * @param {number} options.maxColumnWidth - 最大列宽（px）
     * @param {number} options.containerPadding - 容器内边距（px）
     * @param {boolean} options.enableResponsive - 是否启用响应式
     */
    constructor(options = {}) {
        this.config = {
            minColumnWidth: options.minColumnWidth || 80,
            maxColumnWidth: options.maxColumnWidth || 400,
            containerPadding: options.containerPadding || 20,
            enableResponsive: options.enableResponsive !== false,
            // 列类型权重配置
            columnTypeWeights: {
                identifier: 1.2,    // 标识符列（如基因名）
                numeric: 0.8,       // 数值列
                description: 2.0,   // 描述列
                filename: 1.5,      // 文件名列
                default: 1.0        // 默认权重
            }
        };
        
        this.tables = new Map(); // 存储表格分析结果
        this.resizeObserver = null;
        this.init();
    }

    /**
     * 初始化动态布局系统
     */
    init() {
        // 等待DOM加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.processAllTables());
        } else {
            this.processAllTables();
        }

        // 设置响应式监听
        if (this.config.enableResponsive) {
            this.setupResponsiveHandling();
        }
    }

    /**
     * 处理页面中的所有表格
     */
    processAllTables() {
        const tables = document.querySelectorAll('table');
        tables.forEach((table, index) => {
            this.processTable(table, `table-${index}`);
        });
    }

    /**
     * 处理单个表格
     * @param {HTMLTableElement} table - 表格元素
     * @param {string} tableId - 表格唯一标识
     */
    processTable(table, tableId) {
        try {
            // 分析表格结构和内容
            const analysis = this.analyzeTable(table);
            
            // 计算最优列宽
            const columnWidths = this.calculateOptimalWidths(analysis);
            
            // 应用动态样式
            this.applyDynamicStyles(table, columnWidths, tableId);
            
            // 存储分析结果
            this.tables.set(tableId, {
                table,
                analysis,
                columnWidths,
                lastUpdate: Date.now()
            });

            console.log(`[DynamicTableLayout] 已处理表格 ${tableId}:`, {
                columns: analysis.columnCount,
                widths: columnWidths
            });

        } catch (error) {
            console.error(`[DynamicTableLayout] 处理表格 ${tableId} 时出错:`, error);
        }
    }

    /**
     * 分析表格结构和内容
     * @param {HTMLTableElement} table - 表格元素
     * @returns {Object} 分析结果
     */
    analyzeTable(table) {
        const rows = Array.from(table.rows);
        if (rows.length === 0) {
            throw new Error('表格为空');
        }

        const headerRow = rows[0];
        const columnCount = headerRow.cells.length;
        const columns = [];

        // 分析每一列
        for (let colIndex = 0; colIndex < columnCount; colIndex++) {
            const columnData = this.analyzeColumn(table, colIndex);
            columns.push(columnData);
        }

        return {
            columnCount,
            columns,
            rowCount: rows.length,
            tableWidth: table.offsetWidth || table.parentElement.offsetWidth,
            containerWidth: this.getContainerWidth(table)
        };
    }

    /**
     * 分析单列数据
     * @param {HTMLTableElement} table - 表格元素
     * @param {number} colIndex - 列索引
     * @returns {Object} 列分析结果
     */
    analyzeColumn(table, colIndex) {
        const rows = Array.from(table.rows);
        const cells = rows.map(row => row.cells[colIndex]).filter(cell => cell);
        
        if (cells.length === 0) {
            return this.getDefaultColumnData(colIndex);
        }

        // 获取列标题
        const header = cells[0];
        const headerText = header.textContent.trim();

        // 分析内容类型和长度
        const contentAnalysis = this.analyzeColumnContent(cells.slice(1));
        
        // 确定列类型
        const columnType = this.determineColumnType(headerText, contentAnalysis);
        
        // 计算内容宽度需求
        const contentWidth = this.calculateContentWidth(cells);

        return {
            index: colIndex,
            header: headerText,
            type: columnType,
            contentWidth,
            cellCount: cells.length,
            ...contentAnalysis
        };
    }

    /**
     * 分析列内容特征
     * @param {HTMLTableCellElement[]} cells - 单元格数组
     * @returns {Object} 内容分析结果
     */
    analyzeColumnContent(cells) {
        let numericCount = 0;
        let textCount = 0;
        let maxLength = 0;
        let avgLength = 0;
        let totalLength = 0;

        cells.forEach(cell => {
            const text = cell.textContent.trim();
            const length = text.length;
            
            totalLength += length;
            maxLength = Math.max(maxLength, length);
            
            // 检测数值类型
            if (this.isNumeric(text)) {
                numericCount++;
            } else {
                textCount++;
            }
        });

        avgLength = cells.length > 0 ? totalLength / cells.length : 0;

        return {
            numericCount,
            textCount,
            maxLength,
            avgLength,
            isNumericColumn: numericCount > textCount,
            hasLongContent: maxLength > 50
        };
    }

    /**
     * 确定列类型
     * @param {string} headerText - 列标题
     * @param {Object} contentAnalysis - 内容分析结果
     * @returns {string} 列类型
     */
    determineColumnType(headerText, contentAnalysis) {
        const header = headerText.toLowerCase();
        
        // 基于标题关键词判断
        if (header.includes('gene') || header.includes('id') || header.includes('symbol')) {
            return 'identifier';
        }
        if (header.includes('count') || header.includes('value') || header.includes('p-value') || 
            header.includes('fold') || contentAnalysis.isNumericColumn) {
            return 'numeric';
        }
        if (header.includes('description') || header.includes('annotation') || 
            contentAnalysis.hasLongContent) {
            return 'description';
        }
        if (header.includes('file') || header.includes('path')) {
            return 'filename';
        }
        
        return 'default';
    }

    /**
     * 计算内容宽度需求
     * @param {HTMLTableCellElement[]} cells - 单元格数组
     * @returns {number} 内容宽度（px）
     */
    calculateContentWidth(cells) {
        let maxWidth = 0;
        
        // 创建临时测量元素
        const measurer = this.createMeasuringElement();
        document.body.appendChild(measurer);
        
        try {
            cells.forEach(cell => {
                // 复制单元格样式
                const computedStyle = window.getComputedStyle(cell);
                measurer.style.font = computedStyle.font;
                measurer.style.fontFamily = computedStyle.fontFamily;
                measurer.style.fontSize = computedStyle.fontSize;
                measurer.style.fontWeight = computedStyle.fontWeight;
                
                // 测量文本宽度
                measurer.textContent = cell.textContent;
                const width = measurer.offsetWidth;
                maxWidth = Math.max(maxWidth, width);
            });
        } finally {
            document.body.removeChild(measurer);
        }
        
        // 添加内边距
        return maxWidth + 40; // 20px左右内边距
    }

    /**
     * 创建测量元素
     * @returns {HTMLElement} 测量元素
     */
    createMeasuringElement() {
        const element = document.createElement('div');
        element.style.cssText = `
            position: absolute;
            visibility: hidden;
            height: auto;
            width: auto;
            white-space: nowrap;
            top: -9999px;
            left: -9999px;
        `;
        return element;
    }

    /**
     * 计算最优列宽分配
     * @param {Object} analysis - 表格分析结果
     * @returns {number[]} 列宽数组
     */
    calculateOptimalWidths(analysis) {
        const { columns, containerWidth } = analysis;
        const availableWidth = containerWidth - this.config.containerPadding;
        
        // 第一步：基于内容计算理想宽度
        const idealWidths = columns.map(col => {
            const baseWidth = Math.max(col.contentWidth, this.config.minColumnWidth);
            const weight = this.config.columnTypeWeights[col.type] || this.config.columnTypeWeights.default;
            return Math.min(baseWidth * weight, this.config.maxColumnWidth);
        });
        
        const totalIdealWidth = idealWidths.reduce((sum, width) => sum + width, 0);
        
        // 第二步：如果总宽度超出容器，按比例缩放
        if (totalIdealWidth > availableWidth) {
            const scaleFactor = availableWidth / totalIdealWidth;
            return idealWidths.map(width => {
                const scaledWidth = width * scaleFactor;
                return Math.max(scaledWidth, this.config.minColumnWidth);
            });
        }
        
        // 第三步：如果有剩余空间，智能分配
        const remainingWidth = availableWidth - totalIdealWidth;
        if (remainingWidth > 0) {
            return this.distributeRemainingWidth(idealWidths, remainingWidth, columns);
        }
        
        return idealWidths;
    }

    /**
     * 分配剩余宽度
     * @param {number[]} widths - 当前宽度数组
     * @param {number} remainingWidth - 剩余宽度
     * @param {Object[]} columns - 列信息数组
     * @returns {number[]} 调整后的宽度数组
     */
    distributeRemainingWidth(widths, remainingWidth, columns) {
        const result = [...widths];
        
        // 优先给描述类列分配更多空间
        const expandableColumns = columns
            .map((col, index) => ({ index, type: col.type, hasLongContent: col.hasLongContent }))
            .filter(col => col.type === 'description' || col.hasLongContent)
            .sort((a, b) => {
                // 描述列优先级最高
                if (a.type === 'description' && b.type !== 'description') return -1;
                if (a.type !== 'description' && b.type === 'description') return 1;
                return 0;
            });
        
        if (expandableColumns.length > 0) {
            const extraPerColumn = remainingWidth / expandableColumns.length;
            expandableColumns.forEach(col => {
                result[col.index] += extraPerColumn;
            });
        } else {
            // 如果没有可扩展列，平均分配
            const extraPerColumn = remainingWidth / result.length;
            result.forEach((width, index) => {
                result[index] = width + extraPerColumn;
            });
        }
        
        return result;
    }

    /**
     * 应用动态样式
     * @param {HTMLTableElement} table - 表格元素
     * @param {number[]} columnWidths - 列宽数组
     * @param {string} tableId - 表格ID
     */
    applyDynamicStyles(table, columnWidths, tableId) {
        // 创建或更新样式表
        let styleSheet = document.getElementById(`dynamic-table-${tableId}`);
        if (!styleSheet) {
            styleSheet = document.createElement('style');
            styleSheet.id = `dynamic-table-${tableId}`;
            document.head.appendChild(styleSheet);
        }
        
        // 生成CSS规则
        const cssRules = this.generateCSSRules(table, columnWidths, tableId);
        styleSheet.textContent = cssRules;
        
        // 添加表格类名
        table.classList.add('dynamic-layout');
        table.setAttribute('data-table-id', tableId);
    }

    /**
     * 生成CSS规则
     * @param {HTMLTableElement} table - 表格元素
     * @param {number[]} columnWidths - 列宽数组
     * @param {string} tableId - 表格ID
     * @returns {string} CSS规则字符串
     */
    generateCSSRules(table, columnWidths, tableId) {
        const selector = `table[data-table-id="${tableId}"]`;
        
        let css = `
/* 动态表格布局 - ${tableId} */
${selector} {
    table-layout: fixed !important;
    width: 100% !important;
    border-collapse: collapse !important;
}

${selector} .table-container {
    overflow-x: auto;
    border-radius: 4px;
    border: 1px solid #dee2e6;
}
`;
        
        // 为每列生成宽度规则
        columnWidths.forEach((width, index) => {
            const percentage = (width / columnWidths.reduce((sum, w) => sum + w, 0) * 100).toFixed(2);
            css += `
${selector} th:nth-child(${index + 1}),
${selector} td:nth-child(${index + 1}) {
    width: ${percentage}% !important;
    min-width: ${Math.max(width, this.config.minColumnWidth)}px !important;
    max-width: ${Math.min(width, this.config.maxColumnWidth)}px !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
`;
        });
        
        return css;
    }

    /**
     * 获取容器宽度
     * @param {HTMLTableElement} table - 表格元素
     * @returns {number} 容器宽度
     */
    getContainerWidth(table) {
        const container = table.closest('.table-container') || table.parentElement;
        return container.offsetWidth || window.innerWidth - 40;
    }

    /**
     * 设置响应式处理
     */
    setupResponsiveHandling() {
        // 监听窗口大小变化
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });

        // 使用ResizeObserver监听容器变化
        if (window.ResizeObserver) {
            this.resizeObserver = new ResizeObserver(entries => {
                entries.forEach(entry => {
                    const table = entry.target.querySelector('table[data-table-id]');
                    if (table) {
                        const tableId = table.getAttribute('data-table-id');
                        this.updateTableLayout(tableId);
                    }
                });
            });
        }
    }

    /**
     * 处理窗口大小变化
     */
    handleResize() {
        this.tables.forEach((data, tableId) => {
            this.updateTableLayout(tableId);
        });
    }

    /**
     * 更新表格布局
     * @param {string} tableId - 表格ID
     */
    updateTableLayout(tableId) {
        const tableData = this.tables.get(tableId);
        if (!tableData) return;

        try {
            // 重新分析容器宽度
            const newAnalysis = {
                ...tableData.analysis,
                containerWidth: this.getContainerWidth(tableData.table)
            };

            // 重新计算列宽
            const newColumnWidths = this.calculateOptimalWidths(newAnalysis);

            // 应用新样式
            this.applyDynamicStyles(tableData.table, newColumnWidths, tableId);

            // 更新存储的数据
            this.tables.set(tableId, {
                ...tableData,
                analysis: newAnalysis,
                columnWidths: newColumnWidths,
                lastUpdate: Date.now()
            });

        } catch (error) {
            console.error(`[DynamicTableLayout] 更新表格 ${tableId} 布局时出错:`, error);
        }
    }

    /**
     * 检查是否为数值
     * @param {string} text - 文本内容
     * @returns {boolean} 是否为数值
     */
    isNumeric(text) {
        if (!text || text.trim() === '') return false;
        
        // 科学记数法
        if (/^-?\d+\.?\d*[eE][+-]?\d+$/.test(text)) return true;
        
        // 普通数字（包括小数）
        if (/^-?\d+\.?\d*$/.test(text)) return true;
        
        // p值格式
        if (/^p\s*[<>=]\s*\d+\.?\d*([eE][+-]?\d+)?$/i.test(text)) return true;
        
        return false;
    }

    /**
     * 获取默认列数据
     * @param {number} colIndex - 列索引
     * @returns {Object} 默认列数据
     */
    getDefaultColumnData(colIndex) {
        return {
            index: colIndex,
            header: `Column ${colIndex + 1}`,
            type: 'default',
            contentWidth: this.config.minColumnWidth,
            cellCount: 0,
            numericCount: 0,
            textCount: 0,
            maxLength: 0,
            avgLength: 0,
            isNumericColumn: false,
            hasLongContent: false
        };
    }

    /**
     * 销毁实例，清理资源
     */
    destroy() {
        // 移除样式表
        this.tables.forEach((data, tableId) => {
            const styleSheet = document.getElementById(`dynamic-table-${tableId}`);
            if (styleSheet) {
                styleSheet.remove();
            }
        });

        // 清理ResizeObserver
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }

        // 清理数据
        this.tables.clear();
    }
}

// 自动初始化
window.DynamicTableLayout = DynamicTableLayout;

// 页面加载完成后自动启动
document.addEventListener('DOMContentLoaded', () => {
    window.dynamicTableLayout = new DynamicTableLayout({
        minColumnWidth: 80,
        maxColumnWidth: 400,
        enableResponsive: true
    });
});

// 导出模块（如果支持）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DynamicTableLayout;
}
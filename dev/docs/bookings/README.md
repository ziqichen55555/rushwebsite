# Bookings 模块文档中心

## 文档概述

本目录包含 Rush Car Rental 系统 Bookings 模块的详细技术文档，涵盖业务流程、支付集成和实现分析等方面。这些文档旨在帮助开发者、维护人员和项目利益相关者更好地理解系统的架构、流程和技术实现。

## 文档索引

### 业务流程文档

- [Bookings 模块业务流程](booking_flow.md) - 详细介绍预订模块的业务流程、状态转换和数据流

### 技术实现文档

- [支付集成技术文档](payment_integration.md) - 支付系统的技术细节、集成方式和API参考
- [支付处理模块实现分析](payment_implementation.md) - 支付处理模块的代码分析、数据流和优化建议

## 图表可视化

本文档使用 Mermaid 语法创建可视化图表。在支持 Mermaid 的 Markdown 查看器中（如 GitHub、VS Code+插件等），这些图表会自动渲染。如果您的查看器不支持 Mermaid，可以使用以下工具：

1. [Mermaid Live Editor](https://mermaid.live/) - 复制 \`\`\`mermaid 代码块中的内容到此编辑器
2. 安装支持 Mermaid 的 Markdown 预览插件
3. 使用 mermaid-cli 工具将图表导出为图片

## 文档更新指南

更新这些文档时，请遵循以下原则：

1. 保持文档与代码同步
2. 使用清晰、简洁的语言
3. 使用 Mermaid 图表说明复杂概念
4. 添加实际代码示例
5. 定期审查并更新过时内容

## 相关技术文档

- [数据库设计文档](../database_design.md)
- [Stripe 集成文档](../stripe_integration.md)
- [数据库迁移指南](../database_migration_guide.md)

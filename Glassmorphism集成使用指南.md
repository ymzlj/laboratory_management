# 玻璃拟态（Glassmorphism）UI 集成与使用指南

## 引入与启用
- 已在全局模板 [base.html](file:///d:/laboratory_management/templates/base.html) 引入：
  - 样式文件：[tokens.css](file:///d:/laboratory_management/static/css/tokens.css)，[glass.css](file:///d:/laboratory_management/static/css/glass.css)
  - 启用方式：`<body class="glass-theme">`（已配置）
  - 背景容器：`.main-content` 已应用 `bg-glass-light`（暗黑自动适配）

## 组件覆盖（无侵入）
- 卡片：现有 `.card` 自动应用玻璃风格（作用域：`.glass-theme`）
- 按钮：现有 `.btn` 自动应用玻璃风格
- 输入框：现有 `.form-control` 自动应用玻璃风格

## 布局与分层
- 建议将页面主体包裹在背景容器：
  ```html
  <div class="bg-glass-light dark:bg-glass-dark">
    <!-- 内容 -->
  </div>
  ```
- 栅格建议：使用现有 Bootstrap 栅格或自定义 `grid-cards`（可选）

## 暗黑与响应式
- 自动暗黑：跟随 `prefers-color-scheme` 切换（CSS 变量）
- 响应式模糊强度：桌面 16px / 平板 12px / 手机 8px

## 兼容性与降级
- 支持 `backdrop-filter` 的浏览器启用毛玻璃
- 不支持时：会自动使用渐变+边框高光+阴影进行优雅降级
- 高对比模式：使用系统色（Canvas/CanvasText）确保可访问性
- 减少动效：遵循 `prefers-reduced-motion`

## 无障碍（WCAG 2.1 AA）
- 文本对比：≥ 4.5:1（已通过变量与暗色文本控制）
- 键盘焦点：保持按钮与输入框默认 focus outline
- 颜色不唯一：建议配合图标与文案提示

## 性能建议
- 尽量减少页面内 `backdrop-filter` 图层数量（卡片级别）
- 移动端降低 blur 半径；避免大面积模糊覆盖
- 大背景建议使用静态模糊图（由服务端预处理）

## FAQ
- Q：样式未生效？
  - A：确认 `<body class="glass-theme">` 存在且 tokens/glass 样式已加载
- Q：浏览器不支持毛玻璃？
  - A：已自动降级为高质量非模糊玻璃风格，无需额外操作

## 验收标准
- Lighthouse Accessibility/Best Practices ≥ 90
- Chrome/Safari/Edge/Firefox 手工检查通过
- 移动端 375/768/1024/1440 断点无体验问题

---
交付物：CSS（tokens/glass）、集成完成的模板、兼容与无障碍保障、性能与布局建议。已具备生产上线条件。

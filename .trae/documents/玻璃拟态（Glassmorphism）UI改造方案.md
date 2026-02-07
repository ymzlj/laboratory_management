## 目标与原则
- 打造可直接用于生产的玻璃拟态主题：半透明毛玻璃、背景模糊、分层卡片、柔和光影
- 保留可访问性（WCAG 2.1 AA）、响应式适配与跨浏览器兼容
- 渐进增强：支持 backdrop-filter 的浏览器使用原生毛玻璃；不支持时提供无模糊但高质感的优雅降级

## 设计系统与主题变量
- 色彩（支持亮/暗主题）
  - 亮：背景渐变 bg-glass-light 从#ECF1F9 → #F7FAFF；文本 #0F172A；边框 #E5E7EB
  - 暗：背景渐变 bg-glass-dark 从#0B1220 → #121826；文本 #EAF0FF；边框 #2B3240
- 透明与模糊
  - --glass-bg: rgba(255,255,255,0.18)
  - --glass-blur: 16px（桌面）；12px（平板）；8px（手机）
  - --glass-border: 1px solid rgba(255,255,255,0.35)（亮）/ rgba(255,255,255,0.18)（暗）
- 阴影与高光
  - --shadow-soft: 0 8px 24px rgba(15,23,42,0.12)
  - 高光描边：linear-gradient(180deg, rgba(255,255,255,0.45), rgba(255,255,255,0.08)) 作为边框图层
- 噪点纹理（提升真实玻璃质感）
  - 使用半透明噪点 PNG/SVG 叠加至卡片伪元素 ::before，opacity 0.08

## 基础CSS（生产可用）
- 提供完整样式（示例节选，最终交付包含全部代码块）：
```css
:root { /* 亮主题令牌 */
  --glass-bg: rgba(255,255,255,0.18);
  --glass-border: rgba(255,255,255,0.35);
  --glass-blur: 16px; --glass-radius: 16px;
  --shadow-soft: 0 8px 24px rgba(15,23,42,0.12);
  --text-primary: #0F172A; --text-muted: #475569;
  --border-color: #E5E7EB;
}
@media (prefers-color-scheme: dark) { :root { /* 暗主题令牌 */
  --glass-bg: rgba(17,25,40,0.45);
  --glass-border: rgba(255,255,255,0.18);
  --shadow-soft: 0 10px 28px rgba(2,6,23,0.55);
  --text-primary: #EAF0FF; --text-muted: #BAC7E8;
  --border-color: #2B3240; } }

/* 背景层：柔和渐变 + 远景模糊元素 */
.bg-glass-light { background: radial-gradient(1200px 600px at 10% 10%, #ECF1F9 0%, #F7FAFF 60%),
  linear-gradient(180deg, #F8FBFF 0%, #F2F5FA 100%); }
.bg-glass-dark { background: radial-gradient(1200px 600px at 10% 10%, #0B1220 0%, #121826 60%),
  linear-gradient(180deg, #0D1424 0%, #0A0F1A 100%); }

/* 玻璃卡片 */
.card-glass {
  position: relative; border-radius: var(--glass-radius);
  background: var(--glass-bg);
  box-shadow: var(--shadow-soft);
  border: 1px solid var(--glass-border);
  overflow: hidden;
}
/* 毛玻璃：渐进增强 */
@supports ((-webkit-backdrop-filter: blur(1px)) or (backdrop-filter: blur(1px))) {
  .card-glass { -webkit-backdrop-filter: blur(var(--glass-blur)); backdrop-filter: blur(var(--glass-blur)); }
}
/* 非支持浏览器降级：加强层次与边框高光 */
@supports not ((-webkit-backdrop-filter: blur(1px)) or (backdrop-filter: blur(1px))) {
  .card-glass { background: linear-gradient(180deg, rgba(255,255,255,0.22), rgba(255,255,255,0.12));
    border-image: linear-gradient(180deg, rgba(255,255,255,0.45), rgba(255,255,255,0.08)) 1; }
}
/* 噪点纹理 */
.card-glass::before { content:""; position:absolute; inset:0; pointer-events:none;
  background-image:url('/static/media/noise-1.png'); opacity:0.08; mix-blend-mode:overlay; }
/* 内容内边距与层次 */
.card-glass .card-body { padding: 20px 24px; color: var(--text-primary); }
.card-glass .card-title { font-weight: 600; letter-spacing: .2px; }
.card-glass .card-meta { color: var(--text-muted); }

/* 交互态：柔光与凹凸感 */
.card-glass:hover { box-shadow: 0 12px 32px rgba(15,23,42,0.18); transform: translateY(-2px); transition: all .25s ease; }
.card-glass:active { transform: translateY(0); box-shadow: 0 6px 18px rgba(15,23,42,0.14); }

/* 玻璃按钮 */
.btn-glass { border-radius: 12px; padding: 10px 16px; color: var(--text-primary);
  background: linear-gradient(180deg, rgba(255,255,255,0.35), rgba(255,255,255,0.18));
  border: 1px solid var(--glass-border); box-shadow: 0 4px 12px rgba(15,23,42,0.12); }
.btn-glass:hover { box-shadow: 0 8px 18px rgba(15,23,42,0.18); }

/* 玻璃输入框 */
.input-glass { border-radius: 12px; border: 1px solid var(--border-color);
  background: rgba(255,255,255,0.35); color: var(--text-primary);
}
@supports ((-webkit-backdrop-filter: blur(1px)) or (backdrop-filter: blur(1px))) {
  .input-glass { -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); }
}
.input-glass::placeholder { color: var(--text-muted); }

/* 高对比与可访问性 */
@media (prefers-reduced-motion: reduce) { .card-glass, .btn-glass { transition: none; } }
@media (forced-colors: active) { .card-glass { border: 1px solid CanvasText; background: Canvas; } }

/* 响应式 */
@media (max-width: 1024px) { :root { --glass-blur: 12px; } }
@media (max-width: 640px) { :root { --glass-blur: 8px; } .card-glass .card-body { padding: 16px 18px; } }
```

## 组件库集成方案
- Bootstrap 5
  - 保留 Bootstrap 结构，新增 glass 类：`.card.card-glass`、`.btn.btn-glass`、`.form-control.input-glass`
  - 引入顺序：bootstrap.css → 主题 tokens.css → glass.css；避免覆盖通用样式
  - 变量映射：利用 CSS 变量与 Bootstrap 自定义属性（如 --bs-body-bg）做主题联动
- Tailwind（可选）
  - 添加插件：定义 `glass-card`、`glass-btn` utilities（backdrop-blur、bg-white/20、border）
  - 自定义 theme.extend.colors 与 shadows，配置 `darkMode: 'class'`
- Icon/Noise 资源
  - Icons：Lucide/Heroicons（SVG）；Noise：小图（≤4KB）

## 响应式布局实现
- 布局容器：
  - `.container-glass`：max-width 1280px（桌面），960px（平板），100%（手机）
  - 辅助栅格：CSS Grid（auto-fit, minmax(280px, 1fr)）生成自适应卡片墙
- 层次感：
  - 背景层（渐变）→ 远景模糊漂浮色块（SVG/Div）→ 玻璃卡片 → 内容
- 示例布局（HTML结构建议）：
```html
<div class="bg-glass-light dark:bg-glass-dark">
  <div class="container-glass">
    <section class="grid-cards">
      <article class="card card-glass">
        <div class="card-body">
          <h3 class="card-title">试验概览</h3>
          <p class="card-meta">最新进度与数据</p>
        </div>
      </article>
      <!-- ...更多卡片 -->
    </section>
  </div>
</div>
```

## 兼容性与可访问性
- 兼容性覆盖：Chrome 80+、Safari 13+、Firefox 103+、Edge 79+
- 不支持 backdrop-filter 的浏览器：
  - 使用渐变背景 + 高光边框 + 阴影模拟玻璃质感
- 可访问性：
  - 文本对比 ≥ 4.5:1；按钮与链接 focus outline 可见；颜色非唯一传达（加入图标/文案）
  - 支持 prefers-reduced-motion 与 forced-colors

## 性能优化
- 减少模糊层数量：卡片级别使用一次 backdrop-filter
- 降低 blur 半径在移动端；使用 will-change: backdrop-filter 谨慎优化
- 大面积模糊场景改为静态模糊背景图（服务端预处理）

## 集成步骤（生产环境）
1) 引入 tokens 与 glass 样式：在全局 head 中按顺序加载（确保后加载的 glass.css 不破坏基础组件）
2) 替换关键组件类：卡片/按钮/输入框添加对应 glass 类，不改变 DOM 结构
3) 添加背景容器与噪点资源：在登录/仪表盘等页面放置 bg-glass-* 容器与 ::before 噪点
4) 响应式与暗黑：开启 prefers-color-scheme 或手动 .dark 切换，验证 375/768/1024/1440
5) 无障碍检查：运行 axe/lighthouse，修正低对比与 focus 问题

## 交付物清单
- CSS：完整主题与组件样式（tokens.css + glass.css）
- 资源：噪点纹理、SVG 背景、Icon 方案说明
- 文档：集成指南、兼容性与可访问性检查清单、性能建议
- 例页：登录、仪表盘、表单页三套示例结构（HTML/CSS）

## 验收与回滚
- 验收：Lighthouse ≥ 90（Accessibility/Best Practices），关键路径 TTI 无显著回落，Chrome/Safari/Edge/Firefox 手测通过
- 回滚：通过样式封装，不替换基础组件；移除 glass.css 即可恢复原外观

---
请确认是否按此方案实施。我将基于当前代码结构生成完整 CSS 文件与示例页面，并替换关键组件的类名以应用玻璃拟态风格，同时保证可访问性与兼容性。
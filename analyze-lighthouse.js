const fs = require('fs');
const path = require('path');

// 读取Lighthouse报告文件
const reportPath = path.join(__dirname, 'lighthouse-report-optimized.html');
const reportContent = fs.readFileSync(reportPath, 'utf8');

// 提取JSON数据
const jsonMatch = reportContent.match(/window\.__LIGHTHOUSE_JSON__ = (.*?);<\/script>/);
if (!jsonMatch) {
  console.error('无法从报告中提取JSON数据');
  process.exit(1);
}

const lighthouseData = JSON.parse(jsonMatch[1]);

// 提取关键性能指标
const performanceMetrics = lighthouseData.audits.metrics.details.items[0];

console.log('=== 性能报告分析 ===\n');

// 总体性能分数
console.log('1. 总体性能分数：');
console.log(`   - 性能: ${Math.round(lighthouseData.categories.performance.score * 100)}/100`);
console.log(`   - 可访问性: ${Math.round(lighthouseData.categories.accessibility.score * 100)}/100`);
console.log(`   - 最佳实践: ${Math.round(lighthouseData.categories['best-practices'].score * 100)}/100`);
console.log(`   - SEO: ${Math.round(lighthouseData.categories.seo.score * 100)}/100`);
if (lighthouseData.categories.pwa) {
  console.log(`   - PWA: ${Math.round(lighthouseData.categories.pwa.score * 100)}/100\n`);
} else {
  console.log('   - PWA: 不可用\n');
}

// 核心Web指标
console.log('2. 核心Web指标：');
console.log(`   - FCP (首次内容绘制): ${performanceMetrics.fcp} ms`);
console.log(`   - LCP (最大内容绘制): ${performanceMetrics.lcp} ms`);
console.log(`   - TTI (可交互时间): ${performanceMetrics.tti} ms`);
console.log(`   - TBT (总阻塞时间): ${performanceMetrics.tbt} ms`);
console.log(`   - CLS (累积布局偏移): ${performanceMetrics.cls}\n`);

// 资源统计
console.log('3. 资源统计：');
const resourceSummary = lighthouseData.audits['resource-summary'].details.items;
resourceSummary.forEach(resource => {
  console.log(`   - ${resource.resourceType}: ${resource.requestCount} 个请求，${Math.round(resource.size / 1024)} KB`);
});

// 渲染阻塞资源
console.log('\n4. 渲染阻塞资源：');
const renderBlockingResources = lighthouseData.audits['render-blocking-resources']?.details?.items || [];
if (renderBlockingResources.length > 0) {
  renderBlockingResources.forEach(resource => {
    console.log(`   - ${resource.url}: ${Math.round(resource.size / 1024)} KB，阻塞时间 ${resource.wastedMs} ms`);
  });
} else {
  console.log('   - 无渲染阻塞资源');
}

// 未使用的CSS
console.log('\n5. 未使用的CSS：');
const unusedCss = lighthouseData.audits['unused-css-rules']?.details;
if (unusedCss) {
  console.log(`   - 总CSS大小: ${Math.round(unusedCss.totalKb / 1024)} KB`);
  console.log(`   - 未使用CSS大小: ${Math.round(unusedCss.unusedKb / 1024)} KB (${Math.round(unusedCss.unusedPercent)}%)`);
} else {
  console.log('   - 无未使用CSS数据');
}

// 未使用的JavaScript
console.log('\n6. 未使用的JavaScript：');
const unusedJs = lighthouseData.audits['unused-javascript']?.details;
if (unusedJs) {
  console.log(`   - 总JS大小: ${Math.round(unusedJs.totalBytes / 1024)} KB`);
  console.log(`   - 未使用JS大小: ${Math.round(unusedJs.unusedBytes / 1024)} KB (${Math.round(unusedJs.unusedBytes / unusedJs.totalBytes * 100)}%)`);
} else {
  console.log('   - 无未使用JavaScript数据');
}

// 大型图片
console.log('\n7. 大型图片：');
const largeImages = lighthouseData.audits['properly-sized-images']?.details?.items || [];
if (largeImages.length > 0) {
  largeImages.forEach(image => {
    console.log(`   - ${image.url}: 原始大小 ${Math.round(image.originalSize / 1024)} KB，优化后大小 ${Math.round(image.effectiveSize / 1024)} KB，节省 ${Math.round((image.originalSize - image.effectiveSize) / 1024)} KB`);
  });
} else {
  console.log('   - 无大型图片');
}

// 缓存策略
console.log('\n8. 缓存策略：');
const cachePolicy = lighthouseData.audits['uses-long-cache-ttl']?.details?.items || [];
if (cachePolicy.length > 0) {
  const shortCache = cachePolicy.filter(item => item.cacheTTL < 2592000); // 少于30天
  console.log(`   - 短期缓存资源 (小于30天): ${shortCache.length} 个`);
  shortCache.forEach(item => {
    console.log(`     - ${item.url}: ${item.cacheTTL} 秒`);
  });
} else {
  console.log('   - 无缓存策略数据');
}

// 网络请求
console.log('\n9. 网络请求：');
const networkRequests = lighthouseData.audits['network-requests']?.details?.items || [];
console.log(`   - 总请求数: ${networkRequests.length}`);
console.log(`   - 总传输大小: ${Math.round(networkRequests.reduce((sum, item) => sum + item.transferSize, 0) / 1024)} KB`);

// 服务器响应时间
console.log('\n10. 服务器响应时间：');
const serverResponse = lighthouseData.audits['server-response-time']?.details?.items || [];
if (serverResponse.length > 0) {
  serverResponse.forEach(item => {
    console.log(`   - ${item.url}: ${item.responseTime} ms`);
  });
} else {
  console.log('   - 无服务器响应时间数据');
}

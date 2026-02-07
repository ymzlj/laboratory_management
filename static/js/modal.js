/**
 * 弹窗管理模块
 * 用于显示和隐藏模态弹窗
 */

class ModalManager {
    constructor() {
        this.modals = new Map();
        this.init();
    }

    init() {
        // 处理现有的Django messages
        this.processExistingMessages();
        // 监听新的Django messages
        this.watchDjangoMessages();
    }

    /**
     * 处理页面加载时已存在的Django messages
     */
    processExistingMessages() {
        const alertContainer = document.querySelector('.alert-container');
        if (!alertContainer) return;
        
        const alerts = alertContainer.querySelectorAll('.alert');
        alerts.forEach(alert => {
            this.convertAlertToModal(alert);
            alert.remove();
        });
    }

    /**
     * 监听Django messages并显示为弹窗
     */
    watchDjangoMessages() {
        const alertContainer = document.querySelector('.alert-container');
        if (!alertContainer) return;

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === 1) {
                            const alert = node.querySelector('.alert');
                            if (alert) {
                                this.convertAlertToModal(alert);
                            alert.remove();
                            mutation.target.removeChild(node);
                        }
                    }
                }
            });
        });

        observer.observe(alertContainer, {
            childList: true,
            subtree: true
        });
    }

    /**
     * 将Django alert转换为弹窗
     */
    convertAlertToModal(alertElement) {
        const message = alertElement.textContent.trim();
        const type = this.getAlertType(alertElement);

        this.showModal(message, type);
    }

    /**
     * 获取alert类型
     */
    getAlertType(alertElement) {
        if (alertElement.classList.contains('alert-danger')) {
            return 'error';
        } else if (alertElement.classList.contains('alert-warning')) {
            return 'warning';
        } else if (alertElement.classList.contains('alert-success')) {
            return 'success';
        } else {
            return 'info';
        }
    }

    /**
     * 显示弹窗
     */
    showModal(message, type = 'info') {
        const modalId = `modal-${Date.now()}`;
        const modal = this.createModal(message, type, modalId);
        
        document.body.appendChild(modal);
        
        // 阻止body滚动
        document.body.style.overflow = 'hidden';
        
        // 存储弹窗引用
        this.modals.set(modalId, modal);
        
        // 自动关闭（可选）
        // setTimeout(() => this.closeModal(modalId), 5000);
    }

    /**
     * 创建弹窗元素
     */
    createModal(message, type, modalId) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.id = modalId;

        const iconClass = this.getIconClass(type);
        const title = this.getTitle(type);

        overlay.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-title">
                        <i class="modal-icon ${iconClass}"></i>
                        <span>${title}</span>
                    </div>
                    <button class="modal-close" onclick="modalManager.closeModal('${modalId}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    ${message}
                </div>
                <div class="modal-footer">
                    <button class="modal-btn modal-btn-primary" onclick="modalManager.closeModal('${modalId}')">
                        确定
                    </button>
                </div>
            </div>
        `;

        return overlay;
    }

    /**
     * 获取图标类名
     */
    getIconClass(type) {
        const icons = {
            'success': 'fas fa-check-circle success',
            'error': 'fas fa-exclamation-circle error',
            'warning': 'fas fa-exclamation-triangle warning',
            'info': 'fas fa-info-circle info'
        };
        return icons[type] || icons['info'];
    }

    /**
     * 获取标题
     */
    getTitle(type) {
        const titles = {
            'success': '操作成功',
            'error': '操作失败',
            'warning': '警告',
            'info': '提示'
        };
        return titles[type] || titles['info'];
    }

    /**
     * 关闭弹窗
     */
    closeModal(modalId) {
        const modal = this.modals.get(modalId);
        if (modal) {
            modal.style.animation = 'fadeOut 0.3s ease-in-out';
            
            setTimeout(() => {
                modal.remove();
                this.modals.delete(modalId);
                
                // 恢复body滚动
                if (this.modals.size === 0) {
                    document.body.style.overflow = '';
                }
            }, 300);
        }
    }

    /**
     * 关闭所有弹窗
     */
    closeAllModals() {
        this.modals.forEach((modal, modalId) => {
            this.closeModal(modalId);
        });
    }

    /**
     * 显示成功消息
     */
    showSuccess(message) {
        this.showModal(message, 'success');
    }

    /**
     * 显示错误消息
     */
    showError(message) {
        this.showModal(message, 'error');
    }

    /**
     * 显示警告消息
     */
    showWarning(message) {
        this.showModal(message, 'warning');
    }

    /**
     * 显示信息消息
     */
    showInfo(message) {
        this.showModal(message, 'info');
    }
}

// 添加淡出动画
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from {
            opacity: 1;
        }
        to {
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// 创建全局实例
const modalManager = new ModalManager();

// 导出到全局作用域
window.modalManager = modalManager;

// 兼容旧的showAlert函数
window.showAlert = function(message, type = 'info') {
    modalManager.showModal(message, type);
};

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    modalManager.closeAllModals();
});
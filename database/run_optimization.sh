#!/bin/bash
# 数据库优化实施脚本（Linux/Mac）
# 执行顺序：先执行SQL，再运行Django迁移

echo "开始数据库优化..."

# 步骤1：创建优化的Django迁移文件
echo "创建Django迁移文件..."
cd /opt/laboratory_management
source venv/bin/activate

# 创建空的迁移文件
python manage.py makemigrations tasks --name add_performance_indexes --empty

# 步骤2：提示用户手动编辑迁移文件
echo "请编辑 apps/tasks/migrations/XXXX_add_performance_indexes.py 文件"
echo "将 migration_template.py 中的内容复制进去"
read -p "按回车键继续..."

# 步骤3：执行迁移
echo "执行数据库迁移..."
python manage.py migrate

# 步骤4：执行SQL优化
echo "执行SQL优化..."
mysql -u root -p laboratory_test_management < database/optimize_database.sql

# 步骤5：查看执行结果
echo "验证索引创建..."
mysql -u root -p laboratory_test_management < database/verify_indexes.sql

echo "优化完成！"
# 数据库优化实施脚本
# 执行顺序：先执行SQL，再运行Django迁移

# 步骤1：创建优化的Django迁移文件
python manage.py makemigrations tasks --name add_performance_indexes --empty

# 步骤2：将下面的内容复制到生成的迁移文件中

# 步骤3：执行迁移
python manage.py migrate

# 步骤4：执行SQL优化
mysql -u root -p laboratory_test_management < optimize_database.sql

# 步骤5：查看执行结果
python manage.py dbshell < verify_indexes.sql

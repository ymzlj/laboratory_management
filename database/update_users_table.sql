-- 修改用户表结构，去掉姓和名字段，只保留姓名字段
ALTER TABLE users 
DROP COLUMN first_name,
DROP COLUMN last_name;
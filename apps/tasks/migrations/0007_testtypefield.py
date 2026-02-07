# Generated manually on 2025-11-13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0006_disc_spring_test_data_with_test_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestTypeField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=100, verbose_name='字段名称')),
                ('field_code', models.CharField(max_length=50, verbose_name='字段代码')),
                ('field_type', models.CharField(choices=[('text', '文本'), ('textarea', '多行文本'), ('number', '数字'), ('decimal', '小数'), ('date', '日期'), ('datetime', '日期时间'), ('select', '下拉选择'), ('checkbox', '复选框'), ('file', '文件上传')], default='text', max_length=20, verbose_name='字段类型')),
                ('field_options', models.JSONField(blank=True, default=dict, help_text='对于下拉选择类型，存储选项列表；其他配置如最大值、最小值等', verbose_name='字段选项')),
                ('is_required', models.BooleanField(default=False, verbose_name='是否必填')),
                ('default_value', models.CharField(blank=True, max_length=200, verbose_name='默认值')),
                ('placeholder', models.CharField(blank=True, max_length=200, verbose_name='提示文本')),
                ('help_text', models.CharField(blank=True, max_length=500, verbose_name='帮助文本')),
                ('order', models.IntegerField(default=0, verbose_name='显示顺序')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('test_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_fields', to='tasks.testtype', verbose_name='试验类型')),
            ],
            options={
                'verbose_name': '试验类型字段配置',
                'verbose_name_plural': '试验类型字段配置',
                'db_table': 'test_type_fields',
                'ordering': ['test_type', 'order', 'id'],
                'unique_together': {('test_type', 'field_code')},
            },
        ),
    ]

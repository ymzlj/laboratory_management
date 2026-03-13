<template>
  <div class="test-type-detail-page" v-loading="loading">
    <div class="page-header">
      <h2>
        <i class="fas fa-flask"></i>
        试验类型详情
      </h2>
      <div class="header-actions">
        <button class="btn btn-outline-secondary" @click="goBack">
          <i class="fas fa-arrow-left"></i>
          返回列表
        </button>
        <button v-if="isManager" class="btn btn-primary" @click="goToFieldConfig">
          <i class="fas fa-cog"></i>
          字段配置
        </button>
      </div>
    </div>

    <div class="content-row">
      <div class="left-column">
        <div class="card info-card">
          <div class="card-header">
            <span><i class="fas fa-info-circle me-2"></i>基本信息</span>
            <button v-if="isManager" class="btn btn-sm btn-outline-primary" @click="showEditDialog">
              <i class="fas fa-edit"></i>
              编辑
            </button>
          </div>
          <div class="card-body">
            <div class="info-grid">
              <div class="info-item">
                <label>类型名称：</label>
                <span class="value">{{ testType?.name }}</span>
              </div>
              <div class="info-item">
                <label>类型编码：</label>
                <code class="type-code">{{ testType?.code }}</code>
              </div>
              <div class="info-item">
                <label>父级类型：</label>
                <span class="value">{{ parentTypeName || '无' }}</span>
              </div>
              <div class="info-item">
                <label>类型级别：</label>
                <span class="value">{{ testType?.level_type === 1 ? '总类型' : '分类型' }}</span>
              </div>
              <div class="info-item">
                <label>创建时间：</label>
                <span class="value">{{ formatDateTime(testType?.created_at) }}</span>
              </div>
              <div class="info-item">
                <label>更新时间：</label>
                <span class="value">{{ formatDateTime(testType?.updated_at) }}</span>
              </div>
            </div>
            <div class="description-section" v-if="testType?.description">
              <label>描述：</label>
              <p>{{ testType.description }}</p>
            </div>
          </div>
        </div>

        <div class="card info-card">
          <div class="card-header">
            <span><i class="fas fa-list-alt me-2"></i>字段配置 ({{ customFields.length }})</span>
            <button v-if="isManager" class="btn btn-sm btn-primary" @click="showFieldDialog">
              <i class="fas fa-plus"></i>
              添加字段
            </button>
          </div>
          <div class="card-body" style="padding: 0;">
            <div class="table-responsive" v-if="customFields.length > 0">
              <table class="data-table">
                <thead>
                  <tr>
                    <th style="width: 5%;">序号</th>
                    <th style="width: 18%;">字段名称</th>
                    <th style="width: 15%;">字段编码</th>
                    <th style="width: 12%;">字段类型</th>
                    <th style="width: 8%;">必填</th>
                    <th style="width: 8%;">搜索</th>
                    <th style="width: 8%;">显示</th>
                    <th style="width: 10%;">批量录入</th>
                    <th style="width: 16%;" class="text-center">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(field, index) in customFields" :key="field.id">
                    <td>{{ index + 1 }}</td>
                    <td>
                      <span class="field-name">{{ field.field_name }}</span>
                    </td>
                    <td>
                      <code class="field-code">{{ field.field_code }}</code>
                    </td>
                    <td>
                      <span class="field-type-badge">{{ getFieldTypeLabel(field.field_type) }}</span>
                    </td>
                    <td class="text-center">
                      <i v-if="field.is_required" class="fas fa-check text-success"></i>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td class="text-center">
                      <i v-if="field.is_search_field" class="fas fa-check text-success"></i>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td class="text-center">
                      <i v-if="field.is_active" class="fas fa-check text-success"></i>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td class="text-center">
                      <i v-if="field.is_batch_input_enabled" class="fas fa-check text-success"></i>
                      <span v-else class="text-muted">-</span>
                    </td>
                    <td class="text-center">
                      <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" title="编辑" @click="showEditFieldDialog(field)" v-if="isManager">
                          <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger" title="删除" @click="handleDeleteField(field)" v-if="isManager">
                          <i class="fas fa-trash-alt"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="empty-state">
              <i class="fas fa-inbox fa-2x mb-2 opacity-50"></i>
              <p>暂无字段配置</p>
              <button v-if="isManager" class="btn btn-sm btn-primary" @click="showFieldDialog">
                <i class="fas fa-plus me-1"></i>添加字段
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="right-column">
        <div class="card info-card">
          <div class="card-header">
            <span><i class="fas fa-tasks me-2"></i>相关任务 ({{ taskCount }})</span>
          </div>
          <div class="card-body" style="padding: 0;">
            <div v-if="relatedTasks.length > 0">
              <div 
                v-for="task in relatedTasks.slice(0, 5)" 
                :key="task.id" 
                class="task-item"
                @click="goToTask(task.id)"
              >
                <div class="task-info">
                  <span class="task-number">{{ task.task_number }}</span>
                  <span class="task-name">{{ task.task_name }}</span>
                </div>
                <span class="status-badge" :class="task.status_code">{{ task.status_name }}</span>
              </div>
              <div v-if="taskCount > 5" class="more-link" @click="goToTaskList">
                查看全部 {{ taskCount }} 个任务
              </div>
            </div>
            <div v-else class="empty-state-sm">
              <i class="fas fa-inbox"></i>
              <p>暂无相关任务</p>
            </div>
          </div>
        </div>

        <div class="card info-card" v-if="childTypes.length > 0">
          <div class="card-header">
            <span><i class="fas fa-sitemap me-2"></i>子类型 ({{ childTypes.length }})</span>
          </div>
          <div class="card-body" style="padding: 0;">
            <div 
              v-for="child in childTypes" 
              :key="child.id" 
              class="child-item"
              @click="goToDetail(child.id)"
            >
              <i class="fas fa-file-alt text-primary me-2"></i>
              <span>{{ child.name }}</span>
              <span class="status-badge sm" :class="child.is_active ? 'active' : 'inactive'">
                {{ child.is_active ? '启用' : '禁用' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" title="编辑试验类型" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="类型名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入类型名称" />
        </el-form-item>
        <el-form-item label="类型编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入类型编码" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="fieldDialogVisible" :title="isEditField ? '编辑字段' : '添加字段'" width="600px">
      <el-form ref="fieldFormRef" :model="fieldForm" :rules="fieldRules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="字段名称" prop="field_name">
              <el-input v-model="fieldForm.field_name" placeholder="请输入字段名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="字段编码" prop="field_code">
              <el-input v-model="fieldForm.field_code" placeholder="请输入字段编码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="字段类型" prop="field_type">
              <el-select v-model="fieldForm.field_type" style="width: 100%">
                <el-option label="文本" value="text" />
                <el-option label="数字" value="number" />
                <el-option label="小数" value="decimal" />
                <el-option label="日期" value="date" />
                <el-option label="日期时间" value="datetime" />
                <el-option label="下拉选择" value="select" />
                <el-option label="多选框" value="checkbox" />
                <el-option label="多行文本" value="textarea" />
                <el-option label="文件" value="file" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="fieldForm.order" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="必填">
              <el-switch v-model="fieldForm.is_required" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="批量录入">
              <el-switch v-model="fieldForm.is_batch_input_enabled" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="搜索字段">
              <el-switch v-model="fieldForm.is_search_field" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="显示字段">
              <el-switch v-model="fieldForm.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="帮助文本">
          <el-input v-model="fieldForm.help_text" placeholder="字段帮助说明" />
        </el-form-item>
        <el-form-item label="占位符">
          <el-input v-model="fieldForm.placeholder" placeholder="输入框占位文本" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="fieldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleFieldSubmit" :loading="fieldSubmitting">确定</el-button>
      </template>
    </el-dialog>

    <confirm-modal
      v-model="showConfirmModal"
      :title="confirmTitle"
      :message="confirmMessage"
      @confirm="confirmAction"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
  import { getTestTypeDetail, updateTestType, createTestTypeField, updateTestTypeField, deleteTestTypeField, getTestTypes } from '@/api/modules/tasks'
  import { normalizeTaskList } from '@/utils/normalizeTask'
import { useAuthStore } from '@/stores/auth'
import type { TestType, TestTypeField, Task } from '@/types'
import ConfirmModal from '@/components/ConfirmModal.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const testTypeId = computed(() => Number(route.params.id))
const loading = ref(false)
const testType = ref<TestType | null>(null)
const customFields = ref<TestTypeField[]>([])
const relatedTasks = ref<Task[]>([])
const taskCount = ref(0)
const childTypes = ref<TestType[]>([])
const allTestTypes = ref<TestType[]>([])

const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  code: '',
  description: '',
  is_active: true
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入类型名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入类型编码', trigger: 'blur' }]
}

const fieldDialogVisible = ref(false)
const isEditField = ref(false)
const editFieldId = ref<number | null>(null)
const fieldSubmitting = ref(false)
const fieldFormRef = ref<FormInstance>()

type FieldType = 'text' | 'number' | 'decimal' | 'date' | 'datetime' | 'select' | 'checkbox' | 'textarea' | 'file'

const fieldForm = reactive<{
  field_name: string
  field_code: string
  field_type: FieldType
  is_required: boolean
  is_batch_input_enabled: boolean
  is_search_field: boolean
  is_active: boolean
  order: number
  help_text: string
  placeholder: string
}>({
  field_name: '',
  field_code: '',
  field_type: 'text',
  is_required: false,
  is_batch_input_enabled: false,
  is_search_field: false,
  is_active: true,
  order: 0,
  help_text: '',
  placeholder: ''
})

const fieldRules: FormRules = {
  field_name: [{ required: true, message: '请输入字段名称', trigger: 'blur' }],
  field_code: [{ required: true, message: '请输入字段编码', trigger: 'blur' }],
  field_type: [{ required: true, message: '请选择字段类型', trigger: 'change' }]
}

const showConfirmModal = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
const pendingDeleteField = ref<TestTypeField | null>(null)

const isManager = computed(() => authStore.isManager)

const parentTypeName = computed(() => {
  if (!testType.value?.parent) return ''
  const parent = allTestTypes.value.find(t => t.id === testType.value?.parent)
  return parent?.name || ''
})

const fetchData = async () => {
  loading.value = true
  try {
    const response = await getTestTypeDetail(testTypeId.value)
    const result = response.data || response
    const data = result.data || result
    testType.value = data.test_type
    customFields.value = data.custom_fields || []
    // Normalize related tasks data to ensure status fields exist for UI
    relatedTasks.value = normalizeTaskList(data.tasks || [])
    taskCount.value = data.task_count || 0
    
    const types = await getTestTypes()
    allTestTypes.value = types
    childTypes.value = types.filter(t => t.parent_id === testTypeId.value)
  } catch (err) {
    console.error(err)
    const msg = (err as any)?.response?.data?.message || '获取试验类型详情失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const showEditDialog = () => {
  if (!testType.value) return
  form.name = testType.value.name
  form.code = testType.value.code
  form.description = testType.value.description || ''
  form.is_active = testType.value.is_active
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      await updateTestType(testTypeId.value, {
        name: form.name,
        code: form.code,
        description: form.description,
        is_active: form.is_active
      })
      ElMessage.success('更新成功')
      dialogVisible.value = false
      fetchData()
    } catch {
      ElMessage.error('更新失败')
    } finally {
      submitting.value = false
    }
  })
}

const showFieldDialog = () => {
  isEditField.value = false
  editFieldId.value = null
  Object.assign(fieldForm, {
    field_name: '',
    field_code: '',
    field_type: 'text',
    is_required: false,
    is_batch_input_enabled: false,
    is_search_field: false,
    is_active: true,
    order: customFields.value.length,
    help_text: '',
    placeholder: ''
  })
  fieldDialogVisible.value = true
}

const showEditFieldDialog = (row: TestTypeField) => {
  isEditField.value = true
  editFieldId.value = row.id
  Object.assign(fieldForm, {
    field_name: row.field_name,
    field_code: row.field_code,
    field_type: row.field_type,
    is_required: row.is_required,
    is_batch_input_enabled: row.is_batch_input_enabled,
    is_search_field: row.is_search_field,
    is_active: row.is_active,
    order: row.order,
    help_text: row.help_text || '',
    placeholder: row.placeholder || ''
  })
  fieldDialogVisible.value = true
}

const handleFieldSubmit = async () => {
  if (!fieldFormRef.value) return
  
  await fieldFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    fieldSubmitting.value = true
    try {
      if (isEditField.value && editFieldId.value) {
        await updateTestTypeField(editFieldId.value, fieldForm)
        ElMessage.success('更新成功')
      } else {
        await createTestTypeField(testTypeId.value, fieldForm)
        ElMessage.success('添加成功')
      }
      fieldDialogVisible.value = false
      fetchData()
    } catch {
      ElMessage.error('操作失败')
    } finally {
      fieldSubmitting.value = false
    }
  })
}

const handleDeleteField = (row: TestTypeField) => {
  pendingDeleteField.value = row
  confirmTitle.value = '确认删除'
  confirmMessage.value = `确定要删除字段"${row.field_name}"吗？此操作不可恢复。`
  showConfirmModal.value = true
}

const confirmAction = async () => {
  if (!pendingDeleteField.value) return
  try {
    await deleteTestTypeField(pendingDeleteField.value.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch {
    ElMessage.error('删除失败')
  } finally {
    pendingDeleteField.value = null
  }
}

const goBack = () => router.push('/test-types')
const goToDetail = (id: number) => router.push(`/test-types/${id}`)
const goToTask = (id: number) => router.push(`/tasks/detail/${id}`)
const goToTaskList = () => router.push('/tasks')
const goToFieldConfig = () => router.push(`/test-types/${testTypeId.value}/fields`)

const getFieldTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    text: '文本',
    number: '数字',
    decimal: '小数',
    date: '日期',
    datetime: '日期时间',
    select: '下拉选择',
    checkbox: '多选框',
    textarea: '多行文本',
    file: '文件'
  }
  return labels[type] || type
}

const formatDateTime = (date?: string) => date?.replace('T', ' ').substring(0, 16) || '-'

onMounted(fetchData)
</script>

<style scoped lang="scss">
.test-type-detail-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    
    h2 {
      font-size: 24px;
      font-weight: 600;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .header-actions {
      display: flex;
      gap: 8px;
    }
  }
  
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
    
    &.btn-sm {
      padding: 4px 10px;
      font-size: 12px;
    }
    
    &.btn-primary {
      background-color: #4a90e2;
      color: white;
      border-color: #4a90e2;
      
      &:hover {
        background-color: #3a7bc8;
        border-color: #3a7bc8;
      }
    }
    
    &.btn-outline-secondary {
      background-color: transparent;
      color: #6c757d;
      border-color: #6c757d;
      
      &:hover {
        background-color: #6c757d;
        color: white;
      }
    }
    
    &.btn-outline-primary {
      background-color: transparent;
      color: #4a90e2;
      border-color: #4a90e2;
      
      &:hover {
        background-color: #4a90e2;
        color: white;
      }
    }
    
    &.btn-outline-danger {
      background-color: transparent;
      color: #dc3545;
      border-color: #dc3545;
      
      &:hover {
        background-color: #dc3545;
        color: white;
      }
    }
  }
  
  .btn-group-sm .btn {
    padding: 4px 8px;
    font-size: 12px;
  }
  
  .content-row {
    display: flex;
    gap: 24px;
    
    .left-column { flex: 1; }
    .right-column { width: 360px; flex-shrink: 0; }
  }
  
  .info-card {
    margin-bottom: 20px;
    border: none;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    border-radius: 10px;
    background: white;
    
    .card-header {
      padding: 12px 16px;
      border-bottom: 1px solid #e9ecef;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      
      .me-2 { margin-right: 0.5rem; }
    }
    
    .card-body { padding: 16px; }
  }
  
  .info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    
    .info-item {
      display: flex;
      align-items: center;
      
      label {
        color: #909399;
        margin-right: 8px;
        min-width: 70px;
      }
      
      .value {
        color: #303133;
      }
    }
  }
  
  .type-code, .field-code {
    background: #f5f7fa;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: #606266;
  }
  
  .description-section {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #e9ecef;
    
    label { color: #909399; }
    p { margin-top: 8px; color: #606266; }
  }
  
  .field-name {
    font-weight: 500;
  }
  
  .field-type-badge {
    display: inline-block;
    padding: 2px 8px;
    background: #ecf5ff;
    color: #409eff;
    border-radius: 4px;
    font-size: 12px;
  }
  
  .status-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    
    &.active { background: #dcfce7; color: #166534; }
    &.inactive { background: #f3f4f6; color: #4b5563; }
    &.pending { background: #fef0c3; color: #92400e; }
    &.in_progress { background: #dbeafe; color: #1e40af; }
    &.completed { background: #dcfce7; color: #166534; }
    
    &.sm {
      padding: 2px 8px;
      font-size: 11px;
    }
  }
  
  .task-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background-color 0.2s;
    
    &:hover {
      background-color: #f5f7fa;
    }
    
    .task-info {
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      .task-number {
        font-size: 12px;
        color: #909399;
        font-family: monospace;
      }
      
      .task-name {
        font-weight: 500;
        color: #303133;
      }
    }
  }
  
  .more-link {
    padding: 12px 16px;
    text-align: center;
    color: #4a90e2;
    cursor: pointer;
    font-size: 13px;
    
    &:hover {
      background-color: #f5f7fa;
      text-decoration: underline;
    }
  }
  
  .child-item {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background-color 0.2s;
    
    &:hover {
      background-color: #f5f7fa;
    }
    
    .text-primary { color: #4a90e2; }
    .me-2 { margin-right: 0.5rem; }
    
    .status-badge {
      margin-left: auto;
    }
  }
  
  .empty-state {
    text-align: center;
    padding: 32px 16px;
    color: #909399;
    
    .opacity-50 { opacity: 0.5; }
    .mb-2 { margin-bottom: 0.5rem; }
    
    p { margin-bottom: 12px; }
  }
  
  .empty-state-sm {
    text-align: center;
    padding: 24px 16px;
    color: #909399;
    
    i { font-size: 24px; opacity: 0.5; margin-bottom: 8px; display: block; }
    p { font-size: 13px; }
  }
  
  .text-center { text-align: center; }
  .text-success { color: #28a745; }
  .text-muted { color: #909399; }
  .text-primary { color: #4a90e2; }
  .me-1 { margin-right: 0.25rem; }
  .me-2 { margin-right: 0.5rem; }
}
</style>

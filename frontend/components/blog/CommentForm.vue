<script setup lang="ts">
import { useForm, Field, ErrorMessage } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as zod from 'zod'

const props = defineProps<{
  postId: string
}>()

const emit = defineEmits<{
  (e: 'success'): void
}>()

const { postComment } = useBlog()
const toast = useToast()

const schema = toTypedSchema(
  zod.object({
    author_name: zod.string().min(2, 'Имя слишком короткое').max(50, 'Имя слишком длинное'),
    author_email: zod.string().email('Некорректный email'),
    content: zod.string().min(10, 'Комментарий слишком короткий').max(1000, 'Комментарий слишком длинный')
  })
)

const { handleSubmit, resetForm, isSubmitting } = useForm({
  validationSchema: schema,
  initialValues: {
    author_name: '',
    author_email: '',
    content: ''
  }
})

const onSubmit = handleSubmit(async (values) => {
  try {
    await postComment(props.postId, values)
    toast.success('Комментарий отправлен', 'Он появится после модерации')
    resetForm()
    emit('success')
  } catch (error: any) {
    toast.error('Ошибка', error.message || 'Не удалось отправить комментарий')
  }
})
</script>

<template>
  <div class="comment-form-wrapper">
    <h3 class="title">Оставить комментарий</h3>
    <form @submit.prevent="onSubmit" class="comment-form">
      <div class="row">
        <Field name="author_name" v-slot="{ field, errors }">
          <UInput
            v-bind="field"
            label="Имя"
            placeholder="Ваше имя"
            :error="errors[0]"
            :disabled="isSubmitting"
          />
        </Field>
        <Field name="author_email" v-slot="{ field, errors }">
          <UInput
            v-bind="field"
            label="Email"
            placeholder="Ваш email (скрыт)"
            :error="errors[0]"
            :disabled="isSubmitting"
          />
        </Field>
      </div>

      <Field name="content" v-slot="{ field, errors }">
        <UTextarea
          v-bind="field"
          label="Комментарий"
          placeholder="Напишите, что вы думаете..."
          :rows="4"
          :error="errors[0]"
          :disabled="isSubmitting"
        />
      </Field>

      <UButton
        type="submit"
        :loading="isSubmitting"
        class="submit-btn"
      >
        Отправить
      </UButton>
    </form>
  </div>
</template>

<style scoped>
.comment-form-wrapper {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  padding: 2rem;
  border-radius: var(--radius-lg);
}

.title {
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--color-text);
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .row {
    grid-template-columns: 1fr 1fr;
  }
}

.submit-btn {
  align-self: flex-start;
  min-width: 160px;
}
</style>

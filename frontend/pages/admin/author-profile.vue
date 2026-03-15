<script setup lang="ts">
import { useBlog } from '~/composables/useBlog'

definePageMeta({
  layout: false,
  pageTransition: false,
  middleware: 'auth',
})

const blog = useBlog()
const toast = useToast()

const { data: profile, refresh } = await blog.adminGetMyAuthorProfile()

const form = ref({
  display_name: profile.value?.display_name ?? '',
  bio: profile.value?.bio ?? '',
  avatar_url: profile.value?.avatar_url ?? '',
})

const isSubmitting = ref(false)

const handleSave = async () => {
  if (!form.value.display_name.trim()) {
    toast.error('Отображаемое имя обязательно')
    return
  }
  isSubmitting.value = true
  try {
    await blog.adminUpdateMyAuthorProfile({
      display_name: form.value.display_name || undefined,
      bio: form.value.bio || undefined,
      avatar_url: form.value.avatar_url || undefined,
    })
    toast.success('Профиль автора обновлён')
    await refresh()
  } catch {
    toast.error('Не удалось сохранить профиль')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <NuxtLayout name="admin">
    <template #header-title>Профиль автора</template>
    <template #header-actions>
      <UButton
        :loading="isSubmitting"
        data-testid="author-profile-save"
        @click="handleSave"
      >
        Сохранить
      </UButton>
    </template>

    <div class="author-profile-page">
      <UCard class="profile-card">
        <div class="profile-form">
          <!-- Avatar preview -->
          <div v-if="form.avatar_url" class="avatar-preview">
            <img
              :src="form.avatar_url"
              alt="Аватар автора"
              class="avatar-img"
            />
          </div>
          <div v-else class="avatar-placeholder">
            <Icon name="ph:user-circle-bold" size="64" class="avatar-icon" />
          </div>

          <!-- Display name -->
          <div class="form-group">
            <UInput
              v-model="form.display_name"
              label="Отображаемое имя *"
              placeholder="Введите отображаемое имя"
              required
              data-testid="author-profile-name"
            />
          </div>

          <!-- Bio -->
          <div class="form-group">
            <label class="form-label">О себе / Bio</label>
            <textarea
              v-model="form.bio"
              class="bio-textarea"
              rows="4"
              placeholder="Расскажите о себе..."
              data-testid="author-profile-bio"
            />
          </div>

          <!-- Avatar URL -->
          <div class="form-group">
            <UInput
              v-model="form.avatar_url"
              label="URL аватара"
              placeholder="https://example.com/avatar.jpg"
              data-testid="author-profile-avatar"
            />
          </div>

          <!-- Mobile save button -->
          <div class="mobile-save">
            <UButton
              block
              :loading="isSubmitting"
              data-testid="author-profile-save-mobile"
              @click="handleSave"
            >
              Сохранить
            </UButton>
          </div>
        </div>
      </UCard>
    </div>
  </NuxtLayout>
</template>

<style scoped>
.author-profile-page {
  max-width: 640px;
  margin: 0 auto;
}

.profile-card {
  width: 100%;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Avatar */
.avatar-preview {
  display: flex;
  justify-content: center;
}

.avatar-img {
  width: 96px;
  height: 96px;
  border-radius: var(--radius-full);
  object-fit: cover;
  border: 2px solid var(--color-accent);
}

.avatar-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-icon {
  color: var(--color-text-2);
}

/* Form group */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-2);
}

/* Bio textarea */
.bio-textarea {
  width: 100%;
  padding: 10px 14px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-family: var(--font-sans);
  resize: vertical;
  transition: border-color var(--transition-fast);
  box-sizing: border-box;
  min-height: 100px;
}

.bio-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

/* Mobile save */
.mobile-save {
  display: block;
}

@media (min-width: 768px) {
  .mobile-save {
    display: none;
  }
}
</style>

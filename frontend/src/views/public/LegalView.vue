<template>
  <section class="section">
    <div class="container" style="max-width: 820px">
      <div class="section-eyebrow mb-2">Legal</div>
      <h1 class="section-title mb-2">{{ doc.title }}</h1>
      <p class="text-muted small mb-4">Plain-language summary. This template should be reviewed by a qualified lawyer before public launch.</p>
      <div v-for="s in doc.sections" :key="s.h" class="mb-4">
        <h2 class="h5 fw-bold">{{ s.h }}</h2>
        <p class="text-muted mb-0">{{ s.p }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const DOCS = {
  privacy: { title: 'Privacy Policy', sections: [
    { h: 'What we collect', p: 'Account details (email, password stored only as a secure hash), the profile details you choose to give, saved opportunities, tracker entries, uploaded documents and Saathi AI conversations.' },
    { h: 'Optional sensitive information', p: 'Family income range, social category, gender and disability status are optional. They are used only to check eligibility rules and are never shown to other users.' },
    { h: 'Your documents', p: 'Uploaded files are stored privately, are never publicly accessible, and are served only to you after login. Deleting a document removes the file.' },
    { h: 'AI processing', p: 'When you use Saathi AI, your question, the opportunity details and non-sensitive profile fields (education, course, year, state) are sent to our AI provider to generate an answer. Income, category and documents are not sent.' },
    { h: 'Your rights', p: 'You can download all your data as JSON and delete your account at any time from Settings → Privacy.' },
  ] },
  terms: { title: 'Terms of Use', sections: [
    { h: 'What FormSaathi is', p: 'An independent information and organisation tool. It is not a government service and does not submit applications on your behalf.' },
    { h: 'Accuracy', p: 'We work hard to keep listings accurate and show their official sources, but the official notification always prevails. Confirm details before applying.' },
    { h: 'AI guidance', p: 'Saathi AI provides general guidance in simple language. It is not legal, financial or official government advice.' },
    { h: 'Acceptable use', p: 'Do not upload documents that are not yours, attempt to access other users’ data, or misuse the service.' },
  ] },
}
const route = useRoute()
const doc = computed(() => DOCS[route.meta.doc] || DOCS.privacy)
</script>

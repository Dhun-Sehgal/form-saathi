<template>
  <section class="section">
    <div class="container" style="max-width: 900px">
      <div class="text-center mb-5">
        <div class="section-eyebrow mb-2">How it works</div>
        <h1 class="section-title">Your journey, step by step</h1>
        <p class="text-muted lead">FormSaathi follows one simple loop: Discover → Check eligibility → Understand requirements → Prepare documents → Apply → Track.</p>
      </div>
      <div class="d-grid gap-3">
        <div v-for="(s, i) in steps" :key="s.title" class="fs-card fs-card-pad d-flex gap-3 gap-md-4">
          <div class="step-num flex-shrink-0">{{ i + 1 }}</div>
          <div>
            <h2 class="h5 fw-bold">{{ s.title }}</h2>
            <p class="text-muted mb-2">{{ s.text }}</p>
            <ul class="small text-muted mb-0 ps-3"><li v-for="b in s.points" :key="b">{{ b }}</li></ul>
          </div>
        </div>
      </div>
      <div class="text-center mt-5"><router-link to="/register" class="btn btn-primary btn-lg">Create your free profile</router-link></div>
    </div>
  </section>
</template>

<script setup>
const steps = [
  { title: 'Create your profile', text: 'A short onboarding asks only what helps matching.', points: ['Education, course, year and marks', 'State and city', 'Optional: income range, category, disability — each explained', 'Your interests and preferred language'] },
  { title: 'Discover opportunities', text: 'Search and filter scholarships, internships, fellowships, schemes, exams, jobs and skill programmes.', points: ['Filter by category, education, state, income and deadline', 'Recommendations with clear “why” reasons', 'Expired listings are never recommended'] },
  { title: 'Check eligibility', text: 'A rule engine compares your profile against each rule an admin transcribed from the official notification.', points: ['Eligible / Possibly eligible / Not eligible', 'Every rule shown with the reason and the official wording', 'Missing information is called out, never guessed'] },
  { title: 'Understand requirements', text: 'Saathi AI explains confusing instructions and terms in English, Hindi or Marathi.', points: ['Ask follow-up questions about an opportunity', 'Get a simple checklist of steps', 'AI guidance is clearly labelled and is not official advice'] },
  { title: 'Prepare documents', text: 'Your private document vault matches what you have against what each application needs.', points: ['Upload PDFs and images securely', 'See missing and expiring certificates', 'Download a checklist to take to the cyber café or office'] },
  { title: 'Apply and track', text: 'Apply on the official portal, then track everything in one place.', points: ['Statuses from Interested to Approved', 'Notes, application dates and reference numbers', 'Reminders before deadlines'] },
]
</script>

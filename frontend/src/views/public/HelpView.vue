<template>
  <section class="section">
    <div class="container" style="max-width: 860px">
      <div class="section-eyebrow mb-2">Help Center</div>
      <h1 class="section-title mb-4">How can we help?</h1>
      <div v-for="g in groups" :key="g.title" class="mb-4">
        <h2 class="h5 fw-bold mb-3">{{ g.title }}</h2>
        <div class="d-grid gap-2">
          <details v-for="item in g.items" :key="item.q" class="fs-card p-3">
            <summary class="fw-semibold cursor-pointer">{{ item.q }}</summary>
            <p class="text-muted mt-2 mb-0">{{ item.a }}</p>
          </details>
        </div>
      </div>
      <div class="fs-card fs-card-pad d-flex flex-wrap gap-3 align-items-center">
        <div class="flex-grow-1"><div class="fw-bold">Still stuck?</div><div class="text-muted small">Send us a message and we’ll get back to you.</div></div>
        <router-link to="/contact" class="btn btn-primary">Contact us</router-link>
      </div>
    </div>
  </section>
</template>

<script setup>
const groups = [
  { title: 'Eligibility', items: [
    { q: 'What do “Eligible”, “Possibly eligible” and “Not eligible” mean?', a: 'Eligible: you meet every rule we can check. Possibly eligible: some rules need more profile information or your own review. Not eligible: at least one required rule is not met based on your profile.' },
    { q: 'Why does a rule say “Needs your review”?', a: 'Some rules (like “not receiving another scholarship”) can’t be checked automatically. Read them in the official notification and decide.' },
    { q: 'Can I trust the result completely?', a: 'It is a helpful guide based on your profile and the rules we transcribed. The official notification and the issuing authority always have the final say.' },
  ] },
  { title: 'Verification & data', items: [
    { q: 'What does the Verified badge mean?', a: 'A FormSaathi reviewer checked the listing against its official source on the date shown.' },
    { q: 'How up to date is the information?', a: 'Each listing shows the date it was last checked against its official source. Authorities sometimes extend or change deadlines and rules, so always confirm on the official website before applying.' },
    { q: 'I found a mistake.', a: 'Use “Report a correction” on the opportunity page. Our team reviews every report.' },
  ] },
  { title: 'Documents & privacy', items: [
    { q: 'Who can see my documents?', a: 'Only you. Files are stored privately and are never publicly accessible. Admins cannot browse your files through the app.' },
    { q: 'How do I delete my data?', a: 'Delete any document from the Documents page, or delete your whole account from Settings → Privacy.' },
  ] },
]
</script>

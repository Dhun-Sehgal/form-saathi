<template>
  <section class="section">
    <div class="container">
      <StateBlock title="Page not found" message="The page you’re looking for doesn’t exist or has moved.">
        <div class="d-flex gap-2 justify-content-center">
          <router-link to="/" class="btn btn-primary">Go home</router-link>
          <router-link to="/explore" class="btn btn-soft">Explore opportunities</router-link>
        </div>
      </StateBlock>
    </div>
  </section>
</template>

<script setup>
import StateBlock from '@/components/StateBlock.vue'
</script>

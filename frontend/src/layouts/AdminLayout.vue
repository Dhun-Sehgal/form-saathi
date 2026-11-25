<template>
  <ShellLayout :nav="nav" :tabs="tabs" home="/admin" variant="admin"><slot /></ShellLayout>
</template>

<script setup>
import { BarChart3, FileStack, Megaphone, MessageSquareWarning, MessagesSquare, Shapes, Users } from 'lucide-vue-next'
import ShellLayout from './ShellLayout.vue'

const nav = [
  { to: '/admin', label: 'Overview', icon: BarChart3, exact: true },
  { to: '/admin/opportunities', label: 'Opportunities', icon: FileStack },
  { to: '/admin/corrections', label: 'Corrections', icon: MessageSquareWarning },
  { to: '/admin/categories', label: 'Categories', icon: Shapes },
  { to: '/admin/users', label: 'Users', icon: Users },
  { to: '/admin/announcements', label: 'Announcements', icon: Megaphone },
  { to: '/admin/feedback', label: 'Feedback', icon: MessagesSquare },
]
const tabs = [
  { to: '/admin', label: 'Overview', icon: BarChart3, exact: true },
  { to: '/admin/opportunities', label: 'Listings', icon: FileStack },
  { to: '/admin/corrections', label: 'Reports', icon: MessageSquareWarning },
  { to: '/admin/users', label: 'Users', icon: Users },
]
</script>

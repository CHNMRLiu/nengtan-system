import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const name = ref(localStorage.getItem('name') || '')

  function setUser(data) {
    token.value = data.token
    username.value = data.username
    name.value = data.name
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    localStorage.setItem('name', data.name)
  }

  function logout() {
    token.value = ''
    username.value = ''
    name.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('name')
  }

  return { token, username, name, setUser, logout }
})

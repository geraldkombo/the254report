const token = document.querySelector('meta[name="csrf-token"]')
if (token) {
  window.csrfToken = token.getAttribute("content")
}

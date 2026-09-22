export function getUserFormError(form, passwordRequired = true) {
  const firstName = form.first_name.trim()
  const lastName = form.last_name.trim()
  const email = form.email.trim()
  const password = form.password

  if (!firstName) {
    return 'El nombre es obligatorio.'
  }

  if (firstName.length > 80) {
    return 'El nombre no puede superar los 80 caracteres.'
  }

  if (!lastName) {
    return 'El apellido es obligatorio.'
  }

  if (lastName.length > 80) {
    return 'El apellido no puede superar los 80 caracteres.'
  }

  if (!email) {
    return 'El email es obligatorio.'
  }

  if (email.length > 150) {
    return 'El email no puede superar los 150 caracteres.'
  }

  const emailPattern = /^[^@\s]+@[^@\s]+\.[^@\s]+$/

  if (!emailPattern.test(email)) {
    return 'El formato del email no es válido.'
  }

  if (passwordRequired && !password) {
    return 'La contraseña es obligatoria.'
  }

  if (
    password
    && (password.length < 8 || password.length > 128)
  ) {
    return 'La contraseña debe tener entre 8 y 128 caracteres.'
  }

  return ''
}
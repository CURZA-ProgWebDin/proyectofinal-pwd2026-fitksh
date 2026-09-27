const DEFAULT_ERROR_MESSAGE = (
  'Ocurrió un error al procesar la solicitud.'
)

export function getApiErrorMessage(
  error,
  fallbackMessage = DEFAULT_ERROR_MESSAGE,
) {
  return (
    error?.response?.data?.error
    || error?.response?.data?.msg
    || fallbackMessage
  )
}
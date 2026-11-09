// Acceso a la API con rutas relativas (/api/...).

async function leerError(respuesta) {
  try {
    const cuerpo = await respuesta.json()
    const detalle = cuerpo?.detail
    if (typeof detalle === 'string') return detalle
    if (Array.isArray(detalle) && detalle.length > 0) {
      const primero = detalle[0]
      const campo = (primero.loc || []).filter((p) => p !== 'body').join('.')
      return `Corrige el campo ${campo}: ${primero.msg}`
    }
  } catch {
    // cuerpo no JSON
  }
  return `Error ${respuesta.status} al comunicarse con el servidor`
}

export async function obtenerDepartamentos() {
  const respuesta = await fetch('/api/departamentos')
  if (!respuesta.ok) throw new Error(await leerError(respuesta))
  return respuesta.json()
}

export async function listarEmpleados() {
  const respuesta = await fetch('/api/empleados')
  if (!respuesta.ok) throw new Error(await leerError(respuesta))
  return respuesta.json()
}

export async function registrarEmpleado(datos) {
  const respuesta = await fetch('/api/empleados', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  if (!respuesta.ok) throw new Error(await leerError(respuesta))
  return respuesta.json()
}

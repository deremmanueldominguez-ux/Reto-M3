import { useCallback, useEffect, useState } from 'react'
import { listarEmpleados } from './api.js'
import FormularioEmpleado from './components/FormularioEmpleado.jsx'
import TablaEmpleados from './components/TablaEmpleados.jsx'

// Punto de montaje de las vistas; las historias futuras (edición, baja) se agregan aquí.
export default function App() {
  const [empleados, setEmpleados] = useState([])
  const [errorLista, setErrorLista] = useState('')

  const cargarEmpleados = useCallback(() => {
    listarEmpleados()
      .then((lista) => {
        setEmpleados(lista)
        setErrorLista('')
      })
      .catch((e) => setErrorLista(e.message))
  }, [])

  useEffect(() => {
    cargarEmpleados()
  }, [cargarEmpleados])

  return (
    <main style={{ fontFamily: 'sans-serif', maxWidth: 960, margin: '2rem auto', padding: '0 1rem' }}>
      <h1>Gestión de empleados</h1>
      <FormularioEmpleado alGuardar={cargarEmpleados} />
      {errorLista && <p style={{ color: 'crimson' }}>{errorLista}</p>}
      <TablaEmpleados empleados={empleados} />
    </main>
  )
}

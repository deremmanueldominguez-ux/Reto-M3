import { useEffect, useState } from 'react'
import { obtenerDepartamentos, registrarEmpleado } from '../api.js'

const VACIO = { nombre: '', correo: '', puesto: '', departamento: '', fecha_ingreso: '' }

// Formulario de alta. Las validaciones las decide el backend (noValidate).
export default function FormularioEmpleado({ alGuardar }) {
  const [departamentos, setDepartamentos] = useState([])
  const [datos, setDatos] = useState(VACIO)
  const [exito, setExito] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    obtenerDepartamentos()
      .then((lista) => {
        setDepartamentos(lista)
        setDatos((previos) => (previos.departamento ? previos : { ...previos, departamento: lista[0] || '' }))
      })
      .catch((e) => setError(e.message))
  }, [])

  function cambiar(campo) {
    return (evento) => setDatos({ ...datos, [campo]: evento.target.value })
  }

  async function guardar(evento) {
    evento.preventDefault()
    setEnviando(true)
    setExito('')
    setError('')
    try {
      const empleado = await registrarEmpleado(datos)
      setExito(`Empleado registrado con número ${empleado.numero_empleado}`)
      setDatos({ ...VACIO, departamento: departamentos[0] || '' })
      if (alGuardar) alGuardar(empleado)
    } catch (e) {
      setError(e.message)
    } finally {
      setEnviando(false)
    }
  }

  const estiloCampo = { display: 'flex', flexDirection: 'column', marginBottom: '0.75rem' }

  return (
    <form noValidate onSubmit={guardar}>
      <h2>Registrar empleado</h2>

      <label style={estiloCampo}>
        Nombre
        <input data-testid="empleado-nombre" type="text" value={datos.nombre} onChange={cambiar('nombre')} />
      </label>

      <label style={estiloCampo}>
        Correo
        <input data-testid="empleado-correo" type="email" value={datos.correo} onChange={cambiar('correo')} />
      </label>

      <label style={estiloCampo}>
        Puesto
        <input data-testid="empleado-puesto" type="text" value={datos.puesto} onChange={cambiar('puesto')} />
      </label>

      <label style={estiloCampo}>
        Departamento
        <select data-testid="empleado-departamento" value={datos.departamento} onChange={cambiar('departamento')}>
          {departamentos.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </label>

      <label style={estiloCampo}>
        Fecha de ingreso
        <input
          data-testid="empleado-fecha-ingreso"
          type="date"
          value={datos.fecha_ingreso}
          onChange={cambiar('fecha_ingreso')}
        />
      </label>

      <button data-testid="empleado-guardar" type="submit" disabled={enviando}>
        Guardar
      </button>

      {exito && !error && (
        <p data-testid="mensaje-exito" role="status" style={{ color: 'green' }}>
          {exito}
        </p>
      )}
      {error && (
        <p data-testid="mensaje-error" role="alert" style={{ color: 'crimson' }}>
          {error}
        </p>
      )}
    </form>
  )
}

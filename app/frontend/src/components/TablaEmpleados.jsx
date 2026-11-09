// Directorio mínimo de empleados (HU-05: columna «Antigüedad»).
// La antigüedad se muestra tal como llega del backend: el cálculo vive solo allí.
const ETIQUETA_ESTADO = { activo: 'Activo', baja: 'Baja' }

export default function TablaEmpleados({ empleados }) {
  const celda = { borderBottom: '1px solid #ddd', padding: '0.35rem 0.5rem', textAlign: 'left' }

  return (
    <section>
      <h2>Empleados</h2>
      <table data-testid="tabla-empleados" style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th style={celda}>Número</th>
            <th style={celda}>Nombre</th>
            <th style={celda}>Departamento</th>
            <th style={celda}>Fecha de ingreso</th>
            <th style={celda}>Estado</th>
            <th style={celda}>Antigüedad</th>
          </tr>
        </thead>
        <tbody>
          {empleados.map((e) => (
            <tr key={e.id} data-testid={`fila-empleado-${e.id}`}>
              <td style={celda} data-testid={`numero-empleado-${e.id}`}>
                {e.numero_empleado}
              </td>
              <td style={celda}>{e.nombre}</td>
              <td style={celda}>{e.departamento}</td>
              <td style={celda}>{e.fecha_ingreso}</td>
              <td style={celda} data-testid={`estado-empleado-${e.id}`}>
                {ETIQUETA_ESTADO[e.estado] || e.estado}
              </td>
              <td style={celda} data-testid={`antiguedad-empleado-${e.id}`}>
                {e.antiguedad}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}

# Hoja de historias de usuario (pruebas de navegación)

Cada historia es una prueba Selenium que recorre el sitio como lo haría un rol
real. Verifica las pantallas y también las reglas de negocio que disparan los
datos ingresados. Las pruebas viven en `src/academica_test/tests/stories/` y se
corren en una pantalla virtual con el Makefile:

```bash
make check-selenium                     # verifica chromium, chromedriver, xvfb y PostgreSQL
make test-selenium                      # todas las historias, en paralelo, sin abrir ventanas
make test-selenium-single TEST=academica_test.tests.stories.test_estudiante.EstudianteStories.test_e2_matricula_grupo_pagado_y_pago_sinpe
make test-selenium-single TEST=... GIF=1   # además genera selenium-results/gif/<paso>.gif
make test-selenium-bitacora             # log completo y resumen en selenium-results/
make stories-gif                        # GIF de todas las historias (documentación)
```

Cuando un paso falla, el error dice `paso i/N de '<tramo>' (<descripción>) | xpath | url`,
y en `selenium-results/fallas/` quedan la captura PNG y el HTML de la página.

## Visitante y estudiante (`test_estudiante.py`)

| Historia | Recorrido | Reglas verificadas |
|---|---|---|
| **E1** Registro | Catálogo → "Registrarme" → contraseña débil (rechazada) → corrección → sesión iniciada | El usuario de acceso se toma del correo; se crean `User` y `Student` con la organización; correo `new_user_created_academy` |
| **E2** Matrícula pagada y Sinpe | Login **con el correo** → curso → "Matricularme" → "Pagar ahora" → reporte Sinpe | Factura por el costo del grupo; correo `email_enroll_success`; aviso a `PAYMENT_NOTIFICATION_MAIL`; la factura queda "en verificación" |
| **E3** Grupo gratuito | Curso → "Matricularme" → Mis cursos → historial | Sin factura; aparece en "Cursos Matriculados" y en el historial |
| **E4** Pago con tarjeta | `/bills/` → "Pagar con tarjeta" → checkout (simulado) → vuelve aprobado | Se crea una sola orden; la factura queda pagada; correo `email_invoice_academy` |
| **E5** Perfil y contraseña | Edita el perfil → administración envía la recuperación → cambia la contraseña con el enlace → login | El enlace se invalida después de usarlo (404); la contraseña nueva funciona |

## Flujos entre roles (`test_matricula_flujos.py`)

| Historia | Recorrido | Reglas verificadas |
|---|---|---|
| **F1** Flujo NORMAL | Estudiante se preinscribe → administración "Aperturar matrícula" → estudiante finaliza en Mis cursos | Preinscripción inactiva; correos `email_preenroll_success` y `email_open_group`; se genera la factura |
| **F2** AUTO_PREENROLL | Preinscripción → se abre la ventana de matrícula → "Matricularme" | La preinscripción queda activada sin intervención de administración |
| **F3** Cupo lleno | Grupo lleno → "Agregarme" a la lista de espera → segundo intento → administración matricula desde la lista | No se duplica en la lista; la fila sale de la lista al matricularse |
| **F4** Cupones | Cupón 50 % y 100 % → intento de exceder el 100 % → matrícula → cupones desde pre-inscritos | Factura a la mitad; beca completa = factura **pagada** con monto 0; no se supera el 100 %; solo reciben cupón los marcados |
| **F5** Rechazo | Administración rechaza la preinscripción → el estudiante la ve "Rechazada" | Correo `email_enroll_rejected` |
| **F7** Editar y eliminar cupón | Administración sube un cupón del 50 % al 100 % → lo elimina desde el modal | La factura se recalcula: pagada por beca con el 100 % y pendiente por el costo completo al eliminarlo; correo `coupon_code_notification_updated` |
| **F6** Depósito verificado | Estudiante sube el comprobante → superusuario "approve_payment" en el admin | La factura queda pagada y el depósito verificado; el estudiante no tiene pendientes |

## Administración académica (`test_admin_academico.py`)

| Historia | Recorrido | Reglas verificadas |
|---|---|---|
| **A1** Armar la oferta | Periodo (fechas invertidas → error) → categoría → curso (TinyMCE) → grupo (rangos traslapados → error) → catálogo público | Validaciones de fechas; el grupo aparece para visitantes, con costo y profesor |
| **A2** Cerrar y abrir grupo | "Cerrar grupo y notificar" → catálogo → "Abrir grupo y notificar" | Matrículas desactivadas; el grupo sale del catálogo; correos de cierre y apertura; no se notifica dos veces |
| **A3** Estudiantes | Búsqueda (select2) → alta sin contraseña → exportación → eliminación con modal | Correo `set_email_first_academy`; la exportación es un xlsx; un GET a la URL de borrado no borra (405); el modal borra por POST |
| **A4** Catálogos | Crea un país (ObjectCRUD) → edita el tipo de cambio del euro | El monto que se cobra en USD de una factura en EUR cambia con el tipo de cambio |
| **A5** Página con menú | Crea una página con "Agregar al menú" → el visitante la abre desde el menú | Se crea el `MenuItem` |
| **A6** Reportes | Recorre todos los reportes de `list_reports` | Ninguno da error ni muestra alertas de DataTables |

## Profesor (`test_profesor.py`)

| Historia | Recorrido | Reglas verificadas |
|---|---|---|
| **P1** Primer ingreso | Aviso "Es necesario llenar información…" → perfil → el aviso desaparece | La ruta antigua `edit_profile` lleva al mismo perfil |
| **P2** Calificar | Ve solo sus grupos → calificación en lote (modal) → calificación por fila en la página 2 de la tabla | Se guardan todas las páginas; `never_attend` marca que no asistió |

## Permisos y superusuario (`test_permisos.py`)

| Historia | Recorrido | Reglas verificadas |
|---|---|---|
| **R1** Estudiante | Sidebar y URLs de administración | Solo ve "Matrícula"; la administración pide otro usuario |
| **R2** Profesor | Sidebar → grupo ajeno | No ve Estudiantes, Pagos ni Catálogos; **no puede calificar grupos ajenos** |
| **R3** Administración académica | Sidebar → gestión de usuarios | Ve Académica, Catálogos y Pagos; no ve Administración |
| **S1** Superusuario | Crea un usuario "Profesores" → genera certificados | Se crea el `Professor`; correo `new_user_created_membership`; solo los aprobados reciben certificado (se omite si no está `rsvg-convert`) |

## Bugs que encontraron las historias (corregidos)

- Las plantillas propias (sidebar, barra superior, mensajes) no se usaban: `djgentelella` estaba antes de `membership_core` en `INSTALLED_APPS` (regresión de la migración a Django 6).
- Todos los borrados por enlace daban error 500 desde Django 4 (`DeleteView.get` → `post`).
- Los modales de borrado no abrían con Bootstrap 5 (`.modal()`).
- La asignación de cupones desde pre-inscritos fallaba y se enviaba a todas las filas; un cupón del 100 % dejaba la factura pendiente en 0.
- La calificación por fila solo guardaba la página visible de la tabla.
- Cualquier profesor podía calificar grupos ajenos; las APIs de calificación no validaban permisos.
- `edit_profile` fallaba al guardar (ahora lleva al perfil unificado).
- Las tablas de catálogos mostraban el alert "DataTables warning … actions".
- Al reportar un pago no había confirmación, y el aviso de verificación no estaba traducido.

### Segunda ronda

- Todos los borrados y desactivaciones son POST con CSRF (`js/post_links.js` + `data-post`). Un GET responde 405.
- Editar o eliminar un cupón recalcula las facturas afectadas (`matricula/coupons.py`). Un cupón aplicado a una factura pagada con dinero ya no se puede modificar.
- El reporte consolidado no contaba a quienes no completaron el curso: filtraba por `uncomplete` en lugar de `uncompleted`.
- Los reportes por organización contaban por subcadena: "org" sumaba también a "otraorg" y "Organiza". Ahora se compara el nombre exacto, sin distinguir mayúsculas.
- Los reportes de países y de organizaciones por país ahora se ordenan por nombre, así el orden ya no depende de la base de datos.
- Las 8 pruebas de reportes que fallaban desde antes se corrigieron:
  - dependían de la fecha del día;
  - usaban un estado inexistente;
  - su escenario asignaba campos a un modelo que no los tiene;
  - esperaban un formato de gráfico anterior.

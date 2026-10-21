export interface paths {
    "/api/auth/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Iniciar sesion
         * @description Valida un username o email y devuelve tokens de acceso.
         */
        post: operations["login"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/refresh": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Renovar tokens
         * @description Rota el refresh token y emite un nuevo par de tokens.
         */
        post: operations["refrescarToken"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/logout": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Cerrar sesion
         * @description Revoca el refresh token proporcionado.
         */
        post: operations["cerrarSesion"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/cambiar-password": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Cambiar contrasena
         * @description Actualiza la contrasena del usuario autenticado.
         */
        post: operations["cambiarPassword"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auth/me": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Obtener sesion actual
         * @description Devuelve los datos del usuario autenticado.
         */
        get: operations["obtenerSesion"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/habitaciones": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar habitaciones
         * @description Lista las habitaciones de la gestion hotelera, con filtros opcionales por estado, tipo y limpieza. Devuelve siempre un arreglo completo.
         */
        get: operations["listarHabitaciones"];
        put?: never;
        /**
         * Crear habitacion
         * @description Registra una habitacion nueva.
         */
        post: operations["crearHabitacion"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/habitaciones/room-rack": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Consultar room rack
         * @description Devuelve las habitaciones agrupadas por piso, con su estado operativo y limpieza, para el tablero de recepcion. Los pisos y las habitaciones vienen en orden ascendente.
         */
        get: operations["obtenerRoomRack"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/habitaciones/{habitacion_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Obtener habitacion
         * @description Obtiene una habitacion por su identificador.
         */
        get: operations["obtenerHabitacion"];
        /**
         * Actualizar habitacion
         * @description Actualiza los datos de una habitacion existente.
         */
        put: operations["actualizarHabitacion"];
        post?: never;
        /**
         * Eliminar habitacion
         * @description Elimina una habitacion sin reservas futuras.
         */
        delete: operations["eliminarHabitacion"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/habitaciones/{habitacion_id}/estado": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /**
         * Actualizar estado de habitacion
         * @description Cambia el estado operativo de una habitacion.
         */
        patch: operations["actualizarEstadoHabitacion"];
        trace?: never;
    };
    "/api/habitaciones/{habitacion_id}/limpieza": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /**
         * Actualizar limpieza de habitacion
         * @description Cambia el estado de limpieza de una habitacion. Se permite aunque la habitacion este OCUPADA.
         */
        patch: operations["actualizarLimpiezaHabitacion"];
        trace?: never;
    };
    "/api/habitaciones/{habitacion_id}/imagenes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Subir imagen de habitacion
         * @description Sube una imagen (JPEG, PNG o WEBP, maximo 5 MB) a una habitacion. Si es la primera imagen, queda marcada como principal.
         */
        post: operations["subirImagenHabitacion"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/habitaciones/{habitacion_id}/imagenes/{imagen_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        /**
         * Eliminar imagen de habitacion
         * @description Elimina una imagen de la habitacion y su archivo. Si era la principal, promueve otra imagen como principal.
         */
        delete: operations["eliminarImagenHabitacion"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/habitaciones/{habitacion_id}/imagenes/{imagen_id}/principal": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /**
         * Marcar imagen principal
         * @description Marca una imagen de la habitacion como principal.
         */
        patch: operations["marcarImagenPrincipal"];
        trace?: never;
    };
    "/api/huespedes": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar huespedes
         * @description Lista paginada de huespedes con busqueda y filtros.
         */
        get: operations["listarHuespedes"];
        put?: never;
        /**
         * Crear huesped
         * @description Registra un huesped nuevo con documento unico por tipo.
         */
        post: operations["crearHuesped"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/huespedes/{huesped_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Obtener huesped
         * @description Obtiene un huesped por su identificador.
         */
        get: operations["obtenerHuesped"];
        /**
         * Actualizar huesped
         * @description Actualiza los datos de un huesped existente.
         */
        put: operations["actualizarHuesped"];
        post?: never;
        /**
         * Eliminar huesped
         * @description Elimina un huesped solo si no tiene reservas. Solo ADMIN.
         */
        delete: operations["eliminarHuesped"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/huespedes/{huesped_id}/reservas": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar reservas del huesped
         * @description Lista paginada de reservas del huesped por entrada descendente.
         */
        get: operations["listarReservasDeHuesped"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/usuarios": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar usuarios
         * @description Lista usuarios con paginacion y filtros por rol, estado y texto.
         */
        get: operations["listarUsuarios"];
        put?: never;
        /**
         * Crear usuario
         * @description Crea un usuario y registra la accion en la bitacora.
         */
        post: operations["crearUsuario"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/usuarios/{usuario_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Obtener usuario
         * @description Obtiene un usuario por su identificador.
         */
        get: operations["obtenerUsuario"];
        /**
         * Actualizar usuario
         * @description Actualiza los datos de un usuario existente.
         */
        put: operations["actualizarUsuario"];
        post?: never;
        /**
         * Eliminar usuario
         * @description Elimina fisicamente una cuenta creada por error.
         */
        delete: operations["eliminarUsuario"];
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/usuarios/{usuario_id}/desactivar": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Desactivar usuario
         * @description Desactiva una cuenta sin eliminar su historial.
         */
        post: operations["desactivarUsuario"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/usuarios/{usuario_id}/reactivar": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Reactivar usuario
         * @description Reactiva una cuenta de usuario desactivada.
         */
        post: operations["reactivarUsuario"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/catalogos": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar catalogos
         * @description Lista los catalogos disponibles para la aplicacion.
         */
        get: operations["listarCatalogos"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/catalogos/{nombre}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Obtener catalogo
         * @description Obtiene las opciones de un catalogo por su nombre.
         */
        get: operations["obtenerCatalogo"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/auditoria": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar auditoria
         * @description Consulta eventos recientes de auditoria con filtros opcionales.
         */
        get: operations["listarAuditoria"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/disponibilidad": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Consultar disponibilidad de habitaciones
         * @description Lista las habitaciones activas que estan libres en el rango [entrada, salida). Una salida el mismo dia que otra entrada no se considera solapamiento. Las reservas CANCELADA y NO_SHOW no bloquean.
         */
        get: operations["consultarDisponibilidad"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar reservas
         * @description Lista las reservas de forma paginada, de la fecha de entrada mas reciente a la mas antigua, con filtros opcionales por estado, habitacion, huesped y rango de fechas de entrada.
         */
        get: operations["listarReservas"];
        put?: never;
        /**
         * Crear reserva
         * @description Crea una reserva en estado PENDIENTE. Valida que el huesped y la habitacion existan, que la habitacion este activa, que tenga capacidad suficiente, que la salida sea posterior a la entrada, que la entrada no sea anterior a hoy en Bogota y que no haya solapamiento. El precio por noche queda congelado con la tarifa vigente.
         */
        post: operations["crearReserva"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Obtener reserva
         * @description Obtiene una reserva por su identificador, con un resumen del huesped y de la habitacion.
         */
        get: operations["obtenerReserva"];
        /**
         * Actualizar reserva
         * @description Actualiza una reserva que este en PENDIENTE o CONFIRMADA. Revalida huesped, habitacion, capacidad y solapamiento excluyendo la propia reserva. Si cambian las fechas o la habitacion, el precio por noche se recalcula con la tarifa vigente y el total se vuelve a calcular.
         */
        put: operations["actualizarReserva"];
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/confirmar": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Confirmar reserva
         * @description Cambia una reserva de PENDIENTE a CONFIRMADA. Revalida que la habitacion siga activa y que no haya solapamiento excluyendo la propia reserva. La fecha de entrada no puede ser anterior a hoy en Bogota.
         */
        post: operations["confirmarReserva"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/cancelar": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Cancelar reserva
         * @description Cambia una reserva de PENDIENTE o CONFIRMADA a CANCELADA. Requiere un motivo de 3 a 500 caracteres (se recortan espacios). La habitacion queda libre para nuevas reservas.
         */
        post: operations["cancelarReserva"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/no-show": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Marcar no-show
         * @description Cambia una reserva de CONFIRMADA a NO_SHOW. Solo permitido si hoy (en Bogota) es mayor o igual a la fecha de entrada. La habitacion queda libre para nuevas reservas.
         */
        post: operations["noShowReserva"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/check-in": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Registrar check-in
         * @description Cambia una reserva de CONFIRMADA a CHECK_IN y deja la habitacion OCUPADA. La fecha de entrada no puede ser posterior a hoy y la estancia no puede estar vencida. La habitacion debe estar DISPONIBLE y LIMPIA.
         */
        post: operations["checkInReserva"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/check-out": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Registrar check-out
         * @description Cambia una reserva de CHECK_IN a CHECK_OUT y deja la habitacion SUCIA. No cambia la fecha de salida ni el total: lo facturado sigue siendo lo reservado. La respuesta incluye el resultado economico de la cuenta (total, pagado y saldo pendiente), calculado con calcular_cuenta. El check-out no se bloquea por saldo pendiente: el saldo se expone para que recepcion lo gestione.
         */
        post: operations["checkOutReserva"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/extender": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Extender estancia
         * @description Alarga la estancia de una reserva en CHECK_IN. La nueva fecha de salida debe ser posterior a la actual, no puede solaparse con otra reserva de la misma habitacion y recalcula el total como noches por el precio noche aplicado, sin cambiar el precio congelado. Por decision de negocio no valida el estado de la habitacion (puede seguir en mantenimiento mientras el huesped esta alojado) ni que la fecha de salida actual siga en el futuro: una estancia cuya salida ya paso tambien puede extenderse.
         */
        post: operations["extenderReserva"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/pagos": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar pagos de una reserva
         * @description Devuelve la lista paginada de pagos asociados a la reserva. Incluye un filtro opcional para ver solo los vigentes (no anulados).
         */
        get: operations["listarPagos"];
        put?: never;
        /**
         * Crear pago en una reserva
         * @description Registra un nuevo pago en la reserva. Permitido en todos los estados excepto CANCELADA y NO_SHOW.
         */
        post: operations["crearPago"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/pagos/{pago_id}/anular": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Anular un pago
         * @description Marca el pago como anulado sin borrar el registro. Requiere rol administrador.
         */
        post: operations["anularPago"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/consumos": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Listar consumos de una reserva
         * @description Devuelve la lista paginada de consumos asociados a la reserva. Incluye un filtro opcional para ver solo los vigentes (no anulados).
         */
        get: operations["listarConsumos"];
        put?: never;
        /**
         * Crear consumo en una reserva
         * @description Registra un nuevo consumo (cargo) en la reserva. Solo permitido si la reserva esta en estado CHECK_IN.
         */
        post: operations["crearConsumo"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/reservas/{reserva_id}/consumos/{consumo_id}/anular": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Anular un consumo
         * @description Marca el consumo como anulado sin borrar el registro. Requiere rol administrador.
         */
        post: operations["anularConsumo"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/cuentas/{reserva_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Obtener cuenta de una reserva
         * @description Devuelve el detalle completo de la cuenta de la reserva: total de alojamiento (noches x tarifa), consumos vigentes, pagos vigentes (excluye reembolsos), saldo pendiente y listado completo de consumos y pagos con su estado de anulación.
         */
        get: operations["obtenerCuenta"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/dashboard": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Resumen operativo del hotel
         * @description Devuelve los indicadores del dia para operar el hotel: reservas activas, reservas pendientes de check-in, huespedes alojados, check-outs del dia, habitaciones disponibles, ocupadas y en mantenimiento, y cuentas con saldo pendiente. Usa los estados y las cuentas que ya existen, sin tablas nuevas.
         */
        get: operations["obtenerResumenDashboard"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Comprobar estado del servicio
         * @description Verifica que la API y la base de datos esten disponibles.
         */
        get: operations["healthCheck"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** AuditoriaRead */
        AuditoriaRead: {
            /** Id */
            id: number;
            /** Usuarioid */
            usuarioId: number | null;
            /** Accion */
            accion: string;
            /** Entidad */
            entidad: string;
            /** Entidadid */
            entidadId: number | null;
            /** Ip */
            ip: string | null;
            /** Detalle */
            detalle: {
                [key: string]: unknown;
            } | null;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
        };
        /** Body_subirImagenHabitacion */
        Body_subirImagenHabitacion: {
            /**
             * Archivo
             * @description Archivo de imagen a subir
             */
            archivo: string;
        };
        /** CambiarPasswordRequest */
        CambiarPasswordRequest: {
            /** Passwordactual */
            passwordActual: string;
            /** Passwordnuevo */
            passwordNuevo: string;
        };
        /** CancelarReservaRequest */
        CancelarReservaRequest: {
            /** Motivo */
            motivo: string;
        };
        /** CatalogoRead */
        CatalogoRead: {
            /** Nombre */
            nombre: string;
            /** Etiqueta */
            etiqueta: string;
            /** Valores */
            valores: string[];
        };
        /**
         * CheckOutRead
         * @description Reserva en CHECK_OUT con el resultado economico de su cuenta.
         */
        CheckOutRead: {
            /** Id */
            id: number;
            /** Codigo */
            codigo: string;
            huesped: components["schemas"]["HuespedResumen"];
            habitacion: components["schemas"]["HabitacionResumen"];
            /**
             * Fechaentrada
             * Format: date
             */
            fechaEntrada: string;
            /**
             * Fechasalida
             * Format: date
             */
            fechaSalida: string;
            /** Numerohuespedes */
            numeroHuespedes: number;
            estado: components["schemas"]["EstadoReserva"];
            /** Precionocheaplicado */
            precioNocheAplicado: number;
            /** Totalestimado */
            totalEstimado: number;
            /** Observaciones */
            observaciones: string | null;
            /** Motivocancelacion */
            motivoCancelacion: string | null;
            /** Checkinreal */
            checkInReal: string | null;
            /** Checkoutreal */
            checkOutReal: string | null;
            /** Creadapor */
            creadaPor: number;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            /**
             * Updatedat
             * Format: date-time
             */
            updatedAt: string;
            /**
             * Totalcuenta
             * @description Alojamiento + consumos vigentes
             */
            totalCuenta: number;
            /**
             * Totalpagado
             * @description Pagos vigentes; los reembolsos se restan
             */
            totalPagado: number;
            /**
             * Saldopendiente
             * @description Total de la cuenta menos lo ya pagado
             */
            saldoPendiente: number;
        };
        /** ConsumoAnular */
        ConsumoAnular: {
            /** Motivoanulacion */
            motivoAnulacion: string;
        };
        /** ConsumoCreate */
        ConsumoCreate: {
            /** Descripcion */
            descripcion: string;
            /** Cantidad */
            cantidad: number;
            /** Preciounitario */
            precioUnitario: number | string;
        };
        /** ConsumoRead */
        ConsumoRead: {
            /** Id */
            id: number;
            /** Reservaid */
            reservaId: number;
            /** Descripcion */
            descripcion: string;
            /** Cantidad */
            cantidad: number;
            /** Preciounitario */
            precioUnitario: number;
            /** Anulado */
            anulado: boolean;
            /** Registradopor */
            registradoPor: number;
            /** Anuladopor */
            anuladoPor?: number | null;
            /** Anuladoen */
            anuladoEn?: string | null;
            /** Motivoanulacion */
            motivoAnulacion?: string | null;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            /**
             * Updatedat
             * Format: date-time
             */
            updatedAt: string;
            /** Total */
            readonly total: number;
        };
        /** CuentaDetalleConsumo */
        CuentaDetalleConsumo: {
            /** Id */
            id: number;
            /** Reservaid */
            reservaId: number;
            /** Descripcion */
            descripcion: string;
            /** Cantidad */
            cantidad: number;
            /** Preciounitario */
            precioUnitario: number;
            /** Anulado */
            anulado: boolean;
            /** Registradopor */
            registradoPor: number;
            /** Anuladopor */
            anuladoPor?: number | null;
            /** Anuladoen */
            anuladoEn?: string | null;
            /** Motivoanulacion */
            motivoAnulacion?: string | null;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            /**
             * Updatedat
             * Format: date-time
             */
            updatedAt: string;
        };
        /** CuentaDetallePago */
        CuentaDetallePago: {
            /** Id */
            id: number;
            /** Reservaid */
            reservaId: number;
            /** Monto */
            monto: number;
            metodo: components["schemas"]["MetodoPago"];
            tipo: components["schemas"]["TipoPago"];
            /** Referencia */
            referencia?: string | null;
            /** Anulado */
            anulado: boolean;
            /** Motivoanulacion */
            motivoAnulacion?: string | null;
            /**
             * Fechapago
             * Format: date-time
             */
            fechaPago: string;
            /** Registradopor */
            registradoPor: number;
            /** Anuladopor */
            anuladoPor?: number | null;
            /** Anuladoen */
            anuladoEn?: string | null;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            /**
             * Updatedat
             * Format: date-time
             */
            updatedAt: string;
        };
        /** CuentaRead */
        CuentaRead: {
            /**
             * Totalalojamiento
             * @description Noches x precio_noche_aplicado
             */
            totalAlojamiento: number;
            /**
             * Totalconsumosvigentes
             * @description Suma de consumos no anulados
             */
            totalConsumosVigentes: number;
            /**
             * Totalpagosvigentes
             * @description Suma de pagos no anulados (excluye REEMBOLSO)
             */
            totalPagosVigentes: number;
            /**
             * Saldopendiente
             * @description total_alojamiento + total_consumos_vigentes - total_pagos_vigentes
             */
            saldoPendiente: number;
            /** Detalleconsumos */
            detalleConsumos: components["schemas"]["CuentaDetalleConsumo"][];
            /** Detallepagos */
            detallePagos: components["schemas"]["CuentaDetallePago"][];
        };
        /**
         * DashboardRead
         * @description Resumen operativo y financiero del hotel para un día concreto.
         */
        DashboardRead: {
            /**
             * Reservasactivas
             * @description Reservas en PENDIENTE, CONFIRMADA o CHECK_IN
             */
            reservasActivas: number;
            /**
             * Reservaspendientescheckin
             * @description Reservas que aun no han hecho check-in (PENDIENTE o CONFIRMADA)
             */
            reservasPendientesCheckIn: number;
            /**
             * Huespedesalojados
             * @description Suma de numero_huespedes de las reservas en CHECK_IN
             */
            huespedesAlojados: number;
            /**
             * Checkoutsdeldia
             * @description Check-outs con check_out_real dentro del dia en America/Bogota
             */
            checkOutsDelDia: number;
            /**
             * Habitacionesdisponibles
             * @description Habitaciones en estado DISPONIBLE
             */
            habitacionesDisponibles: number;
            /**
             * Habitacionesocupadas
             * @description Habitaciones en estado OCUPADA
             */
            habitacionesOcupadas: number;
            /**
             * Habitacionesenmantenimiento
             * @description Habitaciones en estado MANTENIMIENTO
             */
            habitacionesEnMantenimiento: number;
            /**
             * Cuentasconsaldopendiente
             * @description Reservas con saldo pendiente mayor que cero
             */
            cuentasConSaldoPendiente: number;
            /**
             * Tasaocupacion
             * @description Porcentaje de ocupacion: habitaciones ocupadas sobre operativas (disponibles + ocupadas), redondeado a 1 decimal
             */
            tasaOcupacion: number;
            /**
             * Ingresosdeldia
             * @description Recaudo neto del dia: pagos vigentes con fecha_pago de hoy en America/Bogota, restando los reembolsos
             */
            ingresosDelDia: number;
            /**
             * Revpar
             * @description Ingresos del dia por habitacion operativa (disponibles + ocupadas)
             */
            revpar: number;
            /**
             * Balancecaja
             * @description Saldo neto de caja acumulado: pagos vigentes de todos los tiempos menos reembolsos vigentes
             */
            balanceCaja: number;
        };
        /**
         * EstadoHabitacion
         * @enum {string}
         */
        EstadoHabitacion: "DISPONIBLE" | "OCUPADA" | "MANTENIMIENTO";
        /**
         * EstadoLimpieza
         * @enum {string}
         */
        EstadoLimpieza: "LIMPIA" | "SUCIA";
        /**
         * EstadoReserva
         * @enum {string}
         */
        EstadoReserva: "PENDIENTE" | "CONFIRMADA" | "CHECK_IN" | "CHECK_OUT" | "CANCELADA" | "NO_SHOW";
        /** ExtenderReservaRequest */
        ExtenderReservaRequest: {
            /**
             * Nuevafechasalida
             * Format: date
             */
            nuevaFechaSalida: string;
        };
        /** HabitacionCreate */
        HabitacionCreate: {
            /** Numero */
            numero: number;
            /** Piso */
            piso: number;
            tipo: components["schemas"]["TipoHabitacion"];
            /** Capacidad */
            capacidad: number;
            /** Preciopornoche */
            precioPorNoche: number | string;
            /** @default DISPONIBLE */
            estado: components["schemas"]["EstadoHabitacion"];
            /** Descripcion */
            descripcion?: string | null;
        };
        /** HabitacionEstado */
        HabitacionEstado: {
            estado: components["schemas"]["EstadoHabitacion"];
        };
        /** HabitacionImagenRead */
        HabitacionImagenRead: {
            /** Id */
            id: number;
            /** Orden */
            orden: number;
            /** Esprincipal */
            esPrincipal: boolean;
            /** Url */
            readonly url: string;
        };
        /** HabitacionLimpieza */
        HabitacionLimpieza: {
            limpieza: components["schemas"]["EstadoLimpieza"];
        };
        /** HabitacionRead */
        HabitacionRead: {
            /** Numero */
            numero: number;
            /** Piso */
            piso: number;
            tipo: components["schemas"]["TipoHabitacion"];
            /** Capacidad */
            capacidad: number;
            /** Preciopornoche */
            precioPorNoche: number;
            /** @default DISPONIBLE */
            estado: components["schemas"]["EstadoHabitacion"];
            /** Descripcion */
            descripcion?: string | null;
            /** Id */
            id: number;
            limpieza: components["schemas"]["EstadoLimpieza"];
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            /**
             * Updatedat
             * Format: date-time
             */
            updatedAt: string;
            /**
             * Imagenes
             * @default []
             */
            imagenes: components["schemas"]["HabitacionImagenRead"][];
            /** Imagenprincipalurl */
            readonly imagenPrincipalUrl: string | null;
        };
        /** HabitacionResumen */
        HabitacionResumen: {
            /** Id */
            id: number;
            /** Numero */
            numero: number;
            tipo: components["schemas"]["TipoHabitacion"];
            /** Capacidad */
            capacidad: number;
            /** Preciopornoche */
            precioPorNoche: number;
        };
        /** HabitacionUpdate */
        HabitacionUpdate: {
            /** Numero */
            numero: number;
            /** Piso */
            piso: number;
            tipo: components["schemas"]["TipoHabitacion"];
            /** Capacidad */
            capacidad: number;
            /** Preciopornoche */
            precioPorNoche: number | string;
            /** @default DISPONIBLE */
            estado: components["schemas"]["EstadoHabitacion"];
            /** Descripcion */
            descripcion?: string | null;
        };
        /** HuespedCreate */
        HuespedCreate: {
            tipoDocumento: components["schemas"]["TipoDocumento"];
            /** Numerodocumento */
            numeroDocumento: string;
            /** Nombres */
            nombres: string;
            /** Apellidos */
            apellidos: string;
            /** Email */
            email?: string | null;
            /** Telefono */
            telefono?: string | null;
            /** Nacionalidad */
            nacionalidad?: string | null;
            /** Fechanacimiento */
            fechaNacimiento?: string | null;
            /** Direccion */
            direccion?: string | null;
            /** Observaciones */
            observaciones?: string | null;
        };
        /** HuespedRead */
        HuespedRead: {
            tipoDocumento: components["schemas"]["TipoDocumento"];
            /** Numerodocumento */
            numeroDocumento: string;
            /** Nombres */
            nombres: string;
            /** Apellidos */
            apellidos: string;
            /** Email */
            email?: string | null;
            /** Telefono */
            telefono?: string | null;
            /** Nacionalidad */
            nacionalidad?: string | null;
            /** Fechanacimiento */
            fechaNacimiento?: string | null;
            /** Direccion */
            direccion?: string | null;
            /** Observaciones */
            observaciones?: string | null;
            /** Id */
            id: number;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            /**
             * Updatedat
             * Format: date-time
             */
            updatedAt: string;
        };
        /** HuespedResumen */
        HuespedResumen: {
            /** Id */
            id: number;
            /** Nombres */
            nombres: string;
            /** Apellidos */
            apellidos: string;
            tipoDocumento: components["schemas"]["TipoDocumento"];
            /** Numerodocumento */
            numeroDocumento: string;
        };
        /** HuespedUpdate */
        HuespedUpdate: {
            tipoDocumento: components["schemas"]["TipoDocumento"];
            /** Numerodocumento */
            numeroDocumento: string;
            /** Nombres */
            nombres: string;
            /** Apellidos */
            apellidos: string;
            /** Email */
            email?: string | null;
            /** Telefono */
            telefono?: string | null;
            /** Nacionalidad */
            nacionalidad?: string | null;
            /** Fechanacimiento */
            fechaNacimiento?: string | null;
            /** Direccion */
            direccion?: string | null;
            /** Observaciones */
            observaciones?: string | null;
        };
        /** LoginRequest */
        LoginRequest: {
            /** Username */
            username?: string | null;
            /** Email */
            email?: string | null;
            /** Password */
            password: string;
        };
        /** LoginResponse */
        LoginResponse: {
            /** Token */
            token: string;
            /** Refreshtoken */
            refreshToken: string;
            /**
             * Tokentype
             * @default bearer
             */
            tokenType: string;
            /** Expiresin */
            expiresIn: number;
            /** Id */
            id: number;
            /** Username */
            username: string;
            /**
             * Email
             * Format: email
             */
            email: string;
            /** Nombre */
            nombre: string;
            role: components["schemas"]["RolUsuario"];
        };
        /**
         * MetodoPago
         * @enum {string}
         */
        MetodoPago: "EFECTIVO" | "TARJETA" | "TRANSFERENCIA" | "OTRO";
        /** Pagina[AuditoriaRead] */
        Pagina_AuditoriaRead_: {
            /** Items */
            items: components["schemas"]["AuditoriaRead"][];
            /** Total */
            total: number;
            /** Pagina */
            pagina: number;
            /** Tamano */
            tamano: number;
        };
        /** Pagina[ConsumoRead] */
        Pagina_ConsumoRead_: {
            /** Items */
            items: components["schemas"]["ConsumoRead"][];
            /** Total */
            total: number;
            /** Pagina */
            pagina: number;
            /** Tamano */
            tamano: number;
        };
        /** Pagina[HuespedRead] */
        Pagina_HuespedRead_: {
            /** Items */
            items: components["schemas"]["HuespedRead"][];
            /** Total */
            total: number;
            /** Pagina */
            pagina: number;
            /** Tamano */
            tamano: number;
        };
        /** Pagina[PagoRead] */
        Pagina_PagoRead_: {
            /** Items */
            items: components["schemas"]["PagoRead"][];
            /** Total */
            total: number;
            /** Pagina */
            pagina: number;
            /** Tamano */
            tamano: number;
        };
        /** Pagina[ReservaDeHuespedRead] */
        Pagina_ReservaDeHuespedRead_: {
            /** Items */
            items: components["schemas"]["ReservaDeHuespedRead"][];
            /** Total */
            total: number;
            /** Pagina */
            pagina: number;
            /** Tamano */
            tamano: number;
        };
        /** Pagina[ReservaRead] */
        Pagina_ReservaRead_: {
            /** Items */
            items: components["schemas"]["ReservaRead"][];
            /** Total */
            total: number;
            /** Pagina */
            pagina: number;
            /** Tamano */
            tamano: number;
        };
        /** Pagina[UsuarioRead] */
        Pagina_UsuarioRead_: {
            /** Items */
            items: components["schemas"]["UsuarioRead"][];
            /** Total */
            total: number;
            /** Pagina */
            pagina: number;
            /** Tamano */
            tamano: number;
        };
        /** PagoAnular */
        PagoAnular: {
            /** Motivoanulacion */
            motivoAnulacion: string;
        };
        /** PagoCreate */
        PagoCreate: {
            /** Monto */
            monto: number | string;
            metodo: components["schemas"]["MetodoPago"];
            tipo: components["schemas"]["TipoPago"];
            /** Referencia */
            referencia?: string | null;
            /** Fechapago */
            fechaPago?: string | null;
        };
        /** PagoRead */
        PagoRead: {
            /** Id */
            id: number;
            /** Reservaid */
            reservaId: number;
            /** Monto */
            monto: number;
            metodo: components["schemas"]["MetodoPago"];
            tipo: components["schemas"]["TipoPago"];
            /** Referencia */
            referencia?: string | null;
            /** Anulado */
            anulado: boolean;
            /** Motivoanulacion */
            motivoAnulacion?: string | null;
            /**
             * Fechapago
             * Format: date-time
             */
            fechaPago: string;
            /** Registradopor */
            registradoPor: number;
            /** Anuladopor */
            anuladoPor?: number | null;
            /** Anuladoen */
            anuladoEn?: string | null;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            /**
             * Updatedat
             * Format: date-time
             */
            updatedAt: string;
        };
        /** RefreshRequest */
        RefreshRequest: {
            /** Refreshtoken */
            refreshToken: string;
        };
        /** ReservaCreate */
        ReservaCreate: {
            /** Huespedid */
            huespedId: number;
            /** Habitacionid */
            habitacionId: number;
            /**
             * Fechaentrada
             * Format: date
             */
            fechaEntrada: string;
            /**
             * Fechasalida
             * Format: date
             */
            fechaSalida: string;
            /** Numerohuespedes */
            numeroHuespedes: number;
            /** Observaciones */
            observaciones?: string | null;
        };
        /** ReservaDeHuespedRead */
        ReservaDeHuespedRead: {
            /** Id */
            id: number;
            /** Codigo */
            codigo: string;
            /** Habitacionid */
            habitacionId: number;
            /**
             * Fechaentrada
             * Format: date
             */
            fechaEntrada: string;
            /**
             * Fechasalida
             * Format: date
             */
            fechaSalida: string;
            estado: components["schemas"]["EstadoReserva"];
        };
        /** ReservaRead */
        ReservaRead: {
            /** Id */
            id: number;
            /** Codigo */
            codigo: string;
            huesped: components["schemas"]["HuespedResumen"];
            habitacion: components["schemas"]["HabitacionResumen"];
            /**
             * Fechaentrada
             * Format: date
             */
            fechaEntrada: string;
            /**
             * Fechasalida
             * Format: date
             */
            fechaSalida: string;
            /** Numerohuespedes */
            numeroHuespedes: number;
            estado: components["schemas"]["EstadoReserva"];
            /** Precionocheaplicado */
            precioNocheAplicado: number;
            /** Totalestimado */
            totalEstimado: number;
            /** Observaciones */
            observaciones: string | null;
            /** Motivocancelacion */
            motivoCancelacion: string | null;
            /** Checkinreal */
            checkInReal: string | null;
            /** Checkoutreal */
            checkOutReal: string | null;
            /** Creadapor */
            creadaPor: number;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            /**
             * Updatedat
             * Format: date-time
             */
            updatedAt: string;
        };
        /** ReservaUpdate */
        ReservaUpdate: {
            /** Huespedid */
            huespedId?: number | null;
            /** Habitacionid */
            habitacionId?: number | null;
            /** Fechaentrada */
            fechaEntrada?: string | null;
            /** Fechasalida */
            fechaSalida?: string | null;
            /** Numerohuespedes */
            numeroHuespedes?: number | null;
            /** Observaciones */
            observaciones?: string | null;
        };
        /**
         * RolUsuario
         * @enum {string}
         */
        RolUsuario: "ADMIN" | "RECEPCION";
        /**
         * RoomRackHabitacion
         * @description Resumen de una habitacion para el tablero (room rack) de recepcion.
         */
        RoomRackHabitacion: {
            /** Id */
            id: number;
            /** Numero */
            numero: number;
            /** Piso */
            piso: number;
            tipo: components["schemas"]["TipoHabitacion"];
            /** Capacidad */
            capacidad: number;
            /** Preciopornoche */
            precioPorNoche: number;
            estado: components["schemas"]["EstadoHabitacion"];
            limpieza: components["schemas"]["EstadoLimpieza"];
        };
        /**
         * RoomRackPiso
         * @description Habitaciones de un piso del hotel, ordenadas por numero.
         */
        RoomRackPiso: {
            /** Piso */
            piso: number;
            /** Habitaciones */
            habitaciones: components["schemas"]["RoomRackHabitacion"][];
        };
        /**
         * TipoDocumento
         * @enum {string}
         */
        TipoDocumento: "CC" | "CE" | "PASAPORTE" | "TI" | "OTRO";
        /**
         * TipoHabitacion
         * @enum {string}
         */
        TipoHabitacion: "SIMPLE" | "DOBLE" | "SUITE" | "PRESIDENCIAL";
        /**
         * TipoPago
         * @enum {string}
         */
        TipoPago: "ABONO" | "PAGO_FINAL" | "REEMBOLSO";
        /** TokenPair */
        TokenPair: {
            /** Token */
            token: string;
            /** Refreshtoken */
            refreshToken: string;
            /**
             * Tokentype
             * @default bearer
             */
            tokenType: string;
            /** Expiresin */
            expiresIn: number;
        };
        /** UsuarioActualizar */
        UsuarioActualizar: {
            /** Username */
            username?: string | null;
            /** Email */
            email?: string | null;
            /** Nombre */
            nombre?: string | null;
            role?: components["schemas"]["RolUsuario"] | null;
            /** Activo */
            activo?: boolean | null;
        };
        /** UsuarioCrear */
        UsuarioCrear: {
            /** Username */
            username: string;
            /**
             * Email
             * Format: email
             */
            email: string;
            /** Nombre */
            nombre: string;
            /** Password */
            password: string;
            /** @default RECEPCION */
            role: components["schemas"]["RolUsuario"];
        };
        /** UsuarioRead */
        UsuarioRead: {
            /** Id */
            id: number;
            /** Username */
            username: string;
            /**
             * Email
             * Format: email
             */
            email: string;
            /** Nombre */
            nombre: string;
            role: components["schemas"]["RolUsuario"];
            /** Activo */
            activo: boolean;
            /**
             * Createdat
             * Format: date-time
             */
            createdAt: string;
            /**
             * Updatedat
             * Format: date-time
             */
            updatedAt: string;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    login: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LoginRequest"];
            };
        };
        responses: {
            /** @description Sesion iniciada */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LoginResponse"];
                };
            };
            /** @description Credenciales incorrectas */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    refrescarToken: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RefreshRequest"];
            };
        };
        responses: {
            /** @description Tokens renovados */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TokenPair"];
                };
            };
            /** @description Refresh token invalido */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    cerrarSesion: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["RefreshRequest"];
            };
        };
        responses: {
            /** @description Sesion cerrada */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Refresh token invalido */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    cambiarPassword: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CambiarPasswordRequest"];
            };
        };
        responses: {
            /** @description Contrasena actualizada */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": {
                        [key: string]: string;
                    };
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtenerSesion: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Sesion actual */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UsuarioRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listarHabitaciones: {
        parameters: {
            query?: {
                estado?: components["schemas"]["EstadoHabitacion"] | null;
                tipo?: components["schemas"]["TipoHabitacion"] | null;
                limpieza?: components["schemas"]["EstadoLimpieza"] | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Listado de habitaciones */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HabitacionRead"][];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar habitaciones */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Filtro invalido (estado, tipo o limpieza) */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    crearHabitacion: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["HabitacionCreate"];
            };
        };
        responses: {
            /** @description Habitacion creada */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HabitacionRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El numero de habitacion ya existe */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Datos de habitacion invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtenerRoomRack: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Habitaciones agrupadas por piso */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["RoomRackPiso"][];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar el room rack */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtenerHabitacion: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                habitacion_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Habitacion encontrada */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HabitacionRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar habitaciones */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Habitacion no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    actualizarHabitacion: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                habitacion_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["HabitacionUpdate"];
            };
        };
        responses: {
            /** @description Habitacion actualizada */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HabitacionRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Habitacion no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El numero de habitacion ya existe */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Datos de habitacion invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    eliminarHabitacion: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                habitacion_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Habitacion eliminada */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Habitacion no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La habitacion tiene reservas futuras */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    actualizarEstadoHabitacion: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                habitacion_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["HabitacionEstado"];
            };
        };
        responses: {
            /** @description Estado actualizado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HabitacionRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para cambiar el estado */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Habitacion no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Estado de habitacion invalido */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    actualizarLimpiezaHabitacion: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                habitacion_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["HabitacionLimpieza"];
            };
        };
        responses: {
            /** @description Limpieza actualizada */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HabitacionRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para cambiar la limpieza */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Habitacion no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Estado de limpieza invalido */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    subirImagenHabitacion: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                habitacion_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "multipart/form-data": components["schemas"]["Body_subirImagenHabitacion"];
            };
        };
        responses: {
            /** @description Imagen subida */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HabitacionImagenRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Habitacion no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La habitacion ya alcanzo el maximo de imagenes */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Formato no permitido o archivo demasiado grande */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    eliminarImagenHabitacion: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                habitacion_id: number;
                imagen_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Imagen eliminada */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Habitacion o imagen no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    marcarImagenPrincipal: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                habitacion_id: number;
                imagen_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Imagen marcada como principal */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HabitacionImagenRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Habitacion o imagen no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listarHuespedes: {
        parameters: {
            query?: {
                /** @description Texto en nombres, apellidos o documento */
                q?: string | null;
                tipoDocumento?: components["schemas"]["TipoDocumento"] | null;
                numeroDocumento?: string | null;
                /** @description Numero de pagina */
                pagina?: number;
                /** @description Registros por pagina */
                tamano?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Pagina de huespedes */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Pagina_HuespedRead_"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar huespedes */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    crearHuesped: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["HuespedCreate"];
            };
        };
        responses: {
            /** @description Huesped creado */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HuespedRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para crear huespedes */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Documento duplicado */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtenerHuesped: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                huesped_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Huesped encontrado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HuespedRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar huespedes */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Huesped no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    actualizarHuesped: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                huesped_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["HuespedUpdate"];
            };
        };
        responses: {
            /** @description Huesped actualizado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HuespedRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para actualizar huespedes */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Huesped no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Documento duplicado */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    eliminarHuesped: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                huesped_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Huesped eliminado */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Huesped no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El huesped tiene reservas */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listarReservasDeHuesped: {
        parameters: {
            query?: {
                /** @description Numero de pagina */
                pagina?: number;
                /** @description Registros por pagina */
                tamano?: number;
            };
            header?: never;
            path: {
                huesped_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Pagina de reservas */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Pagina_ReservaDeHuespedRead_"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar reservas */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Huesped no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listarUsuarios: {
        parameters: {
            query?: {
                rol?: components["schemas"]["RolUsuario"] | null;
                activo?: boolean | null;
                q?: string | null;
                soloActivos?: boolean;
                /** @description Numero de pagina */
                pagina?: number;
                /** @description Registros por pagina */
                tamano?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Pagina de usuarios */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Pagina_UsuarioRead_"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Parametros de consulta invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    crearUsuario: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UsuarioCrear"];
            };
        };
        responses: {
            /** @description Usuario creado */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UsuarioRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El username o email ya existe */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Datos de usuario invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtenerUsuario: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                usuario_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Usuario encontrado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UsuarioRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Usuario no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    actualizarUsuario: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                usuario_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["UsuarioActualizar"];
            };
        };
        responses: {
            /** @description Usuario actualizado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UsuarioRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Usuario no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Los cambios entran en conflicto con las reglas de usuarios */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Datos de usuario invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    eliminarUsuario: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                usuario_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Usuario eliminado */
            204: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Usuario no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No puedes eliminar tu propia cuenta */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    desactivarUsuario: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                usuario_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Usuario desactivado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UsuarioRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Usuario no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description No se puede desactivar esta cuenta */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    reactivarUsuario: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                usuario_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Usuario reactivado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UsuarioRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Usuario no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Los cambios entran en conflicto con las reglas de usuarios */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listarCatalogos: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Listado de catalogos */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CatalogoRead"][];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtenerCatalogo: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                nombre: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Catalogo encontrado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CatalogoRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Catalogo no encontrado */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listarAuditoria: {
        parameters: {
            query?: {
                entidad?: string | null;
                entidadId?: number | null;
                accion?: string | null;
                /** @description Filtra por identificador de usuario */
                usuarioId?: number | null;
                /** @description Fecha inicial inclusiva en la zona America/Bogota */
                desde?: string | null;
                /** @description Fecha final inclusiva en la zona America/Bogota */
                hasta?: string | null;
                /** @description Numero de pagina */
                pagina?: number;
                /** @description Registros por pagina */
                tamano?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Pagina de eventos de auditoria */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Pagina_AuditoriaRead_"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rango de fechas o parametros de consulta invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    consultarDisponibilidad: {
        parameters: {
            query: {
                /** @description Fecha de entrada de la estancia */
                entrada: string;
                /** @description Fecha de salida de la estancia */
                salida: string;
                /** @description Numero de huespedes requeridos */
                huespedes?: number;
                /** @description Filtra por tipo de habitacion */
                tipo?: components["schemas"]["TipoHabitacion"] | null;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Habitaciones disponibles para el rango */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HabitacionResumen"][];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar disponibilidad */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La fecha de salida no es posterior a la de entrada */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Parametros de consulta invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listarReservas: {
        parameters: {
            query?: {
                /** @description Filtra por estado de la reserva */
                estado?: components["schemas"]["EstadoReserva"] | null;
                /** @description Filtra por habitacion */
                habitacionId?: number | null;
                /** @description Filtra por huesped */
                huespedId?: number | null;
                /** @description Fecha de entrada minima incluida (America/Bogota) */
                desde?: string | null;
                /** @description Fecha de entrada maxima incluida (America/Bogota) */
                hasta?: string | null;
                /** @description Numero de pagina */
                pagina?: number;
                /** @description Registros por pagina */
                tamano?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Pagina de reservas */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Pagina_ReservaRead_"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar reservas */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Parametros de consulta o rango de fechas invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    crearReserva: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ReservaCreate"];
            };
        };
        responses: {
            /** @description Reserva creada */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReservaRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para crear reservas */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Huesped o habitacion no encontrados */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Conflicto: habitacion inactiva, capacidad excedida, rango invalido, entrada en el pasado, reserva solapada o codigo no disponible */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Datos de la reserva invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtenerReserva: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Reserva encontrada */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReservaRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar reservas */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    actualizarReserva: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ReservaUpdate"];
            };
        };
        responses: {
            /** @description Reserva actualizada */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReservaRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para actualizar reservas */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva, huesped o habitacion no encontrados */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description La reserva no es editable en su estado actual, o hay conflicto por capacidad, rango, entrada en el pasado o solapamiento */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Datos de la reserva invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    confirmarReserva: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Reserva confirmada */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReservaRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para confirmar reservas */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Transicion invalida (p.ej. de CANCELADA), habitacion inactiva, solapamiento con otra reserva, o fecha de entrada en el pasado */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    cancelarReserva: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["CancelarReservaRequest"];
            };
        };
        responses: {
            /** @description Reserva cancelada */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReservaRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para cancelar reservas */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Transicion invalida (p.ej. de CHECK_IN, NO_SHOW) */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Motivo invalido (3-500 caracteres, sin solo espacios) */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    noShowReserva: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Reserva marcada como NO_SHOW */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReservaRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para marcar no-show */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Transicion invalida (p.ej. de PENDIENTE, CANCELADA) o intento de no-show antes de la fecha de entrada */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    checkInReserva: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Reserva en CHECK_IN */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReservaRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para registrar check-in */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Transicion invalida (la reserva no esta CONFIRMADA), check-in antes de la fecha de entrada, estancia vencida o habitacion no lista (sucia, ocupada o en mantenimiento) */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    checkOutReserva: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Reserva en CHECK_OUT con su resultado economico */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CheckOutRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para registrar check-out */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Transicion invalida (la reserva no esta en CHECK_IN) */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    extenderReserva: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ExtenderReservaRequest"];
            };
        };
        responses: {
            /** @description Estancia extendida */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReservaRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para extender reservas */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Transicion invalida (la reserva no esta en CHECK_IN), rango de fechas invalido o solapamiento con otra reserva */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Nueva fecha de salida invalida */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listarPagos: {
        parameters: {
            query?: {
                soloVigentes?: boolean;
                /** @description Numero de pagina */
                pagina?: number;
                /** @description Registros por pagina */
                tamano?: number;
            };
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Pagina de pagos */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Pagina_PagoRead_"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar pagos */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    crearPago: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PagoCreate"];
            };
        };
        responses: {
            /** @description Pago creado */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PagoRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para crear pagos */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Conflicto con el estado actual */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Datos de pago invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    anularPago: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
                pago_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PagoAnular"];
            };
        };
        responses: {
            /** @description Pago anulado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PagoRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Pago no encontrado o no pertenece a la reserva */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El pago ya fue anulado */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    listarConsumos: {
        parameters: {
            query?: {
                soloVigentes?: boolean;
                /** @description Numero de pagina */
                pagina?: number;
                /** @description Registros por pagina */
                tamano?: number;
            };
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Pagina de consumos */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Pagina_ConsumoRead_"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar consumos */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    crearConsumo: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConsumoCreate"];
            };
        };
        responses: {
            /** @description Consumo creado */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConsumoRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para crear consumos */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Conflicto con el estado actual */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Datos de consumo invalidos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    anularConsumo: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
                consumo_id: number;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConsumoAnular"];
            };
        };
        responses: {
            /** @description Consumo anulado */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConsumoRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Se requiere el rol administrador */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Consumo no encontrado o no pertenece a la reserva */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description El consumo ya fue anulado */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtenerCuenta: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                reserva_id: number;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Cuenta de la reserva */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["CuentaRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar la cuenta */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Reserva no encontrada */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    obtenerResumenDashboard: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Resumen operativo del hotel */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["DashboardRead"];
                };
            };
            /** @description Token de acceso invalido o ausente */
            401: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Rol sin permisos para consultar el dashboard */
            403: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    healthCheck: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Servicio disponible */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
            /** @description Solicitud invalida por datos o parametros incorrectos */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Base de datos no disponible */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
}

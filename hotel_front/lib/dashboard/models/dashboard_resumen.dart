import '../../shared/utils/lectura_json.dart';

/// Indicadores del panel (`GET /api/dashboard`) para el dia en curso.
class DashboardResumen {
  const DashboardResumen({
    required this.reservasActivas,
    required this.reservasPendientesCheckIn,
    required this.huespedesAlojados,
    required this.checkOutsDelDia,
    required this.habitacionesDisponibles,
    required this.habitacionesOcupadas,
    required this.habitacionesEnMantenimiento,
    required this.cuentasConSaldoPendiente,
  });

  final int reservasActivas;
  final int reservasPendientesCheckIn;
  final int huespedesAlojados;
  final int checkOutsDelDia;
  final int habitacionesDisponibles;
  final int habitacionesOcupadas;
  final int habitacionesEnMantenimiento;
  final int cuentasConSaldoPendiente;

  factory DashboardResumen.fromJson(Map<String, dynamic> json) {
    return DashboardResumen(
      reservasActivas: leerEntero(json['reservasActivas']) ?? 0,
      reservasPendientesCheckIn:
          leerEntero(json['reservasPendientesCheckIn']) ?? 0,
      huespedesAlojados: leerEntero(json['huespedesAlojados']) ?? 0,
      checkOutsDelDia: leerEntero(json['checkOutsDelDia']) ?? 0,
      habitacionesDisponibles: leerEntero(json['habitacionesDisponibles']) ?? 0,
      habitacionesOcupadas: leerEntero(json['habitacionesOcupadas']) ?? 0,
      habitacionesEnMantenimiento:
          leerEntero(json['habitacionesEnMantenimiento']) ?? 0,
      cuentasConSaldoPendiente:
          leerEntero(json['cuentasConSaldoPendiente']) ?? 0,
    );
  }
}

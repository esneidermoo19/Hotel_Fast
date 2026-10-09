import 'package:flutter/material.dart';

/// Sistema de diseno de Hotel Fast.
///
/// Material 3 con paleta Navy/Slate + Indigo ejecutivo y acento dorado/sandalo.
/// Define el tema claro, el oscuro y los temas de componentes (tarjetas,
/// botones, campos, dialogos, rail de navegacion, chips y pastillas).
abstract final class AppTheme {
  static const Color indigo = Color(0xFF1D4ED8);
  static const Color indigoOscuro = Color(0xFF1E3A8A);
  static const Color oro = Color(0xFFB45309);
  static const Color oroClaro = Color(0xFFFDE68A);
  static const Color navy = Color(0xFF0F172A);
  static const Color navyClaro = Color(0xFF1E293B);
  static const Color slate200 = Color(0xFFE2E8F0);
  static const Color slate400 = Color(0xFF94A3B8);

  static ThemeData luz() => _base(Brightness.light);
  static ThemeData oscura() => _base(Brightness.dark);

  static ThemeData _base(Brightness brillo) {
    final oscuro = brillo == Brightness.dark;
    final scheme = ColorScheme.fromSeed(seedColor: indigo, brightness: brillo)
        .copyWith(
          secondary: oro,
          onSecondary: Colors.white,
          secondaryContainer: oscuro ? const Color(0xFF5C3A0E) : oroClaro,
          onSecondaryContainer: oscuro ? oroClaro : const Color(0xFF3B2204),
          primary: oscuro ? const Color(0xFF93C5FD) : indigo,
          onPrimary: Colors.white,
          surface: oscuro ? const Color(0xFF0B1220) : const Color(0xFFFFFFFF),
        );

    final base = ThemeData(colorScheme: scheme, useMaterial3: true);
    final textoBase = base.textTheme;
    final texto = textoBase.copyWith(
      headlineSmall: textoBase.headlineSmall?.copyWith(
        fontWeight: FontWeight.w600,
        letterSpacing: -0.3,
      ),
      headlineMedium: textoBase.headlineMedium?.copyWith(
        fontWeight: FontWeight.w600,
        letterSpacing: -0.5,
      ),
      titleLarge: textoBase.titleLarge?.copyWith(fontWeight: FontWeight.w600),
      titleMedium: textoBase.titleMedium?.copyWith(fontWeight: FontWeight.w600),
      titleSmall: textoBase.titleSmall?.copyWith(fontWeight: FontWeight.w600),
      bodyMedium: textoBase.bodyMedium?.copyWith(height: 1.45),
      bodySmall: textoBase.bodySmall?.copyWith(height: 1.35),
      labelLarge: textoBase.labelLarge?.copyWith(fontWeight: FontWeight.w600),
    );

    // Borde fino neutro al 10% para tarjetas y separacion.
    final borde = BorderSide(
      color: oscuro ? const Color(0x1A94A3B8) : const Color(0x1A0F172A),
    );
    // Sombras suaves de poca opacidad.
    final sombra = oscuro ? const Color(0x33000000) : const Color(0x140F172A);

    return base.copyWith(
      textTheme: texto,
      scaffoldBackgroundColor: oscuro ? navy : const Color(0xFFF1F5F9),
      cardTheme: CardThemeData(
        elevation: 1,
        shadowColor: sombra,
        color: scheme.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: borde,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          textStyle: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          textStyle: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          textStyle: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: oscuro ? const Color(0xFF152033) : const Color(0xFFF8FAFC),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: oscuro ? slate400 : slate200),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: oscuro ? slate400 : slate200),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: indigo, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 14,
          vertical: 12,
        ),
      ),
      dialogTheme: DialogThemeData(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      ),
      navigationRailTheme: NavigationRailThemeData(
        indicatorShape: const StadiumBorder(),
        indicatorColor: scheme.secondaryContainer,
        selectedIconTheme: IconThemeData(color: scheme.onSecondaryContainer),
        selectedLabelTextStyle: const TextStyle(fontWeight: FontWeight.w600),
        groupAlignment: -0.9,
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(999),
          side: BorderSide(color: scheme.outlineVariant),
        ),
        selectedColor: scheme.secondaryContainer,
        backgroundColor: oscuro
            ? const Color(0xFF152033)
            : const Color(0xFFFFFFFF),
        labelStyle: const TextStyle(fontWeight: FontWeight.w500),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: oscuro ? navy : const Color(0xFFF1F5F9),
        titleTextStyle: texto.titleLarge,
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      tooltipTheme: TooltipThemeData(
        decoration: BoxDecoration(
          color: scheme.inverseSurface,
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      dividerTheme: DividerThemeData(
        color: oscuro ? const Color(0x1A94A3B8) : const Color(0x1A0F172A),
      ),
    );
  }
}

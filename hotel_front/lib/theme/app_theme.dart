import 'package:flutter/material.dart';

/// Sistema de diseno "Ultra Premium" de Hotel Fast.
///
/// Paleta Midnight Blue + Champagne Gold, tipografia con pesos definidos,
/// sombras suaves, esquinas redondeadas y superficies tipo cristal.
abstract final class AppTheme {
  // Paleta base.
  static const Color midnight = Color(0xFF0F172A);
  static const Color midnightClaro = Color(0xFF1E293B);
  static const Color oro = Color(0xFFC5A059);
  static const Color oroClaro = Color(0xFFE6CF9C);
  static const Color oroBrillante = Color(0xFFD4AF37);
  static const Color fondo = Color(0xFFF8FAFC);
  static const Color blanco = Color(0xFFFFFFFF);
  static const Color borde = Color(0xFFE2E8F0);

  // Estados semanticos (pastel + solido).
  static const Color esmeralda = Color(0xFF10B981);
  static const Color esmeraldaFondo = Color(0xFFECFDF5);
  static const Color borgona = Color(0xFFEF4444);
  static const Color borgonaFondo = Color(0xFFFEF2F2);
  static const Color ambar = Color(0xFFF59E0B);
  static const Color ambarFondo = Color(0xFFFFFBEB);

  static ThemeData luz() => _base(Brightness.light);
  static ThemeData oscura() => _base(Brightness.dark);

  static ThemeData _base(Brightness brillo) {
    final oscuro = brillo == Brightness.dark;

    final scheme = ColorScheme.fromSeed(seedColor: oro, brightness: brillo)
        .copyWith(
          primary: oro,
          onPrimary: midnight,
          primaryContainer: oroClaro,
          onPrimaryContainer: midnight,
          secondary: midnight,
          onSecondary: blanco,
          secondaryContainer: oscuro ? midnightClaro : const Color(0xFFEEF2F7),
          onSecondaryContainer: oscuro ? blanco : midnight,
          surface: oscuro ? midnight : blanco,
          onSurface: oscuro ? const Color(0xFFE2E8F0) : midnight,
          outline: borde,
          outlineVariant: const Color(0xFFCBD5E1),
          error: borgona,
          onError: blanco,
        );

    final base = ThemeData(
      colorScheme: scheme,
      useMaterial3: true,
      fontFamily: 'Inter',
    );
    final textoBase = base.textTheme;
    final texto = textoBase.copyWith(
      headlineMedium: textoBase.headlineMedium?.copyWith(
        fontWeight: FontWeight.w700,
        letterSpacing: -0.5,
      ),
      headlineSmall: textoBase.headlineSmall?.copyWith(
        fontWeight: FontWeight.w700,
        letterSpacing: -0.3,
      ),
      titleLarge: textoBase.titleLarge?.copyWith(fontWeight: FontWeight.w700),
      titleMedium: textoBase.titleMedium?.copyWith(fontWeight: FontWeight.w600),
      titleSmall: textoBase.titleSmall?.copyWith(fontWeight: FontWeight.w600),
      bodyLarge: textoBase.bodyLarge?.copyWith(height: 1.45),
      bodyMedium: textoBase.bodyMedium?.copyWith(height: 1.45),
      bodySmall: textoBase.bodySmall?.copyWith(height: 1.35),
      labelLarge: textoBase.labelLarge?.copyWith(
        fontWeight: FontWeight.w600,
        letterSpacing: 0.2,
      ),
    );

    final bordeLado = BorderSide(
      color: oscuro ? const Color(0x1A94A3B8) : borde,
    );

    return base.copyWith(
      textTheme: texto,
      scaffoldBackgroundColor: oscuro ? midnight : fondo,
      cardTheme: CardThemeData(
        elevation: 0,
        color: oscuro ? midnightClaro : blanco,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: bordeLado,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: oro,
          foregroundColor: midnight,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          textStyle: const TextStyle(
            fontWeight: FontWeight.w700,
            letterSpacing: 0.3,
          ),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: oro,
          foregroundColor: midnight,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: oscuro ? oroClaro : midnight,
          side: BorderSide(color: oscuro ? oro : const Color(0xFFCBD5E1)),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
          textStyle: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: oscuro ? oroClaro : midnight,
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
          borderRadius: BorderRadius.circular(14),
          borderSide: bordeLado,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: bordeLado,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: oro, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 16,
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: oscuro ? midnightClaro : blanco,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      ),
      navigationRailTheme: NavigationRailThemeData(
        backgroundColor: oscuro ? midnightClaro : blanco,
        indicatorShape: const StadiumBorder(),
        indicatorColor: oro,
        selectedIconTheme: const IconThemeData(color: midnight),
        unselectedIconTheme: IconThemeData(
          color: oscuro ? const Color(0xFFCBD5E1) : const Color(0xFF64748B),
        ),
        selectedLabelTextStyle: const TextStyle(
          fontWeight: FontWeight.w700,
          color: midnight,
        ),
        groupAlignment: -0.9,
      ),
      chipTheme: ChipThemeData(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(999),
          side: BorderSide(color: scheme.outlineVariant),
        ),
        selectedColor: oro,
        backgroundColor: oscuro ? const Color(0xFF152033) : blanco,
        labelStyle: const TextStyle(fontWeight: FontWeight.w600),
        secondaryLabelStyle: const TextStyle(color: midnight),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: oscuro ? midnightClaro : midnight,
        foregroundColor: blanco,
        centerTitle: false,
        titleTextStyle: texto.titleLarge?.copyWith(color: blanco),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        backgroundColor: midnight,
        contentTextStyle: const TextStyle(color: blanco),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      tooltipTheme: TooltipThemeData(
        decoration: BoxDecoration(
          color: midnight,
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      dividerTheme: DividerThemeData(
        color: oscuro ? const Color(0x1A94A3B8) : borde,
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(color: oro),
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith(
          (estados) => estados.contains(WidgetState.selected) ? oro : null,
        ),
        trackColor: WidgetStateProperty.resolveWith(
          (estados) => estados.contains(WidgetState.selected) ? oroClaro : null,
        ),
      ),
    );
  }
}

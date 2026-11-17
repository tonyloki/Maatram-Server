import 'package:flutter/widgets.dart';

/// Corner radius tokens matching the organic, rounded editorial visual identity.
abstract final class MaatramRadii {
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 20.0;
  static const double xxl = 24.0;
  static const double xxxl = 32.0;
  static const double pill = 999.0;

  // BorderRadius helpers
  static const BorderRadius radiusXs = BorderRadius.all(Radius.circular(xs));
  static const BorderRadius radiusSm = BorderRadius.all(Radius.circular(sm));
  static const BorderRadius radiusMd = BorderRadius.all(Radius.circular(md));
  static const BorderRadius radiusLg = BorderRadius.all(Radius.circular(lg));
  static const BorderRadius radiusXl = BorderRadius.all(Radius.circular(xl));
  static const BorderRadius radiusXxl = BorderRadius.all(Radius.circular(xxl));
  static const BorderRadius radiusXxxl =
      BorderRadius.all(Radius.circular(xxxl));
  static const BorderRadius radiusPill =
      BorderRadius.all(Radius.circular(pill));

  // Card specific default radius (organic 24dp)
  static const BorderRadius cardRadius = BorderRadius.all(Radius.circular(xxl));
  static const BorderRadius buttonRadius =
      BorderRadius.all(Radius.circular(lg));
  static const BorderRadius bottomSheetRadius =
      BorderRadius.vertical(top: Radius.circular(xxxl));
}

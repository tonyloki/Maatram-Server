import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

class LocalDiskAssetBundle extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async {
    final candidates = [
      key,
      'mobile/$key',
      '../mobile/$key',
      'assets/$key',
      'mobile/assets/$key',
    ];
    for (final c in candidates) {
      final f = File(c);
      if (f.existsSync()) {
        final bytes = await f.readAsBytes();
        return ByteData.view(bytes.buffer);
      }
    }
    return rootBundle.load(key);
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    final data = await load(key);
    return String.fromCharCodes(data.buffer.asUint8List());
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() async {
    // Load Georgia font
    final georgiaFile = File('C:\\Windows\\Fonts\\georgia.ttf');
    if (georgiaFile.existsSync()) {
      final bytes = georgiaFile.readAsBytesSync();
      final loader = FontLoader('Georgia');
      loader.addFont(Future.value(ByteData.view(bytes.buffer)));
      await loader.load();
    }

    // Load Roboto font from Arial / Segoe
    final arialFile = File('C:\\Windows\\Fonts\\arial.ttf');
    if (arialFile.existsSync()) {
      final bytes = arialFile.readAsBytesSync();
      final loader = FontLoader('Roboto');
      loader.addFont(Future.value(ByteData.view(bytes.buffer)));
      await loader.load();
    }
  });

  testWidgets('Test Font and Image Rendering', (tester) async {
    tester.view.physicalSize = const Size(390 * 2, 844 * 2);
    tester.view.devicePixelRatio = 2.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    final key = GlobalKey();

    await tester.pumpWidget(
      DefaultAssetBundle(
        bundle: LocalDiskAssetBundle(),
        child: MaterialApp(
          home: RepaintBoundary(
            key: key,
            child: Scaffold(
              backgroundColor: const Color(0xFFFAF8F5),
              body: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Image.asset(
                      'assets/images/logo.png',
                      height: 60,
                    ),
                    const SizedBox(height: 20),
                    const Text(
                      'Volunteer for a',
                      style: TextStyle(
                        fontFamily: 'Georgia',
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF0A192F),
                      ),
                    ),
                    const Text(
                      'Better Tomorrow',
                      style: TextStyle(
                        fontFamily: 'Georgia',
                        fontSize: 32,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFFD49504),
                      ),
                    ),
                    const SizedBox(height: 20),
                    Image.asset(
                      'assets/images/volunteers-team-hero.jpg',
                      height: 180,
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );

    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));

    await tester.runAsync(() async {
      final boundary = key.currentContext?.findRenderObject() as RenderRepaintBoundary?;
      if (boundary == null) return;
      final image = await boundary.toImage(pixelRatio: 1.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      if (byteData == null) return;
      final file = File('../docs/phase4-visual-audit/test_font_render.png');
      file.writeAsBytesSync(byteData.buffer.asUint8List());
    });
  });
}

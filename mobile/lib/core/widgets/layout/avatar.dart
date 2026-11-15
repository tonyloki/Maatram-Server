import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import '../../theme/colors.dart';
import '../../theme/radii.dart';
import '../../theme/typography.dart';

/// User profile avatar with cached image and robust initials fallback.
class MaatramAvatar extends StatelessWidget {
  final String? imageUrl;
  final String? name;
  final double size;
  final bool showBorder;
  final Color borderColor;

  const MaatramAvatar({
    super.key,
    this.imageUrl,
    this.name,
    this.size = 40.0,
    this.showBorder = true,
    this.borderColor = MaatramColors.primaryGold,
  });

  String _getInitials() {
    if (name == null || name!.trim().isEmpty) return 'MV';
    final parts = name!.trim().split(RegExp(r'\s+'));
    if (parts.length > 1) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return parts[0].substring(0, parts[0].length >= 2 ? 2 : 1).toUpperCase();
  }

  @override
  Widget build(BuildContext context) {
    Widget avatarChild;

    if (imageUrl != null && imageUrl!.trim().isNotEmpty) {
      avatarChild = CachedNetworkImage(
        imageUrl: imageUrl!,
        width: size,
        height: size,
        fit: BoxFit.cover,
        placeholder: (_, __) => _buildInitialsContainer(),
        errorWidget: (_, __, ___) => _buildInitialsContainer(),
      );
    } else {
      avatarChild = _buildInitialsContainer();
    }

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: showBorder
            ? Border.all(color: borderColor, width: size > 48 ? 2.5 : 1.5)
            : null,
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(MaatramRadii.pill),
        child: avatarChild,
      ),
    );
  }

  Widget _buildInitialsContainer() {
    return Container(
      width: size,
      height: size,
      color: MaatramColors.goldSurface,
      alignment: Alignment.center,
      child: Text(
        _getInitials(),
        style: TextStyle(
          fontFamily: MaatramTypography.bodyFamily,
          fontSize: size * 0.38,
          fontWeight: FontWeight.w700,
          color: MaatramColors.goldDeep,
        ),
      ),
    );
  }
}


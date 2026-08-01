#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext
import re

__version__ = "6.7"
__license__ = "GPL-v2"

PluginLanguageDomain = "Ciplushelper"
PluginLanguagePath = 'Extensions/Ciplushelper/locale'


def localeInit():
    gettext.bindtextdomain(
        PluginLanguageDomain,
        resolveFilename(
            SCOPE_PLUGINS,
            PluginLanguagePath))


# ============================================================
# PLACEHOLDER PROTECTION
# ============================================================

def _extract_placeholders(text):
    """
    Extract all placeholders from a string.
    Handles:
    - Python: %(name)s, %(name)d, %s, %d, etc.
    - C# / Enigma2: {name}, {0}, etc.
    """
    if not text:
        return []

    placeholders = []

    # 1. C# style: {name}, {0}, {hours}, etc.
    for match in re.finditer(r'\{[^{}]+\}', text):
        placeholders.append(match.group(0))

    # 2. Python style: %(name)s, %(name)d, etc.
    for match in re.finditer(
        r'%\([a-zA-Z_][a-zA-Z0-9_]*\)[diouxXeEfFgGcrs]',
            text):
        placeholders.append(match.group(0))

    # 3. Python style: %s, %d, %f, etc.
    for match in re.finditer(r'%[diouxXeEfFgGcrs]', text):
        placeholders.append(match.group(0))

    return placeholders


def _restore_placeholders(original, translated):
    """
    Restore placeholders in translated string using original as reference.
    Replaces translated placeholder names with original ones.
    """
    if not original or not translated:
        return translated

    # If no placeholders, return as-is
    if '{' not in original and '%' not in original:
        return translated

    # Extract placeholders from original
    original_placeholders = _extract_placeholders(original)
    if not original_placeholders:
        return translated

    # For each placeholder, try to find it in translated
    result = translated

    for placeholder in original_placeholders:
        # If placeholder is already in translated, keep it
        if placeholder in result:
            continue

        # Try to find if placeholder was translated (e.g., {hours} -> {ore})
        # We need to extract the placeholder name
        if placeholder.startswith('{') and placeholder.endswith('}'):
            # Extract the content without braces
            content = placeholder[1:-1]

            # Look for any {something} in translated that might be the
            # translation
            for match in re.finditer(r'\{[^{}]+\}', result):
                translated_content = match.group(0)[1:-1]
                # If the translated content is different but the placeholder
                # structure is same
                if translated_content != content:
                    # Replace the translated placeholder with the original one
                    result = result.replace(match.group(0), placeholder)
                    break

        # For Python style placeholders, they are less likely to be translated
        # If we can't find them, just keep the translated string as-is

    return result


def _has_placeholders(text):
    """Check if text contains any placeholders."""
    if not text:
        return False
    return (
        ('{' in text and '}' in text) or
        '%(' in text or
        re.search(r'%[diouxXeEfFgGcrs]', text) is not None
    )


# ============================================================
# MAIN TRANSLATION FUNCTION WITH PLACEHOLDER PROTECTION
# ============================================================

def _(txt):
    """
    Translation function with automatic placeholder protection.
    Prevents KeyError when using .format() on translated strings.
    """
    if not txt:
        return ""

    # Store original text for placeholder restoration
    original = txt

    # Translate using gettext
    translated = gettext.dgettext(PluginLanguageDomain, txt)
    if translated:
        # Restore placeholders if needed
        if _has_placeholders(original):
            restored = _restore_placeholders(original, translated)
            return restored
        return translated

    # Fallback
    print(("[%s] fallback to default translation for %s" %
          (PluginLanguageDomain, txt)))
    # if translated != txt:
    translated = gettext.gettext(txt)

    # Restore placeholders if needed
    if _has_placeholders(original):
        restored = _restore_placeholders(original, translated)
        return restored

    return translated


localeInit()
language.addCallback(localeInit)

"""
IoC Unmasker Module - Detection and Unmasking of Obfuscated Indicators.

Handles detection and unmasking of obfuscated/masked IoC values commonly found
in threat intelligence reports and malware analysis:

Supported Unmasking Techniques:
- Base64 encoding/decoding
- Hexadecimal encoding/decoding
- URL encoding/decoding (percent-encoding)
- Unicode escape sequences
- String reversal
- Defanged URLs (hxxp, [dot], (dot), etc.)
- Character substitution (hxxps, hxttp, etc.)

Common Use Cases:
- Processing CSV files with obfuscated IoCs
- Extracting real IoCs from threat reports
- Analyzing malware configuration data
- Processing security vendor feeds with defanged indicators

Example:
    unmasker = IoCUnmasker()
    result = unmasker.unmask("aHR0cHM6Ly9ldmlsLmNvbQ==")
    # Returns: UnmaskResult(original="aHR0cHM6Ly9ldmlsLmNvbQ==",
    #                       unmasked="https://evil.com",
    #                       technique="Base64")
"""

from __future__ import annotations

import base64
import binascii
import re
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Optional, List
from urllib.parse import unquote

from m365_ioc_csv.utils.logger import get_logger

logger = get_logger(__name__)


@unique
class UnmaskTechnique(Enum):
    """Enumeration of unmasking techniques."""

    BASE64 = "Base64"
    HEX = "Hex"
    URL_ENCODED = "URL-encoded"
    UNICODE_ESCAPE = "Unicode-escape"
    REVERSED = "Reversed"
    DEFANGED = "Defanged"
    ORIGINAL = "Original"
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return self.value


@dataclass
class UnmaskResult:
    """
    Result of IoC unmasking operation.

    Attributes:
        original: The original obfuscated value
        unmasked: The unmasked value (may be same as original)
        technique: The technique used to unmask
        confidence: Confidence score (0.0 to 1.0)
        is_valid_ioc: Whether the unmasked value appears to be a valid IoC
    """

    original: str
    unmasked: str
    technique: UnmaskTechnique
    confidence: float = 1.0
    is_valid_ioc: bool = True

    def __post_init__(self) -> None:
        """Validate confidence is in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class UnmaskReport:
    """
    Comprehensive report for unmasking operations.

    Attributes:
        original: Original input value
        results: List of successful unmasking results
        best_result: The most likely correct unmasked value
        techniques_tried: List of techniques attempted
        total_attempts: Number of unmasking attempts made
    """

    original: str
    results: List[UnmaskResult] = field(default_factory=list)
    best_result: Optional[UnmaskResult] = None
    techniques_tried: List[UnmaskTechnique] = field(default_factory=list)
    total_attempts: int = 0

    @property
    def was_unmasked(self) -> bool:
        """Check if value was successfully unmasked."""
        return len(self.results) > 0 and any(
            r.technique not in (UnmaskTechnique.ORIGINAL, UnmaskTechnique.UNKNOWN) for r in self.results
        )

    @property
    def successful_techniques(self) -> List[str]:
        """List of successful unmasking technique names."""
        return [r.technique.value for r in self.results if r.technique != UnmaskTechnique.ORIGINAL]


class IoCUnmasker:
    """
    Detects and unmasks obfuscated IoC values.

    Features:
    - Automatic detection of common obfuscation patterns
    - Multiple unmasking technique attempts
    - Validation of unmasked values as IoCs
    - Confidence scoring for results
    - Comprehensive reporting

    Example:
        unmasker = IoCUnmasker()
        report = unmasker.unmask("aHR0cHM6Ly9ldmlsLmNvbQ==")
        if report.was_unmasked:
            print(f"Unmasked: {report.best_result.unmasked}")

    The unmasker attempts techniques in order of likelihood:
    1. Defanged URLs (safest, most common in reports)
    2. URL-encoded (percent encoding)
    3. Unicode escape sequences
    4. Base64 encoding
    5. Hexadecimal encoding
    6. String reversal
    """

    # Regex patterns for obfuscation detection
    BASE64_RE = re.compile(r'^[A-Za-z0-9+/]{16,}={0,2}$')
    HEX_RE = re.compile(r'^(0x)?[0-9a-fA-F]{8,}$')
    URL_ENCODED_RE = re.compile(r'%[0-9A-Fa-f]{2}')
    UNICODE_ESCAPE_RE = re.compile(r'\\u[0-9A-Fa-f]{4}|\\x[0-9A-Fa-f]{2}')
    DEFANGED_RE = re.compile(r'\[(?:\.|/)\]|\((?:\.|/)\)|hxxps?|hxttp|://\s*\[|\[.*?\]\.', re.IGNORECASE)
    REVERSED_DOMAIN_RE = re.compile(r'^(moc|gro|ten|ude|oc|ed|og|bu)[a-z0-9-]*(\.[a-z0-9-]+)*\.[a-z]{2,}', re.IGNORECASE)

    # Patterns that suggest valid IoCs
    DOMAIN_PATTERN = re.compile(
        r'^(?:[a-z0-9-]+\.)+[a-z]{2,}$',
        re.IGNORECASE
    )
    URL_PATTERN = re.compile(
        r'^https?://(?:[a-z0-9-]+\.)+[a-z]{2,}(?:/.*)?$',
        re.IGNORECASE
    )
    IPv4_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    HASH_PATTERN = re.compile(r'^[0-9a-fA-F]{32,64}$')

    def __init__(self, enable_all: bool = True) -> None:
        """
        Initialize the IoC Unmasker.

        Args:
            enable_all: Enable all unmasking techniques (default: True)
        """
        self.enable_all = enable_all
        logger.debug(f"IoCUnmasker initialized (enable_all={enable_all})")

    def unmask(self, value: str) -> UnmaskReport:
        """
        Attempt to unmask an obfuscated IoC value.

        Attempts multiple unmasking techniques and returns all successful
        results along with a best guess based on confidence scoring.

        Args:
            value: The potentially obfuscated IoC value

        Returns:
            UnmaskReport with all results and best match

        Example:
            unmasker = IoCUnmasker()
            report = unmasker.unmask("hxxps://evil[.]com")
            # report.best_result.unmasked == "https://evil.com"
        """
        if not value:
            unknown_result = UnmaskResult(value, value, UnmaskTechnique.UNKNOWN, 0.0, False)
            return UnmaskReport(
                original=value,
                results=[unknown_result],
                best_result=unknown_result,
                total_attempts=0
            )

        proc_value = value.strip()
        report = UnmaskReport(original=proc_value)

        # Try each technique in order of safety and likelihood
        techniques = [
            (self._try_defanged, UnmaskTechnique.DEFANGED, 1.0),
            (self._try_url_decode, UnmaskTechnique.URL_ENCODED, 0.95),
            (self._try_unicode_escape, UnmaskTechnique.UNICODE_ESCAPE, 0.9),
            (self._try_base64, UnmaskTechnique.BASE64, 0.8),
            (self._try_hex, UnmaskTechnique.HEX, 0.7),
            (self._try_reversed, UnmaskTechnique.REVERSED, 0.6),
        ]

        for try_func, technique, base_confidence in techniques:
            report.techniques_tried.append(technique)
            report.total_attempts += 1

            try:
                result = try_func(proc_value, base_confidence)
                if result and result.is_valid_ioc:
                    report.results.append(result)
                    logger.debug(f"Unmasked with {technique.value}: {proc_value[:20]}... -> {result.unmasked[:20]}...")
            except Exception as e:
                logger.debug(f"Error trying {technique.value}: {e}")
                continue

        # Add original as fallback
        original_result = UnmaskResult(
            original=proc_value,
            unmasked=proc_value,
            technique=UnmaskTechnique.ORIGINAL,
            confidence=0.5,
            is_valid_ioc=self._looks_like_ioc(proc_value)
        )
        report.results.append(original_result)

        # Determine best result
        if len(report.results) > 1:
            # Prefer non-original results
            non_original = [r for r in report.results if r.technique != UnmaskTechnique.ORIGINAL]
            if non_original:
                # Sort by confidence
                non_original.sort(key=lambda x: x.confidence, reverse=True)
                report.best_result = non_original[0]
            else:
                report.best_result = original_result
        else:
            report.best_result = report.results[0]

        if report.was_unmasked:
            logger.info(
                f"Successfully unmasked using {report.best_result.technique.value}: "
                f"{proc_value[:20]}... -> {report.best_result.unmasked[:20]}..."
            )

        return report

    def unmask_batch(self, values: List[str]) -> dict[str, UnmaskReport]:
        """
        Unmask multiple IoC values.

        Args:
            values: List of potentially obfuscated IoC values

        Returns:
            Dictionary mapping original values to their unmask reports

        Example:
            unmasker = IoCUnmasker()
            reports = unmasker.unmask_batch([
                "aHR0cHM6Ly9ldmlsLmNvbQ==",
                "hxxps://evil[.]com"
            ])
        """
        results = {}
        for value in values:
            results[value] = self.unmask(value)

        successful = sum(1 for r in results.values() if r.was_unmasked)
        logger.info(f"Unmasked {successful}/{len(values)} values in batch")
        return results

    def _try_base64(self, value: str, confidence: float) -> Optional[UnmaskResult]:
        """Try Base64 decoding."""
        if not self.BASE64_RE.fullmatch(value):
            return None

        try:
            # Try standard Base64
            decoded = base64.b64decode(value).decode('utf-8', errors='ignore')
            if self._looks_like_ioc(decoded):
                return UnmaskResult(
                    original=value,
                    unmasked=decoded.strip(),
                    technique=UnmaskTechnique.BASE64,
                    confidence=confidence
                )
        except Exception:
            pass

        return None

    def _try_hex(self, value: str, confidence: float) -> Optional[UnmaskResult]:
        """Try hexadecimal decoding."""
        if not self.HEX_RE.fullmatch(value):
            return None

        try:
            # Remove 0x prefix if present
            hex_str = value.lower().replace('0x', '')

            # Must have even length
            if len(hex_str) % 2 != 0:
                return None

            decoded = bytes.fromhex(hex_str).decode('utf-8', errors='ignore')
            if self._looks_like_ioc(decoded):
                return UnmaskResult(
                    original=value,
                    unmasked=decoded.strip(),
                    technique=UnmaskTechnique.HEX,
                    confidence=confidence
                )
        except (binascii.Error, ValueError):
            pass

        return None

    def _try_url_decode(self, value: str, confidence: float) -> Optional[UnmaskResult]:
        """Try URL percent-decoding."""
        if not self.URL_ENCODED_RE.search(value):
            return None

        try:
            decoded = unquote(value)
            if decoded != value and self._looks_like_ioc(decoded):
                return UnmaskResult(
                    original=value,
                    unmasked=decoded,
                    technique=UnmaskTechnique.URL_ENCODED,
                    confidence=confidence
                )
        except Exception:
            pass

        return None

    def _try_unicode_escape(self, value: str, confidence: float) -> Optional[UnmaskResult]:
        """Try Unicode escape sequence decoding."""
        if not self.UNICODE_ESCAPE_RE.search(value):
            return None

        try:
            # Handle \uXXXX and \xXX escape sequences
            decoded = value.encode('utf-8').decode('unicode_escape')
            if decoded != value and self._looks_like_ioc(decoded):
                return UnmaskResult(
                    original=value,
                    unmasked=decoded,
                    technique=UnmaskTechnique.UNICODE_ESCAPE,
                    confidence=confidence
                )
        except Exception:
            pass

        return None

    def _try_reversed(self, value: str, confidence: float) -> Optional[UnmaskResult]:
        """Try string reversal."""
        reversed_str = value[::-1]

        # Check if reversed looks like a domain (e.g., moc.evil.com)
        # OR if it looks like a URL with protocol (e.g., https://evil.com)
        if self.REVERSED_DOMAIN_RE.fullmatch(reversed_str) or self.URL_PATTERN.fullmatch(reversed_str):
            decoded = reversed_str
            if self._looks_like_ioc(decoded):
                # Lower confidence for reversal (could be false positive)
                return UnmaskResult(
                    original=value,
                    unmasked=decoded,
                    technique=UnmaskTechnique.REVERSED,
                    confidence=confidence * 0.7  # Lower confidence
                )

        return None

    def _try_defanged(self, value: str, confidence: float) -> Optional[UnmaskResult]:
        """Try to fix defanged URLs/domains."""
        if not self.DEFANGED_RE.search(value):
            return None

        # Apply defang fixes
        fixed = self._fix_defanged(value)

        if fixed != value and self._looks_like_ioc(fixed):
            return UnmaskResult(
                original=value,
                unmasked=fixed,
                technique=UnmaskTechnique.DEFANGED,
                confidence=confidence
            )

        return None

    def _fix_defanged(self, value: str) -> str:
        """Apply common defang fixes."""
        fixed = value

        # First, fix hxxp/hxttp variants (do this before other replacements)
        fixed = re.sub(r'hxxps://', 'https://', fixed, flags=re.IGNORECASE)
        fixed = re.sub(r'hxttp://', 'http://', fixed, flags=re.IGNORECASE)
        fixed = re.sub(r'hxxp://', 'http://', fixed, flags=re.IGNORECASE)
        fixed = re.sub(r'h[xyz]{2}ps?://', 'http://', fixed, flags=re.IGNORECASE)

        # Replace bracketed dots/slashes directly
        # NOTE: In defanged URLs:
        # - [.] means . (dot) between domain parts
        # - [/] is context-dependent:
        #   - evil[/]com -> evil.com (dot between domain parts)
        #   - evil.com[/]path -> evil.com/path (slash before path)

        # Replace [.] with .
        fixed = re.sub(r'\[\.\]', '.', fixed)

        # Replace [(]. with .
        fixed = re.sub(r'\[\(/]', '.', fixed)

        # Replace [(.)] with .
        fixed = re.sub(r'\[\(\.\)\]', '.', fixed)

        # Handle [/] - context dependent
        # For URLs with protocol, we need to be smarter about host vs path
        if '://' in fixed:
            # Replace all [/] in the HOST portion with .
            # Replace all [/] in the PATH portion with /
            # Strategy: Find the first / after :// to separate host from path
            parts = fixed.split('://', 1)
            if len(parts) == 2:
                protocol, rest = parts
                # Find the first / that's not part of [/
                # We scan character by character
                in_host = True
                i = 0
                rest_result = []
                while i < len(rest):
                    if rest[i:i+3] == '[/]':
                        # Found [/]
                        # Check if there's a . in rest_result before this position
                        # If we've seen a . already, we're probably past the domain
                        has_dot_before = any(c == '.' for c in rest_result)
                        if in_host and has_dot_before:
                            # We're past the domain (which has at least one .), [/] is path separator
                            in_host = False
                            rest_result.append('/')
                        elif in_host:
                            # Still in domain part, [/] is between domain labels
                            rest_result.append('.')
                        else:
                            # In path mode
                            rest_result.append('/')
                        i += 3
                    elif rest[i] == '/' and in_host:
                        # This is the host/path separator
                        in_host = False
                        rest_result.append('/')
                        i += 1
                    else:
                        rest_result.append(rest[i])
                        i += 1
                fixed = f'{protocol}://{"".join(rest_result)}'
        else:
            # No protocol - assume [/] is always between domain parts
            fixed = fixed.replace('[/]', '.')

        # Handle parenthesized dots/slashes
        fixed = re.sub(r'\(\.\)', '.', fixed)
        fixed = re.sub(r'\(\/\]', '/', fixed)

        # Clean up any remaining brackets around text (but not protocol brackets)
        fixed = re.sub(r'\[([a-z0-9.-]+)\]', r'\1', fixed)

        # Handle bracketed protocol separators (e.g., ://[)
        fixed = re.sub(r'://\s*\[', '://', fixed)

        # Handle cases like ]. where ] is followed by .
        fixed = re.sub(r'\]\s*\.', '.', fixed)

        # Remove spaces around protocol separators and dots
        fixed = re.sub(r'\s+:\s*/\s+', '://', fixed)
        fixed = re.sub(r'\s*\.\s*', '.', fixed)

        return fixed.strip()

    def _looks_like_ioc(self, value: str) -> bool:
        """
        Quick check if value looks like a valid IoC.

        Args:
            value: The value to check

        Returns:
            True if value resembles an IoC
        """
        if not value:
            return False

        val_lower = value.lower().strip()

        # Check URL pattern
        if self.URL_PATTERN.fullmatch(value):
            return True

        # Check domain pattern
        if self.DOMAIN_PATTERN.fullmatch(value):
            return True

        # Check IPv4 pattern
        if self.IPv4_PATTERN.fullmatch(value):
            return True

        # Check hash pattern
        if self.HASH_PATTERN.fullmatch(value):
            return True

        # Check for URL-like structure (has http/https or www.)
        if val_lower.startswith(('http://', 'https://', 'www.')):
            return True

        # Check for domain-like structure (has dots and TLD)
        if '.' in value and value.count('.') >= 1:
            parts = value.split('.')
            if len(parts) >= 2 and len(parts[-1]) >= 2:
                return True

        # Check if contains path (likely URL without scheme)
        if '/' in value:
            return True

        return False

    def is_masked(self, value: str) -> bool:
        """
        Check if a value appears to be masked/obfuscated.

        Args:
            value: The value to check

        Returns:
            True if value appears obfuscated
        """
        if not value:
            return False

        # Check for known obfuscation patterns
        if self.BASE64_RE.fullmatch(value):
            return True

        if self.HEX_RE.fullmatch(value):
            return True

        if self.URL_ENCODED_RE.search(value):
            return True

        if self.UNICODE_ESCAPE_RE.search(value):
            return True

        if self.DEFANGED_RE.search(value):
            return True

        if self.REVERSED_DOMAIN_RE.fullmatch(value):
            return True

        return False

    def get_supported_techniques(self) -> List[str]:
        """Get list of supported unmasking techniques."""
        return [
            UnmaskTechnique.DEFANGED.value,
            UnmaskTechnique.URL_ENCODED.value,
            UnmaskTechnique.UNICODE_ESCAPE.value,
            UnmaskTechnique.BASE64.value,
            UnmaskTechnique.HEX.value,
            UnmaskTechnique.REVERSED.value,
        ]

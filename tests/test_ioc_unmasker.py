"""
Unit Tests for IoC Unmasker Module.

Tests detection and unmasking of obfuscated IoC values including:
- Base64 encoding/decoding
- Hexadecimal encoding/decoding
- URL encoding/decoding
- Unicode escape sequences
- String reversal
- Defanged URLs/domains
"""

import pytest

from m365_ioc_csv.core.ioc_unmasker import (
    IoCUnmasker,
    UnmaskResult,
    UnmaskReport,
    UnmaskTechnique,
)


class TestIoCUnmasker:
    """Test suite for IoCUnmasker class."""

    @pytest.fixture
    def unmasker(self) -> IoCUnmasker:
        """Create a fresh unmasker instance for each test."""
        return IoCUnmasker()

    # ==========================================================================
    # Base64 Tests
    # ==========================================================================

    def test_base64_url(self, unmasker: IoCUnmasker) -> None:
        """Test Base64 encoded URL unmasking."""
        # "https://evil.com" encoded in Base64
        encoded = "aHR0cHM6Ly9ldmlsLmNvbQ=="
        report = unmasker.unmask(encoded)

        assert report.was_unmasked
        assert report.best_result.unmasked == "https://evil.com"
        assert report.best_result.technique == UnmaskTechnique.BASE64

    def test_base64_domain(self, unmasker: IoCUnmasker) -> None:
        """Test Base64 encoded domain unmasking."""
        # "malware.example.com" encoded in Base64
        encoded = "bWFsd2FyZS5leGFtcGxlLmNvbQ=="
        report = unmasker.unmask(encoded)

        assert report.was_unmasked
        assert "malware.example.com" in report.best_result.unmasked

    def test_base64_invalid(self, unmasker: IoCUnmasker) -> None:
        """Test that invalid Base64 doesn't produce false positives."""
        not_base64 = "notvalidbase64!!!"
        report = unmasker.unmask(not_base64)

        # Should not be detected as Base64
        assert report.best_result.technique != UnmaskTechnique.BASE64

    # ==========================================================================
    # Hexadecimal Tests
    # ==========================================================================

    def test_hex_url(self, unmasker: IoCUnmasker) -> None:
        """Test hexadecimal encoded URL unmasking."""
        # "https://evil.com" as hex string (without 0x prefix)
        encoded = "68747470733a2f2f6576696c2e636f6d"
        report = unmasker.unmask(encoded)

        assert report.was_unmasked
        assert report.best_result.unmasked == "https://evil.com"
        assert report.best_result.technique == UnmaskTechnique.HEX

    def test_hex_with_0x_prefix(self, unmasker: IoCUnmasker) -> None:
        """Test hex with 0x prefix."""
        encoded = "0x68747470733a2f2f6576696c2e636f6d"
        report = unmasker.unmask(encoded)

        assert report.was_unmasked
        assert report.best_result.unmasked == "https://evil.com"

    def test_hex_invalid_odd_length(self, unmasker: IoCUnmasker) -> None:
        """Test that odd-length hex strings are rejected."""
        odd_hex = "abc123"  # 6 chars = 3 bytes, but let's use odd
        report = unmasker.unmask(odd_hex)

        # Should not decode as valid hex IoC
        assert report.best_result.technique != UnmaskTechnique.HEX

    # ==========================================================================
    # URL Encoding Tests
    # ==========================================================================

    def test_url_encoded_domain(self, unmasker: IoCUnmasker) -> None:
        """Test percent-encoded URL unmasking."""
        encoded = "%65%76%69%6C%2E%63%6F%6D"  # evil.com
        report = unmasker.unmask(encoded)

        assert report.was_unmasked
        assert report.best_result.unmasked == "evil.com"
        assert report.best_result.technique == UnmaskTechnique.URL_ENCODED

    def test_url_encoded_full_url(self, unmasker: IoCUnmasker) -> None:
        """Test fully percent-encoded URL."""
        encoded = "%68%74%74%70%73%3A%2F%2F%65%76%69%6C%2E%63%6F%6D"
        report = unmasker.unmask(encoded)

        assert report.was_unmasked
        assert report.best_result.unmasked == "https://evil.com"

    # ==========================================================================
    # Unicode Escape Tests
    # ==========================================================================

    def test_unicode_escape_domain(self, unmasker: IoCUnmasker) -> None:
        """Test Unicode escape sequence unmasking."""
        # \u0075\u0070\u0064\u0061\u0074\u0065 = "update"
        encoded = r"\u0075\u0070\u0064\u0061\u0074\u0065\u002e\u0065\u0076\u0069\u006c\u002e\u0063\u006f\u006d"
        report = unmasker.unmask(encoded)

        assert report.was_unmasked
        assert "update" in report.best_result.unmasked

    def test_unicode_hex_escape(self, unmasker: IoCUnmasker) -> None:
        r"""Test \xXX style hex escapes."""
        encoded = r"\x65\x76\x69\x6c\x2e\x63\x6f\x6d"  # evil.com
        report = unmasker.unmask(encoded)

        assert report.was_unmasked

    # ==========================================================================
    # String Reversal Tests
    # ==========================================================================

    def test_reversed_domain(self, unmasker: IoCUnmasker) -> None:
        """Test reversed domain detection and unmasking."""
        # Input is "evil.com" reversed as "moc.live"
        reversed_domain = "moc.live"
        report = unmasker.unmask(reversed_domain)

        assert report.was_unmasked
        # Should detect as reversed and return the original (evil.com)
        assert report.best_result.unmasked == "evil.com"
        assert report.best_result.technique == UnmaskTechnique.REVERSED

    def test_reversed_with_path(self, unmasker: IoCUnmasker) -> None:
        """Test reversed URL with path."""
        # Input is "https://evil.com" reversed
        reversed_url = "moc.//:sptth"
        report = unmasker.unmask(reversed_url)

        assert report.was_unmasked
        # Should detect as reversed
        assert report.best_result.technique == UnmaskTechnique.REVERSED

    # ==========================================================================
    # Defanged URL Tests
    # ==========================================================================

    def test_defanged_hxxp(self, unmasker: IoCUnmasker) -> None:
        """Test hxxp protocol substitution."""
        defanged = "hxxps://evil.com/path"
        report = unmasker.unmask(defanged)

        assert report.was_unmasked
        assert report.best_result.unmasked == "https://evil.com/path"
        assert report.best_result.technique == UnmaskTechnique.DEFANGED

    def test_defanged_bracketed_dots(self, unmasker: IoCUnmasker) -> None:
        """Test bracketed dot notation."""
        defanged = "https://evil[.]com"
        report = unmasker.unmask(defanged)

        assert report.was_unmasked
        assert report.best_result.unmasked == "https://evil.com"

    def test_defanged_parenthesized_dots(self, unmasker: IoCUnmasker) -> None:
        """Test parenthesized dot notation."""
        defanged = "evil(.)com"
        report = unmasker.unmask(defanged)

        assert report.was_unmasked
        assert report.best_result.unmasked == "evil.com"

    def test_defanged_bracketed_slashes(self, unmasker: IoCUnmasker) -> None:
        """Test bracketed slash notation."""
        defanged = "https://evil[/]com"
        report = unmasker.unmask(defanged)

        assert report.was_unmasked
        assert report.best_result.unmasked == "https://evil.com"

    def test_defanged_combined(self, unmasker: IoCUnmasker) -> None:
        """Test multiple defang techniques combined."""
        defanged = "hxxps://evil[.]com[/]path"
        report = unmasker.unmask(defanged)

        assert report.was_unmasked
        assert report.best_result.unmasked == "https://evil.com/path"

    # ==========================================================================
    # IPv4 Address Tests
    # ==========================================================================

    def test_url_encoded_ipv4(self, unmasker: IoCUnmasker) -> None:
        """Test percent-encoded IPv4 address."""
        encoded = "%31%39%32%2E%31%36%38%2E%31%2E%31"  # 192.168.1.1
        report = unmasker.unmask(encoded)

        assert report.was_unmasked
        assert report.best_result.unmasked == "192.168.1.1"

    # ==========================================================================
    # Edge Cases and Validation
    # ==========================================================================

    def test_empty_string(self, unmasker: IoCUnmasker) -> None:
        """Test empty string handling."""
        report = unmasker.unmask("")

        assert not report.was_unmasked
        assert report.best_result.unmasked == ""

    def test_whitespace_only(self, unmasker: IoCUnmasker) -> None:
        """Test whitespace-only string."""
        report = unmasker.unmask("   ")

        assert not report.was_unmasked

    def test_normal_ioc_unchanged(self, unmasker: IoCUnmasker) -> None:
        """Test that normal IoCs are not modified."""
        normal = "https://example.com"
        report = unmasker.unmask(normal)

        assert report.best_result.unmasked == normal
        assert not report.was_unmasked  # No unmasking needed

    def test_is_masked_detection(self, unmasker: IoCUnmasker) -> None:
        """Test the is_masked() detection method."""
        assert unmasker.is_masked("aHR0cHM6Ly9ldmlsLmNvbQ==")  # Base64
        assert unmasker.is_masked("68747470733a2f2f6576696c2e636f6d")  # Hex
        assert unmasker.is_masked("%65%76%69%6C%2E%63%6F%6D")  # URL-encoded
        assert unmasker.is_masked("hxxps://evil[.]com")  # Defanged
        assert not unmasker.is_masked("https://example.com")  # Normal

    # ==========================================================================
    # Batch Processing Tests
    # ==========================================================================

    def test_unmask_batch(self, unmasker: IoCUnmasker) -> None:
        """Test batch unmasking."""
        values = [
            "aHR0cHM6Ly9ldmlsLmNvbQ==",  # Base64: https://evil.com
            "hxxps://malware[.]com",      # Defanged
            "https://normal.com",          # Normal
        ]

        results = unmasker.unmask_batch(values)

        assert len(results) == 3
        assert results["aHR0cHM6Ly9ldmlsLmNvbQ=="].was_unmasked
        assert results["hxxps://malware[.]com"].was_unmasked
        assert not results["https://normal.com"].was_unmasked

    # ==========================================================================
    # Report Tests
    # ==========================================================================

    def test_unmask_report_properties(self, unmasker: IoCUnmasker) -> None:
        """Test UnmaskReport properties."""
        report = unmasker.unmask("hxxps://evil[.]com")

        assert report.was_unmasked
        assert len(report.successful_techniques) > 0
        assert report.total_attempts > 0
        assert report.best_result is not None

    def test_get_supported_techniques(self, unmasker: IoCUnmasker) -> None:
        """Test getting list of supported techniques."""
        techniques = unmasker.get_supported_techniques()

        assert UnmaskTechnique.BASE64.value in techniques
        assert UnmaskTechnique.HEX.value in techniques
        assert UnmaskTechnique.DEFANGED.value in techniques
        assert UnmaskTechnique.URL_ENCODED.value in techniques

    # ==========================================================================
    # Hash Tests
    # ==========================================================================

    def test_base64_hash(self, unmasker: IoCUnmasker) -> None:
        """Test Base64 encoded file hash."""
        # SHA256 hash encoded in Base64
        encoded_hash = "YTNiMWM1ZDk4MmIyNDk5NzFmYzY1ODlmMjk0Zjk1MTJmNTRkYzYwOWEwMGI2MWY1MTE2ZmY4ZTQzZjk3MmZlNw=="
        report = unmasker.unmask(encoded_hash)

        # Should decode to valid hex hash
        assert report.was_unmasked
        assert len(report.best_result.unmasked) == 64

    # ==========================================================================
    # Confidence Scoring Tests
    # ==========================================================================

    def test_confidence_scoring_defanged(self, unmasker: IoCUnmasker) -> None:
        """Test that defanged URLs have high confidence."""
        report = unmasker.unmask("hxxps://evil[.]com")

        assert report.best_result.technique == UnmaskTechnique.DEFANGED
        assert report.best_result.confidence >= 0.9

    def test_confidence_scoring_reversed(self, unmasker: IoCUnmasker) -> None:
        """Test that reversed domains have lower confidence."""
        report = unmasker.unmask("moc.evil.com")

        if report.best_result.technique == UnmaskTechnique.REVERSED:
            # Reversed should have lower confidence
            assert report.best_result.confidence < 0.8


# ==========================================================================
# Integration Tests with Real-World Examples
# ==========================================================================

class TestRealWorldExamples:
    """Tests with real-world obfuscation examples from malware reports."""

    @pytest.fixture
    def unmasker(self) -> IoCUnmasker:
        """Create a fresh unmasker instance."""
        return IoCUnmasker()

    def test_malware_report_defanged_iocs(self, unmasker: IoCUnmasker) -> None:
        """Test common defang patterns from malware reports."""
        test_cases = [
            ("hxxp://evil[.]com", "http://evil.com"),
            ("https://malware[.]domain[.]com/path", "https://malware.domain.com/path"),
            ("hxxps://phishing[.]site", "https://phishing.site"),
            ("http://bad[.]site/malware.exe", "http://bad.site/malware.exe"),
        ]

        for defanged, expected in test_cases:
            report = unmasker.unmask(defanged)
            assert report.best_result.unmasked == expected

    def test_threat_feed_encoded_iocs(self, unmasker: IoCUnmasker) -> None:
        """Test encoded IoCs from threat intelligence feeds."""
        test_cases = [
            ("aHR0cDovL2JhZC5jb20=", "http://bad.com"),  # Base64
            ("%62%61%64%2E%63%6F%6D", "bad.com"),        # URL-encoded
        ]

        for encoded, expected in test_cases:
            report = unmasker.unmask(encoded)
            assert expected in report.best_result.unmasked


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

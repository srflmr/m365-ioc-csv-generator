"""
IoC (Indicator of Compromise) Detection Module.

Provides robust detection and categorization of various IoC types:
- File SHA256 hashes (64 hex characters)
- File SHA1 hashes (40 hex characters)
- File MD5 hashes (32 hex characters) - Note: MD5 is cryptographically weak
- IPv4 addresses
- Domain names
- URLs (with or without scheme)

Detection patterns based on Microsoft Defender IoC requirements.
"""

from __future__ import annotations

import re
import ipaddress
from dataclasses import dataclass
from enum import Enum, unique
from typing import Optional

from m365_ioc_csv.utils.error_handler import ValidationError
from m365_ioc_csv.utils.logger import get_logger

logger = get_logger(__name__)


@unique
class IoCType(Enum):
    """Enumeration of supported IoC types matching Microsoft Defender schema."""

    FILE_SHA256 = "FileSha256"
    FILE_SHA1 = "FileSha1"
    FILE_MD5 = "FileMd5"
    IP_ADDRESS = "IpAddress"
    DOMAIN_NAME = "DomainName"
    URL = "Url"
    URL_NO_SCHEME = "UrlNoScheme"  # Internal use, will be converted to URL
    UNKNOWN = "Unknown"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class IoCMatch:
    """
    Represents a detected IoC with its type and metadata.

    Attributes:
        value: The original IoC value
        type: Detected IoC type
        is_valid: Whether the IoC passed validation
    """

    value: str
    type: IoCType
    is_valid: bool = True

    def __post_init__(self) -> None:
        """Validate IoC value matches detected type."""
        if self.is_valid:
            self._validate()

    def _validate(self) -> None:
        """Internal validation to ensure IoC matches its type."""
        if self.type == IoCType.FILE_SHA256:
            if not IoCDetector.SHA256_RE.fullmatch(self.value):
                raise ValidationError(f"Invalid SHA256 hash: {self.value}", "FileSha256")
        elif self.type == IoCType.FILE_SHA1:
            if not IoCDetector.SHA1_RE.fullmatch(self.value):
                raise ValidationError(f"Invalid SHA1 hash: {self.value}", "FileSha1")
        elif self.type == IoCType.FILE_MD5:
            if not IoCDetector.MD5_RE.fullmatch(self.value):
                raise ValidationError(f"Invalid MD5 hash: {self.value}", "FileMd5")
        elif self.type == IoCType.IP_ADDRESS:
            try:
                ipaddress.IPv4Address(self.value)
            except ipaddress.AddressValueError:
                raise ValidationError(f"Invalid IPv4 address: {self.value}", "IpAddress")


class IoCDetector:
    """
    Detects and categorizes Indicators of Compromise (IoCs).

    Features:
    - Regex-based pattern matching
    - Support for multiple IoC types
    - URL detection with/without scheme
    - Strict domain validation
    - IPv4 address validation

    Example:
        detector = IoCDetector()
        match = detector.detect("192.168.1.1")
        # Returns: IoCMatch(value="192.168.1.1", type=IoCType.IP_ADDRESS)
    """

    # Pre-compiled regex patterns for performance
    SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
    SHA1_RE = re.compile(r"^[0-9a-fA-F]{40}$")
    MD5_RE = re.compile(r"^[0-9a-fA-F]{32}$")

    # Strict domain validation (RFC compliant)
    # - Labels 1-63 chars, alphanumeric or hyphen (not start/end with hyphen)
    # - TLD at least 2 chars
    # - Total length 1-253 chars
    # - Supports IDN (internationalized domain names)
    DOMAIN_RE = re.compile(
        r"^(?=.{1,253}$)"  # Length check
        r"(?!-)[A-Za-z0-9-]{1,63}(?<!-)"  # First label
        r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*"  # Additional labels
        r"\.[A-Za-z]{2,63}$"  # TLD
    )

    # URL schemes
    URL_SCHEMES = ("http://", "https://")

    def __init__(self) -> None:
        """Initialize the IoC detector."""
        logger.debug("IoCDetector initialized")

    def detect(self, value: str) -> IoCMatch:
        """
        Detect IoC type from a string value.

        Args:
            value: The IoC value to detect

        Returns:
            IoCMatch with detected type

        Example:
            detector = IoCDetector()
            match = detector.detect("https://evil.com")
            # match.type == IoCType.URL
        """
        if not value:
            return IoCMatch(value="", type=IoCType.UNKNOWN, is_valid=False)

        cleaned = value.strip()

        # Priority detection order (most specific first)

        # 1. URL with scheme
        if cleaned.lower().startswith(self.URL_SCHEMES):
            logger.debug(f"Detected URL with scheme: {cleaned[:50]}...")
            return IoCMatch(value=cleaned, type=IoCType.URL)

        # 2. SHA256 hash (64 hex chars)
        if self.SHA256_RE.fullmatch(cleaned):
            logger.debug(f"Detected SHA256 hash: {cleaned[:16]}...")
            return IoCMatch(value=cleaned, type=IoCType.FILE_SHA256)

        # 3. SHA1 hash (40 hex chars)
        if self.SHA1_RE.fullmatch(cleaned):
            logger.debug(f"Detected SHA1 hash: {cleaned[:16]}...")
            return IoCMatch(value=cleaned, type=IoCType.FILE_SHA1)

        # 4. MD5 hash (32 hex chars)
        if self.MD5_RE.fullmatch(cleaned):
            logger.warning(f"Detected MD5 hash (weak): {cleaned[:16]}... - MD5 is cryptographically broken and should not be relied upon for security purposes")
            return IoCMatch(value=cleaned, type=IoCType.FILE_MD5)

        # 5. IPv4 address
        if self._is_ipv4(cleaned):
            logger.debug(f"Detected IPv4 address: {cleaned}")
            return IoCMatch(value=cleaned, type=IoCType.IP_ADDRESS)

        # 6. URL without scheme (check BEFORE domain, since www.example.com looks like domain)
        # Priority: www. prefix OR contains slash
        if self._looks_like_url_no_scheme(cleaned):
            logger.debug(f"Detected URL without scheme: {cleaned[:50]}...")
            return IoCMatch(value=cleaned, type=IoCType.URL_NO_SCHEME)

        # 7. Domain name (no scheme/path, no www.)
        if self.DOMAIN_RE.fullmatch(cleaned):
            logger.debug(f"Detected domain name: {cleaned}")
            return IoCMatch(value=cleaned, type=IoCType.DOMAIN_NAME)

        # Unknown type
        logger.debug(f"Unknown IoC type: {cleaned[:50]}...")
        return IoCMatch(value=cleaned, type=IoCType.UNKNOWN, is_valid=False)

    def detect_type(self, value: str) -> Optional[str]:
        """
        Detect IoC type and return string representation.

        Convenience method for backward compatibility.

        Args:
            value: The IoC value to detect

        Returns:
            IoC type string or None if unknown
        """
        match = self.detect(value)
        return match.type.value if match.type != IoCType.UNKNOWN else None

    def detect_batch(self, values: list[str]) -> dict[IoCType, list[str]]:
        """
        Detect multiple IoC values and group by type.

        Args:
            values: List of IoC values to detect

        Returns:
            Dictionary mapping IoC types to lists of values

        Example:
            detector = IoCDetector()
            results = detector.detect_batch(["192.168.1.1", "evil.com", "abc123"])
            # results[IoCType.IP_ADDRESS] == ["192.168.1.1"]
            # results[IoCType.DOMAIN_NAME] == ["evil.com"]
        """
        grouped: dict[IoCType, list[str]] = {
            ioc_type for ioc_type in IoCType
            if ioc_type not in (IoCType.UNKNOWN, IoCType.URL_NO_SCHEME)
        }

        for value in values:
            match = self.detect(value)
            if match.is_valid and match.type != IoCType.UNKNOWN:
                if match.type not in grouped:
                    grouped[match.type] = []
                grouped[match.type].append(value)

        logger.info(f"Detected {sum(len(v) for v in grouped.values())} IoCs from {len(values)} inputs")
        return grouped

    @staticmethod
    def _is_ipv4(value: str) -> bool:
        """
        Check if value is a valid IPv4 address.

        Args:
            value: String to validate

        Returns:
            True if valid IPv4 address
        """
        try:
            ipaddress.IPv4Address(value)
            return True
        except (ipaddress.AddressValueError, ValueError):
            return False

    @staticmethod
    def _looks_like_url_no_scheme(value: str) -> bool:
        """
        Check if value looks like a URL without scheme.

        Patterns:
        - www. prefix (even without path)
        - Contains a slash (path) with domain-like host

        Args:
            value: String to check

        Returns:
            True if looks like URL without scheme
        """
        cleaned = value.lower().strip()

        # Check for www. prefix (common URL pattern without scheme)
        if cleaned.startswith("www."):
            # Must have at least one more dot after www.
            parts = cleaned[4:].split(".")
            if len(parts) >= 2 and all(len(p) > 0 for p in parts):
                return True

        # Must contain slash for other URLs
        if "/" not in cleaned:
            return False

        # Extract host part (before first slash)
        host = cleaned.split("/", 1)[0]

        # Remove www. prefix for domain check
        if host.startswith("www."):
            host = host[4:]

        # Check if remaining part looks like a domain
        return bool(IoCDetector.DOMAIN_RE.fullmatch(host))

    @staticmethod
    def fix_url_scheme(url: str, scheme: str = "https://") -> str:
        """
        Add scheme to URL that doesn't have one.

        .. deprecated::
            This method is deprecated and will be removed in a future version.
            URLs without scheme are now exported as-is to Microsoft Defender,
            which handles scheme validation internally based on threat intelligence.

        Args:
            url: URL value (may or may not have scheme)
            scheme: Scheme to add (default: https://)

        Returns:
            URL with scheme

        Example:
            detector = IoCDetector()
            detector.fix_url_scheme("example.com/path")
            # Returns: "https://example.com/path"
        """
        import warnings
        warnings.warn(
            "fix_url_scheme() is deprecated. URLs are now exported as-is to "
            "Microsoft Defender, which handles scheme validation internally.",
            DeprecationWarning,
            stacklevel=2
        )

        if url.lower().startswith(("http://", "https://")):
            return url

        # Ensure scheme ends with ://
        if not scheme.endswith("://"):
            scheme += "://"

        return f"{scheme}{url}"

    def is_valid_ioc(self, value: str) -> bool:
        """
        Quick check if value is a valid IoC.

        Args:
            value: Value to check

        Returns:
            True if value is a recognized IoC type
        """
        match = self.detect(value)
        return match.is_valid and match.type != IoCType.UNKNOWN

    def get_supported_types(self) -> list[str]:
        """
        Get list of supported IoC types.

        Returns:
            List of IoC type names
        """
        return [
            IoCType.FILE_SHA256.value,
            IoCType.FILE_SHA1.value,
            IoCType.FILE_MD5.value,
            IoCType.IP_ADDRESS.value,
            IoCType.DOMAIN_NAME.value,
            IoCType.URL.value,
        ]

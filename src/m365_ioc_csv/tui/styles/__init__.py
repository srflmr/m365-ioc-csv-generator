"""
TCSS (Textual CSS) styles for the application.

Modern responsive theme with auto-sizing and beautiful aesthetics.
Based on Textual 2025/2026 best practices.
"""

from __future__ import annotations

# Main application styles - Modern 2026 Theme
APP_STYLES = """
/* ============================================
   GLOBAL STYLES - Modern Dark Theme
   ============================================ */
Screen {
    background: $panel;
}

/* Header - Gradient effect with modern styling */
Header {
    background: $primary;
    color: $text;
    text-align: center;
    padding: 0 2;
    text-style: bold;
    dock: top;
}

/* Footer - Subtle info bar */
Footer {
    background: $surface;
    color: $text-muted;
    padding: 0 2;
    text-align: center;
    dock: bottom;
}

/* ============================================
   CONTAINER STYLES - Responsive Borders
   ============================================ */
Container {
    background: $panel;
}

/* Panels with beautiful borders */
#file-browser-panel {
    border: thick $primary;
    border-title-color: $accent;
    border-title-style: bold;
    border-subtitle-color: $text-muted;
}

#file-info-container {
    background: $boost;
    border: thick $success;
    border-title-color: $success;
    border-title-style: bold;
}

#config-container {
    background: $boost;
    border: thick $accent;
    border-title-color: $accent;
    border-title-style: bold;
}

#summary-panel {
    background: $boost;
    border: thick $warning;
    border-title-color: $warning;
    border-title-style: bold;
}

/* ============================================
   BUTTON STYLES - Modern with Emojis
   ============================================ */
Button {
    min-width: 15;
    height: 3;
    margin: 0;
    padding: 0 1;
    background: $surface;
    border: round $primary;
    text-style: bold;
}

Button:hover {
    background: $primary;
    color: $text;
    text-style: bold underline;
}

Button.-primary {
    background: $primary;
    color: $text;
    border: round $primary-darken-1;
    text-style: bold;
}

Button.-primary:hover {
    background: $primary-darken-2;
    border: round $primary-darken-3;
}

/* ============================================
   INPUT & SELECT STYLES - Auto Width
   ============================================ */
Input {
    width: 1fr;
    min-width: 20;
    border: solid $primary;
    padding: 0 1;
    background: $panel;
    color: $text;
}

Input:focus {
    border: thick $accent;
    background: $surface;
}

Select {
    width: 1fr;
    min-width: 20;
    border: solid $primary;
    background: $panel;
    color: $text;
}

Select:focus {
    border: thick $accent;
    background: $surface;
}

Select > SelectOverlay {
    background: $surface;
    border: thick $accent;
}

/* ============================================
   LABEL & TEXT STYLES
   ============================================ */
Label {
    color: $text;
    padding: 0 1;
}

.config-label {
    color: $text;
    text-style: bold;
    min-width: 25;
    text-align: right;
}

.info-label {
    color: $text;
    text-style: bold;
    min-width: 20;
    text-align: right;
}

.info-value {
    color: $text-muted;
}

/* Title styling */
#file-browser-title,
#file-info-title,
#config-title,
#summary-title {
    text-style: bold;
    padding: 0 1;
    background: $surface;
    color: $text;
    border-bottom: solid $primary;
}

/* ============================================
   DATA TABLE STYLES - Modern Look
   ============================================ */
DataTable {
    background: $panel;
    border: thick $primary;
}

DataTable > DataTableHeader {
    background: $primary;
    color: $text;
    text-style: bold;
}

DataTable > DataTableCursor {
    background: $accent;
    color: $background;
    text-style: bold;
}

DataTable > DataTableRow {
    color: $text;
}

DataTable > DataTableRow:hover {
    background: $boost;
    text-style: underline;
}

/* ============================================
   DIRECTORY TREE STYLES - Beautiful Icons
   ============================================ */
DirectoryTree {
    background: $panel;
    border: none;
}

DirectoryTree > .directory-tree--directory {
    color: $accent;
    text-style: bold;
}

DirectoryTree > .directory-tree--file {
    color: $text;
}

DirectoryTree > .directory-tree--file.--selected {
    background: $primary;
    color: $text;
    text-style: bold;
}

DirectoryTree.--cursor {
    background: $accent;
    color: $background;
}

/* ============================================
   UTILITY CLASSES - Modern Helpers
   ============================================ */
.-hidden {
    display: none;
}

.-center {
    align: center middle;
}

.-right {
    text-align: right;
}

.-bold {
    text-style: bold;
}

.-muted {
    color: $text-muted;
}

.-accent {
    color: $accent;
}

.-success {
    color: $success;
}

.-warning {
    color: $warning;
}

.-error {
    color: $error;
}

.-info {
    color: $primary;
}

/* ============================================
   SCROLLABLE CONTAINER - Modern Scrollbar
   ============================================ */
ScrollableContainer {
    scrollbar-size: 1 1;
    scrollbar-background: $surface;
    scrollbar-color: $primary;
    scrollbar-gutter: auto;
}

/* ============================================
   SPECIAL HIGHLIGHTS
   ============================================ */
.header-detected {
    text-style: bold;
    color: $success;
}

.header-not-detected {
    text-style: italic;
    color: $warning;
}
"""

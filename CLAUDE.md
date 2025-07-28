# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains materials for "클래식기타 중주단 미련 연주회 2025" (Classical Guitar Ensemble Concert 2025), a Korean classical guitar concert scheduled for August 23, 2025 at SCC Hall.

**Project Type**: Static website for a classical guitar concert
**Main Technology**: Pure HTML/CSS (no build system or frameworks)

## File Structure

```
MRGQ2025/
├── index.html          # Main concert program webpage
├── concert_program.md  # Markdown version of concert program
└── program_notes.md    # Detailed program notes for each piece
```

## Key Files

- **index.html**: Self-contained HTML file with embedded CSS styling that displays the complete concert program and program notes. Uses Korean typography (Noto Serif KR) and classical concert styling.
- **concert_program.md**: Simplified markdown outline of the concert program structure
- **program_notes.md**: Detailed background information about each musical piece being performed

## Development Workflow

Since this is a static HTML project with no build system:

1. **Viewing the site**: Open `index.html` directly in a web browser
2. **Making changes**: Edit files directly with any text editor
3. **No build step required**: Changes are immediately visible when refreshing the browser

## Content Structure

The concert is organized in two parts:
- **Part 1**: Quartet, Trio, Duos, and Solo performances
- **Intermission**
- **Part 2**: Duos and Quintet performances

Each piece includes detailed program notes explaining the musical background, composer information, and performance context.

## Styling Guidelines

The website uses:
- Korean serif typography (Noto Serif KR)
- Warm brown color scheme (#2c1810, #4a2c1a, #8b6f3a)
- Classical concert aesthetic with elegant spacing and typography
- Responsive design for mobile devices
- Hover effects on program items

## Git Repository

This is a git repository with clean status. Recent commits show ongoing updates to composer names and program notes.
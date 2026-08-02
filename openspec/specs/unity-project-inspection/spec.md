# Unity Project Inspection Specification

## Purpose

Durable behavioral contract for `unity-project-inspection`.

## Requirements

### Requirement: Safe project inspector

The package MUST provide a dependency-free Python 3.9+ read-only inspector that

#### Scenario: US4 - Inspect an unfamiliar Unity project safely 1

- **GIVEN** a Unity project root
- **WHEN** the inspector runs
- **THEN** it reports the Editor version, declared packages, assembly definitions, test assemblies, C# file counts, and bounded architectural risk signals with source paths

#### Scenario: US4 - Inspect an unfamiliar Unity project safely 2

- **GIVEN** malformed or missing metadata
- **WHEN** the inspector runs
- **THEN** it returns an actionable warning and nonzero status only when the requested root cannot be inspected as a Unity project

#### Scenario: US4 - Inspect an unfamiliar Unity project safely 3

- **GIVEN** secret-like files or arbitrary source code
- **WHEN** the inspector scans
- **THEN** it excludes secret-like paths and emits counts and paths only, never file contents or credential values

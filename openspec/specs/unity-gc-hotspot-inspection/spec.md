# Unity Gc Hotspot Inspection Specification

## Purpose

Durable behavioral contract for `unity-gc-hotspot-inspection`.

## Requirements

### Requirement: Safe allocation-hotspot inspector

The package MUST provide a dependency-free Python 3.9+ read-only inspector that

#### Scenario: US4 - Inspect Unity allocation signals safely 1

- **GIVEN** a Unity project root
- **WHEN** the inspector runs
- **THEN** it reports Editor version, scripting backend hints when discoverable, declared relevant packages, C# file counts, and bounded paths for LINQ, coroutine, tween, spawn/destroy, query, array-return, collection, lambda, string/logging, and native-container signals

#### Scenario: US4 - Inspect Unity allocation signals safely 2

- **GIVEN** a signal match
- **WHEN** the report is rendered
- **THEN** it labels the match as an investigation lead and never emits source lines, matched values, or an automatic allocation diagnosis

#### Scenario: US4 - Inspect Unity allocation signals safely 3

- **GIVEN** generated/cache/build/VCS/IDE or secret-like paths
- **WHEN** the inspector scans
- **THEN** it excludes them and produces deterministic output without changing any project file

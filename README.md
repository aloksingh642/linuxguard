# LinuxGuard 🛡️

**Intelligent Linux System Health & Storage Manager**

LinuxGuard is a Python-based Linux system monitoring and storage management application designed to analyze disk usage, identify storage-heavy files, detect unusual storage growth, and safely manage selected cleanup operations.

It combines a **FastAPI backend**, **Streamlit dashboard**, **SQLite database**, **machine-learning-based anomaly detection**, and **Docker deployment** into one project.

---

## 🚀 Features

### 🖥️ System Health Monitoring

* Monitor Linux filesystem disk usage.
* Report total, used, and free storage.
* Classify storage health as:

  * `HEALTHY`
  * `WARNING`
  * `CRITICAL`
* Configurable filesystem path for Docker deployments.

### 🔍 Storage Analysis

* Scan directories and files.
* Identify the largest files.
* Analyze file types and categories.
* Categorize files such as:

  * Video
  * Image
  * Document
  * Archive
  * Code
  * Other
* Generate storage reports and CSV exports.

### 🧹 Safe Cleanup Engine

LinuxGuard does not provide unrestricted file deletion.

Cleanup is restricted to explicitly approved directories such as:

```text
<user>/.cache
<user>/Downloads
```

The cleanup engine includes:

* Protected-directory checks
* Symlink protection
* Allowed-directory validation
* Path traversal protection
* Dry-run support
* User confirmation
* Cleanup history
* Success/failure logging

### 🗄️ Database

LinuxGuard uses **SQLite + SQLAlchemy** to persist:

* System scan history
* Disk usage information
* Cleanup actions
* Cleanup status and timestamps

### 🌐 REST API

The FastAPI backend provides endpoints for:

| Endpoint              | Method | Purpose                            |
| --------------------- | ------ | ---------------------------------- |
| `/`                   | GET    | API health check                   |
| `/system`             | GET    | Current system health              |
| `/scan`               | POST   | Create and store a system scan     |
| `/scans`              | GET    | Retrieve scan history              |
| `/storage-analysis`   | GET    | Storage analysis                   |
| `/cleanup-candidates` | GET    | List approved cleanup candidates   |
| `/cleanup`            | POST   | Safely delete an approved file     |
| `/cleanup-history`    | GET    | Retrieve cleanup history           |
| `/anomalies`          | GET    | Retrieve anomaly-detection results |

FastAPI also provides interactive API documentation.

### 📊 Web Dashboard

The Streamlit dashboard provides a graphical interface for:

* System health
* Storage scans
* Scan history
* Storage analysis
* Cleanup candidates
* Safe cleanup
* Cleanup history
* Anomaly detection

### 🤖 Anomaly Detection

LinuxGuard uses **Isolation Forest** from scikit-learn for unsupervised anomaly detection.

The model considers storage-related features including:

* Disk usage percentage
* Used storage
* Change from the previous scan
* Time between scans
* Storage growth rate

The anomaly system is intended to highlight unusual storage-growth patterns rather than predict a specific future storage value.

### 🐳 Docker Deployment

LinuxGuard can run as two Docker services:

```text
                ┌─────────────────────┐
                │   Streamlit         │
                │   Dashboard         │
                │      :8501          │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │     FastAPI         │
                │      :8000          │
                └──────────┬──────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      SQLite DB       Linux Scanner     Cleanup Engine
```

Docker Compose provides:

* API container
* Dashboard container
* Persistent SQLite volume
* Read-only host filesystem scanning
* Restricted writable cleanup mounts
* Configurable host UID/GID
* Non-root container execution

---

## 🏗️ Architecture

```text
                         LinuxGuard
                             │
              ┌──────────────┴──────────────┐
              │                             │
          Streamlit                     FastAPI
          Dashboard                     REST API
              │                             │
              └──────────────┬──────────────┘
                             │
                    Application Services
                             │
       ┌─────────────┬───────┼────────┬──────────────┐
       │             │       │        │              │
    System       Scanner   Cleanup  Anomaly      Reporting
    Monitor                 Engine  Detection      & Export
       │             │       │        │              │
       └─────────────┴───────┼────────┴──────────────┘
                             │
                       Repository Layer
                             │
                       SQLAlchemy ORM
                             │
                         SQLite DB
```

---

## 🔐 Cleanup Safety Model

Cleanup is intentionally more restrictive than scanning.

Scanning can operate on a read-only host filesystem mount, while deletion is limited to exp

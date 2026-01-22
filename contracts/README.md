# Contracts Directory

This directory contains all team contracts for the BalanceCloud MVP project.

**📖 Start Here:** Read `TEAM_WORKFLOW.md` in the root directory for the complete workflow.

---

## 📁 Directory Structure

```
contracts/
├── README.md                          # This file
├── QUICK_START.md                     # 5-minute quick start guide
├── backend-api-v1.0.0.md              # Backend API contract (Bilal - Backend)
├── frontend-backend-v1.0.0.md         # Frontend integration contract (Mouhamad)
├── cloud-accounts-api-v1.0.0.md       # Cloud accounts API contract (Bilal - Backend)
├── cloud-connector-backend-v1.0.0.md  # Cloud connector contract (Helijao)
├── encryption-service-v1.0.0.md        # Encryption service contract (Bilal - Encryption)
└── change-requests/
    ├── TEMPLATE.md                    # CCR template
    └── ccr-001-*.md                   # Actual change requests
```

---

## 📋 Contract Status

| Contract | Owner | Version | Status | Last Updated |
|----------|-------|---------|--------|--------------|
| Backend API | Bilal (Backend) | 1.0.0 | ✅ Stable | 2026-01-22 |
| Frontend-Backend | Mouhamad (Frontend) | 1.0.0 | 📝 Draft | 2026-01-20 |
| Cloud Accounts API | Bilal (Backend) | 1.0.0 | 📝 Draft | 2026-01-20 |
| Cloud Connector | Helijao (Cloud) | 1.0.0 | 📝 Draft | 2026-01-20 |
| Encryption Service | Bilal (Encryption) | 1.0.0 | 📝 Draft | 2026-01-20 |

**Status Legend:**
- 📝 **Draft:** Still being designed, don't integrate yet
- 👀 **Review:** Ready for feedback, can use mocks
- ✅ **Stable:** Production-ready, safe to integrate
- ⚠️ **Deprecated:** Will be removed, migration required

---

## 🚀 Quick Links

- **Team Workflow:** `../docs/team/TEAM_WORKFLOW.md`
- **Tasks Planning:** `../TASKS_PLANING.md` (Reference for contract requirements)
- **Quick Start:** `QUICK_START.md`
- **Change Request Template:** `change-requests/TEMPLATE.md`
- **Mock Handlers:** `../mocks/backend-api/handlers.ts`

---

## 📚 Contracts by Developer Role

### Bilal (Backend Infrastructure)
- **[Backend API Contract](backend-api-v1.0.0.md)** - Core API endpoints (✅ Stable)
- **[Cloud Accounts API Contract](cloud-accounts-api-v1.0.0.md)** - Cloud account management endpoints (📝 Draft)

### Bilal (Encryption & File Services)
- **[Encryption Service Contract](encryption-service-v1.0.0.md)** - Encryption, chunking, key management (📝 Draft)

### Helijao (Cloud Connectors)
- **[Cloud Connector Contract](cloud-connector-backend-v1.0.0.md)** - OAuth flows, Google Drive, OneDrive integration (📝 Draft)

### Mouhamad (Frontend & UX)
- **[Frontend-Backend Contract](frontend-backend-v1.0.0.md)** - Frontend integration patterns (📝 Draft)

---

## 📋 Contract Reference to Tasks

All contracts are based on **TASKS_PLANING.md** which outlines the 1-week sprint plan:

- **Day 1:** Foundation setup (OAuth research, encryption architecture design)
- **Day 2:** Core backend features (database migration, Google Drive integration, encryption service)
- **Day 3:** File operations & cloud upload (staging area, OneDrive integration, cloud upload service)
- **Day 4:** Download & integration (cloud download service, account management, frontend integration)
- **Day 5:** Testing, bug fixes & documentation

Each contract includes implementation tasks from TASKS_PLANING.md in its "Implementation Tasks" section.

---

## 📝 Contract Lifecycle

```
Draft → Review → Stable → (Breaking Change) → Draft
  ↓       ↓        ↓
  └───────┴────────┘
   (Non-breaking updates)
```

**When to use each status:**
- **Draft:** Owner is designing, others should wait
- **Review:** Ready for team feedback, integration can start with mocks
- **Stable:** Production-ready, breaking changes require approval
- **Deprecated:** Will be removed, migration path provided

---

## 🔄 Making Changes

### Non-Breaking Changes
1. Owner updates contract (bump MINOR version)
2. Notify team via Slack/PR
3. 24-hour review period
4. Merge if no objections

### Breaking Changes
1. Create Contract Change Request (CCR)
2. Team reviews and approves
3. Create new MAJOR version
4. Keep old version as deprecated
5. Provide migration guide

See `TEAM_WORKFLOW.md` for detailed process.

---

## ✅ Contract Checklist

Every contract must include:

- [ ] **Owner** clearly identified
- [ ] **Version** number (semantic versioning)
- [ ] **Status** (Draft/Review/Stable/Deprecated)
- [ ] **Dependencies** listed
- [ ] **Interface Definition** (endpoints, schemas, signatures)
- [ ] **Behavior Specification** (responses, errors, edge cases)
- [ ] **Mock Implementation** (or link to mock)
- [ ] **Change Log** (history of changes)

---

## 🆘 Need Help?

1. **New to contracts?** → Read `QUICK_START.md`
2. **Need to change a contract?** → See `change-requests/TEMPLATE.md`
3. **Contract doesn't match implementation?** → Create issue, tag owner
4. **Owner not responding?** → Wait 48 hours, then escalate

---

**Last Updated:** 2026-01-20

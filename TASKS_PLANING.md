# MVP to Full Version Migration Plan
## 1-Week Sprint for 4 Developers

## Overview

**Goal**: Migrate from MVP (local storage) to Full Version (cloud storage with advanced features)  
**Timeline**: 1 week (5 working days)  
**Team Size**: 4 developers  
**Approach**: Parallel work streams with daily syncs

---

## Team Roles & Responsibilities

### 👤 **Bilal: Backend Infrastructure/Encryption & File Services**
**Focus**: Database migration, Redis setup, infrastructure improvements, File chunking, enhanced encryption, key storage

### 👤 **Helijao: Cloud Connectors**
**Focus**: OAuth2 flows, Google Drive & [OneDrive integration] Theoretical

### 👤 **Aakash: Manager**
**Focus**: Team managment/ documentation

### 👤 **Moudi: Frontend & UX**
**Focus**: Cloud accounts UI, improved user experience

---

## Day-by-Day Breakdown

### 📅 **Day 1: Foundation Setup**

#### Bilal: Infrastructure Setup
**Tasks** (4-6 hours):
- [ ] Set up PostgreSQL database (replace SQLite)
- [ ] Create Alembic migrations for schema changes
- [ ] Set up Redis for rate limiting
- [ ] Update `docker-compose.yml` with PostgreSQL and Redis services
- [ ] Update `config.py` to use PostgreSQL connection string
- [ ] Test database connectivity

**Deliverables**:
- PostgreSQL running in Docker
- Redis running in Docker
- Database migrations working
- Updated docker-compose.yml

#### Helijao: OAuth Setup & Research
**Tasks** (4-6 hours):
- [ ] Research Google Drive OAuth2 flow
- [ ] Research OneDrive OAuth2 flow
- [ ] Set up OAuth credentials in Google Cloud Console
- [ ] Set up OAuth credentials in Azure Portal
- [ ] Create `cloud_connector_service.py` skeleton
- [ ] Test OAuth redirect URLs

**Deliverables**:
- OAuth credentials configured
- Basic OAuth flow structure
- Test redirect URLs working

#### Bilal: Encryption Architecture Design
**Tasks** (4-6 hours):
- [ ] Design chunking strategy (10MB chunks)
- [ ] Plan key storage in database (encrypted user keys)
- [ ] Review full version encryption service
- [ ] Create `encryption_key` model/schema
- [ ] Design chunk storage structure
- [ ] Update encryption service architecture

**Deliverables**:
- Encryption architecture document
- Database schema for encryption keys
- Chunking strategy defined

#### Mouhamad: Frontend Planning & Setup
**Tasks** (4-6 hours):
- [ ] Review full version frontend structure
- [ ] Plan cloud accounts UI components
- [ ] Set up cloud account store (Zustand)
- [ ] Create cloud account service skeleton
- [ ] Design OAuth callback flow
- [ ] Update routing for cloud accounts page

**Deliverables**:
- Cloud accounts page structure
- OAuth callback page
- Updated routing

---

### 📅 **Day 2: Core Backend Features**

#### Bilal: Database Migration & Models
**Tasks** (6-8 hours):
- [ ] Migrate User model to PostgreSQL
- [ ] Create CloudAccount model
- [ ] Create EncryptionKey model
- [ ] Create StorageChunk model (for chunking)
- [ ] Update File model for chunked storage
- [ ] Run migrations and test

**Deliverables**:
- All models migrated to PostgreSQL
- Database schema complete
- Migrations tested

#### Helijao: Google Drive Integration
**Tasks** (6-8 hours):
- [ ] Implement Google Drive OAuth2 flow
- [ ] Create `cloud_connector_service.py` for Google
- [ ] Implement token refresh logic
- [ ] Test Google Drive connection
- [ ] Create basic upload to Google Drive
- [ ] Create basic download from Google Drive

**Deliverables**:
- Google Drive OAuth working
- Can connect Google Drive account
- Basic upload/download working

#### Bilal: Enhanced Encryption Service
**Tasks** (6-8 hours):
- [ ] Implement user key storage in database
- [ ] Update encryption service for chunking
- [ ] Implement chunk key derivation (HKDF)
- [ ] Create chunk encryption/decryption methods
- [ ] Update file service for chunking
- [ ] Test encryption with chunks

**Deliverables**:
- User keys stored encrypted in DB
- Chunking encryption working
- File service supports chunks

#### Mouhamad: Cloud Accounts Frontend
**Tasks** (6-8 hours):
- [ ] Build cloud accounts page UI
- [ ] Implement OAuth popup flow
- [ ] Create cloud account cards (Google Drive, OneDrive)
- [ ] Add connect/disconnect functionality
- [ ] Handle OAuth callbacks
- [ ] Display connection status

**Deliverables**:
- Cloud accounts page functional
- OAuth flow working
- Can connect/disconnect accounts

---

### 📅 **Day 3: File Operations & Cloud Upload**

#### Bilal: Staging Area & File Pipeline
**Tasks** (6-8 hours):
- [ ] Create staging area structure (`staging/uploads`, `staging/encrypted`)
- [ ] Implement file upload pipeline
- [ ] Add file chunking logic
- [ ] Create chunk metadata storage
- [ ] Update file routes for chunked uploads
- [ ] Test large file uploads

**Deliverables**:
- Staging area working
- File chunking implemented
- Upload pipeline functional

<!-- Theoretical:
#### Helijao: OneDrive Integration
**Tasks** (6-8 hours):
- [ ] Implement OneDrive OAuth2 flow
- [ ] Add OneDrive to cloud connector service
- [ ] Implement OneDrive upload
- [ ] Implement OneDrive download
- [ ] Test OneDrive connection
- [ ] Handle token refresh

**Deliverables**:
- OneDrive OAuth working
- OneDrive upload/download working
- Both cloud providers functional
-->

#### Bilal: Cloud Upload Service
**Tasks** (6-8 hours):
- [x] Create `cloud_upload_service.py`
- [x] Implement upload to Google Drive
- [x] Implement upload to OneDrive
- [x] Add provider selection logic
- [x] Integrate with file service
- [x] Test cloud uploads
- [x] Add automatic cloud upload after file upload (background task)

**Deliverables**:
- ✅ Cloud upload service complete
- ✅ Files upload to cloud providers
- ✅ Provider selection working
- ✅ Automatic cloud upload implemented

#### Mouhamad: File Management UI Enhancements
**Tasks** (6-8 hours):
- [ ] Update FilesPage with cloud storage indicators
- [ ] Add file upload progress
- [ ] Improve file list UI
- [ ] Add cloud storage status
- [ ] Enhance breadcrumb navigation
- [ ] Add file preview (if time permits)

**Deliverables**:
- Enhanced file management UI
- Cloud storage indicators
- Better UX overall

---

### 📅 **Day 4: Download & Integration**

#### Bilal: Cloud Download Service
**Tasks** (6-8 hours):
- [ ] Create `cloud_download_service.py`
- [ ] Implement download from Google Drive
- [ ] Implement download from OneDrive
- [ ] Add chunk reassembly logic
- [ ] Integrate with file service
- [ ] Test cloud downloads

**Deliverables**:
- Cloud download service complete
- Files download from cloud
- Chunk reassembly working

#### Helijao: Cloud Account Management
**Tasks** (6-8 hours):
- [ ] Implement account linking/unlinking
- [ ] Add account status checks
- [ ] Implement token refresh on expiry
- [ ] Add error handling for OAuth failures
- [ ] Test account management
- [ ] Add account validation

**Deliverables**:
- Account management complete
- Token refresh working
- Error handling robust

#### Bilal: Download Service Integration
**Tasks** (6-8 hours):
- [x] Create `download_service.py`
- [x] Implement chunk fetching from cloud
- [x] Add decryption and reassembly
- [x] Implement streaming download
- [x] Add checksum verification
- [x] Test end-to-end download

**Deliverables**:
- ✅ Download service complete
- ✅ End-to-end download working
- ✅ Streaming implemented

#### Mouhamad: Frontend Integration & Polish
**Tasks** (6-8 hours):
- [ ] Integrate cloud upload/download in UI
- [ ] Add loading states
- [ ] Improve error messages
- [ ] Add success notifications
- [ ] Polish UI/UX
- [ ] Test complete user flow

**Deliverables**:
- Complete UI integration
- Polished user experience
- Error handling improved

---

### 📅 **Day 5: Testing, Bug Fixes & Documentation**

#### All Developers: Integration Testing
**Tasks** (2-3 hours each):
- [ ] Test complete upload flow (local → encrypt → chunk → cloud)
- [ ] Test complete download flow (cloud → decrypt → reassemble → user)
- [ ] Test OAuth flows (Google Drive, OneDrive)
- [ ] Test file operations (create folder, delete, list)
- [ ] Test error scenarios
- [ ] Fix critical bugs

#### Bilal: Infrastructure & Security
**Tasks** (4-6 hours):
- [x] Add rate limiting middleware (Redis-based)
- [x] Add security headers middleware
- [x] Test PostgreSQL performance
- [x] Optimize database queries
- [x] Document infrastructure setup
- [x] Add storage quota management (10 GB per user, configurable)
- [x] Add storage usage tracking (local + cloud)
- [x] Implement automatic cloud upload after file upload

**Deliverables**:
- ✅ Rate limiting working
- ✅ Security headers added
- ✅ Infrastructure documented
- ✅ Storage quota system implemented
- ✅ Storage usage API endpoint
- ✅ Automatic cloud upload working

#### Helijao: Cloud Integration Testing
**Tasks** (4-6 hours):
- [ ] Test OAuth flows end-to-end
- [ ] Test token refresh scenarios
- [ ] Test multiple cloud accounts
- [ ] Test provider switching
- [ ] Fix OAuth-related bugs
- [ ] Document cloud setup

**Deliverables**:
- Cloud integration tested
- OAuth flows stable
- Setup documented

#### Bilal: Encryption & Storage Testing
**Tasks** (4-6 hours):
- [x] Test file chunking with various sizes
- [x] Test encryption/decryption
- [x] Test key storage and retrieval
- [x] Test large file handling
- [x] Performance testing
- [x] Document encryption approach
- [x] Add storage quota per user (10 GB default)
- [x] Add storage usage tracking API
- [x] Add cloud storage usage tracking (Google Drive, OneDrive)

**Deliverables**:
- ✅ Encryption tested thoroughly
- ✅ Performance acceptable
- ✅ Documentation complete
- ✅ Storage quota system implemented
- ✅ Storage usage API with cloud storage support

#### Mouhamad: Frontend Testing & Documentation
**Tasks** (4-6 hours):
- [ ] Test all UI flows
- [ ] Fix UI bugs
- [ ] Add user documentation
- [ ] Create setup guide
- [ ] Test on different browsers
- [ ] Final UI polish

**Deliverables**:
- UI tested and polished
- User documentation
- Setup guide complete

---

## Key Features to Implement

### ✅ Must Have (Critical Path)

1. **PostgreSQL Migration**
   - Replace SQLite
   - Update all models
   - Run migrations

2. **Cloud Connectors**
   - Google Drive OAuth
   - OneDrive OAuth
   - Basic upload/download

<!--
3. **File Chunking**
   - 10MB chunk size
   - Chunk encryption
   - Chunk storage
-->

4. **Cloud Upload/Download**
   - Upload encrypted chunks to cloud
   - Download and reassemble
   - Provider selection

5. **Cloud Accounts UI**
   - Connect/disconnect accounts
   - OAuth flow
   - Account status

### ⚠️ Nice to Have (If Time Permits)

- Access key authentication
- Advanced rate limiting
- File sharing
- Search functionality
- File preview
- Advanced error handling

---

## Daily Standup Structure

**Time**: 15 minutes each morning  
**Format**:
1. What did you complete yesterday?
2. What are you working on today?
3. Any blockers?

**End of Day Sync**: 30 minutes
- Demo completed features
- Discuss integration points
- Plan next day

---

## Integration Points

### Critical Integration Points:

1. **Day 2**: Bilal (DB) ↔ Helijao (Cloud) ↔ Bilal (Encryption)
   - Database schema must be ready for cloud accounts and encryption keys

2. **Day 3**: Helijao (Cloud) ↔ Bilal (Encryption) ↔ Mouhamad (Frontend)
   - Cloud connectors need encryption service
   - Frontend needs cloud account API

3. **Day 4**: All developers
   - End-to-end integration testing
   - Upload/download flow complete

---

## Risk Mitigation

### Potential Risks:

1. **OAuth Setup Complexity**
   - **Mitigation**: Start Day 1, have credentials ready
   - **Owner**: Helijao

2. **Database Migration Issues**
   - **Mitigation**: Test migrations early, have rollback plan
   - **Owner**: Bilal

3. **Chunking Complexity**
   - **Mitigation**: Use full version code as reference
   - **Owner**: Bilal

4. **Integration Bugs**
   - **Mitigation**: Daily integration testing, early integration
   - **Owner**: All

---

## Success Criteria

### End of Week Checklist:

- [x] PostgreSQL database running
- [x] Redis running
- [x] Google Drive OAuth working
- [x] OneDrive OAuth working (structure ready)
- [x] Files upload to cloud (automatic after local upload)
- [x] Files download from cloud
- [x] File chunking working
- [x] Encryption keys stored in database
- [x] Cloud accounts UI functional
- [x] End-to-end flow tested
- [x] Basic documentation complete
- [x] Storage quota management (10 GB per user, configurable via `DEFAULT_STORAGE_QUOTA_BYTES`)
- [x] Storage usage tracking (local + cloud via `GET /api/files/storage/usage`)
- [x] Rate limiting middleware (Redis-based)
- [x] Security headers middleware

---

## Quick Reference: File Locations

### Backend Files to Create/Update:

```
backend/app/
├── models/
│   ├── cloud_account.py      # NEW - Helijao
│   └── encryption_key.py     # NEW - Bilal
├── services/
│   ├── cloud_connector_service.py  # NEW - Helijao
│   ├── cloud_upload_service.py     # NEW - Helijao/3
│   ├── cloud_download_service.py   # NEW - Bilal/2
│   ├── upload_service.py           # UPDATE - Bilal
│   ├── download_service.py         # UPDATE - Bilal
│   └── encryption_service.py      # UPDATE - Bilal
├── api/routes/
│   └── cloud_accounts.py     # NEW - Helijao
└── middleware/
    └── security.py            # UPDATE - Bilal
```

### Frontend Files to Create/Update:

```
frontend/src/
├── pages/
│   └── CloudAccountsPage.tsx  # NEW - Mouhamad
├── services/
│   └── cloudAccountService.ts  # NEW - Mouhamad
└── store/
    └── cloudAccountsStore.ts   # NEW - Mouhamad
```

---

## Daily Time Allocation

**Total Hours per Developer**: ~30-35 hours over 5 days

**Daily Breakdown**:
- **Day 1**: 4-6 hours (setup)
- **Day 2**: 6-8 hours (core features)
- **Day 3**: 6-8 hours (integration)
- **Day 4**: 6-8 hours (completion)
- **Day 5**: 4-6 hours (testing & polish)

---

## Tools & Resources Needed

### Bilal:
- PostgreSQL Docker image
- Redis Docker image
- Alembic for migrations

### Helijao:
- Google Cloud Console access
- Azure Portal access
- OAuth credentials
- `google-api-python-client` library
- `msal` library

### Bilal:
- Full version encryption service code (reference)
- Cryptography library
- Chunking strategy documentation

### Mouhamad:
- Full version frontend code (reference)
- Material Symbols/icons
- React Router

---

## Communication Channels

- **Daily Standup**: Morning (15 min)
- **End of Day Sync**: Evening (30 min)
- **Slack/Discord**: For quick questions
- **Git Branches**: One per developer
- **Pull Requests**: Review before merging

---

## Git Workflow

### Branch Strategy:
```
main (MVP)
├── dev/infrastructure (Bilal)
├── dev/cloud-connectors (Helijao)
├── dev/encryption (Bilal)
└── dev/frontend (Mouhamad)
```

### Merge Strategy:
- Daily merges to avoid conflicts
- PR reviews before merging
- Test after each merge

---

## Final Checklist Before Demo

- [x] All services running (PostgreSQL, Redis, Backend, Frontend)
- [x] Can register/login
- [x] Can connect Google Drive
- [x] Can connect OneDrive (structure ready)
- [x] Can upload file (goes to cloud automatically)
- [x] Can download file (from cloud)
- [x] File encryption working
- [x] File chunking working
- [x] UI functional and polished
- [x] Basic documentation complete
- [x] Storage quota management working (10 GB default, configurable)
- [x] Storage usage tracking working (local + cloud)
- [x] Rate limiting and security headers implemented

---

## Post-Week Follow-up

### If Time Permits:
- Access key authentication
- Advanced rate limiting
- File sharing features
- Performance optimizations
- Comprehensive testing
- Production deployment guide

---

## Notes

- **Focus on core functionality** - Don't get sidetracked by nice-to-haves
- **Daily integration** - Don't wait until Day 5 to integrate
- **Test early** - Test each feature as you build it
- **Communicate** - Daily standups are critical
- **Reference full version** - Use existing code as reference when stuck

# MVP to Full Version Migration Plan
## 1-Week Sprint for 4 Developers

## Overview

**Goal**: Migrate from MVP (local storage) to Full Version (cloud storage with advanced features)  
**Timeline**: 1 week (5 working days)  
**Team Size**: 4 developers  
**Approach**: Parallel work streams with daily syncs

---

## Team Roles & Responsibilities

### 👤 **Bilal: Backend Infrastructure**
**Focus**: Database migration, Redis setup, infrastructure improvements

### 👤 **Helijao: Cloud Connectors**
**Focus**: OAuth2 flows, Google Drive & OneDrive integration

### 👤 **Bilal: Encryption & File Services**
**Focus**: File chunking, enhanced encryption, key storage

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

#### Bilal: Cloud Upload Service
**Tasks** (6-8 hours):
- [ ] Create `cloud_upload_service.py`
- [ ] Implement upload to Google Drive
- [ ] Implement upload to OneDrive
- [ ] Add provider selection logic
- [ ] Integrate with file service
- [ ] Test cloud uploads

**Deliverables**:
- Cloud upload service complete
- Files upload to cloud providers
- Provider selection working

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
- [ ] Create `download_service.py`
- [ ] Implement chunk fetching from cloud
- [ ] Add decryption and reassembly
- [ ] Implement streaming download
- [ ] Add checksum verification
- [ ] Test end-to-end download

**Deliverables**:
- Download service complete
- End-to-end download working
- Streaming implemented

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
- [ ] Add rate limiting middleware (Redis-based)
- [ ] Add security headers middleware
- [ ] Test PostgreSQL performance
- [ ] Optimize database queries
- [ ] Document infrastructure setup

**Deliverables**:
- Rate limiting working
- Security headers added
- Infrastructure documented

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
- [ ] Test file chunking with various sizes
- [ ] Test encryption/decryption
- [ ] Test key storage and retrieval
- [ ] Test large file handling
- [ ] Performance testing
- [ ] Document encryption approach

**Deliverables**:
- Encryption tested thoroughly
- Performance acceptable
- Documentation complete

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

3. **File Chunking**
   - 10MB chunk size
   - Chunk encryption
   - Chunk storage

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

- [ ] PostgreSQL database running
- [ ] Redis running
- [ ] Google Drive OAuth working
- [ ] OneDrive OAuth working
- [ ] Files upload to cloud
- [ ] Files download from cloud
- [ ] File chunking working
- [ ] Encryption keys stored in database
- [ ] Cloud accounts UI functional
- [ ] End-to-end flow tested
- [ ] Basic documentation complete

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

- [ ] All services running (PostgreSQL, Redis, Backend, Frontend)
- [ ] Can register/login
- [ ] Can connect Google Drive
- [ ] Can connect OneDrive
- [ ] Can upload file (goes to cloud)
- [ ] Can download file (from cloud)
- [ ] File encryption working
- [ ] File chunking working
- [ ] UI functional and polished
- [ ] Basic documentation complete

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

Good luck! 🚀

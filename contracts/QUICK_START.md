# Contract Workflow Quick Start

**For:** New team members or quick reference  
**Time:** 5 minutes

---

## 🚀 Setup (One-Time)

### 1. Read Team Workflow
```bash
cat TEAM_WORKFLOW.md
```

### 2. Identify Your Role
Check the "Team Organization" section in `TEAM_WORKFLOW.md`:
- **Dev 1:** Backend Infrastructure → Owns `backend-api-v1.0.0.md`
- **Dev 2:** Frontend → Owns `frontend-backend-v1.0.0.md`
- **Dev 3:** Cloud Connectors → Owns `cloud-connector-backend-v1.0.0.md`
- **Dev 4:** Encryption → Owns `encryption-service-v1.0.0.md`

### 3. Read Your Contracts
```bash
# If you're Frontend (Dev 2)
cat contracts/frontend-backend-v1.0.0.md

# If you depend on Backend API
cat contracts/backend-api-v1.0.0.md
```

---

## 📝 Daily Workflow

### If You're a Contract Owner

**Step 1:** Update your contract (if needed)
```bash
# Edit your contract file
vim contracts/your-contract-v1.0.0.md

# Update status: Draft → Review → Stable
# Update change log
```

**Step 2:** Notify team (if status changed)
```
# In Slack or PR comment:
"Backend API Contract v1.0.0 is now Stable. 
Mock handlers available in mocks/backend-api/handlers.ts"
```

**Step 3:** Implement according to contract
```python
# Your implementation must match contract exactly
@router.post("/auth/register")
async def register(request: UserCreate):
    # Implementation here
    return Token(...)  # Must match contract schema
```

---

### If You're a Contract Consumer

**Step 1:** Check contract status
```bash
# Read contract to see current status
cat contracts/backend-api-v1.0.0.md
# Status: Stable ✅
```

**Step 2:** Set up mocks (if contract is Draft/Review)
```typescript
// frontend/src/mocks/handlers.ts
import { handlers } from '../../../mocks/backend-api/handlers.ts'

// Use MSW to intercept API calls
```

**Step 3:** Develop using mocks
```typescript
// Your code works with mocks
const response = await apiClient.post('/auth/login', credentials)
// Returns mock data until backend is Stable
```

**Step 4:** Switch to real API (when Stable)
```typescript
// Remove mock setup, use real API
// Your code should work without changes
```

---

## 🔄 Common Scenarios

### Scenario 1: Need to Change a Contract

**If you're the owner:**
1. Edit contract file
2. Bump version (1.0.0 → 1.1.0 for non-breaking, 2.0.0 for breaking)
3. Update change log
4. Notify team

**If you're NOT the owner:**
1. Create Contract Change Request (CCR)
```bash
# Create file
vim contracts/change-requests/ccr-001-your-change.md
```
2. Fill out CCR template (see `TEAM_WORKFLOW.md`)
3. Tag owner in PR/Slack
4. Wait for approval (24-48 hours)

---

### Scenario 2: Contract Doesn't Match Implementation

**This is a bug!**

1. Create issue: "Contract mismatch: Backend API v1.0.0"
2. Tag contract owner
3. Owner must fix either:
   - Update contract to match implementation (if implementation is correct)
   - Fix implementation to match contract (if contract is correct)

---

### Scenario 3: Need a New Contract

**If it's your domain:**
1. Create new contract file
```bash
vim contracts/my-new-contract-v1.0.0.md
```
2. Set status to "Draft"
3. Define interface, behaviors, mocks
4. Move to "Review" when ready
5. Move to "Stable" when implemented

**If it's someone else's domain:**
1. Request new contract from owner
2. Provide requirements/use cases
3. Owner creates contract

---

## ✅ Checklist for Sprint Start

- [ ] Read all contracts I depend on
- [ ] Check contract statuses (Draft/Review/Stable)
- [ ] Set up mocks for Draft/Review contracts
- [ ] Identify any missing contracts
- [ ] Review sprint goal and required contracts

---

## ✅ Checklist for Sprint End

- [ ] All my contracts are "Stable" (if they were deliverables)
- [ ] Updated change logs for any changes
- [ ] Notified team of status changes
- [ ] Integration tests pass against real APIs
- [ ] No contract mismatches

---

## 🆘 Quick Troubleshooting

**Q: Contract owner not responding?**  
A: Wait 48 hours, then escalate to team lead

**Q: Mock doesn't work?**  
A: Check MSW setup, ensure handlers match contract exactly

**Q: Implementation doesn't match contract?**  
A: This is a bug - create issue, tag owner

**Q: Need urgent breaking change?**  
A: Use emergency CCR process (see `TEAM_WORKFLOW.md`)

---

## 📚 Key Files

- **Team Workflow:** `TEAM_WORKFLOW.md` (full process)
- **Backend Contract:** `contracts/backend-api-v1.0.0.md`
- **Frontend Contract:** `contracts/frontend-backend-v1.0.0.md`
- **Mock Handlers:** `mocks/backend-api/handlers.ts`
- **Change Requests:** `contracts/change-requests/`

---

**Remember:** Contracts first, implementation second. Use mocks to work in parallel.

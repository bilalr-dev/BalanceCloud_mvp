// MSW Handlers for Backend API
// This matches the Backend API Contract v1.0.0

import { rest } from 'msw'

const API_BASE_URL = 'http://localhost:8000/api'

export const handlers = [
  // POST /api/auth/register
  rest.post(`${API_BASE_URL}/auth/register`, async (req, res, ctx) => {
    const body = await req.json() as { email: string; password: string }
    
    // Simulate validation error
    if (body.email === 'exists@example.com') {
      return res(
        ctx.status(400),
        ctx.json({
          detail: 'Email already exists'
        })
      )
    }
    
    // Success response
    return res(
      ctx.status(201),
      ctx.json({
        access_token: 'mock_token_register_12345',
        token_type: 'bearer'
      })
    )
  }),

  // POST /api/auth/login
  rest.post(`${API_BASE_URL}/auth/login`, async (req, res, ctx) => {
    const body = await req.json() as { email: string; password: string }
    
    // Simulate authentication failure
    if (body.email === 'wrong@example.com' || body.password === 'wrong') {
      return res(
        ctx.status(401),
        ctx.json({
          detail: 'Incorrect email or password'
        })
      )
    }
    
    // Success response
    return res(
      ctx.status(200),
      ctx.json({
        access_token: 'mock_token_login_12345',
        token_type: 'bearer'
      })
    )
  }),

  // GET /api/auth/me
  rest.get(`${API_BASE_URL}/auth/me`, async (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    
    // Simulate missing/invalid token
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({
          detail: 'Invalid authentication credentials'
        })
      )
    }
    
    // Success response
    return res(
      ctx.status(200),
      ctx.json({
        id: 'mock-user-id-12345',
        email: 'mock@example.com',
        is_active: true,
        created_at: '2026-01-20T10:00:00Z'
      })
    )
  }),

  // GET /api/files
  rest.get(`${API_BASE_URL}/files`, async (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    
    // Simulate missing/invalid token
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({
          detail: 'Invalid authentication credentials'
        })
      )
    }
    
    const parentId = req.url.searchParams.get('parent_id')
    
    // Success response
    return res(
      ctx.status(200),
      ctx.json({
        files: [
          {
            id: 'mock-file-id-1',
            user_id: 'mock-user-id',
            name: 'Mock Document.pdf',
            path: '/mock/document.pdf',
            size: 2048,
            mime_type: 'application/pdf',
            is_folder: false,
            parent_id: parentId || null,
            created_at: '2026-01-20T10:00:00Z',
            updated_at: '2026-01-20T10:00:00Z'
          },
          {
            id: 'mock-file-id-2',
            user_id: 'mock-user-id',
            name: 'Mock Folder',
            path: '/mock/folder',
            size: 0,
            mime_type: null,
            is_folder: true,
            parent_id: parentId || null,
            created_at: '2026-01-20T10:00:00Z',
            updated_at: '2026-01-20T10:00:00Z'
          }
        ],
        total: 2
      })
    )
  }),

  // GET /api/files/storage/usage
  rest.get(`${API_BASE_URL}/files/storage/usage`, async (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({
          detail: 'Invalid authentication credentials'
        })
      )
    }
    
    return res(
      ctx.status(200),
      ctx.json({
        used_bytes: 1024,
        total_bytes: 10737418240,
        used_percentage: 0.0,
        used_gb: 0.0,
        total_gb: 10.0,
        cloud_storage: {
          google_drive: null,
          onedrive: null
        }
      })
    )
  }),

  // POST /api/files/upload
  rest.post(`${API_BASE_URL}/files/upload`, async (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({
          detail: 'Invalid authentication credentials'
        })
      )
    }
    
    // Mock file upload response
    return res(
      ctx.status(201),
      ctx.json({
        id: 'mock-file-id-new',
        user_id: 'mock-user-id',
        name: 'uploaded-file.pdf',
        path: '/uploaded-file.pdf',
        size: 1024,
        mime_type: 'application/pdf',
        is_folder: false,
        parent_id: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      })
    )
  }),

  // GET /api/cloud-accounts
  rest.get(`${API_BASE_URL}/cloud-accounts`, async (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({
          detail: 'Invalid authentication credentials'
        })
      )
    }
    
    return res(
      ctx.status(200),
      ctx.json({
        accounts: [],
        total: 0
      })
    )
  }),

  // POST /api/cloud-accounts/connect/:provider
  rest.post(`${API_BASE_URL}/cloud-accounts/connect/:provider`, async (req, res, ctx) => {
    const { provider } = req.params
    
    return res(
      ctx.status(200),
      ctx.json({
        oauth_url: `https://mock-oauth-provider.com/auth?provider=${provider}&state=mock_state_12345`,
        state: 'mock_state_12345'
      })
    )
  }),

  // GET /api/cloud-accounts/callback/:provider
  rest.get(`${API_BASE_URL}/cloud-accounts/callback/:provider`, async (req, res, ctx) => {
    const { provider } = req.params
    const code = req.url.searchParams.get('code')
    const state = req.url.searchParams.get('state')
    
    if (!code || !state) {
      return res(
        ctx.status(400),
        ctx.json({
          detail: 'Missing code or state parameter'
        })
      )
    }
    
    return res(
      ctx.status(200),
      ctx.json({
        account_id: `mock-account-id-${provider}`,
        provider: provider as 'google_drive' | 'onedrive',
        provider_account_id: `mock@${provider}.com`,
        is_connected: true,
        message: 'Account connected successfully'
      })
    )
  }),

  // DELETE /api/cloud-accounts/:account_id
  rest.delete(`${API_BASE_URL}/cloud-accounts/:account_id`, async (req, res, ctx) => {
    const { account_id } = req.params
    
    return res(
      ctx.status(200),
      ctx.json({
        message: 'Account disconnected successfully',
        account_id
      })
    )
  }),
]

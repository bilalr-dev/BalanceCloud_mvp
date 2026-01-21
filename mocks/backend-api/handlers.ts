/**
 * Mock Service Worker (MSW) handlers for Backend API
 * 
 * Usage:
 * 1. Install: npm install msw
 * 2. Import this file in your frontend app
 * 3. Use MSW to intercept API calls during development
 * 
 * This matches the Backend API Contract v1.0.0
 */

import { rest } from 'msw'

const API_BASE_URL = 'http://localhost:8000/api'

export const handlers = [
  // POST /api/auth/register
  rest.post(`${API_BASE_URL}/auth/register`, async (req, res, ctx) => {
    const body = await req.json()
    
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
    const body = await req.json()
    
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
]

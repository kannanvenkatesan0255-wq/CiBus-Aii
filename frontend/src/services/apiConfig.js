/**
 * CIBUS-AI - Centralized API Base URL Configuration
 * File: frontend/src/services/apiConfig.js
 * 
 * Purpose:
 * Centralizes the FastAPI backend URL resolution for all client network calls.
 * 
 * Precedence:
 * 1. import.meta.env.VITE_API_BASE_URL (configured via environment)
 * 2. In production builds/deployments (import.meta.env.PROD): 'https://cibus-ai-backend.onrender.com'
 * 3. In local development environments: 'http://127.0.0.1:8000'
 */

const rawApiBase = import.meta.env.VITE_API_BASE_URL;

export const API_BASE_URL = (rawApiBase && String(rawApiBase).trim())
  ? String(rawApiBase).trim().replace(/\/+$/, '')
  : (import.meta.env.PROD
      ? 'https://cibus-ai-backend.onrender.com'
      : 'http://127.0.0.1:8000');

export default API_BASE_URL;

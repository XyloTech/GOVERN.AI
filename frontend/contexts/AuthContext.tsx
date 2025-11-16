'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { 
  User as FirebaseUser,
  signInWithPopup,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  GoogleAuthProvider
} from 'firebase/auth'
import { auth } from '@/lib/firebase'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface AuthContextType {
  user: FirebaseUser | null
  loading: boolean
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
  idToken: string | null
  refreshToken: () => Promise<string | null>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<FirebaseUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [idToken, setIdToken] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    
    // Set a timeout to ensure loading state resolves even if Firebase takes too long
    const timeoutId = setTimeout(() => {
      if (mounted) {
        console.warn('Auth state check timeout - resolving loading state')
        setLoading(false)
      }
    }, 5000) // 5 second timeout

    // Check if auth is available
    if (!auth) {
      console.error('Firebase auth not initialized')
      setLoading(false)
      return
    }

    const unsubscribe = onAuthStateChanged(
      auth, 
      async (firebaseUser) => {
        if (!mounted) return
        
        try {
          setUser(firebaseUser)
          
          if (firebaseUser) {
            // Get ID token for backend authentication
            try {
              const token = await firebaseUser.getIdToken()
              setIdToken(token)
              
              // Sync user with backend (non-blocking - don't wait for it)
              axios.post(
                `${API_URL}/api/v1/auth/sync`,
                {
                  firebase_uid: firebaseUser.uid,
                  email: firebaseUser.email,
                  display_name: firebaseUser.displayName,
                  photo_url: firebaseUser.photoURL
                },
                {
                  headers: {
                    'Authorization': `Bearer ${token}`
                  },
                  timeout: 3000 // 3 second timeout
                }
              ).catch(error => {
                console.error('Error syncing user with backend (non-critical):', error)
                // Don't block the UI if backend sync fails
              })
            } catch (tokenError) {
              console.error('Error getting ID token:', tokenError)
              // Continue even if token fetch fails
            }
          } else {
            setIdToken(null)
          }
        } catch (error) {
          console.error('Error in auth state change:', error)
        } finally {
          // Always resolve loading state
          if (mounted) {
            clearTimeout(timeoutId)
            setLoading(false)
          }
        }
      },
      (error) => {
        // Handle auth state change errors
        console.error('Firebase auth state change error:', error)
        if (mounted) {
          clearTimeout(timeoutId)
          setLoading(false)
        }
      }
    )

    return () => {
      mounted = false
      clearTimeout(timeoutId)
      unsubscribe()
    }
  }, [])

  const signInWithGoogle = async () => {
    try {
      const provider = new GoogleAuthProvider()
      const result = await signInWithPopup(auth, provider)
      // User state will be updated by onAuthStateChanged
    } catch (error: any) {
      console.error('Error signing in:', error)
      throw error
    }
  }

  const refreshToken = async (): Promise<string | null> => {
    if (!user) {
      console.warn('[Auth] No user available for token refresh')
      return null
    }
    try {
      console.log('[Auth] Refreshing token...')
      const token = await user.getIdToken(true) // Force refresh
      console.log('[Auth] Token refreshed successfully')
      setIdToken(token)
      return token
    } catch (error) {
      console.error('[Auth] Error refreshing token:', error)
      // If refresh fails, try to get a fresh token without forcing
      try {
        const token = await user.getIdToken(false)
        setIdToken(token)
        return token
      } catch (fallbackError) {
        console.error('[Auth] Fallback token fetch also failed:', fallbackError)
        return null
      }
    }
  }

  const signOut = async () => {
    try {
      await firebaseSignOut(auth)
      setIdToken(null)
    } catch (error) {
      console.error('Error signing out:', error)
      throw error
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, signInWithGoogle, signOut, idToken, refreshToken }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}


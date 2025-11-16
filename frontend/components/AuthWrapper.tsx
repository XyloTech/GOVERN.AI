'use client'

import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import LoginView from './LoginView'
import LoadingScreen from './LoadingScreen'
import { ReactNode } from 'react'

function AuthContent({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingScreen message="Initializing..." />
  }

  if (!user) {
    return <LoginView />
  }

  return <>{children}</>
}

export default function AuthWrapper({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <AuthContent>{children}</AuthContent>
    </AuthProvider>
  )
}


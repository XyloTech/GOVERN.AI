'use client'

interface LoadingScreenProps {
  message?: string
  fullScreen?: boolean
}

export default function LoadingScreen({ message = 'Loading...', fullScreen = true }: LoadingScreenProps) {
  const containerClass = fullScreen 
    ? 'min-h-screen bg-dark-bg flex items-center justify-center' 
    : 'flex items-center justify-center p-8'

  return (
    <div className={containerClass}>
      <div className="text-center">
        {/* Animated Logo/Icon */}
        <div className="relative mb-6">
          <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-neon-cyan to-neon-blue flex items-center justify-center animate-pulse">
            <svg className="w-8 h-8 text-dark-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          {/* Spinning ring */}
          <div className="absolute inset-0 w-16 h-16 mx-auto border-4 border-neon-cyan/20 border-t-neon-cyan rounded-full animate-spin"></div>
        </div>
        
        {/* Loading text */}
        <p className="text-gray-400 text-sm font-medium animate-pulse">{message}</p>
        
        {/* Loading dots */}
        <div className="flex justify-center gap-1 mt-3">
          <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-neon-cyan rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  )
}


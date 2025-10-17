// Navbar component

type Props = {
  onNavigate?: (path: string) => void
}

export default function Navbar({ onNavigate }: Props) {
  return (
    <header className="bg-black border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <div className="text-white font-bold text-xl">
              <span>Nexus</span>
            </div>
          </div>
          <div className="flex items-center">
            <nav className="flex space-x-8">
              <a 
                className="text-white hover:text-gray-300 cursor-pointer transition-colors" 
                onClick={() => onNavigate && onNavigate('/')}
              >
                Home
              </a>
              <a 
                className="text-white hover:text-gray-300 cursor-pointer transition-colors" 
                onClick={() => onNavigate && onNavigate('/explore')}
              >
                Explore
              </a>
              <a 
                className="text-white hover:text-gray-300 cursor-pointer transition-colors" 
                onClick={() => onNavigate && onNavigate('/about')}
              >
                About
              </a>
            </nav>
          </div>
          <div className="flex items-center">{/* reserved for CTAs */}</div>
        </div>
      </div>
    </header>
  )
}



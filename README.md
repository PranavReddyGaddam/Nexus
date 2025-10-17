# Nexus - AI-Powered Startup Idea Analysis Platform

## Overview

Nexus is an innovative platform that analyzes startup ideas through the lens of expert personas from around the world. It provides intelligent feedback and ratings by leveraging AI to simulate perspectives from different markets and domains.

## Features

- **Interactive 3D Globe**: Visualize expert personas and their locations worldwide
- **AI Analysis**: Get detailed feedback on your startup idea from multiple expert perspectives
- **File Attachments**: Upload supporting documents for more comprehensive analysis
- **Real-time Results**: Instant feedback with detailed ratings and comments
- **Location-based Insights**: Understand how your idea resonates in different markets

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- React Router for navigation
- Tailwind CSS for styling
- Three.js/React Three Fiber for 3D visualization
- Lucide React for icons

### Backend (Optional)
- FastAPI
- Pydantic for data validation
- OpenAI/Anthropic for LLM integration
- WebSocket support for real-time updates

## Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nexus.git
cd nexus/frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create a `.env` file in the frontend directory:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

4. Start the development server:
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:5173`

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── ui/         # Reusable UI components
│   │   └── ...
│   ├── data/           # Static data and mock data
│   ├── lib/            # Utility functions
│   ├── services/       # API and service layer
│   ├── styles/         # Global styles
│   ├── App.tsx         # Main application component
│   └── main.tsx        # Application entry point
├── .env                # Environment variables
└── package.json        # Project dependencies
```

## Key Components

### Globe Visualization
- Interactive 3D globe using Three.js
- Clickable location markers
- Smooth camera transitions
- Location highlighting

### Expert Analysis
- Dynamic persona selection
- Rating system (0-10 scale)
- Sentiment analysis
- Industry-specific insights
- Location-based feedback

### User Interface
- Modern, responsive design
- Dark mode optimized
- Smooth transitions
- Real-time updates
- File attachment support

## Configuration

### Environment Variables

- `VITE_API_URL`: Backend API endpoint
- `VITE_WS_URL`: WebSocket endpoint
- `VITE_MOCK_MODE`: Enable/disable mock data (default: true)

### LLM Integration

For LLM integration, refer to the `LLM_INTEGRATION_GUIDE.md` in the root directory.

## Development

### Available Scripts

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run preview`: Preview production build
- `npm run lint`: Run ESLint
- `npm run type-check`: Run TypeScript checks

### Code Style

- ESLint configuration for TypeScript
- Prettier for code formatting
- Husky for pre-commit hooks

## Deployment

### Building for Production

1. Update environment variables for production
2. Build the application:
```bash
npm run build
```

3. The built files will be in the `dist` directory

### Deployment Options

- Static hosting (Vercel, Netlify)
- Docker containerization
- Traditional web hosting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Three.js for 3D visualization
- OpenAI/Anthropic for LLM capabilities
- React Three Fiber community
- All contributors and maintainers

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

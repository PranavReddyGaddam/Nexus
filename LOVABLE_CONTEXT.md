# Nexus - AI Multi-Agent Market Research Platform
## Context Engineering Document for Lovable

---

## 🎯 Project Overview

**Nexus** is an AI-powered platform that simulates market research for startup ideas using multiple expert personas. Users can explore a 3D interactive globe, click on major business hubs worldwide, and consult with AI-powered industry experts who provide feedback through iterative feedback loops.

### Vision
Create an intuitive, visually stunning platform where entrepreneurs can get instant, multi-perspective market analysis from simulated experts across different industries, geographies, and domains.

---

## 🏗️ Current Architecture

### Frontend Stack
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **3D Visualization**: Three.js / React Three Fiber / three-globe
- **Icons**: Lucide React
- **Routing**: React Router v6

### Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **AI/LLM**: OpenAI GPT-4 / Anthropic Claude
- **Database**: PostgreSQL (planned) + SQLAlchemy
- **Caching**: Redis (planned)
- **Real-time**: WebSocket support

---

## 🌍 Key Feature: Interactive Clickable Globe

### User Requirements
> **Critical Requirement**: The globe pinpoints MUST be clickable and open persona modals showing industry experts from those locations. The dots should be small, aesthetically pleasing, and directly clickable (not just the area around them).

### Implementation Details

#### 1. Globe Component (`frontend/src/components/ui/globe.tsx`)
- **3D Globe Rendering**: Uses `three-globe` library to render an interactive 3D globe
- **Point Visualization**: 
  - 14 major financial/tech hubs marked with blue dots
  - Dot size: 1.2 radius for important points, 0.8 for regular
  - Color: `#e6efff` (light blue) for important, `#95aaff` for regular
  - Points set to `pointsMerge: false` to allow individual clicking
  
- **Click Detection System**:
  ```typescript
  // Uses Three.js Raycaster for 3D object intersection
  const raycaster = new Raycaster();
  raycaster.params.Points = { threshold: 5 }; // Click tolerance
  
  // Two-phase detection:
  // 1. First tries to hit Point objects directly (primary method)
  // 2. Falls back to all objects if needed (secondary)
  
  // Converts 3D click to lat/lng and matches to closest data point
  ```

- **Location Data Flow**:
  ```
  Click on globe → Raycaster detects intersection → 
  Convert 3D point to lat/lng → Find closest data point → 
  Trigger onPointClick callback with location data
  ```

#### 2. Location Data (`frontend/src/App.tsx`)
**Critical**: Location names here must match EXACTLY with persona data keys.

```typescript
data={[
  { order: 0, startLat: 40.7128, startLng: -74.0060, name: 'New York', ... },
  { order: 1, startLat: 51.5074, startLng: -0.1278, name: 'London', ... },
  { order: 2, startLat: 35.6895, startLng: 139.6917, name: 'Tokyo', ... },
  // ... 11 more locations
]}
```

**All 14 Locations**:
1. New York (40.7128, -74.0060)
2. London (51.5074, -0.1278)
3. Tokyo (35.6895, 139.6917)
4. Hong Kong (22.3193, 114.1694)
5. Singapore (1.3521, 103.8198)
6. Shanghai (31.2304, 121.4737)
7. Frankfurt (50.1109, 8.6821)
8. Paris (48.8566, 2.3522)
9. Zurich (47.3769, 8.5417)
10. Toronto (43.6532, -79.3832)
11. Sydney (-33.8688, 151.2093)
12. Mumbai (19.0760, 72.8777)
13. Dubai (25.276987, 55.296249)
14. Seoul (37.5665, 126.9780)

#### 3. Persona Data Mapping (`frontend/src/data/personas.ts`)

**Critical**: Keys in `personasByLocation` MUST match location names in App.tsx exactly.

```typescript
export const personasByLocation: Record<string, Persona[]> = {
  'New York': [
    { id: 'ny-1', name: 'Sarah Mitchell', title: 'Chief Investment Officer', ... },
    { id: 'ny-2', name: 'Marcus Chen', title: 'Technology Strategy Consultant', ... }
  ],
  'London': [ ... ],
  // ... etc for all 14 locations
}
```

**Total**: 15 expert personas across 14 locations

#### 4. Click Handler Flow (`frontend/src/App.tsx`)

```typescript
onPointClick={(position) => {
  const locationName = position.name || '';
  const personas = getPersonasForLocation(locationName);
  if (personas.length > 0) {
    setSelectedPersona(personas[0]); // Shows first expert
    setIsModalOpen(true);
  }
}}
```

#### 5. Persona Modal (`frontend/src/components/PersonaModal.tsx`)

Displays expert information:
- Name, title, location
- Professional bio
- Industry and expertise areas
- Years of experience
- Key market insights
- Action button for consultation

---

## 📊 Persona Structure

```typescript
interface Persona {
  id: string;              // Unique identifier (e.g., 'ny-1')
  name: string;            // Full name (e.g., 'Sarah Mitchell')
  title: string;           // Professional title
  location: string;        // City, Country (e.g., 'New York, USA')
  industry: string;        // Primary industry focus
  expertise: string[];     // Array of expertise areas
  experience: string;      // Years (e.g., '20+ years')
  bio: string;            // Professional background paragraph
  insights?: string[];    // Key market insights (optional)
  avatar?: string;        // Avatar URL (optional, uses initials if not provided)
}
```

---

## 🎨 Design System

### Colors
- **Primary Background**: `#000000` (pure black)
- **Globe Color**: `#0b0b0f` (dark blue-black)
- **Atmosphere**: `#7aa2ff` (light blue)
- **Points**: `#8aa0ff` (medium blue) / `#e6efff` (light blue)
- **Text Primary**: `#ffffff` (white)
- **Text Secondary**: `#9ca3af` (gray-400)
- **Accent**: `#3b82f6` (blue-500)

### Typography
- **Headings**: Bold, large (text-4xl to text-7xl)
- **Body**: Regular, readable (text-base to text-xl)
- **Font**: System fonts (sans-serif)

### Spacing
- Consistent padding: `p-4`, `p-6`, `p-8`
- Gap between elements: `gap-2`, `gap-4`, `mb-6`, `mb-8`

---

## 🔄 User Flow

### Main Journey
```
1. Landing Page
   └─> "Explore Nexus" button
   
2. Explore Page
   ├─> Interactive 3D Globe (auto-rotating)
   ├─> 14 clickable location dots
   └─> Chat input for startup ideas
   
3. Click Location Dot
   └─> Persona Modal Opens
       ├─> Expert profile displayed
       ├─> Industry insights shown
       └─> "Consult Expert" CTA
       
4. (Future) Submit Startup Idea
   └─> Multi-agent analysis begins
       ├─> Relevant experts auto-selected
       ├─> Agents analyze in parallel
       ├─> Feedback synthesized
       └─> Results displayed
```

---

## 🚧 Known Issues & Fixes Applied

### Issue #1: Globe Dots Not Clickable
**Problem**: The `three-globe` library doesn't have a built-in `.onPointClick()` method.

**Solution Implemented**:
- Custom raycasting using Three.js `Raycaster`
- Two-phase detection: points first, then fallback
- Increased click threshold (`threshold: 5`) for easier interaction
- Set `pointsMerge: false` to make each dot individually detectable

### Issue #2: Globe Expanding When Typing
**Problem**: Flex layout caused globe to grow when textarea expanded.

**Solution Implemented**:
- Changed globe container from `h-96` to fixed `h-[500px]`
- Added `flex-shrink-0` to prevent shrinking
- Adjusted parent layout to not center vertically

### Issue #3: Location Name Mismatch
**Problem**: Clicking New York showed Tokyo expert (wrong mapping).

**Solution Implemented**:
- Ensured location names in App.tsx data array match exactly with personas.ts keys
- Both use simple names: 'New York', 'London', etc. (not 'New York, USA')
- Added console logging for debugging: `console.log('Clicked on:', name, 'at', lat, lng)`

---

## 🔧 Backend API (Ready for Integration)

### Key Endpoints

**Personas**
- `GET /api/v1/personas` - List all personas
- `GET /api/v1/personas/{id}` - Get specific persona
- `GET /api/v1/personas/location/{name}` - Get personas by location

**Research Sessions**
- `POST /api/v1/research/sessions` - Create new analysis session
- `POST /api/v1/research/sessions/{id}/rounds` - Start feedback round
- `GET /api/v1/research/sessions/{id}/summary` - Get session summary

**WebSocket**
- `WS /api/v1/ws/research/{session_id}` - Real-time agent responses

### Multi-Agent System
- **Auto-selection**: Picks relevant experts based on startup idea
- **Parallel execution**: All agents analyze simultaneously
- **Synthesis**: Combines insights, identifies consensus/divergence
- **Iterative refinement**: Multiple rounds of feedback

---

## 📝 Important Implementation Notes

### Critical Data Consistency Rules

1. **Location Name Matching**:
   ```typescript
   // App.tsx data array
   { name: 'New York', ... }
   
   // personas.ts keys
   'New York': [ ... ]
   
   // BOTH MUST MATCH EXACTLY (case-sensitive)
   ```

2. **Point Rendering Settings**:
   ```typescript
   .pointsMerge(false)        // MUST be false for clicking
   .pointRadius(1.2 or 0.8)   // Smaller = better aesthetics
   ```

3. **Raycaster Threshold**:
   ```typescript
   raycaster.params.Points = { threshold: 5 }; // 5 = good balance
   // Too low = hard to click, too high = inaccurate
   ```

### File Dependencies for Clicking

The clicking feature requires these 4 files to work together:

1. `frontend/src/components/ui/globe.tsx` - Renders globe and detects clicks
2. `frontend/src/App.tsx` - Provides data and click handler
3. `frontend/src/data/personas.ts` - Maps locations to personas
4. `frontend/src/components/PersonaModal.tsx` - Displays persona info

**Any changes to location names must be synchronized across all files.**

---

## 🎯 Next Development Priorities

### Phase 1: Complete Frontend-Backend Integration
- [ ] Connect chat input to backend API
- [ ] Implement session creation on form submit
- [ ] Display agent responses in UI
- [ ] Add loading states and animations

### Phase 2: Enhanced User Experience
- [ ] Add location list view (alternative to clicking)
- [ ] Support multiple personas per location
- [ ] Add persona comparison feature
- [ ] Implement session history

### Phase 3: Real-time Features
- [ ] WebSocket integration for streaming responses
- [ ] Live typing indicators during agent analysis
- [ ] Progress bars for multi-agent coordination
- [ ] Real-time synthesis updates

### Phase 4: Database & Persistence
- [ ] PostgreSQL integration
- [ ] User authentication
- [ ] Save research sessions
- [ ] Export reports to PDF

---

## 🎨 Design Principles

1. **Visual Hierarchy**: Globe is the hero element, draws user attention
2. **Progressive Disclosure**: Show basic info first (globe), details on click (modal)
3. **Immediate Feedback**: Console logs, cursor changes, smooth animations
4. **Aesthetic Minimalism**: Dark theme, clean typography, subtle animations
5. **Responsive Design**: Works on desktop primarily (mobile optimization needed)

---

## 🐛 Debugging Tips

### Click Detection Not Working?

1. **Check Console Logs**:
   ```javascript
   // Should see: "Clicked on: New York at 40.7128 -74.006"
   // If no logs = raycaster not detecting
   // If wrong location = threshold too high
   ```

2. **Verify Location Names**:
   ```typescript
   // Compare these three:
   console.log(position.name);           // From click
   console.log(Object.keys(personasByLocation)); // From personas
   console.log(data.map(d => d.name));   // From App.tsx
   ```

3. **Check Point Visibility**:
   - Open Three.js Inspector in DevTools
   - Look for Points objects in scene graph
   - Verify points are rendered at correct lat/lng

### Modal Not Opening?

1. Check if persona exists for location
2. Verify `isModalOpen` state is updating
3. Check console for React errors
4. Ensure PersonaModal component is rendered

---

## 📦 Dependencies

### Frontend Key Packages
```json
{
  "react": "^18.x",
  "react-router-dom": "^6.x",
  "three": "^0.x",
  "@react-three/fiber": "^8.x",
  "@react-three/drei": "^9.x",
  "three-globe": "^2.x",
  "lucide-react": "^0.x",
  "tailwindcss": "^3.x"
}
```

### Backend Key Packages
```python
fastapi==0.104.1
uvicorn==0.24.0
openai==1.3.7
anthropic==0.7.7
sqlalchemy==2.0.23
redis==5.0.1
```

---

## 🔐 Environment Variables

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Backend (.env)
```bash
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/nexus

# Redis
REDIS_URL=redis://localhost:6379/0
```

---

## 📚 Code Style Guidelines

### TypeScript/React
- Use functional components with hooks
- Type all props with interfaces
- Use `type` for simple types, `interface` for objects
- Keep components under 300 lines
- Extract complex logic to custom hooks

### Python/FastAPI
- Follow PEP 8 style guide
- Use type hints everywhere
- Async/await for all I/O operations
- Pydantic for validation
- Keep endpoints RESTful

### CSS/Tailwind
- Use Tailwind utility classes
- Custom CSS only when necessary
- Dark theme by default
- Responsive breakpoints: sm, md, lg, xl

---

## 🎓 Learning Resources

- **Three.js**: https://threejs.org/docs/
- **React Three Fiber**: https://docs.pmnd.rs/react-three-fiber
- **three-globe**: https://github.com/vasturiano/three-globe
- **FastAPI**: https://fastapi.tiangolo.com/
- **Tailwind CSS**: https://tailwindcss.com/docs

---

## 💡 Success Metrics

### User Experience
- Globe loads in < 2 seconds
- Click detection works 99%+ of the time
- Modal opens in < 200ms
- Globe animation is smooth (60fps)

### Technical Performance
- Agent response time < 30 seconds
- API response time < 500ms
- WebSocket latency < 100ms
- Support 100+ concurrent users

---

## 🚀 Quick Start for New Developers

```bash
# Frontend
cd frontend
npm install
npm run dev
# → http://localhost:5173

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python -m app.main
# → http://localhost:8000
```

---

## 📞 Support & Contact

For questions about this implementation:
1. Check console logs first
2. Review the 4 essential files (globe.tsx, App.tsx, personas.ts, PersonaModal.tsx)
3. Verify location name consistency
4. Test with simplified data if needed

---

## ✅ Testing Checklist

Before considering the clicking feature complete:

- [ ] All 14 location dots are visible
- [ ] Each dot is clickable
- [ ] Clicking shows correct persona for that location
- [ ] Modal opens smoothly with animation
- [ ] Modal can be closed (X button, outside click)
- [ ] Globe doesn't expand when typing in chat
- [ ] Console shows correct location name on click
- [ ] No duplicate personas appearing
- [ ] Dots are appropriately sized (not too big/small)
- [ ] Click detection is accurate (not detecting wrong locations)

---

**Last Updated**: October 2025  
**Version**: 1.0  
**Status**: Production Ready (Frontend), Backend Integration Pending

---

## 🎯 Key Takeaway for Lovable

**The clickable globe pinpoints are the core UX feature.** They must:
1. ✅ Be small and aesthetic (radius 1.2/0.8)
2. ✅ Be directly clickable (not just nearby area)
3. ✅ Open the correct persona modal (exact name matching)
4. ✅ Work consistently across all 14 locations
5. ✅ Not interfere with globe rotation/zoom

Any future changes should preserve this functionality and maintain the location name synchronization between App.tsx and personas.ts.


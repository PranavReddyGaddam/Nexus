import { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar'
import PixelBlast from './PixelBlast/PixelBlast'
import { World } from './components/ui/globe'
import { Mic } from 'lucide-react'
import PersonaModal from './components/PersonaModal'
import ResultsSidebar from './components/ResultsSidebar'
import type { Persona } from './components/PersonaModal'
import { getPersonasForLocation, getAllPersonas } from './data/personas'

interface PersonaRating {
  persona: Persona;
  rating: number;
  sentiment: 'positive' | 'neutral' | 'cautious';
  keyInsight: string;
}

function App() {
  const [chatInput, setChatInput] = useState("");
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [startupIdea, setStartupIdea] = useState("");
  const [analysisResults, setAnalysisResults] = useState<PersonaRating[]>([]);

  // Simulate persona selection and rating based on startup idea keywords
  const analyzeIdea = (idea: string) => {
    const ideaLower = idea.toLowerCase();
    const allPersonas = getAllPersonas();
    
    // Simple keyword matching to select relevant personas
    const relevantPersonas = allPersonas.filter(persona => {
      const industryMatch = persona.industry.toLowerCase().split(' ').some(word => 
        ideaLower.includes(word.toLowerCase())
      );
      const expertiseMatch = persona.expertise.some(exp => 
        ideaLower.includes(exp.toLowerCase().split(' ')[0])
      );
      return industryMatch || expertiseMatch;
    });

    // If no matches, select random 3-5 personas
    const selectedPersonas = relevantPersonas.length > 0 
      ? relevantPersonas.slice(0, 5)
      : allPersonas.sort(() => Math.random() - 0.5).slice(0, 4);

    // Generate sample ratings for each persona
    const results: PersonaRating[] = selectedPersonas.map(persona => {
      const rating = Math.floor(Math.random() * 4) + 6; // 6-10 range
      const sentiment = rating >= 8 ? 'positive' : rating >= 6 ? 'neutral' : 'cautious';
      
      // Pick a random insight from their insights array
      const keyInsight = persona.insights && persona.insights.length > 0
        ? persona.insights[Math.floor(Math.random() * persona.insights.length)]
        : `Based on ${persona.experience} in ${persona.industry}, this shows potential.`;

      return {
        persona,
        rating,
        sentiment,
        keyInsight
      };
    });

    return results.sort((a, b) => b.rating - a.rating); // Sort by rating descending
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (chatInput.trim().length === 0) return;
      
      // Analyze the startup idea
      const results = analyzeIdea(chatInput);
      setStartupIdea(chatInput);
      setAnalysisResults(results);
      setIsSidebarOpen(true);
      
      console.log("Analyzing idea:", chatInput);
      console.log("Selected personas:", results.map(r => r.persona.name));
      
      // Don't clear input immediately so user can see what they submitted
      // setChatInput("");
    }
  };

  const handleSubmit = () => {
    if (chatInput.trim().length === 0) return;
    
    const results = analyzeIdea(chatInput);
    setStartupIdea(chatInput);
    setAnalysisResults(results);
    setIsSidebarOpen(true);
    
    console.log("Analyzing idea:", chatInput);
  };

  const navigate = (path: string) => {
    window.history.pushState({}, "", path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  };

  return (
    <Router>
      <div className="app dark">
        <Navbar onNavigate={navigate} />
        
        <Routes>
          <Route path="/" element={
            <section className="relative min-h-screen">
              <div className="absolute inset-0">
                <PixelBlast
                  variant="square"
                  pixelSize={18}
                  color="#A3BAF0"
                  patternScale={2}
                  patternDensity={0.4}
                  pixelSizeJitter={0.6}
                  enableRipples={false}
                  rippleSpeed={0.4}
                  rippleThickness={0.12}
                  rippleIntensityScale={0.6}
                  liquid={false}
                  liquidStrength={0.1}
                  liquidRadius={1.0}
                  liquidWobbleSpeed={4.5}
                  speed={0.6}
                  edgeFade={0.8}
                  transparent={false}
                />
              </div>
              <main className="relative z-10 flex items-center justify-center min-h-screen bg-black bg-opacity-50">
                <div className="max-w-4xl mx-auto text-center px-4">
                  <h1 className="text-4xl font-medium tracking-tight text-balance text-white sm:text-7xl">
                    AI agents for simulated market research
                  </h1>
                  <p className="text-xl text-gray-300 mb-8">
                    Get a market analysis in minutes, not months.
                  </p>
                  <button className="bg-white text-black px-8 py-4 rounded-full font-semibold hover:bg-gray-200 transition-colors text-lg" onClick={() => navigate("/explore")}>
                    Explore Nexus ↗
                  </button>
                </div>
              </main>
            </section>
          } />
          
          <Route path="/explore" element={
            <div className="min-h-screen flex flex-col items-center px-8 pb-8 bg-black relative">
              <div className="mb-6 text-center pt-8">
                <h2 className="text-3xl font-bold text-white mb-2">Global Expert Network</h2>
                <p className="text-gray-400">
                  {isSidebarOpen 
                    ? "Expert analysis complete - review insights on the right" 
                    : "Click on any location to explore industry experts or submit your startup idea below"}
                </p>
              </div>
              <div className="w-[500px] h-[400px] flex-shrink-0 flex items-center justify-center mb-8 mx-auto">
                <World
                  globeConfig={{
                    globeColor: '#0b0b0f',
                    atmosphereColor: '#7aa2ff',
                    showAtmosphere: true,
                    atmosphereAltitude: 0.22,
                    polygonColor: 'rgba(180,200,255,0.55)',
                    ambientLight: '#ffffff',
                    directionalLeftLight: '#9fb5ff',
                    directionalTopLight: '#9fb5ff',
                    pointLight: '#9fb5ff',
                    autoRotate: true,
                  }}
                  data={[
                    // Financial hubs data - names must match personas.ts exactly
                    { order: 0, startLat: 40.7128, startLng: -74.0060, endLat: 40.7128, endLng: -74.0060, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'New York' },
                    { order: 1, startLat: 51.5074, startLng: -0.1278, endLat: 51.5074, endLng: -0.1278, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'London' },
                    { order: 2, startLat: 35.6895, startLng: 139.6917, endLat: 35.6895, endLng: 139.6917, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Tokyo' },
                    { order: 3, startLat: 22.3193, startLng: 114.1694, endLat: 22.3193, endLng: 114.1694, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Hong Kong' },
                    { order: 4, startLat: 1.3521, startLng: 103.8198, endLat: 1.3521, endLng: 103.8198, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Singapore' },
                    { order: 5, startLat: 31.2304, startLng: 121.4737, endLat: 31.2304, endLng: 121.4737, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Shanghai' },
                    { order: 6, startLat: 50.1109, startLng: 8.6821, endLat: 50.1109, endLng: 8.6821, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Frankfurt' },
                    { order: 7, startLat: 48.8566, startLng: 2.3522, endLat: 48.8566, endLng: 2.3522, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Paris' },
                    { order: 8, startLat: 47.3769, startLng: 8.5417, endLat: 47.3769, endLng: 8.5417, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Zurich' },
                    { order: 9, startLat: 43.6532, startLng: -79.3832, endLat: 43.6532, endLng: -79.3832, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Toronto' },
                    { order: 10, startLat: -33.8688, startLng: 151.2093, endLat: -33.8688, endLng: 151.2093, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Sydney' },
                    { order: 11, startLat: 19.0760, startLng: 72.8777, endLat: 19.0760, endLng: 72.8777, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Mumbai' },
                    { order: 12, startLat: 25.276987, startLng: 55.296249, endLat: 25.276987, endLng: 55.296249, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Dubai' },
                    { order: 13, startLat: 37.5665, startLng: 126.9780, endLat: 37.5665, endLng: 126.9780, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Seoul' },
                  ]}
                  onPointClick={(position) => {
                    const locationName = position.name || '';
                    const personas = getPersonasForLocation(locationName);
                    if (personas.length > 0) {
                      setSelectedPersona(personas[0]); // Show first persona, can be enhanced to show all
                      setIsModalOpen(true);
                    }
                  }}
                />
              </div>
              
              {/* Chatbox */}
              <div className="flex justify-center p-4 w-full">
                <div className={`w-full rounded-2xl bg-gray-900 bg-opacity-85 border border-gray-700 shadow-2xl backdrop-blur-lg ${isSidebarOpen ? 'max-w-xl mr-[400px]' : 'max-w-2xl'}`}>
                  <textarea
                    className="chatbox-input"
                    placeholder="Describe your startup idea... (e.g., 'An AI-powered fitness app that creates personalized workout plans')"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    rows={2}
                  ></textarea>
                  <div className="flex justify-between items-center p-2">
                    <div className="flex items-center gap-2">
                      <button className="w-9 h-9 flex items-center justify-center text-gray-400 bg-gray-800 border border-gray-600 rounded-full cursor-pointer hover:bg-gray-700" aria-label="Attach">
                        <svg
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M21.44 11.05l-9.19 9.19a6 6 0 1 1-8.49-8.49l10-10a4 4 0 1 1 5.66 5.66l-10 10a2 2 0 1 1-2.83-2.83l9.19-9.19" />
                        </svg>
                      </button>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="w-9 h-9 flex items-center justify-center text-gray-400 bg-gray-800 border border-gray-600 rounded-full cursor-pointer hover:bg-gray-700" aria-label="Settings">
                        <svg
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" />
                          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 8 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 3.6 15a1.65 1.65 0 0 0-1.51-1H2a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 3.6 8a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 8 3.6a1.65 1.65 0 0 0 1-1.51V2a2 2 0 1 1 4 0v.09A1.65 1.65 0 0 0 15 3.6a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 20.4 8c.36 0 .7.13.97.36" />
                        </svg>
                      </button>
                      <button className="w-9 h-9 flex items-center justify-center text-gray-400 bg-gray-800 border border-gray-600 rounded-full cursor-pointer hover:bg-gray-700" aria-label="Voice input">
                        <Mic size={18} />
                      </button>
                      <button
                        className={`send-btn${
                          chatInput.trim().length === 0 ? " disabled" : ""
                        }`}
                        onClick={handleSubmit}
                        disabled={chatInput.trim().length === 0}
                        aria-label="Send"
                      >
                        <svg
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        >
                          <path d="M22 2L11 13" />
                          <path d="M22 2l-7 20-4-9-9-4 20-7z" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <PersonaModal
                persona={selectedPersona}
                isOpen={isModalOpen}
                onClose={() => {
                  setIsModalOpen(false);
                  setSelectedPersona(null);
                }}
              />

              <ResultsSidebar
                isOpen={isSidebarOpen}
                onClose={() => setIsSidebarOpen(false)}
                startupIdea={startupIdea}
                results={analysisResults}
                onPersonaClick={(persona) => {
                  setSelectedPersona(persona);
                  setIsModalOpen(true);
                }}
              />
            </div>
          } />
          
          <Route path="/about" element={
            <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-black text-white text-center max-w-4xl mx-auto">
              <h1 className="text-4xl font-medium tracking-tight text-balance text-white sm:text-7xl">About Nexus</h1>
              <p className="text-xl leading-relaxed mb-6 text-gray-300">
                Nexus is an innovative platform designed to connect ideas and foster collaboration.
                We believe in the power of shared knowledge and aim to provide tools that empower
                users to explore, create, and interact with information in new and meaningful ways.
              </p>
              <p className="text-xl leading-relaxed mb-6 text-gray-300">
                Our mission is to build a community where creativity thrives and groundbreaking
                projects come to life. Join us on this journey of discovery and transformation.
              </p>
            </div>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

import React, { useState, useMemo, useCallback, memo } from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar'
import PixelBlast from './PixelBlast/PixelBlast'
import { World } from './components/ui/globe'
import { Mic } from 'lucide-react'
import PersonaModal from './components/PersonaModal'
import ResultsSidebar from './components/ResultsSidebar'
import AnalysisTab from './components/AnalysisTab'
import type { Persona } from './components/PersonaModal'
import { getPersonasForLocation, getAllPersonas } from './data/personas'
import { analyzeStartupIdea, LLM_CONFIG, type PersonaRating } from './services/analysisService'

// Wrap World so it won't re-render unless its props change
const MemoWorld = memo(World);

function App() {
  const [chatInput, setChatInput] = useState("");
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [startupIdea, setStartupIdea] = useState("");
  const [analysisResults, setAnalysisResults] = useState<PersonaRating[]>([]);
  const [focusLocation, setFocusLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [highlightedLocations, setHighlightedLocations] = useState<string[]>([]);

  // Analyze startup idea using the analysis service
  const handleAnalyzeIdea = async (idea: string) => {
    const allPersonas = getAllPersonas();
    
    try {
      // Call the analysis service
      // Set useRealLLM to true when your backend is ready
      const analysis = await analyzeStartupIdea(allPersonas, {
        idea,
        maxPersonas: 5,
        useRealLLM: LLM_CONFIG.enabled, // Currently false, will use mock
      });
      
      // Process results first
      const topPersona = analysis.results[0];
      const locations = analysis.results.map(r => r.persona.location.split(',')[0]);
      
      // Find focus location for top persona
      let focusPoint = null;
      if (topPersona) {
        const locationData = locationPoints.find(point => point.name === topPersona.persona.location.split(',')[0]);
        if (locationData) {
          focusPoint = { lat: locationData.startLat, lng: locationData.startLng };
        }
      }
      
      // Update all state at once
      setStartupIdea(idea);
      setAnalysisResults(analysis.results);
      setHighlightedLocations(locations);
      setFocusLocation(focusPoint);
      
      // Auto-open sidebar on first analysis
      if (!isSidebarOpen) {
        setIsSidebarOpen(true);
      }
      
      console.log("Analysis complete:", {
        idea,
        personasSelected: analysis.results.map(r => r.persona.name),
        averageRating: analysis.summary.averageRating,
        sentiment: analysis.summary.overallSentiment,
        usingLLM: LLM_CONFIG.enabled,
      });
      
    } catch (error) {
      console.error("Analysis failed:", error);
      // Could show an error message to user here
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (chatInput.trim().length === 0) return;
      
      handleAnalyzeIdea(chatInput);
      
      // Don't clear input immediately so user can see what they submitted
      // setChatInput("");
    }
  };

  // Stable globe config (only changes when focus/highlights change)
  const globeConfig = useMemo(() => ({
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
    focusPoint: focusLocation || undefined,
    highlightedPoints: highlightedLocations,
  }), [focusLocation, highlightedLocations]);

  // Stable data array
  const pointsData = useMemo(() => ([
    { order: 0,  startLat: 40.7128,  startLng: -74.0060,  endLat: 40.7128,  endLng: -74.0060,  arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'New York' },
    { order: 1,  startLat: 51.5074,  startLng: -0.1278,   endLat: 51.5074,  endLng: -0.1278,   arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'London' },
    { order: 2,  startLat: 35.6895,  startLng: 139.6917,  endLat: 35.6895,  endLng: 139.6917,  arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Tokyo' },
    { order: 3,  startLat: 22.3193,  startLng: 114.1694,  endLat: 22.3193,  endLng: 114.1694,  arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Hong Kong' },
    { order: 4,  startLat: 1.3521,   startLng: 103.8198,  endLat: 1.3521,   endLng: 103.8198,  arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Singapore' },
    { order: 5,  startLat: 31.2304,  startLng: 121.4737,  endLat: 31.2304,  endLng: 121.4737,  arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Shanghai' },
    { order: 6,  startLat: 50.1109,  startLng: 8.6821,    endLat: 50.1109,  endLng: 8.6821,    arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Frankfurt' },
    { order: 7,  startLat: 48.8566,  startLng: 2.3522,    endLat: 48.8566,  endLng: 2.3522,    arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Paris' },
    { order: 8,  startLat: 47.3769,  startLng: 8.5417,    endLat: 47.3769,  endLng: 8.5417,    arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Zurich' },
    { order: 9,  startLat: 43.6532,  startLng: -79.3832,  endLat: 43.6532,  endLng: -79.3832,  arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Toronto' },
    { order: 10, startLat: -33.8688, startLng: 151.2093,  endLat: -33.8688, endLng: 151.2093,  arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Sydney' },
    { order: 11, startLat: 19.0760,  startLng: 72.8777,   endLat: 19.0760,  endLng: 72.8777,   arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Mumbai' },
    { order: 12, startLat: 25.276987,startLng: 55.296249, endLat: 25.276987,endLng: 55.296249, arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Dubai' },
    { order: 13, startLat: 37.5665,  startLng: 126.9780,  endLat: 37.5665,  endLng: 126.9780,  arcAlt: 0, color: '#8aa0ff', importance: 1, name: 'Seoul' },
  ]), []); // never changes

  // Store location points for easy access (for analysis results)
  const locationPoints = useMemo(() => pointsData.map(point => ({
    name: point.name,
    startLat: point.startLat,
    startLng: point.startLng,
  })), []);

  const handleSubmit = () => {
    if (chatInput.trim().length === 0) return;
    handleAnalyzeIdea(chatInput);
  };

  // Clear highlights when closing modal
  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedPersona(null);
    // Only clear focus/highlights if we don't have analysis results
    if (analysisResults.length === 0) {
      setFocusLocation(null);
      setHighlightedLocations([]);
    }
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
                <MemoWorld
                  globeConfig={globeConfig}
                  data={pointsData}
                  onPointClick={useCallback((position: any) => {
                    const locationName = position?.name || '';
                    const personas = getPersonasForLocation(locationName);
                    if (personas.length > 0) {
                      setSelectedPersona(personas[0]);
                      setIsModalOpen(true);
                      
                      // Update focus and highlights when clicking globe points
                      const locationData = locationPoints.find(point => point.name === locationName);
                      if (locationData) {
                        setFocusLocation({ lat: locationData.startLat, lng: locationData.startLng });
                        // If we have analysis results, highlight those locations
                        if (analysisResults.length > 0) {
                          setHighlightedLocations(analysisResults.map(r => r.persona.location.split(',')[0]));
                        } else {
                          // Otherwise just highlight the clicked location
                          setHighlightedLocations([locationName]);
                        }
                      }
                    }
                  }, [locationPoints, analysisResults])}
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
                onClose={handleModalClose}
              />

              {/* Analysis Tab */}
              <AnalysisTab
                isOpen={isSidebarOpen}
                hasResults={analysisResults.length > 0}
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              />

              {/* Results Sidebar */}
              <ResultsSidebar
                isOpen={isSidebarOpen}
                onClose={() => setIsSidebarOpen(false)}
                startupIdea={startupIdea}
                results={analysisResults}
                onPersonaClick={(persona) => {
                  setSelectedPersona(persona);
                  setIsModalOpen(true);

                  // Update globe focus when clicking persona
                  const locationName = persona.location.split(',')[0];
                  const locationData = locationPoints.find(point => point.name === locationName);
                  if (locationData) {
                    setFocusLocation({ lat: locationData.startLat, lng: locationData.startLng });
                    // Highlight all locations from current analysis
                    setHighlightedLocations(analysisResults.map(r => r.persona.location.split(',')[0]));
                  }
                } } onFocusLocation={function (coords: { lat: number; lng: number; }, opts?: { highlight?: boolean; spinIntoView?: boolean; }): void {
                  throw new Error("Function not implemented.");
                } }              />
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

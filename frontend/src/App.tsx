import React, { useState, useMemo, useCallback, memo } from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar'
import HeroBackground from './components/HeroBackground'
import { World } from './components/ui/globe'
import { Mic } from 'lucide-react'
import FileUpload from './components/FileUpload'
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
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [focusLocation, setFocusLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [highlightedLocations, setHighlightedLocations] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Analyze startup idea using the analysis service
  const handleAnalyzeIdea = async (idea: string) => {
    setIsLoading(true);
    const allPersonas = getAllPersonas();
    
    // Process attached files if any
    const fileContents: { name: string; content: string; }[] = [];
    
    if (selectedFiles.length > 0) {
      try {
        // Read all files
        const readPromises = selectedFiles.map(file => {
          return new Promise<{ name: string; content: string; }>((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
              resolve({
                name: file.name,
                content: reader.result as string
              });
            };
            reader.onerror = reject;
            
            // Read as text if text file, otherwise as data URL
            if (file.type.startsWith('text/') || 
                file.name.endsWith('.json') || 
                file.name.endsWith('.md')) {
              reader.readAsText(file);
            } else {
              reader.readAsDataURL(file);
            }
          });
        });
        
        const results = await Promise.all(readPromises);
        fileContents.push(...results);
      } catch (error) {
        console.error('Error reading files:', error);
      }
    }
    
    try {
      // Call the analysis service
      // Set useRealLLM to true when your backend is ready
      const analysis = await analyzeStartupIdea(allPersonas, {
        idea,
        maxPersonas: 5,
        useRealLLM: LLM_CONFIG.enabled, // Currently false, will use mock
        attachments: fileContents
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
      setSelectedFiles([]); // Clear files after analysis
      
      // Auto-open sidebar on first analysis
      if (!isSidebarOpen) {
        setIsSidebarOpen(true);
      }
      
      setIsLoading(false);
      console.log("Analysis complete:", {
        idea,
        personasSelected: analysis.results.map(r => r.persona.name),
        averageRating: analysis.summary.averageRating,
        sentiment: analysis.summary.overallSentiment,
        usingLLM: LLM_CONFIG.enabled,
      });
      
    } catch (error) {
      console.error("Analysis failed:", error);
      setIsLoading(false);
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
    autoRotate: false,
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
            <section className="min-h-screen pt-16">
              <div className="fixed inset-0">
                <HeroBackground />
              </div>
              <main className="relative z-10 flex items-center justify-center min-h-screen">
                <div className="max-w-4xl mx-auto text-center px-4">
                  <div className="relative">
                    <div className="absolute inset-0 blur-[100px] bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-pink-500/20 rounded-full transform -translate-y-1/2"></div>
                    <h1 className="relative text-4xl font-medium tracking-tight text-balance text-white sm:text-7xl bg-clip-text">
                      Your startup ideas, tested by Experts
                  </h1>
                  </div>
                  <h2 className="text-2xl text-blue-300/90 mt-6 mb-4 font-light">
                    Get instant feedback from virtual VCs, developers, and industry leaders worldwide
                  </h2>
                  <div className="flex flex-wrap justify-center gap-6 mb-8">
                    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm">
                      <span className="text-gray-300">Smart Validation</span>
                    </div>
                    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm">
                      <span className="text-gray-300">Expert Insights</span>
                    </div>
                    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm">
                      <span className="text-gray-300">Market Signals</span>
                    </div>
                  </div>
                  <p className="text-xl text-gray-400 mb-12">
                    Turn your idea into validated insights in seconds
                  </p>
                  <div className="flex flex-col items-center gap-4">
                    {/* Primary CTA */}
                    <button 
                      className="relative group bg-gradient-to-r from-blue-500 to-purple-600 px-8 py-4 rounded-full font-semibold text-lg text-white overflow-hidden transition-all duration-300 hover:shadow-[0_0_30px_-5px] hover:shadow-blue-500/50"
                      onClick={() => navigate("/explore")}
                    >
                      <span className="relative z-10 flex items-center gap-2">
                        Test My Startup Idea
                        <svg 
                          className="w-5 h-5 transition-transform duration-300 transform group-hover:translate-x-1" 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                      </span>
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    </button>

                    {/* Secondary CTA */}
                    <button 
                      className="group px-6 py-2 text-gray-300 hover:text-white transition-colors duration-300"
                      onClick={() => {
                        const demoSection = document.getElementById('how-it-works');
                        demoSection?.scrollIntoView({ behavior: 'smooth' });
                      }}
                    >
                      {/* <span className="flex items-center gap-2">
                        <svg 
                          className="w-5 h-5 text-blue-400" 
                          fill="none" 
                          stroke="currentColor" 
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Watch Demo
                      </span> */}
                  </button>

                    {/* Scroll Indicator */}
                    {/* <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex flex-col items-center animate-bounce">
                      <span className="text-gray-400 text-sm mb-2">See How It Works</span>
                      <svg 
                        className="w-6 h-6 text-gray-400" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                      </svg>
                    </div> */}
                  </div>
                </div>
              </main>
            </section>
          } />
          
          <Route path="/explore" element={
            <div className="min-h-screen flex flex-col items-center px-8 pb-8 bg-black relative pt-16">
              <div className="w-full max-w-6xl mx-auto">
                <div className="mt-8 text-center">
                  <h2 className="text-3xl font-bold text-white mb-2">Global Expert Network</h2>
                  <p className="text-gray-400">
                    {isSidebarOpen 
                      ? "Expert analysis complete - review insights on the right" 
                      : "Click on any location to explore industry experts or submit your startup idea below"}
                  </p>
                </div>
                <div className="w-[500px] h-[400px] flex-shrink-0 flex items-center justify-center my-8 mx-auto">
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
                <div className="flex justify-center p-4 w-full max-w-6xl mx-auto -translate-y-[10%]">
                  <div className={`w-full rounded-2xl bg-gray-900 bg-opacity-85 border border-gray-700 shadow-2xl backdrop-blur-lg ${isSidebarOpen ? 'max-w-xl mr-[400px]' : 'max-w-2xl'}`}>
                  <textarea
                    className={`chatbox-input ${isLoading ? 'opacity-50' : ''}`}
                    disabled={isLoading}
                      placeholder="Describe your startup idea... (e.g., 'An AI-powered fitness app that creates personalized workout plans')"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    rows={2}
                  ></textarea>
                  <div className="flex justify-between items-center p-2">
                    <div className="flex items-center gap-2">
                        <FileUpload
                          selectedFiles={selectedFiles}
                          onFilesSelected={(files) => {
                            // Limit total files to 5
                            const newFiles = [...selectedFiles, ...files];
                            if (newFiles.length > 5) {
                              console.warn('Maximum 5 files allowed');
                              return;
                            }
                            // Limit each file to 10MB
                            const tooLarge = files.some(file => file.size > 10 * 1024 * 1024);
                            if (tooLarge) {
                              console.warn('Files must be under 10MB');
                              return;
                            }
                            setSelectedFiles(newFiles);
                          }}
                          onRemoveFile={(index) => {
                            setSelectedFiles(files => files.filter((_, i) => i !== index));
                          }}
                        />
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
                          disabled={chatInput.trim().length === 0 || isLoading}
                          aria-label="Send"
                        >
                          {isLoading ? (
                            <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-white" />
                          ) : (
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
                          )}
                        </button>
                    </div>
                  </div>
                </div>
                </div>
                
                <PersonaModal
                  persona={selectedPersona}
                  isOpen={isModalOpen}
                  onClose={handleModalClose}
                  analysisContext={
                    selectedPersona && analysisResults.length > 0
                      ? {
                          rating: analysisResults.find(r => r.persona.id === selectedPersona.id)?.rating,
                          sentiment: analysisResults.find(r => r.persona.id === selectedPersona.id)?.sentiment,
                          keyInsight: analysisResults.find(r => r.persona.id === selectedPersona.id)?.keyInsight,
                          startupIdea: startupIdea
                        }
                      : undefined
                  }
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
                  onPersonaClick={useCallback((persona) => {
                    setSelectedPersona(persona);
                    setIsModalOpen(true);

                    // Update globe focus when clicking persona
                    const locationName = persona.location.split(',')[0];
                    const locationData = locationPoints.find(point => point.name === locationName);
                    if (locationData) {
                      setFocusLocation({ lat: locationData.startLat, lng: locationData.startLng });
                      // Highlight all locations from current analysis
                      if (analysisResults.length > 0) {
                        setHighlightedLocations(analysisResults.map(r => r.persona.location.split(',')[0]));
                      } else {
                        setHighlightedLocations([locationName]);
                      }
                    }
                  }, [locationPoints, analysisResults])}
                  onFocusLocation={useCallback((coords, opts) => {
                    setFocusLocation(coords);
                    if (opts?.highlight && analysisResults.length > 0) {
                      setHighlightedLocations(analysisResults.map(r => r.persona.location.split(',')[0]));
                    }
                  }, [analysisResults])}
                />
              </div>
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
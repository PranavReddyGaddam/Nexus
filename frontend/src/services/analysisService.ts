import type { Persona } from '../components/PersonaModal';

export interface PersonaRating {
  persona: Persona;
  rating: number; // 0-10
  sentiment: 'positive' | 'neutral' | 'cautious';
  keyInsight: string;
  relevanceScore?: number; // How relevant this persona is to the idea (0-1)
  detailedAnalysis?: string; // Detailed explanation from the persona
}

export interface AnalysisRequest {
  idea: string;
  maxPersonas?: number;
  useRealLLM?: boolean; // Toggle between mock and real LLM
}

export interface AnalysisResponse {
  results: PersonaRating[];
  summary: {
    averageRating: number;
    overallSentiment: 'positive' | 'neutral' | 'cautious';
    topConcerns: string[];
    topOpportunities: string[];
  };
}

/**
 * Mock implementation - randomly selects personas and generates ratings
 * This simulates what the LLM would do
 */
function mockAnalysis(allPersonas: Persona[], idea: string, maxPersonas: number = 5): PersonaRating[] {
  // Randomly shuffle and select personas
  const shuffled = [...allPersonas].sort(() => Math.random() - 0.5);
  const selectedPersonas = shuffled.slice(0, Math.min(maxPersonas, allPersonas.length));

  // Generate randomized ratings for each
  const results: PersonaRating[] = selectedPersonas.map(persona => {
    const rating = parseFloat((Math.random() * 4 + 5.5).toFixed(1)); // 5.5-9.5 range
    const sentiment = rating >= 8 ? 'positive' : rating >= 6.5 ? 'neutral' : 'cautious';
    
    // Pick a random insight
    const keyInsight = persona.insights && persona.insights.length > 0
      ? persona.insights[Math.floor(Math.random() * persona.insights.length)]
      : `Based on ${persona.experience} in ${persona.industry}, this idea has potential with some considerations.`;

    return {
      persona,
      rating,
      sentiment,
      keyInsight,
      relevanceScore: Math.random(), // Random relevance for now
    };
  });

  // Sort by rating descending
  return results.sort((a, b) => b.rating - a.rating);
}

/**
 * LLM-powered analysis - sends idea to backend for AI analysis
 * PLACEHOLDER: This will call your backend API which uses OpenAI/Anthropic
 */
async function llmAnalysis(allPersonas: Persona[], idea: string, maxPersonas: number = 5): Promise<PersonaRating[]> {
  try {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
    const response = await fetch(`${API_BASE_URL}/rank`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idea, max_personas: maxPersonas }),
    });

    if (!response.ok) throw new Error('LLM analysis failed');

    const data = await response.json();
    const mapped: PersonaRating[] = data.results.map((r: any, idx: number) => {
      const persona: Persona = {
        id: r.persona?.id ?? String(idx + 1),
        name: r.persona?.name ?? `Persona ${idx + 1}`,
        title: r.persona?.title ?? 'Professional',
        location: r.persona?.location ?? 'Unknown',
        industry: r.persona?.industry ?? 'General',
        expertise: r.persona?.expertise ?? [],
        experience: r.persona?.experience ?? '—',
        bio: '',
        insights: [],
      };

      return {
        persona,
        rating: r.rating,
        sentiment: (r.sentiment || 'neutral') as 'positive' | 'neutral' | 'cautious',
        keyInsight: r.keyInsight || '—',
        relevanceScore: r.relevanceScore,
        detailedAnalysis: r.reason || '—',
      };
    });
    return mapped.sort((a, b) => b.rating - a.rating);
  } catch (error) {
    console.error('LLM analysis failed, falling back to mock:', error);
    return mockAnalysis(allPersonas, idea, maxPersonas);
  }
}

/**
 * Main analysis function - automatically chooses between mock and LLM
 * 
 * @param allPersonas - All available personas to choose from
 * @param request - Analysis request with idea and options
 * @returns Analysis response with persona ratings and summary
 */
export async function analyzeStartupIdea(
  allPersonas: Persona[],
  request: AnalysisRequest
): Promise<AnalysisResponse> {
  const { idea, maxPersonas = 5, useRealLLM = false } = request;

  // Choose analysis method
  const results = useRealLLM 
    ? await llmAnalysis(allPersonas, idea, maxPersonas)
    : mockAnalysis(allPersonas, idea, maxPersonas);

  // Calculate summary statistics
  const averageRating = results.reduce((sum, r) => sum + r.rating, 0) / results.length;
  const positiveCount = results.filter(r => r.sentiment === 'positive').length;
  const totalCount = results.length;
  
  const overallSentiment: 'positive' | 'neutral' | 'cautious' = 
    positiveCount / totalCount >= 0.6 ? 'positive' :
    positiveCount / totalCount >= 0.3 ? 'neutral' : 'cautious';

  // Extract top concerns and opportunities (placeholder - LLM would do this better)
  const topConcerns = results
    .filter(r => r.rating < 7)
    .map(r => r.keyInsight)
    .slice(0, 3);

  const topOpportunities = results
    .filter(r => r.rating >= 8)
    .map(r => r.keyInsight)
    .slice(0, 3);

  return {
    results,
    summary: {
      averageRating: parseFloat(averageRating.toFixed(1)),
      overallSentiment,
      topConcerns: topConcerns.length > 0 ? topConcerns : ['Consider market validation'],
      topOpportunities: topOpportunities.length > 0 ? topOpportunities : ['Explore different angles'],
    },
  };
}

/**
 * Configuration for LLM integration
 * Update these when you're ready to connect to your backend
 */
export const LLM_CONFIG = {
  enabled: true, // Backend ready
  apiUrl: 'http://localhost:8000/api',
  timeout: 30000, // 30 second timeout
  maxRetries: 2,
};

/**
 * Helper to check if LLM is available and configured
 */
export async function checkLLMAvailability(): Promise<boolean> {
  if (!LLM_CONFIG.enabled) return false;
  
  try {
    const response = await fetch(`${LLM_CONFIG.apiUrl}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });
    return response.ok;
  } catch {
    return false;
  }
}


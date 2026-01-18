'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface Insight {
  id: string;
  insight_text: string;
  confidence_score: number;
  supporting_data: any;
  generated_at: string;
}

interface Pattern {
  pattern_type: string;
  description: string;
  frequency: number;
  confidence: number;
  examples: string[];
}

interface AnalyticsDashboardProps {
  surveyId: string;
}

export default function AnalyticsDashboard({ surveyId }: AnalyticsDashboardProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [generating, setGenerating] = useState(false);
  const [selectedInsight, setSelectedInsight] = useState<string | null>(null);
  const [trace, setTrace] = useState<any>(null);

  useEffect(() => {
    loadAnalytics();
  }, [surveyId]);

  const loadAnalytics = async () => {
    setLoading(true);
    
    const [insightsRes, patternsRes] = await Promise.all([
      apiClient.getInsights(surveyId),
      apiClient.getPatterns(surveyId),
    ]);

    if (insightsRes.error) {
      setError(insightsRes.error);
    } else {
      setInsights(insightsRes.data || []);
    }

    if (!patternsRes.error) {
      setPatterns(patternsRes.data || []);
    }

    setLoading(false);
  };

  const handleGenerateInsights = async () => {
    setGenerating(true);
    const response = await apiClient.generateInsights(surveyId);
    
    if (response.error) {
      setError(response.error);
    } else {
      await loadAnalytics();
    }
    
    setGenerating(false);
  };

  const handleViewTrace = async (insightId: string) => {
    setSelectedInsight(insightId);
    const response = await apiClient.getInsightTrace(insightId);
    
    if (response.error) {
      setError(response.error);
    } else {
      setTrace(response.data);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
        <button
          onClick={handleGenerateInsights}
          disabled={generating}
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 disabled:bg-gray-400"
        >
          {generating ? 'Generating...' : 'Generate New Insights'}
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">AI-Generated Insights</h3>
          
          {insights.length === 0 ? (
            <p className="text-gray-600">No insights yet. Generate insights to get started.</p>
          ) : (
            <div className="space-y-4">
              {insights.map((insight) => (
                <div key={insight.id} className="border rounded-lg p-4">
                  <p className="text-gray-800 mb-2">{insight.insight_text}</p>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">
                      Confidence: {(insight.confidence_score * 100).toFixed(1)}%
                    </span>
                    <button
                      onClick={() => handleViewTrace(insight.id)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      View Trace
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Generated: {new Date(insight.generated_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold mb-4">Detected Patterns</h3>
          
          {patterns.length === 0 ? (
            <p className="text-gray-600">No patterns detected yet.</p>
          ) : (
            <div className="space-y-4">
              {patterns.map((pattern, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-gray-900">{pattern.pattern_type}</h4>
                    <span className="text-sm text-gray-600">
                      {pattern.frequency} occurrences
                    </span>
                  </div>
                  <p className="text-gray-700 text-sm mb-2">{pattern.description}</p>
                  <div className="text-xs text-gray-600">
                    Confidence: {(pattern.confidence * 100).toFixed(1)}%
                  </div>
                  {pattern.examples.length > 0 && (
                    <div className="mt-2 text-xs text-gray-500">
                      Examples: {pattern.examples.slice(0, 2).join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {selectedInsight && trace && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">Insight Traceability</h3>
            <button
              onClick={() => {
                setSelectedInsight(null);
                setTrace(null);
              }}
              className="text-gray-600 hover:text-gray-800"
            >
              Close
            </button>
          </div>
          
          <div className="space-y-4">
            <div>
              <h4 className="font-semibold mb-2">Source Responses</h4>
              <div className="bg-gray-50 rounded p-3">
                <p className="text-sm text-gray-700">
                  {trace.source_responses?.length || 0} responses analyzed
                </p>
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-2">Analysis Steps</h4>
              <ol className="list-decimal list-inside space-y-2">
                {trace.analysis_steps?.map((step: string, index: number) => (
                  <li key={index} className="text-sm text-gray-700">{step}</li>
                ))}
              </ol>
            </div>

            {trace.memory_context && trace.memory_context.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Memory Context Used</h4>
                <div className="bg-gray-50 rounded p-3">
                  <p className="text-sm text-gray-700">
                    {trace.memory_context.length} historical context items
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

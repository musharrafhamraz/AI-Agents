'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import AnalyticsDashboard from '@/components/AnalyticsDashboard';

export default function AnalyticsPage() {
  const params = useParams();
  const surveyId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [survey, setSurvey] = useState<any>(null);

  useEffect(() => {
    loadSurvey();
  }, [surveyId]);

  const loadSurvey = async () => {
    setLoading(true);
    const response = await apiClient.getSurvey(surveyId);
    
    if (response.error) {
      setError(response.error);
    } else {
      setSurvey(response.data);
    }
    
    setLoading(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !survey) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error || 'Survey not found'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href={`/surveys/${surveyId}`} className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
            ← Back to Survey
          </Link>
          
          <h1 className="text-3xl font-bold text-gray-900">{survey.title}</h1>
          <p className="text-gray-600 mt-2">AI-Powered Analytics & Insights</p>
        </div>

        <AnalyticsDashboard surveyId={surveyId} />
      </div>
    </main>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import Link from 'next/link';

interface Survey {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
  questions: any[];
}

export default function SurveyList() {
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSurveys();
  }, []);

  const loadSurveys = async () => {
    setLoading(true);
    const response = await apiClient.getSurveys();
    
    if (response.error) {
      setError(response.error);
    } else {
      setSurveys(response.data || []);
    }
    
    setLoading(false);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this survey?')) return;
    
    const response = await apiClient.deleteSurvey(id);
    
    if (response.error) {
      alert(`Error: ${response.error}`);
    } else {
      loadSurveys();
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Surveys</h2>
        <Link
          href="/surveys/create"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Create Survey
        </Link>
      </div>

      {surveys.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-600">No surveys yet. Create your first survey!</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {surveys.map((survey) => (
            <div
              key={survey.id}
              className="border rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold mb-2">{survey.title}</h3>
                  {survey.description && (
                    <p className="text-gray-600 mb-3">{survey.description}</p>
                  )}
                  <div className="flex gap-4 text-sm text-gray-500">
                    <span>Status: <span className="font-medium">{survey.status}</span></span>
                    <span>{survey.questions.length} questions</span>
                    <span>Created: {new Date(survey.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Link
                    href={`/surveys/${survey.id}`}
                    className="text-blue-600 hover:text-blue-800 px-3 py-1 border border-blue-600 rounded"
                  >
                    View
                  </Link>
                  <Link
                    href={`/surveys/${survey.id}/responses`}
                    className="text-green-600 hover:text-green-800 px-3 py-1 border border-green-600 rounded"
                  >
                    Responses
                  </Link>
                  <Link
                    href={`/surveys/${survey.id}/analytics`}
                    className="text-purple-600 hover:text-purple-800 px-3 py-1 border border-purple-600 rounded"
                  >
                    Analytics
                  </Link>
                  <button
                    onClick={() => handleDelete(survey.id)}
                    className="text-red-600 hover:text-red-800 px-3 py-1 border border-red-600 rounded"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import ResponseForm from '@/components/ResponseForm';

export default function SurveyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const surveyId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [survey, setSurvey] = useState<any>(null);
  const [showResponseForm, setShowResponseForm] = useState(false);

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

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this survey?')) return;
    
    const response = await apiClient.deleteSurvey(surveyId);
    
    if (response.error) {
      alert(`Error: ${response.error}`);
    } else {
      router.push('/');
    }
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
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error || 'Survey not found'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
            ← Back to Surveys
          </Link>
          
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{survey.title}</h1>
              {survey.description && (
                <p className="text-gray-600 mt-2">{survey.description}</p>
              )}
              <div className="flex gap-4 text-sm text-gray-500 mt-3">
                <span>Status: <span className="font-medium">{survey.status}</span></span>
                <span>{survey.questions.length} questions</span>
                <span>Created: {new Date(survey.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            
            <div className="flex gap-2">
              <Link
                href={`/surveys/${surveyId}/responses`}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
              >
                View Responses
              </Link>
              <Link
                href={`/surveys/${surveyId}/analytics`}
                className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
              >
                Analytics
              </Link>
              <button
                onClick={handleDelete}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Questions</h2>
            <button
              onClick={() => setShowResponseForm(!showResponseForm)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              {showResponseForm ? 'Hide Form' : 'Fill Out Survey'}
            </button>
          </div>

          {!showResponseForm ? (
            <div className="space-y-4">
              {survey.questions.map((question: any, index: number) => (
                <div key={question.id} className="border rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <span className="font-semibold text-gray-700">{index + 1}.</span>
                    <div className="flex-1">
                      <p className="text-gray-900 font-medium">{question.text}</p>
                      <div className="flex gap-3 text-sm text-gray-600 mt-2">
                        <span>Type: {question.type}</span>
                        {question.required && <span className="text-red-600">Required</span>}
                      </div>
                      {question.options && question.options.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm text-gray-600">Options:</p>
                          <ul className="list-disc list-inside text-sm text-gray-700 ml-2">
                            {question.options.map((option: string, i: number) => (
                              <li key={i}>{option}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <ResponseForm
              surveyId={surveyId}
              questions={survey.questions}
              onSubmit={() => {
                setShowResponseForm(false);
                router.push(`/surveys/${surveyId}/responses`);
              }}
            />
          )}
        </div>
      </div>
    </main>
  );
}

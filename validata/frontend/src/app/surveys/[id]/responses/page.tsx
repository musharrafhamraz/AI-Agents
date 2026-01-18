'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { apiClient } from '@/lib/api';
import ValidationStatus from '@/components/ValidationStatus';

export default function ResponsesPage() {
  const params = useParams();
  const surveyId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [survey, setSurvey] = useState<any>(null);
  const [responses, setResponses] = useState<any[]>([]);
  const [selectedResponse, setSelectedResponse] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [surveyId]);

  const loadData = async () => {
    setLoading(true);
    
    const [surveyRes, responsesRes] = await Promise.all([
      apiClient.getSurvey(surveyId),
      apiClient.getSurveyResponses(surveyId),
    ]);

    if (surveyRes.error) {
      setError(surveyRes.error);
    } else {
      setSurvey(surveyRes.data);
    }

    if (!responsesRes.error) {
      setResponses(responsesRes.data || []);
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
          <p className="text-gray-600 mt-2">Survey Responses</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">
              Responses ({responses.length})
            </h2>

            {responses.length === 0 ? (
              <p className="text-gray-600">No responses yet.</p>
            ) : (
              <div className="space-y-3">
                {responses.map((response) => (
                  <div
                    key={response.id}
                    onClick={() => setSelectedResponse(response.id)}
                    className={`border rounded-lg p-4 cursor-pointer hover:shadow-md transition-shadow ${
                      selectedResponse === response.id ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm text-gray-600">
                          Response ID: {response.id.substring(0, 8)}...
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Submitted: {new Date(response.submitted_at).toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500">
                          Channel: {response.channel}
                        </p>
                      </div>
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          response.validation_status === 'validated'
                            ? 'bg-green-100 text-green-800'
                            : response.validation_status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {response.validation_status}
                      </span>
                    </div>
                    <div className="mt-3 text-sm text-gray-700">
                      {response.answers.length} answers
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            {selectedResponse ? (
              <div>
                <h2 className="text-xl font-semibold mb-4">Response Details</h2>
                
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">Answers</h3>
                  <div className="space-y-3">
                    {responses
                      .find(r => r.id === selectedResponse)
                      ?.answers.map((answer: any, index: number) => {
                        const question = survey.questions.find((q: any) => q.id === answer.question_id);
                        return (
                          <div key={index} className="border-l-4 border-blue-500 pl-3">
                            <p className="text-sm font-medium text-gray-700">
                              {question?.text || 'Unknown question'}
                            </p>
                            <p className="text-gray-900 mt-1">
                              {typeof answer.value === 'object' 
                                ? JSON.stringify(answer.value) 
                                : answer.value}
                            </p>
                          </div>
                        );
                      })}
                  </div>
                </div>

                <div className="border-t pt-6">
                  <h3 className="font-semibold mb-3">Validation Status</h3>
                  <ValidationStatus responseId={selectedResponse} />
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-600 py-12">
                Select a response to view details
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { apiClient } from '@/lib/api';

export default function TemplatesPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [templates, setTemplates] = useState<any[]>([]);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    setLoading(true);
    const response = await apiClient.getTemplates();
    
    if (response.error) {
      setError(response.error);
    } else {
      setTemplates(response.data || []);
    }
    
    setLoading(false);
  };

  const handleUseTemplate = async (template: any) => {
    const surveyData = {
      title: template.name,
      description: template.description,
      account_id: 'default-account', // TODO: Get from auth context
      questions: template.questions,
      status: 'draft',
    };

    const response = await apiClient.createSurvey(surveyData);

    if (response.error) {
      alert(`Error: ${response.error}`);
    } else {
      router.push(`/surveys/${response.data.id}`);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
            ← Back to Home
          </Link>
          
          <h1 className="text-3xl font-bold text-gray-900">Survey Templates</h1>
          <p className="text-gray-600 mt-2">
            Start with a pre-built template and customize it to your needs
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {templates.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-600">No templates available yet.</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <div
                key={template.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
              >
                <div className="mb-4">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {template.name}
                  </h3>
                  <p className="text-gray-600 text-sm">{template.description}</p>
                </div>

                <div className="mb-4">
                  <p className="text-sm text-gray-500">
                    {template.questions.length} questions
                  </p>
                  {template.category && (
                    <span className="inline-block mt-2 px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                      {template.category}
                    </span>
                  )}
                </div>

                <button
                  onClick={() => handleUseTemplate(template)}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                >
                  Use Template
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

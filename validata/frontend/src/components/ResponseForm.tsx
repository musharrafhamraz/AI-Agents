'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';

interface Question {
  id: string;
  type: string;
  text: string;
  options?: string[];
  required: boolean;
}

interface ResponseFormProps {
  surveyId: string;
  questions: Question[];
  onSubmit?: () => void;
}

export default function ResponseForm({ surveyId, questions, onSubmit }: ResponseFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [answers, setAnswers] = useState<Record<string, any>>({});

  const handleAnswerChange = (questionId: string, value: any) => {
    setAnswers({ ...answers, [questionId]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required questions
    const missingRequired = questions
      .filter(q => q.required && !answers[q.id])
      .map(q => q.text);
    
    if (missingRequired.length > 0) {
      setError(`Please answer all required questions: ${missingRequired.join(', ')}`);
      return;
    }

    setLoading(true);
    setError(null);

    const responseData = {
      survey_id: surveyId,
      respondent_id: null,
      answers: Object.entries(answers).map(([question_id, value]) => ({
        question_id,
        value,
      })),
      channel: 'form',
    };

    const response = await apiClient.submitResponse(responseData);

    if (response.error) {
      setError(response.error);
      setLoading(false);
    } else {
      setSuccess(true);
      setLoading(false);
      if (onSubmit) {
        setTimeout(onSubmit, 1500);
      }
    }
  };

  if (success) {
    return (
      <div className="bg-green-50 border border-green-200 text-green-700 px-6 py-8 rounded-lg text-center">
        <div className="text-4xl mb-4">✓</div>
        <h3 className="text-xl font-semibold mb-2">Response Submitted!</h3>
        <p>Your response has been submitted and is being validated.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {questions.map((question, index) => (
        <div key={question.id} className="border rounded-lg p-6 bg-white">
          <label className="block text-lg font-medium text-gray-900 mb-3">
            {index + 1}. {question.text}
            {question.required && <span className="text-red-600 ml-1">*</span>}
          </label>

          {question.type === 'text' && (
            <textarea
              value={answers[question.id] || ''}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
              required={question.required}
            />
          )}

          {question.type === 'multiple_choice' && (
            <div className="space-y-2">
              {question.options?.map((option, optIndex) => (
                <label key={optIndex} className="flex items-center space-x-3 p-3 border rounded hover:bg-gray-50 cursor-pointer">
                  <input
                    type="radio"
                    name={question.id}
                    value={option}
                    checked={answers[question.id] === option}
                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                    required={question.required}
                    className="w-4 h-4"
                  />
                  <span className="text-gray-700">{option}</span>
                </label>
              ))}
            </div>
          )}

          {question.type === 'rating' && (
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  onClick={() => handleAnswerChange(question.id, rating)}
                  className={`px-4 py-2 rounded border ${
                    answers[question.id] === rating
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {rating}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-medium"
      >
        {loading ? 'Submitting...' : 'Submit Response'}
      </button>
    </form>
  );
}

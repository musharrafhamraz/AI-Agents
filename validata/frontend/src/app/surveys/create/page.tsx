import SurveyForm from '@/components/SurveyForm';

export default function CreateSurveyPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Create New Survey</h1>
          <p className="text-gray-600 mt-2">
            Build your survey by adding questions and configuring options
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <SurveyForm />
        </div>
      </div>
    </main>
  );
}

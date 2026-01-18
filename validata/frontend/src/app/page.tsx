import Link from 'next/link';
import SurveyList from '@/components/SurveyList';
import Navigation from '@/components/Navigation';

export default function Home() {
  return (
    <>
      <Navigation />
      <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Validata
          </h1>
          <p className="text-xl text-gray-600">
            AI-Native Survey & Insights Platform with 7-Layer Reasoning Engine
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-blue-600 text-3xl mb-3">🎯</div>
            <h3 className="text-lg font-semibold mb-2">AI-Assisted Surveys</h3>
            <p className="text-gray-600">
              Generate intelligent surveys with context-aware questions using GPT-4
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-green-600 text-3xl mb-3">✓</div>
            <h3 className="text-lg font-semibold mb-2">7-Layer Validation</h3>
            <p className="text-gray-600">
              Advanced validation system to detect AI hallucinations and ensure data quality
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-purple-600 text-3xl mb-3">📊</div>
            <h3 className="text-lg font-semibold mb-2">AI-Powered Analytics</h3>
            <p className="text-gray-600">
              Automated insights generation with full traceability to source data
            </p>
          </div>
        </div>

        {/* Survey List */}
        <div className="bg-white rounded-lg shadow p-6">
          <SurveyList />
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid md:grid-cols-2 gap-4">
          <Link
            href="/surveys/create"
            className="bg-blue-600 text-white p-6 rounded-lg hover:bg-blue-700 transition-colors text-center"
          >
            <div className="text-2xl mb-2">➕</div>
            <div className="font-semibold">Create New Survey</div>
            <div className="text-sm text-blue-100 mt-1">
              Use AI to generate questions or start from a template
            </div>
          </Link>

          <Link
            href="/templates"
            className="bg-purple-600 text-white p-6 rounded-lg hover:bg-purple-700 transition-colors text-center"
          >
            <div className="text-2xl mb-2">📋</div>
            <div className="font-semibold">Browse Templates</div>
            <div className="text-sm text-purple-100 mt-1">
              Start with pre-built survey templates
            </div>
          </Link>
        </div>
      </div>
    </main>
    </>
  );
}

import Link from 'next/link';

export default function Navigation() {
  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center">
            <span className="text-2xl font-bold text-blue-600">Validata</span>
          </Link>

          <div className="flex gap-6">
            <Link
              href="/"
              className="text-gray-700 hover:text-blue-600 font-medium"
            >
              Surveys
            </Link>
            <Link
              href="/templates"
              className="text-gray-700 hover:text-blue-600 font-medium"
            >
              Templates
            </Link>
            <Link
              href="/surveys/create"
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Create Survey
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default function LoadingSpinner() {
  return (
    <div className="flex items-start space-x-3 animate-fade-in">
      {/* AI Avatar */}
      <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center shadow-md">
        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      </div>

      {/* Loading Message */}
      <div className="bg-white dark:bg-gray-800 px-5 py-4 rounded-2xl rounded-tl-sm shadow-md border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="flex space-x-1.5">
            <div className="w-2.5 h-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full animate-bounce"></div>
            <div className="w-2.5 h-2.5 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2.5 h-2.5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
          <span className="text-sm text-gray-600 dark:text-gray-400 font-medium">AI is analyzing...</span>
        </div>
      </div>
    </div>
  );
}
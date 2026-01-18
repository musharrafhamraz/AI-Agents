'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface LayerResult {
  layer: number;
  layer_name: string;
  passed: boolean;
  reasoning: string;
  confidence: number;
  timestamp: string;
}

interface ValidationStatusProps {
  responseId: string;
}

export default function ValidationStatus({ responseId }: ValidationStatusProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [validation, setValidation] = useState<any>(null);

  useEffect(() => {
    loadValidation();
  }, [responseId]);

  const loadValidation = async () => {
    setLoading(true);
    const response = await apiClient.getValidationStatus(responseId);
    
    if (response.error) {
      setError(response.error);
    } else {
      setValidation(response.data);
    }
    
    setLoading(false);
  };

  const handleRevalidate = async () => {
    setLoading(true);
    const response = await apiClient.revalidateResponse(responseId);
    
    if (response.error) {
      setError(response.error);
      setLoading(false);
    } else {
      await loadValidation();
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

  if (!validation) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded">
        Validation pending...
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'validated': return 'green';
      case 'failed': return 'red';
      case 'pending': return 'yellow';
      default: return 'gray';
    }
  };

  const statusColor = getStatusColor(validation.final_status);

  return (
    <div className="space-y-6">
      <div className={`bg-${statusColor}-50 border border-${statusColor}-200 rounded-lg p-6`}>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-xl font-semibold mb-2">
              Validation Status: {validation.final_status.toUpperCase()}
            </h3>
            <p className="text-gray-600">
              Confidence Score: {(validation.confidence_score * 100).toFixed(1)}%
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Validated: {new Date(validation.validated_at).toLocaleString()}
            </p>
          </div>
          <button
            onClick={handleRevalidate}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Revalidate
          </button>
        </div>
      </div>

      <div>
        <h4 className="text-lg font-semibold mb-4">7-Layer Validation Results</h4>
        <div className="space-y-3">
          {validation.layer_results?.map((layer: LayerResult) => (
            <div
              key={layer.layer}
              className={`border rounded-lg p-4 ${
                layer.passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className={`text-2xl ${layer.passed ? 'text-green-600' : 'text-red-600'}`}>
                    {layer.passed ? '✓' : '✗'}
                  </span>
                  <div>
                    <h5 className="font-semibold">
                      Layer {layer.layer}: {layer.layer_name}
                    </h5>
                    <p className="text-sm text-gray-600">
                      Confidence: {(layer.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
              <p className="text-gray-700 text-sm mt-2">{layer.reasoning}</p>
            </div>
          ))}
        </div>
      </div>

      {validation.audit_log && validation.audit_log.length > 0 && (
        <div>
          <h4 className="text-lg font-semibold mb-4">Audit Log</h4>
          <div className="bg-gray-50 border rounded-lg p-4">
            <pre className="text-xs text-gray-700 overflow-x-auto">
              {JSON.stringify(validation.audit_log, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import { useState } from 'react';
import { useBoxes, useBundles, useCreateBundle } from '@/hooks/api';
import type { CreateBundleInput } from '@/hooks/api';

export default function Bundles() {
  const { data: bundles, isLoading: bundlesLoading } = useBundles();
  const { data: boxes } = useBoxes();
  const createBundle = useCreateBundle();
  const [isCreating, setIsCreating] = useState(false);
  const [newBundle, setNewBundle] = useState<CreateBundleInput>({
    name: '',
    description: '',
    boxIds: [],
  });

  if (bundlesLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const handleCreateBundle = async () => {
    if (newBundle.name && newBundle.description && newBundle.boxIds.length > 0) {
      await createBundle.mutateAsync(newBundle);
      setIsCreating(false);
      setNewBundle({ name: '', description: '', boxIds: [] });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Your Bundles</h2>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-primary text-white px-4 py-2 rounded-md hover:bg-blue-600"
        >
          Create New Bundle
        </button>
      </div>

      {isCreating && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Create New Bundle</h3>
          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <input
                type="text"
                id="name"
                value={newBundle.name}
                onChange={(e) => setNewBundle({ ...newBundle, name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                value={newBundle.description}
                onChange={(e) => setNewBundle({ ...newBundle, description: e.target.value })}
                rows={3}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Select Boxes</label>
              <div className="mt-2 space-y-2">
                {boxes?.map((box) => (
                  <label key={box.id} className="inline-flex items-center mr-4">
                    <input
                      type="checkbox"
                      checked={newBundle.boxIds.includes(box.id)}
                      onChange={(e) => {
                        const boxIds = e.target.checked
                          ? [...newBundle.boxIds, box.id]
                          : newBundle.boxIds.filter((id) => id !== box.id);
                        setNewBundle({ ...newBundle, boxIds });
                      }}
                      className="form-checkbox h-4 w-4 text-primary rounded focus:ring-primary"
                    />
                    <span className="ml-2 text-sm text-gray-700">{box.name}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setIsCreating(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateBundle}
                disabled={!newBundle.name || !newBundle.description || newBundle.boxIds.length === 0}
                className="px-4 py-2 text-sm font-medium text-white bg-primary border border-transparent rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                Create Bundle
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {bundles?.map((bundle) => (
          <div key={bundle.id} className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900">{bundle.name}</h3>
            <p className="mt-1 text-sm text-gray-500">{bundle.description}</p>
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900">Boxes:</h4>
              <ul className="mt-2 space-y-2">
                {bundle.boxes.map((box) => (
                  <li key={box.id} className="text-sm text-gray-600">
                    {box.name}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
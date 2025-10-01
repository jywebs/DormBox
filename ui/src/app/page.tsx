'use client';

import { useState } from 'react';
import { useBoxes, useCreateBox } from '@/hooks/api';
import type { CreateBoxInput } from '@/hooks/api';

export default function Home() {
  const { data: boxes, isLoading } = useBoxes();
  const createBox = useCreateBox();
  const [isCreating, setIsCreating] = useState(false);
  const [newBox, setNewBox] = useState<CreateBoxInput>({
    name: '',
    description: '',
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const handleCreateBox = async () => {
    if (newBox.name && newBox.description) {
      await createBox.mutateAsync(newBox);
      setIsCreating(false);
      setNewBox({ name: '', description: '' });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Your Boxes</h2>
        <button
          onClick={() => setIsCreating(true)}
          className="bg-primary text-white px-4 py-2 rounded-md hover:bg-blue-600"
        >
          Add New Box
        </button>
      </div>

      {isCreating && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Create New Box</h3>
          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <input
                type="text"
                id="name"
                value={newBox.name}
                onChange={(e) => setNewBox({ ...newBox, name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                value={newBox.description}
                onChange={(e) => setNewBox({ ...newBox, description: e.target.value })}
                rows={3}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setIsCreating(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateBox}
                disabled={!newBox.name || !newBox.description}
                className="px-4 py-2 text-sm font-medium text-white bg-primary border border-transparent rounded-md hover:bg-blue-600 disabled:opacity-50"
              >
                Create Box
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {boxes?.map((box) => (
          <div key={box.id} className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900">{box.name}</h3>
            <p className="mt-1 text-sm text-gray-500">{box.description}</p>
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900">Items:</h4>
              <ul className="mt-2 space-y-2">
                {box.items.map((item) => (
                  <li key={item.id} className="flex justify-between text-sm">
                    <span className="text-gray-600">{item.name}</span>
                    <span className="text-gray-900">x{item.quantity}</span>
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
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Box {
  id: string;
  name: string;
  description: string;
  items: Array<{
    id: string;
    name: string;
    quantity: number;
  }>;
}

export interface Bundle {
  id: string;
  name: string;
  description: string;
  boxes: Array<{
    id: string;
    name: string;
  }>;
}

export interface CreateBoxInput {
  name: string;
  description: string;
}

export interface CreateBundleInput {
  name: string;
  description: string;
  boxIds: string[];
}

export function useBoxes() {
  return useQuery<Box[]>('boxes', async () => {
    const response = await axios.get(`${API_URL}/api/boxes`);
    return response.data;
  });
}

export function useBox(id: string) {
  return useQuery<Box>(['box', id], async () => {
    const response = await axios.get(`${API_URL}/api/boxes/${id}`);
    return response.data;
  });
}

export function useCreateBox() {
  const queryClient = useQueryClient();
  return useMutation(
    async (input: CreateBoxInput) => {
      const response = await axios.post(`${API_URL}/api/boxes`, input);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('boxes');
      },
    }
  );
}

export function useBundles() {
  return useQuery<Bundle[]>('bundles', async () => {
    const response = await axios.get(`${API_URL}/api/bundles`);
    return response.data;
  });
}

export function useBundle(id: string) {
  return useQuery<Bundle>(['bundle', id], async () => {
    const response = await axios.get(`${API_URL}/api/bundles/${id}`);
    return response.data;
  });
}

export function useCreateBundle() {
  const queryClient = useQueryClient();
  return useMutation(
    async (input: CreateBundleInput) => {
      const response = await axios.post(`${API_URL}/api/bundles`, input);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('bundles');
      },
    }
  );
}
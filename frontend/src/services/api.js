import { smartFetch } from './config';

export async function fetchNodes() {
  const res = await smartFetch('/network/nodes');
  if (!res.ok) throw new Error('Failed to fetch nodes');
  return res.json();
}

export async function fetchRoads() {
  const res = await smartFetch('/network/roads');
  if (!res.ok) throw new Error('Failed to fetch roads');
  return res.json();
}

export async function fetchIncidents() {
  const res = await smartFetch('/incidents');
  if (!res.ok) throw new Error('Failed to fetch incidents');
  return res.json();
}

export async function fetchGovDashboard() {
  const res = await smartFetch('/government/dashboard');
  if (!res.ok) throw new Error('Failed to fetch government dashboard');
  return res.json();
}

export async function fetchCurrentWeather(location) {
  const res = await smartFetch(`/weather/current?location=${encodeURIComponent(location)}`);
  if (!res.ok) throw new Error('Failed to fetch weather');
  return res.json();
}

export async function searchGeocoding(query) {
  const res = await smartFetch(`/geocoding/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchPanIndiaHazards() {
  const res = await smartFetch('/hazards');
  if (!res.ok) return { hazards: [], data_mode: 'prototype' };
  return res.json();
}

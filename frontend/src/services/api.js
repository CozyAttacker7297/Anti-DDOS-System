import axios from 'axios';

// Set up your backend URL (change if needed)
const apiUrl = 'http://localhost:8000/api/attacks';
const baseUrl = 'http://localhost:8000/api';

// GET request: Get all attacks
export const getAttacks = async () => {
  try {
    const response = await axios.get(apiUrl);
    return response.data;
  } catch (error) {
    console.error('Error fetching attacks:', error);
    throw error;
  }
};

// POST request: Create a new attack
export const createAttack = async (attackData) => {
  try {
    const response = await axios.post(apiUrl, attackData);
    return response.data;
  } catch (error) {
    console.error('Error creating attack:', error);
    throw error;
  }
};

// DELETE request: Delete an attack by ID
export const deleteAttack = async (attackId) => {
  try {
    const response = await axios.delete(`${apiUrl}/${attackId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting attack:', error);
    throw error;
  }
};

// PUT request: Update an attack by ID
export const updateAttack = async (attackId, updatedData) => {
  try {
    const response = await axios.put(`${apiUrl}/${attackId}`, updatedData);
    return response.data;
  } catch (error) {
    console.error('Error updating attack:', error);
    throw error;
  }
};

export const getAttackLogs = async () => {
  try {
    const response = await axios.get(`${baseUrl}/attack-logs`);
    return response.data;
  } catch (error) {
    console.error('Error fetching attack logs:', error);
    throw error;
  }
};

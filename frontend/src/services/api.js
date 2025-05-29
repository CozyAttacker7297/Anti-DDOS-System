import axios from 'axios';

// Set up your backend URL (change if needed)
const apiUrl = 'http://localhost:5000/api/attacks';

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

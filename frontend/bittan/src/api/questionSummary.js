import axiosInstance from "./axiosConfig";

export const getQuestionSummary = async (question_id) => {
  try {
    const response = await axiosInstance.get(`/question/${question_id}/summary`);
    return response.data;
  } catch (error) {
    console.error('Error fetching question summary', error);
    throw error;
  }
};

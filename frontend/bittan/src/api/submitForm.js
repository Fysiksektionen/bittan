import axiosInstance from "./axiosConfig";

/**
 * Submits a form to the current session. 
 *
 * @param {string} sessionId - The session ID of the session. 
 * @param {object} formData - The data to be submitted in the form. 
 * @returns {boolean} True if successful.  
 * @throws {Error} If the request fails 
 */

export const submitForm = async (sessionId, formData) => {
	try {
		const response = await axiosInstance.post(
			'/submit_form/',
			{
				session_id: sessionId,
				form_data: formData
			}
		)
		return true
	} catch (error) {
		throw error
	}

}

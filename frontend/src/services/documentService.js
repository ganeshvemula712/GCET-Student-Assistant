import api from "./api";

const documentService = {
  // Get all uploaded documents
  async getDocuments() {
    const response = await api.get("/documents");
    return response.data;
  },

  // Upload a PDF document with optional versioning supersedesId
  async uploadDocument(file, supersedesId = null) {
    const formData = new FormData();
    formData.append("file", file);
    if (supersedesId) {
      formData.append("supersedes_id", supersedesId);
    }

    const response = await api.post(
      "/documents/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  },

  // Delete a document
  async deleteDocument(documentId) {
    const response = await api.delete(
      `/documents/${documentId}`
    );

    return response.data;
  },
};

export default documentService;